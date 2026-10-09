from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import ThreadPost, TagSummary
from .scraper import ThreadsScraper

app = FastAPI(
    title="ThreadLens Intelligence API",
    description="Backend API untuk Scraping dan Ranking Tren Threads (Anti-Slop Architecture)",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = ThreadsScraper()

# Mock dataset Top Tags
MASTER_TAGS: List[TagSummary] = [
    TagSummary(rank=1, tag="coffee", label="coffee", icon="mdi-coffee", total_posts=1240, total_reach=1450000, total_comments=48200, growth="+34%"),
    TagSummary(rank=2, tag="skincare", label="skincare", icon="mdi-sparkles", total_posts=980, total_reach=1290000, total_comments=56100, growth="+28%"),
    TagSummary(rank=3, tag="kuliner", label="kuliner", icon="mdi-noodles", total_posts=1120, total_reach=980000, total_comments=39500, growth="+19%"),
    TagSummary(rank=4, tag="startup", label="startup", icon="mdi-rocket-launch-outline", total_posts=640, total_reach=870000, total_comments=31200, growth="+12%"),
    TagSummary(rank=5, tag="karir", label="karir", icon="mdi-briefcase-outline", total_posts=830, total_reach=820000, total_comments=42100, growth="+22%"),
    TagSummary(rank=6, tag="finansial", label="finansial", icon="mdi-cash-multiple", total_posts=590, total_reach=790000, total_comments=28900, growth="+15%"),
    TagSummary(rank=7, tag="gadget", label="gadget", icon="mdi-cellphone", total_posts=710, total_reach=750000, total_comments=24300, growth="+9%"),
    TagSummary(rank=8, tag="kpop", label="kpop", icon="mdi-music-note", total_posts=1450, total_reach=710000, total_comments=68400, growth="+45%"),
    TagSummary(rank=9, tag="properti", label="properti", icon="mdi-home-city-outline", total_posts=420, total_reach=680000, total_comments=18700, growth="+8%"),
    TagSummary(rank=10, tag="otomotif", label="otomotif", icon="mdi-car-sports", total_posts=510, total_reach=640000, total_comments=19500, growth="+11%"),
]

@app.get("/")
def read_root():
    return {
        "status": "online",
        "engine": "ThreadLens Python Scraper",
        "version": "1.0.0"
    }

@app.get("/api/tags", response_model=List[TagSummary])
def get_tags(
    sort_by: str = Query("reach", description="Sort by: reach, comments, posts"),
    limit: int = Query(20, description="Limit displayed tags (e.g. 20, 50)")
):
    """
    Mengambil daftar summary leaderboard tagging.
    """
    sorted_tags = sorted(
        MASTER_TAGS,
        key=lambda x: getattr(x, f"total_{sort_by}" if sort_by != "reach" else "total_reach"),
        reverse=True
    )
    # Re-rank
    for idx, item in enumerate(sorted_tags):
        item.rank = idx + 1
    return sorted_tags[:limit]

@app.get("/api/posts", response_model=List[ThreadPost])
async def get_posts(
    tag: str = Query("coffee", description="Tagging keyword"),
    country: str = Query("ID", description="Target country"),
    sort_by: str = Query("reach", description="reach, replies, likes, newest")
):
    """
    Scrape atau ambil postingan berdasarkan tag dan filter negara.
    """
    posts = await scraper.scrape_by_tag(tag=tag, country=country)
    return posts
