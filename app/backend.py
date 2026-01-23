import os
import json
import time
import requests
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
# ================= ENV =================
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
SERP_API_KEY = os.getenv("SERP_API_KEY")
model = genai.GenerativeModel("gemini-3-flash-preview")

RATE_LIMIT_WAIT = 20

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= OPENAI CONNECTOR =================
def call_openai(prompt, system_role):
    def _call():
        chat = model.start_chat(
            history=[
                {
                    "role": "model",
                    "parts": [system_role]
                },
            ]
        )
        return chat.send_message(prompt)

    for _ in range(5):
        try:
            return _call()
        except Exception as e:
            print("Retrying OpenAI...", e)
            time.sleep(RATE_LIMIT_WAIT)

    raise Exception("OpenAI failed")

# ================= PDF / TEXT =================
def extract_text(file: UploadFile):
    if file.content_type == "application/pdf":
        reader = PdfReader(file.file)
        return "\n".join(
            page.extract_text()
            for page in reader.pages
            if page.extract_text()
        )
    return file.file.read().decode("utf-8", errors="ignore")

# ================= TOPIC AGENT =================
def extract_topic_with_llm(text):
    prompt = f"""
Analyze the document below and extract:
1. Core topic
2. Target audience
3. Search intent (informational/commercial/transactional)

Return ONLY JSON:
{{
  "core_topic": "",
  "target_audience": "",
  "search_intent": ""
}}

Document:
{text[:3000]}
"""
    res = call_openai(prompt, "Topic analysis agent. JSON only.")
    return json.loads(res.candidates[0].content.parts[0].text)

# ================= SERP =================
def fetch_serp(keyword):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": keyword,
        "num": 10,
        "api_key": SERP_API_KEY
    }
    return requests.get(url, params=params).json()

def analyze_serp_with_llm(serp_data):
    prompt = f"""
Analyze SERP and return insights.

Return ONLY JSON:
{{
  "serp_type": "",
  "serp_features": [],
  "top_domains": [],
  "competitor_strengths": [],
  "competitor_weaknesses": [],
  "keyword_difficulty": "",
  "ranking_probability": ""
}}

SERP DATA:
{json.dumps(serp_data)[:6000]}
"""
    res = call_openai(prompt, "SEO SERP research agent. JSON only.")
    return json.loads(res.candidates[0].content.parts[0].text)

# ================= BLOG ANGLES =================
def generate_blog_angles(context, count):
    prompt = f"""
Generate {count} DISTINCT blog angles.

Return ONLY JSON:
{{ "angles": [] }}

Context:
{json.dumps(context)}
"""
    res = call_openai(prompt, "Content ideation agent. JSON only.")
    print(res)
    return json.loads(res.candidates[0].content.parts[0].text)["angles"]

# ================= RESEARCH BRIEF =================
def generate_research_brief(context, serp_analysis, blog_angle):
    prompt = f"""
Generate SERP Research Brief.

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

SERP:
{json.dumps(serp_analysis)}

Angle:
{blog_angle}
"""
    res = call_openai(prompt, "Content strategy agent. JSON only.")
    return json.loads(res.candidates[0].content.parts[0].text)

# ================= API =================
@app.post("/run-serp-agent")
async def run_agent(
    topic: str = Form(None),
    target_audience: str = Form(None),
    content_goal: str = Form(...),
    brand: str = Form(""),
    region: str = Form(""),
    blog_count: int = Form(...),
    file: UploadFile = None
):
    if file:
        text = extract_text(file)
        context_data = extract_topic_with_llm(text)
        context = {
            "topic": context_data["core_topic"],
            "target_audience": context_data["target_audience"],
            "content_goal": content_goal,
            "brand": brand,
            "region": region,
            "search_intent": context_data["search_intent"]
        }
    else:
        context = {
            "topic": topic,
            "target_audience": target_audience,
            "content_goal": content_goal,
            "brand": brand,
            "region": region
        }

    serp_data = fetch_serp(context["topic"])
    serp_analysis = analyze_serp_with_llm(serp_data)

    angles = generate_blog_angles(context, blog_count)
    results = []

    print(results)

    for i, angle in enumerate(angles, start=1):
        brief = generate_research_brief(context, serp_analysis, angle)
        brief["blog_number"] = i
        brief["blog_angle"] = angle
        results.append(brief)

    return {"research_briefs": results}
