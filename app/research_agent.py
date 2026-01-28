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
    """Extract JSON from response that might be wrapped in markdown code blocks"""
    content = content.strip()
    # Remove markdown code blocks if present
    if content.startswith("```"):
        # Find the start of actual JSON
        lines = content.split("\n")
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("{") or line.strip().startswith("["):
                start_idx = i
                break
        
        # Find the end of JSON
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
        content = res.text.strip()
        content = extract_json_from_response(content)
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"⚠️ Topic extraction parsing error: {e}")
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

    # Extract content safely
    try:
        if not res or not hasattr(res, 'text'):
            print(f"⚠️ Unexpected response structure: {res}")
            raise ValueError("Invalid response from Gemini")
        
        content = res.text.strip()
        if not content:
            print("⚠️ Empty content received from Gemini")
            raise ValueError("Empty response content")
        
        # Extract JSON from potential markdown wrapping
        content = extract_json_from_response(content)
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing error: {e}")
        print(f"Content was: {content[:500]}")
        # Return a default structure if parsing fails
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
# ================= FINAL RESEARCH BRIEF AGENT (STRICT) =================
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

    try:
        content = res.text.strip()
        content = extract_json_from_response(content)
        data = json.loads(content)

        # HARD SCHEMA ENFORCEMENT (safety net)
        return {
            "primary_keyword": data.get("primary_keyword", ""),
            "secondary_keywords": data.get("secondary_keywords", []),
            "question_keywords": data.get("question_keywords", []),
            "content_angle": data.get("content_angle", ""),
            "ranking_feasibility": data.get("ranking_feasibility", ""),
            "writing_instructions": data.get("writing_instructions", "")
        }

    except json.JSONDecodeError as e:
        raise Exception(f"❌ Invalid JSON from Research Agent: {e}")

# ================= SAVE OUTPUT =================
def save_research_briefs(research_briefs):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = f"{OUTPUT_DIR}/research_briefs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(research_briefs, f, indent=2)
    return path

# ================= RESOURCE LINK HELPER =================
def generate_resource_link(query):
    return f"https://www.google.com/search?q={query.replace(' ', '+')}"

# ================= MAIN RESEARCH AGENT FUNCTION =================
# ================= MAIN RESEARCH AGENT FUNCTION =================
async def run_research_agent(request_data: ResearchRequest, file_content=None):

    # ---- CONTEXT ----
    if file_content:
        text = extract_text_from_pdf(file_content)
        context_data = extract_topic_with_llm(text)
        context = {
            "topic": context_data.get("core_topic", ""),
            "target_audience": context_data.get("target_audience", ""),
            "content_goal": request_data.content_goal,
            "brand": request_data.brand,
            "region": request_data.region,
            "search_intent": context_data.get("search_intent", "")
        }
    else:
        if not request_data.topic or not request_data.target_audience:
            return {
                "status": "error",
                "message": "Topic and Target Audience are required"
            }

        context = {
            "topic": request_data.topic,
            "target_audience": request_data.target_audience,
            "content_goal": request_data.content_goal,
            "brand": request_data.brand,
            "region": request_data.region
        }

    # ---- SERP ----
    serp_data = fetch_serp(context["topic"])
    serp_analysis = analyze_serp_with_llm(serp_data)

    # ---- FINAL STRICT RESEARCH OUTPUT ----
    research_output = generate_research_brief(context, serp_analysis)

    return research_output