from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import google.generativeai as genai
import json
import os
from fastapi import FastAPI
# ... other imports

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "The Astrologai Engine is Live", "version": "1.0"}

# Your existing @app.post("/oracle") code below...
app = FastAPI(title="Astrologai FaaS Engine")

# Allow your React app to talk to this Python app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, put your Vercel URL here
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Dataset
df = pd.read_csv("Complete_Astrology_DataSet.zip", compression="zip")

# Define what data the React app will send us
class OracleRequest(BaseModel):
    name: str
    dob: str
    tob: str
    city: str
    question: str

@app.post("/api/generate-reading")
async def generate_reading(req: OracleRequest):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key missing on server.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    # 1. Ask Gemini to calculate positions (Agent 1)
    calc_prompt = f"Calculate chart for Date:{req.dob}, Time:{req.tob}, City:{req.city}. Return strictly JSON with keys: House, Planet, Mahadasha, Antardasha, Pratyanerdasha."
    try:
        calc_res = model.generate_content(calc_prompt).text.replace("```json", "").replace("```", "").strip()
        chart_facts = json.loads(calc_res)
    except:
        chart_facts = {"House": 1, "Planet": "Sun", "Mahadasha": "Sun", "Antardasha": "Sun", "Pratyanerdasha": "Moon"}

    # 2. Search your proprietary dataset
    try:
        match = df[(df['House'] == int(chart_facts.get('House', 1))) & 
                   (df['Planet'].str.contains(chart_facts.get('Planet', 'Sun'), case=False))]
        proprietary_data = f"Effect: {match.iloc[0]['Effect']} | Remedy: {match.iloc[0]['Remedies']}" if not match.empty else "Use general Vedic principles."
    except:
        proprietary_data = "Database lookup error."

    # 3. Generate Final Response (Agent 2)
    final_prompt = f"""
    USER: {req.name} | QUESTION: {req.question}
    FACTS: {chart_facts} | DATABASE: {proprietary_data}
    Write EXACTLY 8 crisp lines of reading, one blank line, then EXACTLY 2 lines of remedies. No fluff.
    """
    
    final_reading = model.generate_content(final_prompt).text

    # Split the response into reading and remedies for the React UI to display beautifully
    parts = final_reading.split('\n\n')
    reading = parts[0] if len(parts) > 0 else final_reading
    remedies = parts[1] if len(parts) > 1 else "Consult a priest for specific remedies."

    return {
        "status": "success",
        "chart_facts": chart_facts,
        "reading": reading,
        "remedies": remedies
    }

