from datetime import datetime, timezone


EXPECTED_LIVE_IDS = {"fartcoin", "arc", "ban", "jellyjelly", "ansem"}


def _create_post(api_client, base_url, token_id, headers, text):
    response = api_client.post(
        f"{base_url}/api/communities/{token_id}/posts",
        json={"text": text, "kind": "post"},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()


# community directory + combined feed contracts
def test_communities_directory_shape_and_no_objectid(api_client, base_url):
    response = api_client.get(f"{base_url}/api/communities")
    assert response.status_code == 200

    rows = response.json()
    ids = {row["id"] for row in rows}
    assert EXPECTED_LIVE_IDS.issubset(ids)

    sample = rows[0]
    assert "_id" not in sample
    assert isinstance(sample["id"], str)
    assert isinstance(sample["name"], str)
    assert isinstance(sample["symbol"], str)
    assert isinstance(sample["district"], str)
    assert isinstance(sample["color"], str)
    assert isinstance(sample["posts"], int)
    assert isinstance(sample["members"], int)


def test_social_feed_includes_posts_from_two_different_live_tokens_and_invalid_cursor_400(
    api_client,
    base_url,
    creator_auth_headers,
    mongo_db,
):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    text_a = f"TEST_FEED_A_{stamp}"
    text_b = f"TEST_FEED_B_{stamp}"

    post_a = _create_post(api_client, base_url, "fartcoin", creator_auth_headers, text_a)
    post_b = _create_post(api_client, base_url, "arc", creator_auth_headers, text_b)

    feed = api_client.get(f"{base_url}/api/social/feed")
    assert feed.status_code == 200
    items = feed.json()["items"]
    by_text = {item["text"]: item for item in items}
    assert text_a in by_text
    assert text_b in by_text
    assert by_text[text_a]["token_id"] == "fartcoin"
    assert by_text[text_b]["token_id"] == "arc"

    invalid = api_client.get(f"{base_url}/api/social/feed", params={"cursor": "invalid_cursor_123"})
    assert invalid.status_code == 400

    post_ids = [post_a["id"], post_b["id"]]
    mongo_db.social_likes.delete_many({"post_id": {"$in": post_ids}})
    mongo_db.social_reposts.delete_many({"post_id": {"$in": post_ids}})
    mongo_db.social_feed.delete_many({"post_id": {"$in": post_ids}})
    mongo_db.activity.delete_many({"post_id": {"$in": post_ids}})
    mongo_db.social_posts.delete_many({"id": {"$in": post_ids}})


def test_social_feed_like_repost_and_delete_flow_updates_counts(
    api_client,
    base_url,
    creator_auth_headers,
    participant_auth_headers,
    mongo_db,
):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    post = _create_post(api_client, base_url, "ban", creator_auth_headers, f"TEST_INTERACT_{stamp}")
    post_id = post["id"]

    like_on = api_client.post(
        f"{base_url}/api/social/posts/{post_id}/like",
        json={"active": True},
        headers=participant_auth_headers,
    )
    assert like_on.status_code == 200
    assert like_on.json()["likes"] == 1
    assert like_on.json()["viewer_liked"] is True

    repost_on = api_client.post(
        f"{base_url}/api/social/posts/{post_id}/repost",
        json={"active": True},
        headers=participant_auth_headers,
    )
    assert repost_on.status_code == 200
    assert repost_on.json()["reposts"] == 1
    assert repost_on.json()["viewer_reposted"] is True

    repost_off = api_client.post(
        f"{base_url}/api/social/posts/{post_id}/repost",
        json={"active": False},
        headers=participant_auth_headers,
    )
    assert repost_off.status_code == 200
    assert repost_off.json()["reposts"] == 0

    like_off = api_client.post(
        f"{base_url}/api/social/posts/{post_id}/like",
        json={"active": False},
        headers=participant_auth_headers,
    )
    assert like_off.status_code == 200
    assert like_off.json()["likes"] == 0

    deleted = api_client.post(f"{base_url}/api/social/posts/{post_id}/delete", headers=creator_auth_headers)
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True

    feed = api_client.get(f"{base_url}/api/social/feed")
    assert feed.status_code == 200
    assert all(item["id"] != post_id for item in feed.json()["items"])

    mongo_db.social_likes.delete_many({"post_id": post_id})
    mongo_db.social_reposts.delete_many({"post_id": post_id})
    mongo_db.social_feed.delete_many({"post_id": post_id})
    mongo_db.activity.delete_many({"post_id": post_id})
    mongo_db.social_posts.delete_many({"id": post_id})


def test_social_feed_pagination_next_cursor_works(api_client, base_url, creator_auth_headers, participant_auth_headers, mongo_db):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    created_ids = []

    for i in range(11):
        post = _create_post(
            api_client,
            base_url,
            "jellyjelly" if i % 2 == 0 else "ansem",
            creator_auth_headers,
            f"TEST_PAGE_CREATOR_{stamp}_{i}",
        )
        created_ids.append(post["id"])

    for i in range(11):
        post = _create_post(
            api_client,
            base_url,
            "fartcoin" if i % 2 == 0 else "arc",
            participant_auth_headers,
            f"TEST_PAGE_PARTICIPANT_{stamp}_{i}",
        )
        created_ids.append(post["id"])

    first = api_client.get(f"{base_url}/api/social/feed")
    assert first.status_code == 200
    first_data = first.json()
    assert len(first_data["items"]) == 20
    assert isinstance(first_data["next_cursor"], str)

    second = api_client.get(f"{base_url}/api/social/feed", params={"cursor": first_data["next_cursor"]})
    assert second.status_code == 200
    second_data = second.json()
    assert len(second_data["items"]) >= 1

    first_ids = {item["event_id"] for item in first_data["items"]}
    second_ids = {item["event_id"] for item in second_data["items"]}
    assert first_ids.isdisjoint(second_ids)

    mongo_db.social_likes.delete_many({"post_id": {"$in": created_ids}})
    mongo_db.social_reposts.delete_many({"post_id": {"$in": created_ids}})
    mongo_db.social_feed.delete_many({"post_id": {"$in": created_ids}})
    mongo_db.activity.delete_many({"post_id": {"$in": created_ids}})
    mongo_db.social_posts.delete_many({"id": {"$in": created_ids}})