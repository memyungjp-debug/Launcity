import json
from pathlib import Path

from dotenv import dotenv_values
from pymongo import MongoClient


RUNTIME_PATH = Path("/app/tests/iter5_runtime_fixture.json")


def main():
    if not RUNTIME_PATH.exists():
        return

    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    creator_wallet = runtime["creator_wallet"]
    participant_wallet = runtime["participant_wallet"]
    token_id = runtime["token_id"]

    env = dotenv_values("/app/backend/.env")
    mongo = MongoClient(env["MONGO_URL"])
    db = mongo[env["DB_NAME"]]

    posts = list(db.social_posts.find({"token_id": token_id}, {"id": 1, "_id": 0}))
    post_ids = [p["id"] for p in posts]

    if post_ids:
        db.social_likes.delete_many({"post_id": {"$in": post_ids}})
        db.social_reposts.delete_many({"post_id": {"$in": post_ids}})
        db.social_feed.delete_many({"post_id": {"$in": post_ids}})
        db.activity.delete_many({"post_id": {"$in": post_ids}})

    db.social_likes.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.social_reposts.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.social_posts.delete_many({"token_id": token_id})
    db.social_feed.delete_many({"token_id": token_id})
    db.activity.delete_many({"token_id": token_id})
    db.communities.delete_many({"token_id": token_id})

    db.follows.delete_many(
        {
            "$or": [
                {"wallet": {"$in": [creator_wallet, participant_wallet]}},
                {"target": {"$in": [creator_wallet, participant_wallet]}},
            ]
        }
    )
    db.profiles.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.files.delete_many(
        {
            "$or": [
                {"owner": {"$in": [creator_wallet, participant_wallet]}},
                {"token_id": token_id},
            ]
        }
    )
    db.sessions.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.challenges.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.launch_sessions.delete_many({"wallet": {"$in": [creator_wallet, participant_wallet]}})
    db.nexus_registry.delete_many({"token_id": token_id})
    db.tokens.delete_many({"id": token_id})

    mongo.close()
    RUNTIME_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
