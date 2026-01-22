import json
import os
import time
from pathlib import Path
import openai
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise Exception("❌ OPENAI_API_KEY not set")

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent

RESEARCH_PATH = BASE_DIR / "agent_outputs" / "research_briefs.json"
SUMMARY_PATH  = BASE_DIR / "agent_outputs" / "summary.json"
ARTICLE_PATH  = BASE_DIR / "outputs" / "article.md"
OUTPUT_PATH   = BASE_DIR / "outputs" / "article_branded.md"

RATE_WAIT = 30
SCORE_THRESHOLD = 80

# ================= HELPERS =================
def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"❌ Missing file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data[0] if isinstance(data, list) else data

def load_md(path):
    if not path.exists():
        raise FileNotFoundError(f"❌ Missing file: {path}")
    return path.read_text(encoding="utf-8")

def safe_openai_call(fn):
    while True:
        try:
            return fn()
        except openai.error.RateLimitError:
            print(f"⏳ Rate limit hit. Waiting {RATE_WAIT}s...")
            time.sleep(RATE_WAIT)

# ================= BRAND SCORING AGENT =================
def brand_score_agent(article, research, summary):
    prompt = f"""
You are a strict BRAND EVALUATION AGENT.

Brand Voice:
{json.dumps(summary, indent=2)}

Research Direction:
{json.dumps(research, indent=2)}

Article Content:
{article[:3500]}

Evaluate on a 0–100 scale:

1. Tone match
2. Audience alignment
3. SEO keyword usage
4. Informational clarity (NO selling)
5. Brand consistency

Return ONLY valid JSON:
{{
  "overall_score": number,
  "breakdown": {{
    "tone": number,
    "audience": number,
    "keywords": number,
    "clarity": number,
    "consistency": number
  }},
  "issues": [
    "clear short issue 1",
    "clear short issue 2"
  ]
}}
"""

    response = safe_openai_call(lambda: openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a brand auditor"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    ))

    return json.loads(response["choices"][0]["message"]["content"])

# ================= REWRITE AGENT =================
def rewrite_article(article, brand_report, research, summary):
    prompt = f"""
You are a SENIOR BRAND EDITOR.

Brand Voice:
{json.dumps(summary, indent=2)}

Research Direction:
{json.dumps(research, indent=2)}

Improve the article based on these insights:
{json.dumps(brand_report.get("issues", []), indent=2)}

Rewrite rules:
- Improve tone, clarity, flow
- Warm, nurturing, parent-focused
- Indian cultural sensitivity
- Informational only (NO sales)
- SEO keywords naturally
- Preserve markdown formatting

Article:
{article}

Return ONLY rewritten markdown.
"""

    response = safe_openai_call(lambda: openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a brand editor"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    ))

    return response["choices"][0]["message"]["content"]

# ================= MAIN =================
def run():
    print("\n🚀 BRANDING AGENT STARTED\n")

    research = load_json(RESEARCH_PATH)
    summary  = load_json(SUMMARY_PATH)
    article  = load_md(ARTICLE_PATH)

    print("🔍 Evaluating brand alignment...\n")
    report = brand_score_agent(article, research, summary)

    print(f"📊 BRAND SCORE: {report['overall_score']}%")
    print("📌 BREAKDOWN:")
    for k, v in report["breakdown"].items():
        print(f"   {k}: {v}")

    rewrite_required = report["overall_score"] < SCORE_THRESHOLD

    if not rewrite_required:
        user_choice = input(
            "\n✅ Brand alignment is strong.\n"
            "👉 Do you want to rewrite anyway? (yes/no): "
        ).strip().lower()
        rewrite_required = user_choice == "yes"

    if not rewrite_required:
        print("\n🚫 Rewrite skipped by user.")
        return

    print("\n✍️ Rewriting article...\n")
    rewritten = rewrite_article(article, report, research, summary)
    OUTPUT_PATH.write_text(rewritten, encoding="utf-8")

    print("🔁 Re-evaluating rewritten article...\n")
    new_report = brand_score_agent(rewritten, research, summary)

    print(f"✅ NEW BRAND SCORE: {new_report['overall_score']}%")
    print("📌 NEW BREAKDOWN:")
    for k, v in new_report["breakdown"].items():
        print(f"   {k}: {v}")

    print(f"\n📁 FINAL ARTICLE SAVED → {OUTPUT_PATH}")

# ================= ENTRY =================
if __name__ == "__main__":
    run()