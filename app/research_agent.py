import os
import json
import time
import requests
import streamlit as st
import openai
from pypdf import PdfReader
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

OUTPUT_DIR = "agent_outputs"
RATE_LIMIT_WAIT = 20

# ================= OPENAI CONNECTOR =================
def call_openai(prompt, system_role, model="gpt-4.1-mini", temperature=0.3):
    def _call():
        return openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

    for _ in range(5):
        try:
            return _call()
        except Exception as e:
            print(f"⏳ OpenAI error: {e}. Retrying...")
            time.sleep(RATE_LIMIT_WAIT)

    raise Exception("❌ OpenAI failed after retries")

# ================= DOCUMENT INGESTION =================
def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join(
            page.extract_text()
            for page in reader.pages
            if page.extract_text()
        )
    return file.read().decode("utf-8", errors="ignore")

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

    res = call_openai(
        prompt=prompt,
        system_role="Topic analysis agent. JSON only.",
        temperature=0.2
    )

    return json.loads(res["choices"][0]["message"]["content"])

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

    res = call_openai(
        prompt=prompt,
        system_role="SEO SERP research agent. JSON only.",
        temperature=0.3
    )

    return json.loads(res["choices"][0]["message"]["content"])

# ================= FINAL RESEARCH BRIEF AGENT =================
def generate_research_brief(topic_data, serp_analysis):
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

Topic Data:
{topic_data}

SERP Analysis:
{serp_analysis}
"""

    res = call_openai(
        prompt=prompt,
        system_role="Content strategy agent. JSON only.",
        temperature=0.25
    )

    return json.loads(res["choices"][0]["message"]["content"])

# ================= SAVE OUTPUT =================
def save_research_brief(research_brief):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = f"{OUTPUT_DIR}/research_brief.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(research_brief, f, indent=2)
    return path

# ================= STREAMLIT UI =================
st.set_page_config(page_title="SERP Research Agent", layout="wide")
st.title("🔍 SERP Research Agent – Writing Agent Input Generator")

uploaded_file = st.file_uploader("Upload PDF or TXT document")

if uploaded_file:
    text = extract_text(uploaded_file)

    st.subheader("📄 Document Preview")
    st.text_area("Preview", text[:2000], height=200)

    if st.button("🚀 Run SERP Research Agent"):
        with st.spinner("Analyzing topic, SERP & competitors..."):
            topic_data = extract_topic_with_llm(text)
            serp_data = fetch_serp(topic_data["core_topic"])
            serp_analysis = analyze_serp_with_llm(serp_data)
            research_brief = generate_research_brief(topic_data, serp_analysis)
            output_path = save_research_brief(research_brief)

        st.subheader("📊 Research Brief (Output for Writing Agent)")
        st.json(research_brief)

        st.success(f"✅ Research Brief saved at: {output_path}")
