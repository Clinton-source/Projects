from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import requests

app = FastAPI()

# Enable CORS so the grading script can talk to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/classify")
def classify_name(name: str = Query(None)):

    if not name:
        return {"status": "error", "message": "Missing or empty name parameter"}, 400

    try:
        external_api_url = f"https://api.genderize.io?name={name}"
        response = requests.get(external_api_url)
        data = response.json()
        
        # Check for Genderize edge cases (no data found)

        if data.get("gender") is None:
            return {"status": "error", "message": "No prediction available for the provided name"}

        # Processing the data

        probability = data.get("probability", 0)
        sample_size = data.get("count", 0)
        
        # Confidence Rule: Prob >= 0.7 AND Sample >= 100

        is_confident = (probability >= 0.7) and (sample_size >= 100)
        
        # Generate current UTC time

        processed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Return the structured response
        
        return {
            "status": "success",
            "data": {
                "name": name,
                "gender": data.get("gender"),
                "probability": probability,
                "sample_size": sample_size,
                "is_confident": is_confident,
                "processed_at": processed_at
            }
        }

    except Exception:
        return {"status": "error", "message": "Internal server error"}, 500