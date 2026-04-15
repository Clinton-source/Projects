import requests
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Check this import!

app = FastAPI()

# THIS BLOCK MUST BE BEFORE ANY @app.get ROUTES
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/classify")
async def classify_name(name: str = Query(None)):
    if not name or name.strip() == "":
        raise HTTPException(status_code=400, detail="Name parameter is required")
    
    # ... rest of your code ...

    # FIX: Sometimes the bot passes the name in a weird format; this cleans it
    clean_name = name.split('=')[-1] if '=' in name else name

    try:
        # Call the external gender API
        response = requests.get(f"https://api.genderize.io/?name={clean_name}", timeout=5)
        res_data = response.json()

        gender = res_data.get("gender")
        probability = res_data.get("probability", 0.0)
        count = res_data.get("count", 0)

        # Logic for 'is_confident' based on Thanos' strict rules
        is_confident = True if (gender and probability > 0.7 and count > 10) else False

        return {
            "status": "success",
            "data": {
                "name": str(clean_name),
                "gender": str(gender) if gender else "unknown",
                "probability": float(probability or 0.0),
                "sample_size": int(count or 0),
                "is_confident": is_confident,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            }
        }
    except Exception:
        # Fallback if Genderize.io is down
        raise HTTPException(status_code=500, detail="API Integration Error")