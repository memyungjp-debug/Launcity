import base64
import io
import os

import pytest
import requests
from PIL import Image
from solders.keypair import Keypair


def _tiny_png_bytes(color=(160, 120, 220)):
    image = Image.new("RGB", (10, 10), color)
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def _upload_token_image(base_url, auth_headers):
    upload = requests.post(
        f"{base_url}/api/media/upload",
        headers={"Authorization": auth_headers["Authorization"]},
        data={"purpose": "token-image"},
        files={"file": ("token.png", _tiny_png_bytes(), "image/png")},
        timeout=60,
    )
    return upload


def _prepare_launch(api_client, base_url, creator_auth_headers):
    upload = _upload_token_image(base_url, creator_auth_headers)
    assert upload.status_code == 200
    image_id = upload.json()["id"]

    mint = str(Keypair().pubkey())
    payload = {
        "mint": mint,
        "name": "TEST Pump Prepare",
        "symbol": "TPREP",
        "description": "prepare flow",
        "image_id": image_id,
        "district": "meme",
        "color": "#b6f36e",
    }
    response = api_client.post(
        f"{base_url}/api/pump/launches/prepare",
        json=payload,
        headers=creator_auth_headers,
    )
    return response


# pump module coverage: deprecations, prepare, and submission guardrails
def test_pump_config_contract(api_client, base_url):
    response = api_client.get(f"{base_url}/api/pump/config")
    assert response.status_code == 200
    data = response.json()
    assert data["launch_mode"] == "nexus_official_sdk"
    assert data["registry_only"] is True
    assert data["creator_fees_managed_by"] == "pump.fun"


def test_deprecated_routes_return_410_authenticated(api_client, base_url, creator_auth_headers):
    verify = api_client.post(
        f"{base_url}/api/pump/verify",
        json={"mint": "ignored", "signature": "ignored"},
        headers=creator_auth_headers,
    )
    imported = api_client.post(
        f"{base_url}/api/pump/import",
        json={"mint": "ignored", "signature": "ignored", "district": "meme", "color": "#b6f36e"},
        headers=creator_auth_headers,
    )
    launches = api_client.post(f"{base_url}/api/launches", headers=creator_auth_headers)
    assert verify.status_code == 410
    assert imported.status_code == 410
    assert launches.status_code == 410


def test_prepare_launch_works_with_real_rpc_and_storage(api_client, base_url, creator_auth_headers):
    prepared = _prepare_launch(api_client, base_url, creator_auth_headers)
    if prepared.status_code in [429, 500, 502, 503, 504]:
        pytest.skip(f"Temporary dependency issue in storage/RPC: {prepared.status_code}")
    assert prepared.status_code == 200
    body = prepared.json()
    assert body["status"] == "prepared"
    assert body["network_fee_lamports"] is None or isinstance(body["network_fee_lamports"], int)
    assert body["transaction_base64"]
    assert body["message_sha256"]
    assert "/api/media/" in body["metadata_uri"]


def test_prepare_rejects_mint_equal_wallet(api_client, base_url, creator_auth_headers, creator_identity):
    upload = _upload_token_image(base_url, creator_auth_headers)
    assert upload.status_code == 200
    payload = {
        "mint": creator_identity["wallet"],
        "name": "TEST Bad Mint",
        "symbol": "TBAD",
        "description": "mint equals wallet",
        "image_id": upload.json()["id"],
        "district": "meme",
        "color": "#b6f36e",
    }
    response = api_client.post(f"{base_url}/api/pump/launches/prepare", json=payload, headers=creator_auth_headers)
    assert response.status_code == 400


def test_submit_rejects_wrong_wallet(api_client, base_url, creator_auth_headers, participant_auth_headers):
    prepared = _prepare_launch(api_client, base_url, creator_auth_headers)
    if prepared.status_code != 200:
        pytest.skip(f"prepare failed with {prepared.status_code}")
    body = prepared.json()
    submit = api_client.post(
        f"{base_url}/api/pump/launches/{body['id']}/submit",
        json={"transaction_base64": body["transaction_base64"]},
        headers=participant_auth_headers,
    )
    assert submit.status_code == 404


def test_submit_rejects_missing_signatures(api_client, base_url, creator_auth_headers):
    prepared = _prepare_launch(api_client, base_url, creator_auth_headers)
    if prepared.status_code != 200:
        pytest.skip(f"prepare failed with {prepared.status_code}")
    body = prepared.json()
    submit = api_client.post(
        f"{base_url}/api/pump/launches/{body['id']}/submit",
        json={"transaction_base64": body["transaction_base64"]},
        headers=creator_auth_headers,
    )
    assert submit.status_code == 400


def test_submit_rejects_tampered_payload(api_client, base_url, creator_auth_headers):
    prepared = _prepare_launch(api_client, base_url, creator_auth_headers)
    if prepared.status_code != 200:
        pytest.skip(f"prepare failed with {prepared.status_code}")
    body = prepared.json()
    raw = bytearray(base64.b64decode(body["transaction_base64"]))
    raw[-1] ^= 1
    tampered = base64.b64encode(bytes(raw)).decode()
    submit = api_client.post(
        f"{base_url}/api/pump/launches/{body['id']}/submit",
        json={"transaction_base64": tampered},
        headers=creator_auth_headers,
    )
    assert submit.status_code in [400, 409]
