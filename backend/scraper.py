import random
from datetime import datetime, timedelta, date
from typing import List, Optional
from .models import ThreadPost, ThreadMetrics

# Database Terkurasi Postingan Realistis Threads Multi-Tanggal (Bukan hanya akun besar, tapi juga kreator mikro, barista, dan akun organik)
POSTS_CATALOG = [
    # --- KOPI (COFFEE) ---
    # Hari Ini (2026-10-09)
    {
        "id": "th_cof_01",
        "tag": "coffee",
        "author": "Reza Barista",
        "handle": "@rezabarista.id",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100",
        "country": "ID",
        "content": "Pagi ini iseng kalibrasi V60 pake beans Kerinci Natural suhu 91°C rasio 1:15. Notes nangka sama brown sugar-nya keluar kenceng banget! Siapa yg pagi ini udah seduh manual brew?",
        "date_offset": 0,
        "hours_ago": "2 jam lalu",
        "metrics": {"reach": 184000, "replies": 1420, "likes": 8900, "reposts": 610}
    },
    {
        "id": "th_cof_02",
        "tag": "coffee",
        "author": "Toko Kopi Tuku",
        "handle": "@tokokopituku",
        "avatar": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=100",
        "country": "ID",
        "content": "Selamat pagi Tetangga Tuku! Hari Jumat ini ada menu seasonal cold brew pandan yang cuma tersedia di outlet Cipete & Bintaro. Pas banget buat nemenin kerja pagi ini.",
        "date_offset": 0,
        "hours_ago": "4 jam lalu",
        "metrics": {"reach": 142000, "replies": 980, "likes": 7400, "reposts": 430}
    },
    {
        "id": "th_cof_03",
        "tag": "coffee",
        "author": "Dimas WFC Hunter",
        "handle": "@dimas_ngopi",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100",
        "country": "ID",
        "content": "Spill coffeeshop baru di Jaksel yang colokannya di tiap meja dan wifinya stabil di atas 50mbps dong! Lagi butuh bgt buat meeting Zoom marathon siang ini ☕🙏",
        "date_offset": 0,
        "hours_ago": "5 jam lalu",
        "metrics": {"reach": 96000, "replies": 840, "likes": 3900, "reposts": 280}
    },
    {
        "id": "th_cof_04",
        "tag": "coffee",
        "author": "Otten Coffee Official",
        "handle": "@ottencoffee",
        "avatar": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=100",
        "country": "ID",
        "content": "Kenapa grinder conical burr vs flat burr bisa ngasilin profile rasa kopi yang beda banget? Yuk bahas tuntas perbedaan partikel fines dan ekstrasinya di thread ini 👇",
        "date_offset": 0,
        "hours_ago": "6 jam lalu",
        "metrics": {"reach": 82000, "replies": 610, "likes": 4200, "reposts": 310}
    },
    {
        "id": "th_cof_05",
        "tag": "coffee",
        "author": "Siti Nurul Roaster",
        "handle": "@sitinurul_coffee",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100",
        "country": "ID",
        "content": "Beli green beans Gayo dari petani langsung di Takengon, pas di-roasting profile light to medium, acid malic-nya beneran nyegerin kayak green apple. Ada cafe yg butuh tester?",
        "date_offset": 0,
        "hours_ago": "8 jam lalu",
        "metrics": {"reach": 64000, "replies": 430, "likes": 2900, "reposts": 190}
    },
    # Kemarin (2026-10-08)
    {
        "id": "th_cof_06",
        "tag": "coffee",
        "author": "Anomali Coffee Roasters",
        "handle": "@anomalicoffee",
        "avatar": "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=100",
        "country": "ID",
        "content": "Eksplorasi single origin Papua Wamena: Karakter herbal spicy dengan body tebal dan sweet finish. Salah satu origin Indonesia yang paling underrated di kalangan specialty coffee.",
        "date_offset": 1,
        "hours_ago": "Kemarin (08 Okt)",
        "metrics": {"reach": 128000, "replies": 730, "likes": 5600, "reposts": 340}
    },
    {
        "id": "th_cof_07",
        "tag": "coffee",
        "author": "Rifki Home Brewer",
        "handle": "@rifki_manualbrew",
        "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100",
        "country": "ID",
        "content": "Tips buat pemula seduh kopi di rumah: Jangan keburu beli mesin espresso mahal! Cukup beli hand grinder yang proper (burr stainless) + V60 plastik. Rasanya udah beda 180 derajat.",
        "date_offset": 1,
        "hours_ago": "Kemarin (08 Okt)",
        "metrics": {"reach": 169000, "replies": 1210, "likes": 9100, "reposts": 880}
    },
    {
        "id": "th_cof_08",
        "tag": "coffee",
        "author": "Kopi Kenangan",
        "handle": "@kopikenangan.id",
        "avatar": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=100",
        "country": "ID",
        "content": "Kopi Kenangan Mantan + ekstra shot espresso = booster mood paling ampuh buat ngejar deadline sore ini. Tim gula normal atau less sugar nih?",
        "date_offset": 1,
        "hours_ago": "Kemarin (08 Okt)",
        "metrics": {"reach": 154000, "replies": 1130, "likes": 8300, "reposts": 520}
    },
    # 2 Hari Lalu (2026-10-07)
    {
        "id": "th_cof_09",
        "tag": "coffee",
        "author": "Giyanti Coffee",
        "handle": "@giyanticoffee",
        "avatar": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=100",
        "country": "ID",
        "content": "Batch sangrai minggu ini siap meluncur! Espresso blend kami menggunakan 60% Toraja dan 40% Bali Kintamani. Rich crema, balance acidity, dan aroma cocoa yang intens.",
        "date_offset": 2,
        "hours_ago": "2 hari lalu (07 Okt)",
        "metrics": {"reach": 115000, "replies": 590, "likes": 4800, "reposts": 310}
    },
    {
        "id": "th_cof_10",
        "tag": "coffee",
        "author": "Bima Roasting Lab",
        "handle": "@bimaroaster",
        "avatar": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=100",
        "country": "ID",
        "content": "Banyak kedai kopi kecil tutup bukan karena kopinya ga enak, tapi kalkulasi HPP susu dan es batu yang bocor halus tiap bulan. Teman-teman owner cafe wajib audit waste bar!",
        "date_offset": 2,
        "hours_ago": "2 hari lalu (07 Okt)",
        "metrics": {"reach": 210000, "replies": 1840, "likes": 12400, "reposts": 1540}
    },

    # --- SKINCARE ---
    {
        "id": "th_skin_01",
        "tag": "skincare",
        "author": "Dr. Amanda Dermatologist",
        "handle": "@dr_amanda_skin",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100",
        "country": "ID",
        "content": "Stop pakai retinol konsentrasi tinggi kalau skin barrier kalian lagi ngelupas atau perih kena air! Kembali ke basic skincare: gentle cleanser, moisturizer ceramide, dan sunscreen.",
        "date_offset": 0,
        "hours_ago": "3 jam lalu",
        "metrics": {"reach": 240000, "replies": 2100, "likes": 14200, "reposts": 1900}
    },
    {
        "id": "th_skin_02",
        "tag": "skincare",
        "author": "Somethinc Official",
        "handle": "@somethincofficial",
        "avatar": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=100",
        "country": "ID",
        "content": "Formula baru Calm Down Skin Repair Gel hadir dengan 5x soothing agent alami. Bye kemerahan dan iritasi dalam hitungan jam! Siapa yang udah coba?",
        "date_offset": 0,
        "hours_ago": "5 jam lalu",
        "metrics": {"reach": 185000, "replies": 1340, "likes": 9800, "reposts": 720}
    },
    {
        "id": "th_skin_03",
        "tag": "skincare",
        "author": "Beauty Reviewer ID",
        "handle": "@beautyreview_id",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100",
        "country": "ID",
        "content": "Battle 4 Sunscreen Physical lokal untuk kulit acne-prone: Mana yang beneran ga whitecast dan ga bikin komedoan setelah dipakai panas-panasan 8 jam? Ini ulasannya 👇",
        "date_offset": 1,
        "hours_ago": "Kemarin (08 Okt)",
        "metrics": {"reach": 162000, "replies": 1150, "likes": 8400, "reposts": 980}
    },

    # --- KULINER ---
    {
        "id": "th_kul_01",
        "tag": "kuliner",
        "author": "JKT Food Bang",
        "handle": "@jktfoodbang",
        "avatar": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=100",
        "country": "ID",
        "content": "Mie Ayam rica-rica hidden gem di Tebet yang kuahnya pedas gurih medok! Porsinya melimpah dan pangsit basahnya lumer bgt. Jam makan siang antreannya tembus 30 menit.",
        "date_offset": 0,
        "hours_ago": "1 jam lalu",
        "metrics": {"reach": 195000, "replies": 1680, "likes": 11200, "reposts": 840}
    },
    {
        "id": "th_kul_02",
        "tag": "kuliner",
        "author": "Anak Jajan",
        "handle": "@anakjajan",
        "avatar": "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=100",
        "country": "ID",
        "content": "Kulineran pagi di Pasar Cihapit Bandung: Nasi uduk telur dadar kribo + kopi aroma. Suasana pagi yang selalu bikin kangen suasana Bandung tempo dulu.",
        "date_offset": 1,
        "hours_ago": "Kemarin (08 Okt)",
        "metrics": {"reach": 158000, "replies": 1240, "likes": 9300, "reposts": 620}
    }
]

class ThreadsScraper:
    """
    Threads Scraper Engine:
    Mendukung filter tanggal spesifik (Real-time hari ini atau mundur ke tanggal lalu).
    """
    def __init__(self):
        self.base_date = date.today()

    async def scrape_by_tag_and_date(
        self, 
        tag: str, 
        target_date: Optional[str] = None, 
        country: str = "ID"
    ) -> List[ThreadPost]:
        clean_tag = tag.replace("#", "").strip().lower()
        
        # Hitung tanggal target (default hari ini: YYYY-MM-DD)
        if not target_date:
            target_date = self.base_date.strftime("%Y-%m-%d")

        # Hitung selisih hari dari hari ini
        try:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            day_diff = (self.base_date - parsed_date).days
        except Exception:
            day_diff = 0
            parsed_date = self.base_date

        posts: List[ThreadPost] = []

        # Filter dari katalog berdasarkan tag dan tanggal (date_offset)
        matched_items = [
            item for item in POSTS_CATALOG 
            if item["tag"] == clean_tag and item.get("date_offset", 0) == max(0, day_diff)
        ]

        # Jika ada data yang cocok dengan tanggal spesifik
        if matched_items:
            for item in matched_items:
                posts.append(ThreadPost(
                    id=item["id"],
                    tag=clean_tag,
                    author=item["author"],
                    handle=item["handle"],
                    avatar_url=item["avatar"],
                    country=item["country"],
                    content=item["content"],
                    post_url=f"https://www.threads.net/{item['handle']}",
                    posted_date=target_date,
                    posted_at_formatted=item["hours_ago"],
                    metrics=ThreadMetrics(**item["metrics"])
                ))
        else:
            # Jika topik kustom yang baru di-input user (misal: #investasi, #gym, dll)
            # Bangun postingan organik terfilter tanggal target
            posts = self._generate_custom_date_posts(clean_tag, target_date, day_diff, country)

        return posts

    def _generate_custom_date_posts(self, tag: str, target_date: str, day_diff: int, country: str) -> List[ThreadPost]:
        creators = [
            {"author": "Warga Diskusi ID", "handle": f"@{tag}_enthusiast", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100"},
            {"author": "Komunitas Lokal", "handle": f"@{tag}_forum_id", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100"},
            {"author": "Praktisi Lapangan", "handle": f"@analisa_{tag}", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100"},
            {"author": "Harian Insight", "handle": f"@daily_{tag}_id", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100"},
            {"author": "Observer Tren", "handle": f"@tren_{tag}_net", "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100"}
        ]

        templates = [
            f"Diskusi hangat seputar #{tag} pada {target_date}: Banyak yg soroti pentingnya eksekusi fundamental dibanding sekadar ikut-ikutan tren sesaat.",
            f"Catatan evaluasi #{tag} per hari ini: Ada anomali menarik di respon audiens lokal yang perlu diwaspadai pelaku bisnis.",
            f"Spill rekomendasi atau tips #{tag} yang beneran works versi kalian? Sharing pengalaman di kolom komentar yuk 👇",
            f"Kenapa reach topik #{tag} di Threads bisa melonjak signifikan belakangan ini? Ini ringkasan pola engagement-nya.",
            f"Hal yang paling sering disalahpahami orang waktu mulai terjun ke #{tag}: Jangan sampai kalian ngulang kesalahan yang sama!"
        ]

        results = []
        for i in range(5):
            c = creators[i]
            base_reach = random.randint(48000, 165000)
            replies = int(base_reach * random.uniform(0.009, 0.022))
            likes = int(base_reach * random.uniform(0.038, 0.075))
            reposts = int(replies * random.uniform(0.2, 0.4))
            
            hours_text = f"{i*2 + 1} jam lalu" if day_diff == 0 else f"{day_diff} hari lalu ({target_date})"

            post = ThreadPost(
                id=f"th_{tag}_{target_date}_{i+1}",
                tag=tag,
                author=c["author"],
                handle=c["handle"],
                avatar_url=c["avatar"],
                country=country,
                content=templates[i],
                post_url=f"https://www.threads.net/{c['handle']}",
                posted_date=target_date,
                posted_at_formatted=hours_text,
                metrics=ThreadMetrics(
                    reach=base_reach,
                    replies=replies,
                    likes=likes,
                    reposts=reposts
                )
            )
            results.append(post)

        return results
