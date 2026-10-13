from fastapi import FastAPI, Query, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, date
import asyncio
from .models import ThreadPost, TagSummary, UserLoginRequest, UserProfile
from .scraper import ThreadsScraper

app = FastAPI(
    title="ThreadLens Intelligence API",
    description="Backend API untuk Scraping dan Ranking Tren Threads Real-time dengan Background Scraper",
    version="2.0.0"
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
ACCOUNTS_DB = {
    "superadmin": {"password": "password123", "role": "super_admin", "name": "Super Administrator"},
    "admin": {"password": "password123", "role": "admin", "name": "Operations Admin"},
    "user": {"password": "password123", "role": "user", "name": "Guest Analyst"}
}

# MASTER TAGS: Dimulai KOSONG (Semua data sample dummy dibersihkan)
# Tag hanya akan bertambah ketika Admin/Super Admin mendaftarkan kata kunci baru
MASTER_TAGS: List[TagSummary] = []

async def perform_background_scraping(clean_tag: str, country: str = "ID"):
    """
    Fungsi worker asinkron di latar belakang:
    1. Membuka browser Playwright & memindai hasil pencarian Threads secara riil.
    2. Menghitung akumulasi metrik nyata (total posts, total reach, total replies, total likes).
    3. Mengupdate status TagSummary menjadi 'ready'.
    """
    tag_obj = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)
    if not tag_obj:
        return

    tag_obj.status = "scraping"
    tag_obj.status_message = "Membuka browser & mengekstrak data langsung dari Threads..."

    try:
        posts = await scraper.scrape_by_tag(clean_tag, country=country, force_refresh=True)
        if posts:
            tag_obj.total_posts = len(posts)
            tag_obj.total_reach = sum(p.metrics.reach for p in posts)
            tag_obj.total_comments = sum(p.metrics.replies for p in posts)
            tag_obj.total_likes = sum(p.metrics.likes for p in posts)
            tag_obj.status = "ready"
            tag_obj.status_message = f"Selesai ({len(posts)} postingan)"
            tag_obj.last_scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[Worker] Scraping sukses untuk #{clean_tag}: {len(posts)} postingan asli terkumpul.")
        else:
            tag_obj.total_posts = 0
            tag_obj.total_reach = 0
            tag_obj.total_comments = 0
            tag_obj.total_likes = 0
            tag_obj.status = "ready"
            tag_obj.status_message = "Tidak ada postingan publik ditemukan di Threads"
            tag_obj.last_scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[Worker] Scraping selesai untuk #{clean_tag}, tetapi tidak ada postingan.")
    except Exception as e:
        print(f"[Worker Error] Scraping gagal untuk #{clean_tag}: {e}")
        tag_obj.status = "failed"
        tag_obj.status_message = f"Gagal: {str(e)[:50]}"
        tag_obj.last_scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "engine": "ThreadLens Real-time Asynchronous Scraper",
        "version": "2.0.0",
        "active_tags_count": len(MASTER_TAGS)
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

# GET TAGS (Leaderboard Tagging)
@app.get("/api/tags")
def get_tags(
    sort_by: str = Query("reach", description="Sort criteria: reach, comments, posts, likes"),
    page: int = Query(1, ge=1, description="Halaman paging tags"),
    page_size: int = Query(10, ge=1, le=50, description="Jumlah tag per halaman")
):
    sort_key = "total_reach"
    if sort_by == "comments":
        sort_key = "total_comments"
    elif sort_by == "posts":
        sort_key = "total_posts"
    elif sort_by == "likes":
        sort_key = "total_likes"

    sorted_tags = sorted(MASTER_TAGS, key=lambda x: getattr(x, sort_key, 0), reverse=True)
    
    for idx, item in enumerate(sorted_tags):
        item.rank = idx + 1

    total_items = len(sorted_tags)
    total_pages = max(1, (total_items + page_size - 1) // page_size) if total_items > 0 else 1
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

# GET STATUS TAG
@app.get("/api/tags/status/{tag}")
def get_tag_status(tag: str):
    clean_tag = tag.replace("#", "").strip().lower()
    tag_obj = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)
    if not tag_obj:
        raise HTTPException(status_code=404, detail="Tag tidak ditemukan")
    return tag_obj

# GET POSTS (Mendukung semua jenis sorting metrik)
@app.get("/api/posts")
async def get_posts(
    tag: str = Query("coffee", description="Topik kata kunci"),
    country: str = Query("ID", description="Kode negara"),
    sort_by: str = Query("likes", description="Sort postingan: likes, replies, reposts, quotes, shares, reach, newest"),
    target_date: Optional[str] = Query(None, description="Filter tanggal postingan YYYY-MM-DD (opsional)"),
    limit: int = Query(20, ge=1, le=50, description="Jumlah maksimal hasil (default 20)"),
    page: int = Query(1, ge=1, description="Halaman paging posts"),
    page_size: int = Query(20, ge=1, le=50, description="Jumlah postingan per halaman")
):
    clean_tag = tag.replace("#", "").strip().lower()
    tag_obj = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)

    if not tag_obj:
        return {
            "tag": clean_tag,
            "status": "not_found",
            "status_message": f"Tag #{clean_tag} belum terdaftar.",
            "items": [],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": 0,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False
            }
        }

    if tag_obj.status == "scraping":
        return {
            "tag": clean_tag,
            "status": "scraping",
            "status_message": tag_obj.status_message,
            "items": [],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": 0,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False
            }
        }

    posts = await scraper.scrape_by_tag(
        tag=clean_tag,
        country=country
    )

    # Sorting berdasarkan metrik yang dipilih user
    if sort_by == "replies":
        posts.sort(key=lambda p: p.metrics.replies, reverse=True)
    elif sort_by == "likes":
        posts.sort(key=lambda p: p.metrics.likes, reverse=True)
    elif sort_by == "reposts":
        posts.sort(key=lambda p: p.metrics.reposts, reverse=True)
    elif sort_by == "quotes":
        posts.sort(key=lambda p: getattr(p.metrics, "quotes", 0), reverse=True)
    elif sort_by == "shares":
        posts.sort(key=lambda p: p.metrics.shares, reverse=True)
    elif sort_by == "newest":
        posts.sort(key=lambda p: p.posted_date, reverse=True)
    else:
        posts.sort(key=lambda p: p.metrics.likes, reverse=True)

    # Filter berdasarkan tanggal jika dipilih user
    exact_matched = True
    filter_note = ""
    if target_date and target_date.strip():
        req_date = target_date.strip()
        matched = [p for p in posts if p.posted_date == req_date]
        if matched:
            posts = matched
        else:
            exact_matched = False
            filter_note = f"Tidak ada postingan Threads pada tanggal {req_date}. Menampilkan 20 postingan terbaik yang tersedia untuk #{clean_tag}:"

    # Limit hasil ke top-N (default 20)
    posts = posts[:limit]

    total_items = len(posts)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return {
        "tag": clean_tag,
        "status": tag_obj.status,
        "status_message": tag_obj.status_message,
        "sort_by": sort_by,
        "target_date": target_date or "",
        "exact_date_matched": exact_matched,
        "filter_note": filter_note,
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

# POST REGISTER TAG DENGAN ASYNC BACKGROUND SCRAPER
@app.post("/api/tags/register")
async def register_tag(
    tag: str, 
    country: str = "ID",
    x_user_role: Optional[str] = Header(None, description="Role pengakses: super_admin, admin, user")
):
    if x_user_role == "user":
        raise HTTPException(
            status_code=403, 
            detail="Akses Ditolak: Role 'user' hanya dapat mencari postingan dan tidak diizinkan menambahkan tagging baru."
        )

    clean_tag = tag.replace("#", "").strip().lower()
    if not clean_tag:
        raise HTTPException(status_code=400, detail="Tag tidak boleh kosong")

    existing = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)
    
    if not existing:
        new_tag = TagSummary(
            rank=len(MASTER_TAGS) + 1,
            tag=clean_tag,
            label=clean_tag,
            icon="mdi-pound",
            total_posts=0,
            total_reach=0,
            total_comments=0,
            total_likes=0,
            growth="+New",
            status="scraping",
            status_message="Sedang memindai Threads di latar belakang...",
            last_scraped_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        MASTER_TAGS.append(new_tag)

        # Trigger Asynchronous Background Scraping secara instan tanpa memblokir response
        asyncio.create_task(perform_background_scraping(clean_tag, country))

        return {
            "status": "queued",
            "message": f"Tag #{clean_tag} berhasil ditambahkan dan proses background scraping telah dimulai.",
            "tag": new_tag
        }
    else:
        # Jika sudah ada tetapi statusnya belum ready atau ingin refresh
        if existing.status != "scraping":
            asyncio.create_task(perform_background_scraping(clean_tag, country))
        return {
            "status": "exists",
            "message": f"Tag #{clean_tag} sudah terdaftar.",
            "tag": existing
        }

# POST REFRESH SCRAPE TAG
@app.post("/api/tags/refresh")
async def refresh_tag_scrape(
    tag: str,
    country: str = "ID",
    x_user_role: Optional[str] = Header(None)
):
    if x_user_role == "user":
        raise HTTPException(status_code=403, detail="Role user tidak berhak merefresh scraping.")

    clean_tag = tag.replace("#", "").strip().lower()
    tag_obj = next((t for t in MASTER_TAGS if t.tag == clean_tag), None)
    if not tag_obj:
        raise HTTPException(status_code=404, detail="Tag tidak ditemukan")

    tag_obj.status = "scraping"
    tag_obj.status_message = "Sedang memperbarui data dari Threads..."
    asyncio.create_task(perform_background_scraping(clean_tag, country))
    return {"status": "queued", "tag": tag_obj}

# DELETE TAG
@app.delete("/api/tags/{tag}")
def delete_tag(
    tag: str,
    x_user_role: Optional[str] = Header(None)
):
    if x_user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Hanya Admin dan Super Admin yang dapat menghapus tag.")

    clean_tag = tag.replace("#", "").strip().lower()
    global MASTER_TAGS
    before_count = len(MASTER_TAGS)
    MASTER_TAGS = [t for t in MASTER_TAGS if t.tag != clean_tag]
    
    if len(MASTER_TAGS) == before_count:
        raise HTTPException(status_code=404, detail=f"Tag #{clean_tag} tidak ditemukan.")

    from .scraper import REAL_POSTS_CACHE
    for k in list(REAL_POSTS_CACHE.keys()):
        if k.startswith(f"{clean_tag}_"):
            del REAL_POSTS_CACHE[k]

    return {"status": "deleted", "message": f"Tag #{clean_tag} berhasil dihapus."}
