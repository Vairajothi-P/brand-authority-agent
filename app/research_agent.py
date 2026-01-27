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
    blog_count: int

# ================= GEMINI CONNECTOR =================
def call_gemini(prompt, system_role, model="gemini-2.5-flash", temperature=0.3):
    for _ in range(5):
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
            print(f"⏳ Gemini error: {e}. Retrying...")
            time.sleep(RATE_LIMIT_WAIT)

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

# ================= BLOG ANGLE GENERATOR =================
def generate_blog_angles(context, count):
    prompt = f"""
You are a content strategy expert.

Generate {count} DISTINCT blog angles for the topic below.
Each angle must target a different search intent or sub-topic.

Return ONLY JSON:
{{
  "angles": []
}}

Context:
{json.dumps(context, indent=2)}
"""
    res = call_gemini(
        prompt=prompt,
        system_role="Content ideation agent. JSON only.",
        temperature=0.4
    )
    try:
        content = res.text.strip()
        content = extract_json_from_response(content)
        data = json.loads(content)
        return data.get("angles", [])
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"⚠️ Blog angles parsing error: {e}")
        return [f"Angle {i+1}: Analysis of {context.get('topic', 'topic')}" for i in range(int(count))]

# ================= FINAL RESEARCH BRIEF AGENT =================
def generate_research_brief(context, serp_analysis, blog_angle=None):
    prompt = f"""
Generate a SERP Research Brief for a Writing Agent.

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

SERP Analysis:
{json.dumps(serp_analysis, indent=2)}

Blog Angle:
{blog_angle if blog_angle else ""}
"""
    res = call_gemini(
        prompt=prompt,
        system_role="Content strategy agent. JSON only.",
        temperature=0.25
    )
    try:
        content = res.text.strip()
        content = extract_json_from_response(content)
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"⚠️ Research brief parsing error: {e}")
        # Return a default research brief structure
        return {
            "primary_keyword": context.get("topic", "keyword"),
            "secondary_keywords": [],
            "question_keywords": [],
            "content_angle": blog_angle or "Comprehensive guide",
            "recommended_structure": ["Introduction", "Main Content", "Conclusion"],
            "recommended_word_count": "2000-3000 words",
            "ranking_feasibility": "moderate",
            "writing_instructions": "Write comprehensive, SEO-optimized content"
        }

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
async def run_research_agent(request_data: ResearchRequest, file_content=None):
    """Main research agent workflow - same logic as Streamlit version"""
    
    # Decide input source (same as Streamlit if/else logic)
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
        # Validate topic and target_audience (same as Streamlit)
        if not request_data.topic or not request_data.target_audience:
            return {
                "status": "error",
                "message": "❗ Please provide at least Topic and Target Audience."
            }
        context = {
            "topic": request_data.topic,
            "target_audience": request_data.target_audience,
            "content_goal": request_data.content_goal,
            "brand": request_data.brand,
            "region": request_data.region
        }

    # Analyzing SERP & competitors (same as Streamlit spinner)
    serp_data = fetch_serp(context["topic"])
    serp_analysis = analyze_serp_with_llm(serp_data)

    # Generate blog angles and research briefs (same as Streamlit loop)
    blog_angles = generate_blog_angles(context, request_data.blog_count)
    all_research_briefs = []

    for idx, angle in enumerate(blog_angles, start=1):
        brief = generate_research_brief(context, serp_analysis, angle)
        brief["blog_number"] = idx
        brief["blog_angle"] = angle
        all_research_briefs.append(brief)

    # Save research briefs (same as Streamlit)
    output_path = save_research_briefs(all_research_briefs)

    return {
        "status": "success",
        "message": f"✅ Research Briefs saved at: {output_path}",
        "context": context,
        "serp_analysis": serp_analysis,
        "research_briefs": all_research_briefs
    }
