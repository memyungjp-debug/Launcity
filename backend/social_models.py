"""Public response contracts: database identifiers never leave the API."""
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class ProfileView(BaseModel):
    model_config = ConfigDict(extra='ignore')
    wallet: str
    handle: str | None = None
    display_name: str
    bio: str = ''
    avatar_id: str | None = None
    avatar_url: str | None = None
    joined_at: str | None = None
    followers: int = 0
    following: int = 0
    viewer_follows: bool = False

class PostView(BaseModel):
    id: str
    token_id: str
    wallet: str
    text: str
    media: list[dict[str,str]] = Field(default_factory=list)
    parent_id: str | None = None
    kind: str
    created_at: str
    deleted: bool = False
    author: ProfileView
    is_creator: bool
    token: dict[str,Any]
    likes: int = 0
    replies: int = 0
    reposts: int = 0
    viewer_liked: bool = False
    viewer_reposted: bool = False
    event_id: str | None = None
    reposted_by: ProfileView | None = None

class FeedView(BaseModel):
    items: list[PostView]
    next_cursor: str | None = None

class CommunityView(BaseModel):
    token_id: str
    creator: str | None
    posts: int
    members: int
    announcements: int

class CommunityDirectoryItem(BaseModel):
    id: str
    name: str
    symbol: str
    image: str | None = None
    color: str
    district: str
    description: str = ''
    posts: int = 0
    members: int = 0