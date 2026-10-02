import io
import base64
from datetime import datetime, timedelta, timezone

import pytest
import requests
from PIL import Image
from nacl.signing import SigningKey


def _tiny_png_bytes(color=(120, 200, 140)):
    image = Image.new("RGB", (8, 8), color)
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def _sign_message(sk: SigningKey, message: str) -> str:
    signed = sk.sign(message.encode())
    return base64.b64encode(signed.signature).decode()


@pytest.fixture()
def nexus_fixture_bundle(mongo_db, creator_identity, participant_identity):
    """registry/social fixture: two confirmed NEXUS tokens + cleanup"""
    creator_wallet = creator_identity["wallet"]
    participant_wallet = participant_identity["wallet"]
    now_iso = datetime.now(timezone.utc).isoformat()

    token_a = {
        "id": "TEST_NEXUS_TOKEN_A",
        "mint": "TEST_NEXUS_TOKEN_A",
        "name": "TEST Nexus Alpha",
        "symbol": "TNXA",
        "district": "meme",
        "color": "#b6f36e",
        "x": -16,
        "z": 9,
        "creator": creator_wallet,
        "description": "alpha",
        "nexus_launched": True,
        "community_enabled": True,
        "registry_status": "nexus",
        "listed_at": now_iso,
    }
    token_b = {
        "id": "TEST_NEXUS_TOKEN_B",
        "mint": "TEST_NEXUS_TOKEN_B",
        "name": "TEST Nexus Beta",
        "symbol": "TNXB",
        "district": "ai",
        "color": "#58b7ff",
        "x": 11,
        "z": -7,
        "creator": creator_wallet,
        "description": "beta",
        "nexus_launched": True,
        "community_enabled": True,
        "registry_status": "nexus",
        "listed_at": now_iso,
    }
    spoof = {
        "id": "TEST_EXTERNAL_SPOOF",
        "mint": "TEST_EXTERNAL_SPOOF",
        "name": "Spoof",
        "symbol": "SPF",
        "district": "defi",
        "color": "#f9b06a",
        "x": 3,
        "z": 3,
        "creator": participant_wallet,
        "nexus_launched": True,
        "community_enabled": True,
        "registry_status": "nexus",
        "listed_at": now_iso,
    }

    for token in [token_a, token_b, spoof]:
        mongo_db.tokens.delete_many({"id": token["id"]})
    for token in [token_a, token_b]:
        mongo_db.nexus_registry.delete_many({"token_id": token["id"]})

    mongo_db.tokens.insert_many([token_a, token_b, spoof])
    mongo_db.nexus_registry.insert_many(
        [
            {
                "mint": token_a["mint"],
                "token_id": token_a["id"],
                "launch_session_id": "TEST_LAUNCH_A",
                "creator": creator_wallet,
                "status": "confirmed",
                "registered_at": now_iso,
            },
            {
                "mint": token_b["mint"],
                "token_id": token_b["id"],
                "launch_session_id": "TEST_LAUNCH_B",
                "creator": creator_wallet,
                "status": "confirmed",
                "registered_at": now_iso,
            },
        ]
    )

    yield {
        "creator": creator_wallet,
        "participant": participant_wallet,
        "token_a": token_a["id"],
        "token_b": token_b["id"],
        "spoof": spoof["id"],
    }

    for token_id in [token_a["id"], token_b["id"], spoof["id"]]:
        posts = list(mongo_db.social_posts.find({"token_id": token_id}, {"id": 1, "_id": 0}))
        post_ids = [p["id"] for p in posts]
        if post_ids:
            mongo_db.social_likes.delete_many({"post_id": {"$in": post_ids}})
            mongo_db.social_reposts.delete_many({"post_id": {"$in": post_ids}})
            mongo_db.social_feed.delete_many({"post_id": {"$in": post_ids}})
            mongo_db.activity.delete_many({"post_id": {"$in": post_ids}})
        mongo_db.social_posts.delete_many({"token_id": token_id})
        mongo_db.communities.delete_many({"token_id": token_id})
        mongo_db.bounties.delete_many({"token_id": token_id})
    mongo_db.submissions.delete_many({"bounty_id": {"$regex": "TEST_"}})
    mongo_db.follows.delete_many({
        "$or": [
            {"wallet": creator_wallet},
            {"wallet": participant_wallet},
            {"target": creator_wallet},
            {"target": participant_wallet},
        ]
    })
    mongo_db.profiles.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    mongo_db.files.delete_many({"owner": {"$in": [creator_wallet, participant_wallet]}})
    mongo_db.nexus_registry.delete_many(
        {"token_id": {"$in": [token_a['id'], token_b['id']]}}
    )
    mongo_db.tokens.delete_many(
        {"id": {"$in": [token_a['id'], token_b['id'], spoof['id']]}}
    )


# world/registry module coverage
def test_world_excludes_unregistered_spoof_tokens(api_client, base_url, nexus_fixture_bundle):
    response = api_client.get(f"{base_url}/api/world")
    assert response.status_code == 200
    payload = response.json()
    ids = {t["id"] for t in payload["tokens"]}
    assert nexus_fixture_bundle["token_a"] in ids
    assert nexus_fixture_bundle["token_b"] in ids
    assert nexus_fixture_bundle["spoof"] not in ids


def test_registry_tokens_returns_only_confirmed_registry(api_client, base_url, nexus_fixture_bundle):
    response = api_client.get(f"{base_url}/api/registry/tokens")
    assert response.status_code == 200
    ids = {row["id"] for row in response.json()}
    assert nexus_fixture_bundle["token_a"] in ids
    assert nexus_fixture_bundle["token_b"] in ids
    assert nexus_fixture_bundle["spoof"] not in ids


def test_community_blocks_external_spoof_token(api_client, base_url, creator_auth_headers, nexus_fixture_bundle):
    response = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['spoof']}/posts",
        json={"text": "Hello spoof", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert response.status_code == 403


# social module coverage
def test_social_whitespace_validation_and_basic_post(api_client, base_url, creator_auth_headers, nexus_fixture_bundle):
    bad = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "    ", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert bad.status_code == 422

    good = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "TEST hello community", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert good.status_code == 200
    body = good.json()
    assert body["text"] == "TEST hello community"
    assert body["token_id"] == nexus_fixture_bundle["token_a"]


def test_social_cross_token_reply_blocked(api_client, base_url, creator_auth_headers, nexus_fixture_bundle):
    parent = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "Parent alpha", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert parent.status_code == 200
    parent_id = parent.json()["id"]

    invalid = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_b']}/posts",
        json={"text": "Wrong token reply", "parent_id": parent_id, "kind": "post"},
        headers=creator_auth_headers,
    )
    assert invalid.status_code == 400


def test_social_announcement_and_delete_permissions(api_client, base_url, creator_auth_headers, participant_auth_headers, nexus_fixture_bundle):
    forbidden_announcement = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "not creator", "kind": "announcement"},
        headers=participant_auth_headers,
    )
    assert forbidden_announcement.status_code == 403

    created = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "creator announcement", "kind": "announcement"},
        headers=creator_auth_headers,
    )
    assert created.status_code == 200
    post_id = created.json()["id"]

    forbidden_delete = api_client.post(
        f"{base_url}/api/social/posts/{post_id}/delete",
        headers=participant_auth_headers,
    )
    assert forbidden_delete.status_code == 403


def test_social_duplicate_like_repost_idempotent(api_client, base_url, creator_auth_headers, participant_auth_headers, nexus_fixture_bundle):
    post = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "idempotent target", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert post.status_code == 200
    post_id = post.json()["id"]

    first_like = api_client.post(f"{base_url}/api/social/posts/{post_id}/like", json={"active": True}, headers=participant_auth_headers)
    second_like = api_client.post(f"{base_url}/api/social/posts/{post_id}/like", json={"active": True}, headers=participant_auth_headers)
    assert first_like.status_code == 200
    assert second_like.status_code == 200
    assert second_like.json()["likes"] == 1

    first_repost = api_client.post(f"{base_url}/api/social/posts/{post_id}/repost", json={"active": True}, headers=participant_auth_headers)
    second_repost = api_client.post(f"{base_url}/api/social/posts/{post_id}/repost", json={"active": True}, headers=participant_auth_headers)
    assert first_repost.status_code == 200
    assert second_repost.status_code == 200
    assert second_repost.json()["reposts"] == 1


def test_social_follow_feed_and_announcements_tab(api_client, base_url, creator_auth_headers, participant_auth_headers, nexus_fixture_bundle):
    post = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "creator post", "kind": "post"},
        headers=creator_auth_headers,
    )
    ann = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "creator ann", "kind": "announcement"},
        headers=creator_auth_headers,
    )
    assert post.status_code == 200
    assert ann.status_code == 200

    follow_1 = api_client.post(
        f"{base_url}/api/profiles/{nexus_fixture_bundle['creator']}/follow",
        json={"active": True},
        headers=participant_auth_headers,
    )
    follow_2 = api_client.post(
        f"{base_url}/api/profiles/{nexus_fixture_bundle['creator']}/follow",
        json={"active": True},
        headers=participant_auth_headers,
    )
    assert follow_1.status_code == 200
    assert follow_2.status_code == 200
    assert follow_2.json()["viewer_follows"] is True

    following_feed = api_client.get(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/feed",
        params={"tab": "following"},
        headers=participant_auth_headers,
    )
    assert following_feed.status_code == 200
    assert len(following_feed.json()["items"]) >= 1

    ann_feed = api_client.get(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/feed",
        params={"tab": "announcements"},
    )
    assert ann_feed.status_code == 200
    assert all(item["kind"] == "announcement" for item in ann_feed.json()["items"])


def test_profile_edit_avatar_and_handle_uniqueness_case_insensitive(
    api_client,
    base_url,
    creator_auth_headers,
    participant_auth_headers,
    nexus_fixture_bundle,
):
    avatar_bytes = _tiny_png_bytes()
    upload = requests.post(
        f"{base_url}/api/media/upload",
        headers={"Authorization": creator_auth_headers["Authorization"]},
        data={"purpose": "avatar"},
        files={"file": ("avatar.png", avatar_bytes, "image/png")},
        timeout=45,
    )
    assert upload.status_code == 200
    avatar_id = upload.json()["id"]

    edit = api_client.patch(
        f"{base_url}/api/profiles/me",
        json={
            "display_name": "  Creator Name  ",
            "handle": "CaseHandle",
            "bio": "  bio trim  ",
            "avatar_id": avatar_id,
        },
        headers=creator_auth_headers,
    )
    assert edit.status_code == 200
    profile = edit.json()
    assert profile["display_name"] == "Creator Name"
    assert profile["handle"] == "casehandle"
    assert profile["avatar_id"] == avatar_id

    conflict = api_client.patch(
        f"{base_url}/api/profiles/me",
        json={
            "display_name": "Participant",
            "handle": "casehandle",
            "bio": "participant",
            "avatar_id": None,
        },
        headers=participant_auth_headers,
    )
    assert conflict.status_code == 409


def test_deleted_post_tombstone_and_replies_accessible(api_client, base_url, creator_auth_headers, participant_auth_headers, nexus_fixture_bundle):
    root = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "Root post", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert root.status_code == 200
    root_id = root.json()["id"]

    reply = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "Reply remains", "parent_id": root_id, "kind": "post"},
        headers=participant_auth_headers,
    )
    assert reply.status_code == 200

    deleted = api_client.post(f"{base_url}/api/social/posts/{root_id}/delete", headers=creator_auth_headers)
    assert deleted.status_code == 200

    root_detail = api_client.get(f"{base_url}/api/social/posts/{root_id}")
    replies = api_client.get(f"{base_url}/api/social/posts/{root_id}/replies")
    assert root_detail.status_code == 200
    assert root_detail.json()["deleted"] is True
    assert replies.status_code == 200
    assert len(replies.json()) == 1


def test_activity_and_feed_pagination(api_client, base_url, creator_auth_headers, nexus_fixture_bundle):
    first = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "A1", "kind": "post"},
        headers=creator_auth_headers,
    )
    second = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "A2", "kind": "post"},
        headers=creator_auth_headers,
    )
    assert first.status_code == 200
    assert second.status_code == 200

    feed = api_client.get(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/feed",
        params={"tab": "all", "limit": 1},
    )
    assert feed.status_code == 200
    first_page = feed.json()
    assert len(first_page["items"]) >= 1

    if first_page["next_cursor"]:
        second_page = api_client.get(
            f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/feed",
            params={"tab": "all", "cursor": first_page["next_cursor"]},
        )
        assert second_page.status_code == 200

    activity = api_client.get(f"{base_url}/api/activity", params={"token_id": nexus_fixture_bundle["token_a"]})
    assert activity.status_code == 200
    assert isinstance(activity.json(), list)
    assert any(item.get("kind") == "community" for item in activity.json())


def test_auth_invalid_signature_and_replayed_nonce(api_client, base_url, creator_identity):
    challenge = api_client.get(f"{base_url}/api/auth/challenge/{creator_identity['wallet']}")
    assert challenge.status_code == 200
    payload = challenge.json()

    bad = api_client.post(
        f"{base_url}/api/auth/verify",
        json={"wallet": creator_identity["wallet"], "nonce": payload["nonce"], "signature": "not_base64"},
    )
    assert bad.status_code == 401

    challenge2 = api_client.get(f"{base_url}/api/auth/challenge/{creator_identity['wallet']}")
    assert challenge2.status_code == 200
    payload2 = challenge2.json()
    signature = _sign_message(creator_identity["sk"], payload2["message"])
    first = api_client.post(
        f"{base_url}/api/auth/verify",
        json={"wallet": creator_identity["wallet"], "nonce": payload2["nonce"], "signature": signature},
    )
    replay = api_client.post(
        f"{base_url}/api/auth/verify",
        json={"wallet": creator_identity["wallet"], "nonce": payload2["nonce"], "signature": signature},
    )
    assert first.status_code == 200
    assert replay.status_code == 401


def test_community_image_binding_and_feed_pagination_over_20(
    api_client,
    base_url,
    creator_auth_headers,
    participant_auth_headers,
    nexus_fixture_bundle,
):
    upload = requests.post(
        f"{base_url}/api/media/upload",
        headers={"Authorization": creator_auth_headers["Authorization"]},
        data={"purpose": "community", "token_id": nexus_fixture_bundle["token_a"]},
        files={"file": ("community.png", _tiny_png_bytes((90, 190, 220)), "image/png")},
        timeout=45,
    )
    assert upload.status_code == 200
    image_id = upload.json()["id"]

    valid_post = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
        json={"text": "Post with bound image", "kind": "post", "media_ids": [image_id]},
        headers=creator_auth_headers,
    )
    assert valid_post.status_code == 200
    media = valid_post.json()["media"]
    assert len(media) == 1
    assert "/api/media/" in media[0]["url"]

    invalid_cross_token = api_client.post(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_b']}/posts",
        json={"text": "Wrong token image", "kind": "post", "media_ids": [image_id]},
        headers=creator_auth_headers,
    )
    assert invalid_cross_token.status_code == 400

    for i in range(11):
        created = api_client.post(
            f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
            json={"text": f"Creator post {i}", "kind": "post"},
            headers=creator_auth_headers,
        )
        assert created.status_code == 200
    for i in range(10):
        created = api_client.post(
            f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/posts",
            json={"text": f"Participant post {i}", "kind": "post"},
            headers=participant_auth_headers,
        )
        assert created.status_code == 200

    page1 = api_client.get(f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/feed", params={"tab": "all"})
    assert page1.status_code == 200
    data1 = page1.json()
    assert len(data1["items"]) == 20
    assert data1["next_cursor"]

    page2 = api_client.get(
        f"{base_url}/api/communities/{nexus_fixture_bundle['token_a']}/feed",
        params={"tab": "all", "cursor": data1["next_cursor"]},
    )
    assert page2.status_code == 200
    data2 = page2.json()
    assert len(data2["items"]) >= 1
    assert {i["event_id"] for i in data1["items"]}.isdisjoint({i["event_id"] for i in data2["items"]})


# launch/bounty module coverage under registry-only rules
def test_launches_deprecated_410_with_auth(api_client, base_url, creator_auth_headers):
    response = api_client.post(f"{base_url}/api/launches", headers=creator_auth_headers)
    assert response.status_code == 410


def test_bounty_creator_rule_and_future_date(api_client, base_url, creator_auth_headers, participant_auth_headers, nexus_fixture_bundle):
    end = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    participant_create = api_client.post(
        f"{base_url}/api/bounties",
        json={
            "token_id": nexus_fixture_bundle["token_a"],
            "name": "Unauthorized",
            "reward": 0.01,
            "objective": "Objective text with enough characters",
            "rules": "rules",
            "eligibility": "open",
            "ends_at": end,
            "distribution": "one winner",
        },
        headers=participant_auth_headers,
    )
    assert participant_create.status_code == 403

    past = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    creator_past = api_client.post(
        f"{base_url}/api/bounties",
        json={
            "token_id": nexus_fixture_bundle["token_a"],
            "name": "Past Date Bounty",
            "reward": 0.01,
            "objective": "Objective text with enough characters",
            "rules": "rules",
            "eligibility": "open",
            "ends_at": past,
            "distribution": "one winner",
        },
        headers=creator_auth_headers,
    )
    assert creator_past.status_code == 400
