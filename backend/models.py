from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ThreadMetrics(BaseModel):
    reach: int = Field(default=0, description="Estimated reach / views")
    replies: int = Field(default=0, description="Total replies / comments")
    likes: int = Field(default=0, description="Total likes")
    reposts: int = Field(default=0, description="Total reposts")

class ThreadPost(BaseModel):
    id: str
    tag: str
    author: str
    handle: str
    avatar_url: Optional[str] = None
    country: str = "ID"
    content: str
    post_url: Optional[str] = None
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    hours_ago: int = 1
    metrics: ThreadMetrics

class TagSummary(BaseModel):
    rank: int
    tag: str
    label: str
    icon: str = "mdi-tag-outline"
    total_posts: int
    total_reach: int
    total_comments: int
    growth: str = "+0%"
