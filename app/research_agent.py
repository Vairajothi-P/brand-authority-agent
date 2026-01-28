import os
import json
import time
import requests
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv
from pydantic import BaseModel
from io import BytesIO

# ================= ENV =================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
SERP_API_KEY = os.getenv("SERP_API_KEY")

OUTPUT_DIR = "agent_outputs"
RATE_LIMIT_WAIT = 20

# ================= MODELS =================
class ResearchRequest(BaseModel):
    topic: str
    target_audience: str
    content_goal: str
    brand: str
    region: str

# ================= GEMINI CONNECTOR =================
def call_gemini(prompt, system_role, model="gemini-2.5-flash", temperature=0.3):
    for attempt in range(5):
        try:
            model_obj = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_role,
            )
            response = model_obj.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=0.95,
                    top_k=40,
                )
            )
            return response
        except Exception as e:
            if attempt < 4:
                print(f"⏳ Gemini error: {e}. Retrying...")
                time.sleep(RATE_LIMIT_WAIT)
            else:
                raise Exception("❌ Gemini failed after retries")

# ================= JSON EXTRACTION HELPER =================
def extract_json_from_response(content):
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("{") or line.strip().startswith("["):
                start_idx = i
                break
        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().endswith("}") or lines[i].strip().endswith("]"):
                end_idx = i + 1
                break
        content = "\n".join(lines[start_idx:end_idx])
    return content

# ================= DOCUMENT INGESTION =================
def extract_text_from_pdf(file_content):
    reader = PdfReader(BytesIO(file_content))
    return "\n".join(
        page.extract_text()
        for page in reader.pages
        if page.extract_text()
    )

# ✅ FIXED: supports FastAPI UploadFile, bytes, or None
def extract_text_from_file(file_content, filename: str | None):
    if not file_content or not filename:
        return ""

    filename = filename.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(
            file_content.read() if hasattr(file_content, "read") else file_content
        )

    if filename.endswith(".txt"):
        content = file_content.read() if hasattr(file_content, "read") else file_content
        return content.decode("utf-8", errors="ignore")

    return ""

# ================= TOPIC UNDERSTANDING AGENT =================
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

    res = call_gemini(
        prompt=prompt,
        system_role="Topic analysis agent. JSON only.",
        temperature=0.2
    )

    try:
        content = extract_json_from_response(res.text.strip())
        return json.loads(content)
    except Exception:
        return {
            "core_topic": "Unknown topic",
            "target_audience": "General audience",
            "search_intent": "informational"
        }

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

# ================= SERP ANALYSIS AGENT =================
def analyze_serp_with_llm(serp_data):
    prompt = f"""
Analyze the Google SERP data and return insights.

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

    res = call_gemini(
        prompt=prompt,
        system_role="SEO SERP research agent. JSON only.",
        temperature=0.3
    )

    try:
        content = extract_json_from_response(res.text.strip())
        return json.loads(content)
    except Exception:
        return {
            "serp_type": "unknown",
            "serp_features": [],
            "top_domains": [],
            "competitor_strengths": [],
            "competitor_weaknesses": [],
            "keyword_difficulty": "medium",
            "ranking_probability": "moderate"
        }

# ================= FINAL RESEARCH BRIEF AGENT =================
def generate_research_brief(context, serp_analysis):
    prompt = f"""
You are an SEO research agent.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT add markdown
- Do NOT add explanations
- Do NOT add extra fields
- Match the output schema EXACTLY

Output JSON schema:
{{
  "primary_keyword": "",
  "secondary_keywords": [],
  "question_keywords": [],
  "content_angle": "",
  "ranking_feasibility": "",
  "writing_instructions": ""
}}

Context:
{json.dumps(context, indent=2)}

SERP Analysis:
{json.dumps(serp_analysis, indent=2)}
"""

    res = call_gemini(
        prompt=prompt,
        system_role="SEO research agent. Output strict JSON only.",
        temperature=0.2
    )

    content = extract_json_from_response(res.text.strip())
    data = json.loads(content)

    return {
        "primary_keyword": data.get("primary_keyword", ""),
        "secondary_keywords": data.get("secondary_keywords", []),
        "question_keywords": data.get("question_keywords", []),
        "content_angle": data.get("content_angle", ""),
        "ranking_feasibility": data.get("ranking_feasibility", ""),
        "writing_instructions": data.get("writing_instructions", "")
    }

# ================= MAIN RESEARCH AGENT FUNCTION =================
async def run_research_agent(
    request_data: ResearchRequest,
    file_content=None,
    filename: str | None = None,
    suggestion: str | None = None
):
    context = {
        "topic": request_data.topic,
        "target_audience": request_data.target_audience,
        "content_goal": request_data.content_goal,
        "brand": request_data.brand,
        "region": request_data.region,

        # NEW INPUTS (SAFE)
        "user_suggestion": suggestion or "",
        "document_text": extract_text_from_file(file_content, filename)[:3000]
    }

    serp_data = fetch_serp(context["topic"])
    serp_analysis = analyze_serp_with_llm(serp_data)

    return generate_research_brief(context, serp_analysis)
