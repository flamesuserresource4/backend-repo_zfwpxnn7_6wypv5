import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import create_document, get_documents, db

app = FastAPI(title="Lumina Health API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
class ImageInput(BaseModel):
    image_url: str = Field(..., description="Publicly accessible image URL")

class ChatInput(BaseModel):
    message: str
    context: Optional[List[str]] = None

class NutritionInput(BaseModel):
    text: str = Field(..., description="Free-form food description, e.g., '2 eggs and a banana' or 'chicken salad' ")

class CommunityPostIn(BaseModel):
    title: str
    content: str
    author: str
    tags: Optional[List[str]] = []

# -----------------------------
# Root + Health
# -----------------------------
@app.get("/")
def read_root():
    return {"name": "Lumina", "message": "Lumina Health API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from Lumina backend!"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response

# -----------------------------
# AI-like endpoints (stubbed logic)
# -----------------------------
@app.post("/api/analyze-mood")
def analyze_mood(payload: ImageInput):
    # Stubbed heuristic: choose mood by simple hash of URL
    score = sum(ord(c) for c in payload.image_url) % 100
    moods = ["calm", "focused", "anxious", "uplifted", "neutral"]
    mood = moods[score % len(moods)]
    return {
        "mood": mood,
        "confidence": round(0.6 + (score % 40) / 100, 2),
        "explanation": "Quick, demo-only estimation based on image metadata fingerprint.",
        "recommendations": [
            "Try a 3-minute breathing exercise",
            "Take a short walk and hydrate",
            "Write down one thing you're grateful for"
        ]
    }

@app.post("/api/diagnose-image")
def diagnose_image(payload: ImageInput):
    return {
        "diagnosis": "Demo-only visual screening suggests no urgent issues",
        "confidence": 0.72,
        "notes": "For real diagnostics, consult a licensed professional.",
    }

@app.post("/api/chat")
def health_chat(input: ChatInput):
    text = input.message.lower()
    if "stress" in text or "anxious" in text:
        reply = "I'm here with you. Let's try box breathing: inhale 4, hold 4, exhale 4, hold 4, for 4 rounds."
    elif "sleep" in text:
        reply = "Aim for a consistent bedtime. Try reducing screens 60 minutes before sleep and a 10-minute wind-down."
    elif "diet" in text or "food" in text:
        reply = "A simple plate: half veggies, quarter lean protein, quarter whole grains. Hydration helps too."
    else:
        reply = "Tell me how you're feeling today, and I can suggest a quick exercise or resource."
    return {"reply": reply}

@app.post("/api/nutrition")
def nutrition_estimate(inp: NutritionInput):
    # Naive calorie estimation based on keywords; demo-only
    db_map = {
        "banana": 105, "apple": 95, "egg": 78, "eggs": 156, "bread": 80,
        "rice": 200, "salad": 120, "chicken": 220, "yogurt": 150,
        "coffee": 5, "latte": 190, "orange": 62, "oats": 150
    }
    text = inp.text.lower()
    total = 0
    hits: List[dict] = []
    for k, v in db_map.items():
        if k in text:
            total += v
            hits.append({"item": k, "calories": v})
    confidence = 0.5 if hits else 0.2
    return {"estimated_calories": total, "items": hits, "confidence": confidence}

@app.get("/api/youtube-recs")
def youtube_recommendations():
    # Curated mental fitness and mindfulness sessions (IDs only)
    videos = [
        {
            "title": "5-Minute Guided Breathing",
            "youtube_id": "nmFUDkj1Aq0",
            "category": "breathing"
        },
        {
            "title": "10-Min Body Scan Meditation",
            "youtube_id": "ihO02wUzgkc",
            "category": "meditation"
        },
        {
            "title": "Beginner Yoga Flow",
            "youtube_id": "v7AYKMP6rOE",
            "category": "exercise"
        }
    ]
    return {"videos": videos}

# -----------------------------
# Community (uses database)
# -----------------------------
@app.get("/api/community/posts")
def get_community_posts(limit: int = 20):
    try:
        posts = get_documents("communitypost", {}, limit)
        # Convert ObjectId to str
        for p in posts:
            if "_id" in p:
                p["id"] = str(p.pop("_id"))
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community/posts")
def create_community_post(post: CommunityPostIn):
    try:
        post_id = create_document("communitypost", post.model_dump())
        return {"id": post_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
