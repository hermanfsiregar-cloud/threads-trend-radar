from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import ThreadPost, TagSummary
from .scraper import ThreadsScraper

app = FastAPI(
    title="ThreadLens Intelligence API",
    description="Backend API untuk Scraping dan Ranking Tren Threads (Anti-Slop Architecture)",
    version="1.1.0"
)

# Enable CORS agar Frontend index.html dapat mengakses API secara lokal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = ThreadsScraper()

# Master Dataset Tagging Awal (Persistent in-memory)
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
    TagSummary(rank=11, tag="film", label="film", icon="mdi-movie-open-outline", total_posts=890, total_reach=610000, total_comments=32000, growth="+17%"),
    TagSummary(rank=12, tag="travel", label="travel", icon="mdi-airplane", total_posts=730, total_reach=580000, total_comments=21400, growth="+14%"),
    TagSummary(rank=13, tag="fitness", label="fitness", icon="mdi-dumbbell", total_posts=490, total_reach=520000, total_comments=16800, growth="+10%"),
    TagSummary(rank=14, tag="parenting", label="parenting", icon="mdi-baby-face-outline", total_posts=380, total_reach=490000, total_comments=22100, growth="+21%"),
    TagSummary(rank=15, tag="ai", label="ai", icon="mdi-robot-outline", total_posts=620, total_reach=460000, total_comments=15900, growth="+31%"),
    TagSummary(rank=16, tag="crypto", label="crypto", icon="mdi-bitcoin", total_posts=540, total_reach=430000, total_comments=14200, growth="+5%" ),
    TagSummary(rank=17, tag="buku", label="buku", icon="mdi-book-open-page-variant-outline", total_posts=310, total_reach=390000, total_comments=11400, growth="+13%"),
    TagSummary(rank=18, tag="fashion", label="fashion", icon="mdi-tshirt-crew-outline", total_posts=680, total_reach=370000, total_comments=13900, growth="+18%"),
    TagSummary(rank=19, tag="freelance", label="freelance", icon="mdi-laptop", total_posts=410, total_reach=340000, total_comments=17600, growth="+26%"),
    TagSummary(rank=20, tag="gaming", label="gaming", icon="mdi-gamepad-variant-outline", total_posts=820, total_reach=310000, total_comments=19800, growth="+7%"),
    TagSummary(rank=21, tag="resep", label="resep", icon="mdi-chef-hat", total_posts=410, total_reach=285000, total_comments=16400, growth="+12%"),
    TagSummary(rank=22, tag="psikologi", label="psikologi", icon="mdi-brain", total_posts=290, total_reach=240000, total_comments=12200, growth="+19%"),
    TagSummary(rank=23, tag="investasi", label="investasi", icon="mdi-chart-line", total_posts=350, total_reach=210000, total_comments=10100, growth="+8%"),
    TagSummary(rank=24, tag="musik", label="musik", icon="mdi-headphones", total_posts=510, total_reach=180000, total_comments=9400, growth="+4%"),
    TagSummary(rank=25, tag="fotografi", label="fotografi", icon="mdi-camera", total_posts=270, total_reach=150000, total_comments=7800, growth="+6%")
]

@app.get("/")
def health_check():
    return {
        "status": "online",
        "engine": "ThreadLens Python Scraper",
        "version": "1.1.0"
    }

@app.get("/api/tags", response_model=List[TagSummary])
def get_tags(
    sort_by: str = Query("reach", description="Kriteria sorting: reach, comments, posts"),
    limit: Optional[int] = Query(20, description="Batas tag ditampilkan (20, 50, atau null untuk semua)")
):
    """
    Mengambil data leaderboard summary tagging.
    """
    # Menentukan attribute sort
    sort_key = "total_reach"
    if sort_by == "comments":
        sort_key = "total_comments"
    elif sort_by == "posts":
        sort_key = "total_posts"

    sorted_tags = sorted(MASTER_TAGS, key=lambda x: getattr(x, sort_key), reverse=True)
    
    # Re-assign nomor urut ranking
    for idx, item in enumerate(sorted_tags):
        item.rank = idx + 1

    if limit and limit > 0:
        return sorted_tags[:limit]
    return sorted_tags

@app.get("/api/posts", response_model=List[ThreadPost])
async def get_posts(
    tag: str = Query("coffee", description="Topik kata kunci"),
    country: str = Query("ID", description="Kode negara"),
    sort_by: str = Query("reach", description="Sort postingan: reach, replies, likes, newest")
):
    """
    Scrape dan kembalikan daftar postingan terfilter & terurut.
    """
    clean_tag = tag.replace("#", "").strip().lower()
    posts = await scraper.scrape_by_tag(tag=clean_tag, country=country)

    # Sorting hasil posts
    if sort_by == "replies":
        posts.sort(key=lambda p: p.metrics.replies, reverse=True)
    elif sort_by == "likes":
        posts.sort(key=lambda p: p.metrics.likes, reverse=True)
    elif sort_by == "newest":
        posts.sort(key=lambda p: p.hours_ago)
    else:  # Default by reach
        posts.sort(key=lambda p: p.metrics.reach, reverse=True)

    return posts

@app.post("/api/tags/register")
def register_tag(tag: str, country: str = "ID"):
    """
    Mendaftarkan tag baru ke database master jika belum ada.
    """
    clean_tag = tag.replace("#", "").strip().lower()
    existing = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)
    
    if not existing:
        new_tag = TagSummary(
            rank=len(MASTER_TAGS) + 1,
            tag=clean_tag,
            label=clean_tag,
            icon="mdi-pound",
            total_posts=140,
            total_reach=320000,
            total_comments=11400,
            growth="+New"
        )
        MASTER_TAGS.append(new_tag)
        return {"status": "created", "tag": new_tag}
        
    return {"status": "exists", "tag": existing}
