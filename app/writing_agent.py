import os
import json
import time
import re
from dotenv import load_dotenv
import google.generativeai as genai

# ================= ENV =================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("❌ GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)

# ================= PATH CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESEARCH_JSON_PATH = os.path.join(BASE_DIR, "agent_outputs", "research_briefs.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# ================= UTILS =================
def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0] if isinstance(data, list) else data

def call_gemini(prompt):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction="""
You are a professional SEO content writer.

STRICT RULES:
- Follow ONLY the provided research data
- DO NOT introduce unrelated topics
- DO NOT explain theory
- Structure must be VERY CLEAN

FORMAT RULES (MANDATORY):
- MAIN HEADINGS → ALL CAPS + **BOLD**
- SUBHEADINGS → **BOLD**
- CONTENT → BULLET POINTS ONLY
- NO LONG PARAGRAPHS
- NO FILLER
- 1000–1200 words

CONTENT STYLE:
- Clear
- Practical
- Structured
- Easy to scan
"""
    )

    res = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.35,
            "max_output_tokens": 4096
        }
    )
    return res.text.strip()

# ================= MAIN WRITING AGENT =================
def run():
    print("\n🚀 Writing Agent Started (STRICT STRUCTURE MODE)\n")

    research = load_json(RESEARCH_JSON_PATH)

    topic = research.get("primary_keyword", "Topic")
    content_angle = research.get("content_angle", "")
    questions = research.get("question_keywords", [])
    secondary = research.get("secondary_keywords", [])

    prompt = f"""
Analyze the following research data and write a FULL article.

RESEARCH DATA:
Topic focus: {topic}

Content intent:
{content_angle}

User questions to address:
{questions}

Related concepts (use naturally, no stuffing):
{secondary}



FINAL RULES:
- Headings MUST be bold & capitalized
- Subheadings MUST be bold
- Use bullet points ONLY
- Around 1000–1200 words
- SEO friendly but natural
- DO NOT add new topics
- DO NOT explain theory
"""

    article = call_gemini(prompt)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "article.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print("✅ Article generated successfully")
    print(f"📄 Saved to → {output_path}")

# ================= ENTRY =================
if __name__ == "__main__":
    run()

