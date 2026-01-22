# app.py
import os
import json
import time
import requests
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai

# ================= ENV =================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

RATE_LIMIT_WAIT = 20

app = FastAPI()

# ================= CORS (IMPORTANT) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= OPENAI CONNECTOR =================
def call_openai(prompt, system_role, model="gpt-4.1-mini", temperature=0.3):
    for _ in range(5):
        try:
            return openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
        except Exception as e:
            print("Retrying OpenAI:", e)
            time.sleep(RATE_LIMIT_WAIT)
    raise Exception("OpenAI failed after retries")

# ================= SERP FETCH =================
def fetch_serp(keyword):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": keyword,
        "num": 10,
        "api_key": SERP_API_KEY
    }
    return requests.get(url, params=params).json()

# ================= MAIN API =================
@app.post("/run-agent")
async def run_agent(
    topic: str = Form(...),
    target_audience: str = Form(...),
    content_goal: str = Form(...),
    brand: str = Form(""),
    region: str = Form(""),
    blog_count: int = Form(1),
):

    context = {
        "topic": topic,
        "target_audience": target_audience,
        "content_goal": content_goal,
        "brand": brand,
        "region": region
    }

    # ---- SERP ANALYSIS ----
    serp_data = fetch_serp(topic)

    serp_prompt = f"""
Return ONLY JSON:
{{
  "serp_type": "",
  "serp_features": [],
  "top_domains": [],
  "keyword_difficulty": "",
  "ranking_probability": ""
}}

SERP DATA:
{json.dumps(serp_data)[:5000]}
"""
    serp_analysis = json.loads(
        call_openai(serp_prompt, "SEO SERP research agent").choices[0].message.content
    )

    # ---- BLOG ANGLES ----
    angles_prompt = f"""
Generate {blog_count} DISTINCT blog angles.
Return ONLY JSON:
{{ "angles": [] }}

Context:
{json.dumps(context)}
"""
    angles = json.loads(
        call_openai(angles_prompt, "Content ideation agent").choices[0].message.content
    )["angles"]

    # ---- RESEARCH BRIEFS ----
    briefs = []

    for idx, angle in enumerate(angles, start=1):
        brief_prompt = f"""
Return ONLY JSON:
{{
  "primary_keyword": "",
  "secondary_keywords": [],
  "question_keywords": [],
  "content_angle": "",
  "recommended_structure": [],
  "recommended_word_count": "",
  "ranking_feasibility": "",
  "writing_instructions": ""
}}

Context:
{json.dumps(context)}

SERP Analysis:
{json.dumps(serp_analysis)}

Blog Angle:
{angle}
"""
        brief = json.loads(
            call_openai(brief_prompt, "Content strategy agent").choices[0].message.content
        )

        brief["blog_number"] = idx
        brief["blog_angle"] = angle
        briefs.append(brief)

    return briefs
