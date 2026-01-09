from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from instagram import analyze_instagram
from youtube import main as analyze_youtube

app = FastAPI()

# =====================================================
# ✅ CORS CONFIGURATION
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 📸 INSTAGRAM ANALYZER API
# =====================================================
@app.post("/instagram/analyze")
def analyze_instagram_api(payload: dict):
    api_key = payload.get("api_key")
    username = payload.get("username")
    date_filter = payload.get("date_filter")

    # 🔒 Validation
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")

    if not username:
        raise HTTPException(status_code=400, detail="username is required")

    try:
        return analyze_instagram(
            api_key=api_key,
            username=username,
            date_input=date_filter
        )
    except Exception as e:
        # ❌ Safe backend error
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ▶️ YOUTUBE ANALYZER API
# =====================================================
@app.post("/youtube/analyze")
def analyze_youtube_api(payload: dict):
    api_key = payload.get("api_key")
    handle = payload.get("handle")

    # 🔒 Validation
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")

    if not handle:
        raise HTTPException(status_code=400, detail="channel handle is required")

    try:
        return analyze_youtube(api_key, handle)
    except Exception as e:
        # ❌ Safe backend error
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 🟢 HEALTH CHECK (OPTIONAL BUT RECOMMENDED)
# =====================================================
@app.get("/")
def health():
    return {"status": "Backend running 🚀"}
