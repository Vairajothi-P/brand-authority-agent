# app.py
import os
import json
import time
import requests
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing")

openai.api_key = OPENAI_KEY

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- HEALTH CHECK ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- OPENAI ----------
def call_openai(prompt, system_role):
    return openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

# ---------- SERP ----------
def fetch_serp(keyword):
    res = requests.get(
        "https://serpapi.com/search.json",
        params={
            "engine": "google",
            "q": keyword,
            "num": 10,
            "api_key": SERP_API_KEY
        },
        timeout=20
    )
    res.raise_for_status()
    return res.json()

# ---------- API ----------
@app.post("/research-agent")
async def research_agent(
    topic: str = Form(...),
    target_audience: str = Form(...),
    content_goal: str = Form(...),
    brand: str = Form(""),
    region: str = Form(""),
    blog_count: int = Form(1),
):
    try:
        context = {
            "topic": topic,
            "target_audience": target_audience,
            "content_goal": content_goal,
            "brand": brand,
            "region": region
        }

        serp_data = fetch_serp(topic)

        serp_prompt = f"""
Return ONLY JSON:
{{"keyword_difficulty":"","ranking_probability":""}}
SERP DATA:
{json.dumps(serp_data)[:3000]}
"""
        serp_analysis = json.loads(
            call_openai(serp_prompt, "SEO agent")
            .choices[0].message.content
        )

        angles_prompt = f"""
Generate {blog_count} blog angles.
Return ONLY JSON: {{ "angles": [] }}
Context:{json.dumps(context)}
"""
        angles = json.loads(
            call_openai(angles_prompt, "Angle agent")
            .choices[0].message.content
        )["angles"]

        briefs = []
        for i, angle in enumerate(angles, 1):
            briefs.append({
                "blog_number": i,
                "blog_angle": angle,
                "primary_keyword": topic,
                "recommended_word_count": "1200–1500",
                "writing_instructions": "Write SEO-optimized content."
            })

        return briefs

    except Exception as e:
        return {"error": str(e)}
