from fastapi import FastAPI, Query, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date
from .models import ThreadPost, TagSummary, UserLoginRequest, UserProfile
from .scraper import ThreadsScraper

app = FastAPI(
    title="ThreadLens Intelligence API",
    description="Backend API untuk Scraping dan Ranking Tren Threads dengan Role-based Access Control",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = ThreadsScraper()

# MASTER AKUN LOGIN & ROLES
# 1. Super Admin: full access
# 2. Admin: bisa tambah tagging & scrape
# 3. User: hanya bisa melihat dan searching, tidak bisa tambah tagging
ACCOUNTS_DB = {
    "superadmin": {"password": "password123", "role": "super_admin", "name": "Super Administrator"},
    "admin": {"password": "password123", "role": "admin", "name": "Operations Admin"},
    "user": {"password": "password123", "role": "user", "name": "Guest Analyst"}
}

# 20 Master Tags Terkurasi
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
    TagSummary(rank=16, tag="crypto", label="crypto", icon="mdi-bitcoin", total_posts=540, total_reach=430000, total_comments=14200, growth="+5%"),
    TagSummary(rank=17, tag="buku", label="buku", icon="mdi-book-open-page-variant-outline", total_posts=310, total_reach=390000, total_comments=11400, growth="+13%"),
    TagSummary(rank=18, tag="fashion", label="fashion", icon="mdi-tshirt-crew-outline", total_posts=680, total_reach=370000, total_comments=13900, growth="+18%"),
    TagSummary(rank=19, tag="freelance", label="freelance", icon="mdi-laptop", total_posts=410, total_reach=340000, total_comments=17600, growth="+26%"),
    TagSummary(rank=20, tag="gaming", label="gaming", icon="mdi-gamepad-variant-outline", total_posts=820, total_reach=310000, total_comments=19800, growth="+7%")
]

@app.get("/")
def health_check():
    return {
        "status": "online",
        "engine": "ThreadLens Python Scraper",
        "version": "1.3.0"
    }

# ENDPOINT LOGIN
@app.post("/api/auth/login")
def login(payload: UserLoginRequest):
    user_data = ACCOUNTS_DB.get(payload.username.lower())
    if not user_data or user_data["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Username atau password salah")
    
    return {
        "status": "success",
        "user": {
            "username": payload.username.lower(),
            "role": user_data["role"],
            "name": user_data["name"]
        }
    }

@app.get("/api/tags")
def get_tags(
    sort_by: str = Query("reach", description="Sort criteria: reach, comments, posts"),
    page: int = Query(1, ge=1, description="Halaman paging tags (1, 2, dst)"),
    page_size: int = Query(10, ge=1, le=50, description="Jumlah tag per halaman (default 10)")
):
    """
    Mengambil summary tags dengan Pagination (Next / Previous).
    """
    sort_key = "total_reach"
    if sort_by == "comments":
        sort_key = "total_comments"
    elif sort_by == "posts":
        sort_key = "total_posts"

    sorted_tags = sorted(MASTER_TAGS, key=lambda x: getattr(x, sort_key), reverse=True)
    
    for idx, item in enumerate(sorted_tags):
        item.rank = idx + 1

    total_items = len(sorted_tags)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return {
        "items": sorted_tags[start_idx:end_idx],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

@app.get("/api/posts")
async def get_posts(
    tag: str = Query("coffee", description="Topik kata kunci"),
    country: str = Query("ID", description="Kode negara"),
    target_date: Optional[str] = Query(None, description="Filter tanggal spesifik YYYY-MM-DD"),
    sort_by: str = Query("reach", description="Sort postingan: reach, replies, likes, newest"),
    page: int = Query(1, ge=1, description="Halaman paging posts"),
    page_size: int = Query(5, ge=5, le=50, description="Kelipatan postingan per halaman: 5, 10, 15, 20")
):
    """
    Mengambil postingan terfilter tanggal spesifik & paging.
    Dapat diakses oleh semua role (Super Admin, Admin, dan User).
    """
    clean_tag = tag.replace("#", "").strip().lower()
    posts = await scraper.scrape_by_tag_and_date(
        tag=clean_tag,
        target_date=target_date,
        country=country
    )

    if sort_by == "replies":
        posts.sort(key=lambda p: p.metrics.replies, reverse=True)
    elif sort_by == "likes":
        posts.sort(key=lambda p: p.metrics.likes, reverse=True)
    elif sort_by == "newest":
        posts.sort(key=lambda p: p.posted_date, reverse=True)
    else:
        posts.sort(key=lambda p: p.metrics.reach, reverse=True)

    total_items = len(posts)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return {
        "tag": clean_tag,
        "target_date": target_date or str(date.today()),
        "items": posts[start_idx:end_idx],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

# ROLE-BASED ACCESS CONTROL UNTUK TAMBAH TAGGING
@app.post("/api/tags/register")
def register_tag(
    tag: str, 
    country: str = "ID",
    x_user_role: Optional[str] = Header(None, description="Role pengakses: super_admin, admin, user")
):
    """
    Hanya Super Admin & Admin yang berhak menambahkan tagging baru.
    Role 'user' dilarang menambahkan tagging.
    """
    if x_user_role == "user":
        raise HTTPException(
            status_code=403, 
            detail="Akses Ditolak: Role 'user' hanya dapat mencari postingan dan tidak diizinkan menambahkan tagging baru."
        )

    clean_tag = tag.replace("#", "").strip().lower()
    existing = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)
    
    if not existing:
        new_tag = TagSummary(
            rank=len(MASTER_TAGS) + 1,
            tag=clean_tag,
            label=clean_tag,
            icon="mdi-pound",
            total_posts=180,
            total_reach=380000,
            total_comments=14500,
            growth="+New"
        )
        MASTER_TAGS.append(new_tag)
        return {"status": "created", "tag": new_tag}
        
    return {"status": "exists", "tag": existing}
