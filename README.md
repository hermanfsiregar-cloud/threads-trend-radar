# Threads Trend Radar & Scraper (ThreadLens)

Aplikasi intelligence dan data scraper untuk **Threads (Meta)** berbasis **Python FastAPI** dan antarmuka **Anti-Slop** yang bersih dan profesional.

---

## 📁 Struktur Direktori Project

```
threads-trend-radar/
├── backend/
│   ├── main.py          # FastAPI application & router endpoints
│   ├── models.py        # Pydantic schema (ThreadPost, TagSummary, Metrics)
│   └── scraper.py       # Threads Scraper Engine (Python)
├── index.html           # UI Frontend (Poppins, MDI, Anti-Slop 3-Color System)
├── requirements.txt     # Python Dependencies
└── README.md
```

---

## 🚀 Cara Menjalankan Project di Laptop / IDE Anda

### 1. Buka Terminal di Folder Project:
```bash
cd /Users/user/.gemini/antigravity/scratch/threads-trend-radar
```

### 2. Buat Virtual Environment (Opsional tapi Direkomendasikan):
```bash
python3 -m venv venv
source venv/bin/activate  # Di Mac / Linux
```

### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 4. Jalankan Server Backend (FastAPI):
```bash
uvicorn backend.main:app --reload --port 8000
```
Server backend akan aktif di `http://127.0.0.1:8000`.
Anda bisa melihat dokumentasi API otomatis di `http://127.0.0.1:8000/docs`.

### 5. Jalankan Frontend UI:
Cukup buka file `index.html` langsung di browser Anda atau gunakan ekstensi *Live Server* di IDE (VS Code / Cursor).
