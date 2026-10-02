import pytest


EXPECTED_IDS = {"fartcoin", "arc", "ban", "jellyjelly", "ansem"}


# showcase retirement contract
def test_showcase_api_endpoints_return_404(api_client, base_url):
    guest = api_client.get(f"{base_url}/api/showcase/guest")
    config = api_client.get(f"{base_url}/api/showcase/config")

    assert guest.status_code == 404
    assert config.status_code == 404


# live world contract for curated identities
def test_world_returns_exact_five_curated_live_identities(api_client, base_url):
    response = api_client.get(f"{base_url}/api/world")
    assert response.status_code == 200

    data = response.json()
    tokens = data["tokens"]
    curated = [token for token in tokens if token.get("curated_live") is True]
    ids = {token["id"] for token in curated}

    assert len(curated) == 5
    assert ids == EXPECTED_IDS

    for token in curated:
        assert token["curated_live"] is True
        assert token["nexus_launched"] is False
        assert token["creator"] is None
        assert token["community_enabled"] is True


# visibility and no forged registry entries into list
def test_registry_tokens_matches_curated_five_only(api_client, base_url):
    response = api_client.get(f"{base_url}/api/registry/tokens")
    assert response.status_code == 200

    rows = response.json()
    curated = [row for row in rows if row.get("curated_live") is True]
    ids = {row["id"] for row in curated}

    assert len(curated) == 5
    assert ids == EXPECTED_IDS


# idempotency contract at API level
def test_world_endpoint_stable_across_repeated_calls(api_client, base_url):
    first = api_client.get(f"{base_url}/api/world")
    second = api_client.get(f"{base_url}/api/world")

    assert first.status_code == 200
    assert second.status_code == 200

    first_tokens = {
        t["id"]: (t["mint"], t["curated_live"], t["nexus_launched"])
        for t in first.json()["tokens"]
        if t.get("curated_live") is True
    }
    second_tokens = {
        t["id"]: (t["mint"], t["curated_live"], t["nexus_launched"])
        for t in second.json()["tokens"]
        if t.get("curated_live") is True
    }

    assert set(first_tokens.keys()) == EXPECTED_IDS
    assert first_tokens == second_tokens


# market data integrity sanity (no fabricated negative values)
def test_world_market_values_are_non_negative_when_present(api_client, base_url):
    response = api_client.get(f"{base_url}/api/world")
    assert response.status_code == 200

    for token in response.json()["tokens"]:
        if token.get("price") is not None:
            assert token["price"] >= 0
        if token.get("market_cap") is not None:
            assert token["market_cap"] >= 0


# authz contracts on live community and territory writes
def test_unauthenticated_community_write_returns_401(api_client, base_url):
    response = api_client.post(
        f"{base_url}/api/communities/fartcoin/posts",
        json={"text": "Unauth write", "kind": "post"},
    )
    assert response.status_code == 401


def test_unauthorized_presence_edit_returns_403(api_client, base_url, creator_auth_headers):
    response = api_client.patch(
        f"{base_url}/api/tokens/fartcoin/presence",
        json={"description": "test", "color": "#b6f36e", "image": None},
        headers=creator_auth_headers,
    )
    assert response.status_code == 403
