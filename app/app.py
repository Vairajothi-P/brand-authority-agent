# app.py
import os
import json
import requests
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
#commit
# ================= ENV =================
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing")
if not SERP_API_KEY:
    raise RuntimeError("SERP_API_KEY is missing")

openai.api_key = OPENAI_KEY

# ================= APP =================
app = FastAPI()

# ---------- HEALTH CHECK ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= OPENAI HELPER =================
def call_openai(prompt, system_role, temperature=0.3):
    res = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return res.choices[0].message.content

# ================= SERP FETCH =================
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

# ================= SERP ANALYSIS AGENT =================
def analyze_serp(serp_data):
    prompt = f"""
Analyze the SERP data and estimate ranking difficulty.

Return ONLY JSON:
{{
  "keyword_difficulty": "",
  "ranking_feasibility": ""
}}

SERP DATA:
{json.dumps(serp_data)[:4000]}
"""
    return json.loads(call_openai(prompt, "SEO SERP analysis agent"))

# ================= BLOG ANGLE AGENT =================
def generate_blog_angles(context, count):
    prompt = f"""
Generate {count} DISTINCT blog angles.
Each angle must target a different sub-topic or intent.

Return ONLY JSON:
{{ "angles": [] }}

Context:
{json.dumps(context, indent=2)}
"""
    return json.loads(
        call_openai(prompt, "Content ideation agent", temperature=0.4)
    )["angles"]

# ================= RESEARCH BRIEF AGENT =================
def generate_research_brief(context, serp_analysis, angle):
    prompt = f"""
Generate a detailed SEO research brief.

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
{json.dumps(context, indent=2)}

SERP Insights:
{json.dumps(serp_analysis, indent=2)}

Blog Angle:
{angle}
"""
    return json.loads(call_openai(prompt, "SEO research brief agent"))

# ================= API =================
@app.post("/research-agent")
async def research_agent(
    topic: str = Form(...),
    target_audience: str = Form(...),
    content_goal: str = Form(...),
    region: str = Form(...),
    blog_count: int = Form(...),
):
    context = {
        "topic": topic,
        "target_audience": target_audience,
        "content_goal": content_goal,
        "region": region
    }

    serp_data = fetch_serp(topic)
    serp_analysis = analyze_serp(serp_data)
    angles = generate_blog_angles(context, blog_count)

    briefs = []
    for idx, angle in enumerate(angles, start=1):
        brief = generate_research_brief(context, serp_analysis, angle)
        brief["blog_number"] = idx
        brief["blog_angle"] = angle
        briefs.append(brief)

    return briefs
