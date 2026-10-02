import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from base58 import b58encode
from dotenv import dotenv_values
from nacl.signing import SigningKey
from pymongo import MongoClient


RUNTIME_PATH = Path("/app/tests/iter5_runtime_fixture.json")


def _generate_wallet():
    sk = SigningKey.generate()
    wallet = b58encode(bytes(sk.verify_key)).decode()
    return sk, wallet


def _sign_message(sk: SigningKey, message: str) -> str:
    signed = sk.sign(message.encode("utf-8"))
    return base64.b64encode(signed.signature).decode()


def _auth_token(base_url: str, wallet: str, sk: SigningKey) -> str:
    challenge = requests.get(f"{base_url}/api/auth/challenge/{wallet}", timeout=30)
    challenge.raise_for_status()
    payload = challenge.json()
    signature = _sign_message(sk, payload["message"])
    verify = requests.post(
        f"{base_url}/api/auth/verify",
        json={"wallet": wallet, "nonce": payload["nonce"], "signature": signature},
        timeout=30,
    )
    verify.raise_for_status()
    return verify.json()["token"]


def main():
    frontend_env = dotenv_values("/app/frontend/.env")
    backend_env = dotenv_values("/app/backend/.env")
    base_url = frontend_env["REACT_APP_BACKEND_URL"].rstrip("/")

    creator_sk, creator_wallet = _generate_wallet()
    participant_sk, participant_wallet = _generate_wallet()
    _, mint_wallet = _generate_wallet()

    tag = f"ITER5_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    token_id = mint_wallet
    now = datetime.now(timezone.utc).isoformat()

    mongo = MongoClient(backend_env["MONGO_URL"])
    db = mongo[backend_env["DB_NAME"]]

    db.social_likes.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.social_reposts.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.social_feed.delete_many({"actor": {"$in": [creator_wallet, participant_wallet]}})
    db.activity.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.social_posts.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.follows.delete_many(
        {
            "$or": [
                {"wallet": {"$in": [creator_wallet, participant_wallet]}},
                {"target": {"$in": [creator_wallet, participant_wallet]}},
            ]
        }
    )
    db.profiles.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.files.delete_many({"owner": {"$in": [creator_wallet, participant_wallet]}})
    db.sessions.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.challenges.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.launch_sessions.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})

    db.nexus_registry.delete_many({"token_id": token_id})
    db.communities.delete_many({"token_id": token_id})
    db.tokens.delete_many({"id": token_id})

    creator_token = _auth_token(base_url, creator_wallet, creator_sk)
    participant_token = _auth_token(base_url, participant_wallet, participant_sk)

    db.tokens.insert_one(
        {
            "id": token_id,
            "mint": token_id,
            "name": f"{tag} NEXUS Token",
            "symbol": f"I5{tag[-4:]}",
            "district": "meme",
            "color": "#b6f36e",
            "x": -14,
            "z": 8,
            "creator": creator_wallet,
            "description": "Iter5 isolated social E2E fixture",
            "nexus_launched": True,
            "community_enabled": True,
            "registry_status": "nexus",
            "listed_at": now,
            "image": None,
            "market_cap": None,
            "price": None,
            "change_24h": None,
            "volume_24h": None,
            "liquidity": None,
            "holders": None,
            "source": "TEST",
        }
    )
    db.nexus_registry.insert_one(
        {
            "mint": token_id,
            "token_id": token_id,
            "launch_session_id": f"{tag}_launch_session",
            "creator": creator_wallet,
            "status": "confirmed",
            "registered_at": now,
        }
    )
    db.communities.insert_one({"token_id": token_id, "creator": creator_wallet, "created_at": now})

    db.profiles.insert_many(
        [
            {
                "wallet": creator_wallet,
                "handle": f"{tag.lower()}_creator",
                "display_name": "Iter5 Creator",
                "bio": "",
                "avatar_id": None,
                "avatar_url": None,
                "joined_at": now,
            },
            {
                "wallet": participant_wallet,
                "handle": f"{tag.lower()}_participant",
                "display_name": "Iter5 Participant",
                "bio": "",
                "avatar_id": None,
                "avatar_url": None,
                "joined_at": now,
            },
        ]
    )

    mongo.close()

    runtime_payload = {
        "tag": tag,
        "token_id": token_id,
        "creator_wallet": creator_wallet,
        "participant_wallet": participant_wallet,
        "creator_bearer": creator_token,
        "participant_bearer": participant_token,
    }
    RUNTIME_PATH.write_text(json.dumps(runtime_payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "creator_wallet": creator_wallet,
                "participant_wallet": participant_wallet,
                "creator_bearer": creator_token,
                "participant_bearer": participant_token,
            }
        )
    )


if __name__ == "__main__":
    main()
