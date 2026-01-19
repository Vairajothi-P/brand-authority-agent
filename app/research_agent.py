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
def generate_research_brief(context, serp_analysis):
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

# ================= RESOURCE LINK HELPER =================
def generate_resource_link(query):
    return f"https://www.google.com/search?q={query.replace(' ', '+')}"

# ================= STREAMLIT UI =================
st.set_page_config(page_title="SERP Research Agent", layout="wide")
st.title("🔍 SERP Research Agent ")

uploaded_file = st.file_uploader("Upload PDF or TXT document (optional)")

st.markdown("**Or provide context manually:**")
topic = st.text_input("Context :", placeholder="Eg: AI for school students")
target_audience = st.text_input("Target Audience :", placeholder="Eg: Kids aged 10–14")
content_goal = st.selectbox(
    "Content Goal :",
    ["Educational", "Informational", "Commercial", "Brand Authority"]
)
brand = st.text_input("Brand :", placeholder="Eg: AstroKids")
region = st.text_input("Region :", placeholder="Eg: India")
if st.button("🚀 Run SERP Research Agent"):

    # Decide input source
    if uploaded_file:
        text = extract_text(uploaded_file)
        context_data = extract_topic_with_llm(text)
        context = {
            "topic": context_data.get("core_topic", ""),
            "target_audience": context_data.get("target_audience", ""),
            "content_goal": content_goal,
            "brand": brand,
            "region": region,
            "search_intent": context_data.get("search_intent", "")
        }
    else:
        if not topic or not target_audience:
            st.error("❗ Please provide at least Topic and Target Audience.")
            st.stop()
        context = {
            "topic": topic,
            "target_audience": target_audience,
            "content_goal": content_goal,
            "brand": brand,
            "region": region
        }

    with st.spinner("Analyzing SERP & competitors..."):
        serp_data = fetch_serp(context["topic"])
        serp_analysis = analyze_serp_with_llm(serp_data)
        research_brief = generate_research_brief(context, serp_analysis)
        output_path = save_research_brief(research_brief)

    st.subheader("📊 Research Brief (Output for Writing Agent)")

    pk = research_brief["primary_keyword"]
    st.markdown(f"### 🎯 Primary Keyword\n**{pk}** [🔗]({generate_resource_link(pk)})")

    st.markdown("### 🔑 Secondary Keywords")
    for kw in research_brief["secondary_keywords"]:
        st.markdown(f"- {kw} [🔗]({generate_resource_link(kw)})")

    st.markdown("### ❓ Question Keywords")
    for q in research_brief["question_keywords"]:
        st.markdown(f"- {q} [🔗]({generate_resource_link(q)})")

    st.markdown(f"### 🧠 Content Angle\n{research_brief['content_angle']}")
    st.markdown("### 🧱 Recommended Structure")
    for sec in research_brief["recommended_structure"]:
        st.markdown(f"- {sec}")

    st.markdown(f"### 📏 Word Count\n{research_brief['recommended_word_count']}")
    st.markdown(f"### 🚀 Ranking Feasibility\n{research_brief['ranking_feasibility']}")
    st.markdown(f"### ✍️ Writing Instructions\n{research_brief['writing_instructions']}")

    st.success(f"✅ Research Brief saved at: {output_path}")
