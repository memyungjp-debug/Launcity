from datetime import datetime, timezone

from dotenv import dotenv_values
from pymongo import MongoClient


FIXTURE_TOKEN_ID = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
FIXTURE_CREATOR = "11111111111111111111111111111111"
FIXTURE_PARTICIPANT = "So11111111111111111111111111111111111111112"


def main():
    env = dotenv_values("/app/backend/.env")
    client = MongoClient(env["MONGO_URL"])
    db = client[env["DB_NAME"]]
    now = datetime.now(timezone.utc).isoformat()

    db.nexus_registry.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.tokens.delete_many({"id": FIXTURE_TOKEN_ID})
    db.communities.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.social_posts.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.social_feed.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.activity.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.social_likes.delete_many({"post_id": {"$regex": "^ui-"}})
    db.social_reposts.delete_many({"post_id": {"$regex": "^ui-"}})
    db.profiles.delete_many({"wallet": {"$in": [FIXTURE_CREATOR, FIXTURE_PARTICIPANT]}})

    db.tokens.insert_one(
        {
            "id": FIXTURE_TOKEN_ID,
            "mint": FIXTURE_TOKEN_ID,
            "name": "UI Fixture Nexus",
            "symbol": "UIFX",
            "district": "meme",
            "color": "#b6f36e",
            "x": -18,
            "z": -12,
            "creator": FIXTURE_CREATOR,
            "description": "Fixture token for UI verification.",
            "nexus_launched": True,
            "community_enabled": True,
            "registry_status": "nexus",
            "listed_at": now,
        }
    )
    db.nexus_registry.insert_one(
        {
            "mint": FIXTURE_TOKEN_ID,
            "token_id": FIXTURE_TOKEN_ID,
            "launch_session_id": "ui-fixture-session",
            "creator": FIXTURE_CREATOR,
            "status": "confirmed",
            "registered_at": now,
        }
    )
    db.communities.insert_one({"token_id": FIXTURE_TOKEN_ID, "creator": FIXTURE_CREATOR, "created_at": now})
    db.profiles.insert_many(
        [
            {
                "wallet": FIXTURE_CREATOR,
                "handle": "fixture_creator",
                "display_name": "Fixture Creator",
                "bio": "",
                "avatar_id": None,
                "avatar_url": None,
                "joined_at": now,
            },
            {
                "wallet": FIXTURE_PARTICIPANT,
                "handle": "fixture_participant",
                "display_name": "Fixture Participant",
                "bio": "",
                "avatar_id": None,
                "avatar_url": None,
                "joined_at": now,
            },
        ]
    )
    db.social_posts.insert_many(
        [
            {
                "id": "ui-post-root",
                "token_id": FIXTURE_TOKEN_ID,
                "wallet": FIXTURE_CREATOR,
                "text": "Welcome to UIFX community",
                "media": [],
                "parent_id": None,
                "kind": "post",
                "created_at": now,
                "deleted": False,
            },
            {
                "id": "ui-post-ann",
                "token_id": FIXTURE_TOKEN_ID,
                "wallet": FIXTURE_CREATOR,
                "text": "Creator announcement fixture",
                "media": [],
                "parent_id": None,
                "kind": "announcement",
                "created_at": now,
                "deleted": False,
            },
            {
                "id": "ui-post-reply",
                "token_id": FIXTURE_TOKEN_ID,
                "wallet": FIXTURE_PARTICIPANT,
                "text": "Reply fixture",
                "media": [],
                "parent_id": "ui-post-root",
                "kind": "post",
                "created_at": now,
                "deleted": False,
            },
        ]
    )
    db.social_feed.insert_many(
        [
            {
                "id": "post:ui-post-root",
                "token_id": FIXTURE_TOKEN_ID,
                "post_id": "ui-post-root",
                "actor": FIXTURE_CREATOR,
                "kind": "post",
                "created_at": now,
            },
            {
                "id": "post:ui-post-ann",
                "token_id": FIXTURE_TOKEN_ID,
                "post_id": "ui-post-ann",
                "actor": FIXTURE_CREATOR,
                "kind": "post",
                "created_at": now,
            },
        ]
    )
    db.activity.insert_many(
        [
            {
                "id": "ui-activity-1",
                "token_id": FIXTURE_TOKEN_ID,
                "wallet": FIXTURE_CREATOR,
                "kind": "community",
                "text": "Posted in the community",
                "post_id": "ui-post-root",
                "created_at": now,
            },
            {
                "id": "ui-activity-2",
                "token_id": FIXTURE_TOKEN_ID,
                "wallet": FIXTURE_CREATOR,
                "kind": "community",
                "text": "Published a creator announcement",
                "post_id": "ui-post-ann",
                "created_at": now,
            },
        ]
    )

    client.close()
    print(FIXTURE_TOKEN_ID)


if __name__ == "__main__":
    main()
