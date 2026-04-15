from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/classify")
async def classify_name(name: str = Query(None)):
    # Handle missing or empty name (gives 400 error as requested)
    if not name or name.strip() == "":
        raise HTTPException(status_code=400, detail="Name parameter is required")

    try:
        #  External API Integration
        response = requests.get(f"https://api.genderize.io/?name={name}")
        response.raise_for_status()
        res_data = response.json()

        gender = res_data.get("gender")
        probability = res_data.get("probability", 0)
        count = res_data.get("count", 0)

        # Confidence Logic
        # Confident if probability > 0.7 and we have a decent sample size
        is_confident = False
        if gender and probability > 0.7 and count > 10:
            is_confident = True

        #  Exact JSON Structure requested by the bot
        return {
            "status": "success",
            "data": {
                "name": name,
                "gender": gender if gender else "unknown",
                "probability": float(probability),
                "sample_size": int(count),
                "is_confident": is_confident,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")