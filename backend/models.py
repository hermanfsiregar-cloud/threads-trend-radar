from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

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
    posted_date: str = Field(description="Format YYYY-MM-DD")
    posted_at_formatted: str = Field(description="Human readable time e.g. 2 jam lalu atau 08 Okt 2026")
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
