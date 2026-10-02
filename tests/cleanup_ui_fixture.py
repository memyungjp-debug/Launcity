from dotenv import dotenv_values
from pymongo import MongoClient


FIXTURE_TOKEN_ID = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
FIXTURE_CREATOR = "11111111111111111111111111111111"
FIXTURE_PARTICIPANT = "So11111111111111111111111111111111111111112"


def main():
    env = dotenv_values("/app/backend/.env")
    client = MongoClient(env["MONGO_URL"])
    db = client[env["DB_NAME"]]

    db.social_likes.delete_many({"post_id": {"$regex": "^ui-"}})
    db.social_reposts.delete_many({"post_id": {"$regex": "^ui-"}})
    db.social_posts.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.social_feed.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.activity.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.communities.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.nexus_registry.delete_many({"token_id": FIXTURE_TOKEN_ID})
    db.tokens.delete_many({"id": FIXTURE_TOKEN_ID})
    db.profiles.delete_many({"wallet": {"$in": [FIXTURE_CREATOR, FIXTURE_PARTICIPANT]}})
    client.close()


if __name__ == "__main__":
    main()
