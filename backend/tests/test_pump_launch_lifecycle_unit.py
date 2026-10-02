import asyncio
import base64
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

sys.path.append(str(Path(__file__).resolve().parents[1]))
import pump_routes


class _AsyncCollection:
    def __init__(self):
        self.docs = []
        self.operations = []

    @staticmethod
    def _match(doc, query):
        for key, value in query.items():
            if isinstance(value, dict):
                if "$in" in value:
                    if doc.get(key) not in value["$in"]:
                        return False
                else:
                    return False
            elif doc.get(key) != value:
                return False
        return True

    @staticmethod
    def _project(doc, projection):
        if not projection:
            return dict(doc)
        if set(projection.values()) == {0}:
            out = dict(doc)
            for key, mode in projection.items():
                if mode == 0:
                    out.pop(key, None)
            return out
        out = {}
        for key, mode in projection.items():
            if mode and key in doc:
                out[key] = doc[key]
        return out

    async def find_one(self, query, projection=None):
        for doc in self.docs:
            if self._match(doc, query):
                return self._project(doc, projection)
        return None

    async def update_one(self, query, update, upsert=False):
        self.operations.append({"query": query, "update": update, "upsert": upsert})
        target = None
        for doc in self.docs:
            if self._match(doc, query):
                target = doc
                break

        created = False
        if target is None and upsert:
            target = {k: v for k, v in query.items() if not isinstance(v, dict)}
            self.docs.append(target)
            created = True

        if target is None:
            return

        if "$set" in update:
            target.update(update["$set"])
        if "$setOnInsert" in update and created:
            target.update(update["$setOnInsert"])

    async def count_documents(self, query):
        if "$and" in query:
            constraints = query["$and"]
            count = 0
            for doc in self.docs:
                if all(self._match(doc, c) for c in constraints if isinstance(c, dict) and c):
                    count += 1
            return count
        return sum(1 for doc in self.docs if self._match(doc, query))


class _FakeDB:
    def __init__(self):
        self.launch_sessions = _AsyncCollection()
        self.nexus_registry = _AsyncCollection()
        self.tokens = _AsyncCollection()
        self.communities = _AsyncCollection()
        self.activity = _AsyncCollection()


# pump launch lifecycle unit coverage: confirm branches + registration idempotency
def test_confirm_session_pending_to_confirmed_registration(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)
    monkeypatch.setattr(pump_routes, "VersionedTransaction", type("V", (), {"from_bytes": staticmethod(lambda _raw: object())}))
    monkeypatch.setattr(pump_routes, "message_bytes", lambda _tx: b"expected-message")

    async def fake_rpc(method, _params):
        if method == "getSignatureStatuses":
            return {"value": [{"err": None, "confirmationStatus": "confirmed"}]}
        if method == "getTransaction":
            encoded = base64.b64encode(b"chain-transaction").decode()
            return {"transaction": [encoded, "base64"]}
        raise AssertionError(f"Unexpected RPC method {method}")

    async def fake_verify(_mint, _signature, _wallet):
        return {"mint": "MINT_A", "name": "Name A", "symbol": "NMA", "metadata_uri": "uri://meta"}

    async def fake_register(_session, _verified):
        return {"id": "MINT_A"}

    monkeypatch.setattr(pump_routes, "rpc", fake_rpc)
    monkeypatch.setattr(pump_routes, "verify_creation", fake_verify)
    monkeypatch.setattr(pump_routes, "register_confirmed", fake_register)

    session = {
        "id": "session-a",
        "mint": "MINT_A",
        "wallet": "WALLET_A",
        "name": "Name A",
        "symbol": "NMA",
        "metadata_uri": "uri://meta",
        "message_base64": base64.b64encode(b"expected-message").decode(),
        "message_sha256": "unused",
        "signature": "SIG_A",
        "last_valid_block_height": 10,
        "status": "submitted",
    }

    out = asyncio.run(pump_routes.confirm_session(session))
    assert out["status"] == "confirmed"
    assert out["token_id"] == "MINT_A"
    assert any(op["update"].get("$set", {}).get("status") == "confirmed" for op in fake_db.launch_sessions.operations)


def test_confirm_session_failed_chain_tx(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)

    async def fake_rpc(method, _params):
        if method == "getSignatureStatuses":
            return {"value": [{"err": {"InstructionError": [0, "custom"]}, "confirmationStatus": "confirmed"}]}
        raise AssertionError(f"Unexpected RPC method {method}")

    monkeypatch.setattr(pump_routes, "rpc", fake_rpc)
    session = {"id": "session-b", "signature": "SIG_B", "status": "submitted", "last_valid_block_height": 1}
    out = asyncio.run(pump_routes.confirm_session(session))
    assert out["status"] == "failed"
    assert "failed on-chain" in out["error"]


def test_confirm_session_expired_when_no_chain_status(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)

    async def fake_rpc(method, _params):
        if method == "getSignatureStatuses":
            return {"value": [None]}
        if method == "getBlockHeight":
            return 100
        raise AssertionError(f"Unexpected RPC method {method}")

    monkeypatch.setattr(pump_routes, "rpc", fake_rpc)
    session = {"id": "session-c", "signature": "SIG_C", "status": "submitted", "last_valid_block_height": 99}
    out = asyncio.run(pump_routes.confirm_session(session))
    assert out["status"] == "expired"
    assert "expiry" in out["error"]


def test_confirm_session_processed_not_prematurely_expired(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)

    async def fake_rpc(method, _params):
        if method == "getSignatureStatuses":
            return {"value": [{"err": None, "confirmationStatus": "processed"}]}
        raise AssertionError(f"Unexpected RPC method {method}")

    monkeypatch.setattr(pump_routes, "rpc", fake_rpc)
    session = {"id": "session-d", "signature": "SIG_D", "status": "submitted", "last_valid_block_height": 1}
    out = asyncio.run(pump_routes.confirm_session(session))
    assert out["status"] == "submitted"
    assert not any(op["update"].get("$set", {}).get("status") == "expired" for op in fake_db.launch_sessions.operations)


def test_confirm_session_rejects_changed_message(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)
    monkeypatch.setattr(pump_routes, "VersionedTransaction", type("V", (), {"from_bytes": staticmethod(lambda _raw: object())}))
    monkeypatch.setattr(pump_routes, "message_bytes", lambda _tx: b"different-message")

    async def fake_rpc(method, _params):
        if method == "getSignatureStatuses":
            return {"value": [{"err": None, "confirmationStatus": "confirmed"}]}
        if method == "getTransaction":
            return {"transaction": [base64.b64encode(b"raw-chain").decode(), "base64"]}
        raise AssertionError(f"Unexpected RPC method {method}")

    monkeypatch.setattr(pump_routes, "rpc", fake_rpc)
    session = {
        "id": "session-e",
        "mint": "MINT_E",
        "wallet": "WALLET_E",
        "name": "Name E",
        "symbol": "NME",
        "metadata_uri": "uri://meta-e",
        "message_base64": base64.b64encode(b"expected-message").decode(),
        "signature": "SIG_E",
        "status": "submitted",
        "last_valid_block_height": 10,
    }
    with pytest.raises(HTTPException) as exc:
        asyncio.run(pump_routes.confirm_session(session))
    assert exc.value.status_code == 409
    assert "does not match" in exc.value.detail


def test_confirm_session_rejects_changed_identity(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)
    monkeypatch.setattr(pump_routes, "VersionedTransaction", type("V", (), {"from_bytes": staticmethod(lambda _raw: object())}))
    monkeypatch.setattr(pump_routes, "message_bytes", lambda _tx: b"stable-message")

    async def fake_rpc(method, _params):
        if method == "getSignatureStatuses":
            return {"value": [{"err": None, "confirmationStatus": "confirmed"}]}
        if method == "getTransaction":
            return {"transaction": [base64.b64encode(b"raw-chain").decode(), "base64"]}
        raise AssertionError(f"Unexpected RPC method {method}")

    async def fake_verify(_mint, _signature, _wallet):
        return {"mint": "MINT_F", "name": "Different Name", "symbol": "NMF", "metadata_uri": "uri://meta-f"}

    monkeypatch.setattr(pump_routes, "rpc", fake_rpc)
    monkeypatch.setattr(pump_routes, "verify_creation", fake_verify)
    session = {
        "id": "session-f",
        "mint": "MINT_F",
        "wallet": "WALLET_F",
        "name": "Original Name",
        "symbol": "NMF",
        "metadata_uri": "uri://meta-f",
        "message_base64": base64.b64encode(b"stable-message").decode(),
        "signature": "SIG_F",
        "status": "submitted",
        "last_valid_block_height": 10,
    }
    with pytest.raises(HTTPException) as exc:
        asyncio.run(pump_routes.confirm_session(session))
    assert exc.value.status_code == 409
    assert "identity does not match" in exc.value.detail


def test_register_confirmed_is_idempotent_registry_community_activity(monkeypatch):
    fake_db = _FakeDB()
    monkeypatch.setattr(pump_routes, "db", fake_db)

    async def _visible_query():
        return {}

    import ecosystem

    monkeypatch.setattr(ecosystem, "visible_query", _visible_query)

    session = {
        "id": "session-g",
        "mint": "MINT_G",
        "wallet": "WALLET_G",
        "name": "Name G",
        "symbol": "NMG",
        "metadata_uri": "uri://meta-g",
        "description": "desc",
        "district": "meme",
        "color": "#b6f36e",
        "image": "https://example.com/image.webp",
        "signature": "SIG_G",
        "message_sha256": "sha",
    }
    verified = {"mint": "MINT_G", "name": "Name G", "symbol": "NMG", "metadata_uri": "uri://meta-g"}

    first = asyncio.run(pump_routes.register_confirmed(session, verified))
    second = asyncio.run(pump_routes.register_confirmed(session, verified))

    assert first["id"] == "MINT_G"
    assert second["id"] == "MINT_G"
    assert len(fake_db.nexus_registry.docs) == 1
    assert len(fake_db.communities.docs) == 1
    assert len(fake_db.activity.docs) == 1


def test_confirmed_status_available_without_rpc(monkeypatch):
    async def rpc_should_not_run(_method, _params):
        raise AssertionError("RPC should not be called for already confirmed sessions")

    monkeypatch.setattr(pump_routes, "rpc", rpc_should_not_run)
    session = {
        "id": "session-h",
        "mint": "MINT_H",
        "name": "Name H",
        "symbol": "NMH",
        "status": "confirmed",
        "signature": "SIG_H",
        "last_valid_block_height": 100,
    }
    out = asyncio.run(pump_routes.confirm_session(session))
    assert out["status"] == "confirmed"
