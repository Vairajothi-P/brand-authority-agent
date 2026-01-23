# app.py
import os
import json
import requests
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
from pathlib import Path

# ================= ENV =================
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")

# Only warn if keys are missing, don't crash
if not OPENAI_KEY:
    print("⚠️  WARNING: OPENAI_API_KEY not set in .env")
if not SERP_API_KEY:
    print("⚠️  WARNING: SERP_API_KEY not set in .env")

if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# ================= CONSTANTS =================
OUTPUT_PATH = r"C:\Users\hi\brand-authority-agent\app\agent_outputs\research_briefs.json"
LAST_OUTPUT = []

# ================= APP =================
app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- HEALTH ----------
@app.get("/")
def root():
    return {"status": "ok", "message": "Brand Authority Agent Backend Running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ================= OPENAI =================
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

# ================= SERP =================
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

# ================= ANALYSIS =================
def analyze_serp(serp_data):
    prompt = f"""
Return ONLY JSON:
{{ "keyword_difficulty": "", "ranking_feasibility": "" }}

SERP DATA:
{json.dumps(serp_data)[:4000]}
"""
    return json.loads(call_openai(prompt=prompt, system_role="SEO SERP analysis agent"))

# ================= ANGLES =================
def generate_blog_angles(context, count):
    prompt = f"""
Generate {count} blog angles.

Return ONLY JSON:
{{ "angles": [] }}

Context:
{json.dumps(context)}
"""
    return json.loads(call_openai(prompt=prompt, system_role="Content ideation agent", temperature=0.4))["angles"]

# ================= BRIEF =================
def generate_research_brief(context, serp_analysis, angle):
    prompt = f"""
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
{angle}
"""
    return json.loads(call_openai(prompt=prompt, system_role="SEO research brief agent"))

# ================= SAVE =================
def save_output(data):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ================= API =================
@app.post("/research-agent")
async def research_agent(
    topic: str = Form(...),
    target_audience: str = Form(...),
    content_goal: str = Form(...),
    region: str = Form(...),
    blog_count: int = Form(...),
):
    global LAST_OUTPUT

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
    for i, angle in enumerate(angles, 1):
        brief = generate_research_brief(context, serp_analysis, angle)
        brief["blog_number"] = i
        brief["blog_angle"] = angle
        briefs.append(brief)

    LAST_OUTPUT = briefs
    return briefs

@app.post("/save-output")
async def save_current_output():
    if not LAST_OUTPUT:
        return {"error": "No output to save"}

    save_output(LAST_OUTPUT)
    return {"status": "saved"}

@app.post("/refine-output")
async def refine_output(
    suggestion: str = Form(...)
):
    global LAST_OUTPUT

    prompt = f"""
Improve the research briefs based on this suggestion:
{suggestion}

Return ONLY JSON array.

Current output:
{json.dumps(LAST_OUTPUT, indent=2)}
"""
    refined = json.loads(call_openai(prompt=prompt, system_role="Research refinement agent", temperature=0.3))
    LAST_OUTPUT = refined
    return {"status": "refined", "data": refined}
# ================= WRITING AGENT =================
try:
    from writing_agent import ArticleState, OutlineAgent, WritingAgent, OutputAgent, Supervisor, load_json as load_json_writer
    
    @app.post("/writing-agent")
    async def writing_agent_endpoint():
        """Run the writing agent to generate article based on research briefs and summary"""
        try:
            # Load research and summary
            research_path = Path(__file__).parent / "agent_outputs" / "research_briefs.json"
            summary_path = Path(__file__).parent / "agent_outputs" / "summary.json"
            
            if not research_path.exists() or not summary_path.exists():
                return {"error": "Research briefs or summary not found. Run research agent first."}
            
            research = load_json_writer(str(research_path), "research_briefs.json")
            summary = load_json_writer(str(summary_path), "summary.json")
            
            # Create article state and run agents
            article = ArticleState(research, summary)
            
            agents = {
                "OUTLINE": OutlineAgent(),
                "WRITE": WritingAgent(),
                "SAVE": OutputAgent()
            }
            
            supervisor = Supervisor()
            
            while True:
                step = supervisor.decide(article)
                if step == "DONE":
                    break
                agents[step].act(article)
            
            # Read the generated article
            output_path = Path(__file__).parent / "outputs" / "article.md"
            if output_path.exists():
                article_content = output_path.read_text(encoding="utf-8")
                return {
                    "status": "success",
                    "article": article_content,
                    "topic": article.topic,
                    "primary_keyword": article.primary_keyword,
                    "secondary_keywords": article.secondary_keywords
                }
            else:
                return {"error": "Article generation failed"}
        
        except Exception as e:
            return {"error": str(e)}

    @app.get("/article-output")
    async def get_article_output():
        """Get the last generated article"""
        try:
            output_path = Path(__file__).parent / "outputs" / "article.md"
            if output_path.exists():
                return {
                    "status": "found",
                    "article": output_path.read_text(encoding="utf-8")
                }
            else:
                return {"status": "not_found", "article": ""}
        except Exception as e:
            return {"error": str(e)}

except ImportError as e:
    print(f"⚠️  Writing agent import failed: {e}")