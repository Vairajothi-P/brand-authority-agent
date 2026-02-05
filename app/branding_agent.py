import json
import os
import time
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

if not os.getenv("GEMINI_API_KEY"):
    raise Exception("❌ GEMINI_API_KEY not set")

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent

RESEARCH_PATH = BASE_DIR / "agent_outputs" / "research_briefs.json"
ARTICLE_PATH  = BASE_DIR / "outputs" / "article.md"
OUTPUT_PATH   = BASE_DIR / "outputs" / "article_branded.md"

RATE_WAIT = 30
SCORE_THRESHOLD = 50  # Auto-regenerate if below 50%

brand_tone = """
Warm, nurturing, informative
Target audience: Indian parents
No sales language
SEO-friendly but human
"""

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

# ================= BRAND SCORING AGENT =================
def brand_score_agent(article, research, brand_tone):
    prompt = f"""
You are a strict BRAND EVALUATION AGENT.

Brand Voice Guidelines:
{brand_tone}

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

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction="You are a brand auditor"
    )
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0)
    )

    text = (response.text or "").strip()
    if not text:
        raise Exception("Empty response from model when computing brand score")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
            try:
                return json.loads(candidate)
            except Exception:
                pass
        snippet = text[:1000].replace('\n', ' ')
        raise Exception(f"Invalid JSON from model when computing brand score. Response snippet: {snippet}")

# ================= REWRITE AGENT =================
def rewrite_article(article, brand_report, research, brand_tone):
    prompt = f"""
You are a SENIOR BRAND EDITOR.

Brand Voice Guidelines:
{brand_tone}

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

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction="You are a brand editor"
    )
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.4)
    )

    return response.text

# ================= API MODE =================
def run_branding_agent_api(brand_tone, suggestion=None):
    try:
        article = load_md(ARTICLE_PATH)
        research = load_json(RESEARCH_PATH)

        report = brand_score_agent(article, research, brand_tone)
        initial_score = report['overall_score']

        final_article = article
        final_score = initial_score

        print(f"📊 Initial score: {initial_score}%")

        if suggestion:
            prompt = f"""
You are a SENIOR BRAND EDITOR.

Brand Voice Guidelines:
{brand_tone}

User Feedback:
{suggestion}

Article:
{article}

Rewrite the article considering the user's feedback while maintaining brand voice.
Return ONLY rewritten markdown.
"""
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a brand editor"
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.4)
            )
            final_article = response.text

            new_report = brand_score_agent(final_article, research, brand_tone)
            final_score = new_report['overall_score']

            OUTPUT_PATH.write_text(final_article, encoding="utf-8")

            return {
                "status": "success",
                "initial_score": initial_score,
                "final_score": final_score,
                "article": final_article,
                "brand_score": new_report
            }

        OUTPUT_PATH.write_text(article, encoding="utf-8")
        return {
            "status": "success",
            "initial_score": initial_score,
            "final_score": initial_score,
            "article": article,
            "brand_score": report
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

async def run_branding_agent(brand_tone, suggestion=None):
    return run_branding_agent_api(brand_tone=brand_tone, suggestion=suggestion)

# ================= MAIN =================
def run():
    print("\n🚀 BRANDING AGENT STARTED\n")

    research = load_json(RESEARCH_PATH)
    article  = load_md(ARTICLE_PATH)

    print("🔍 Evaluating brand alignment...\n")
    report = brand_score_agent(article, research, brand_tone)

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
    rewritten = rewrite_article(article, report, research, brand_tone)
    OUTPUT_PATH.write_text(rewritten, encoding="utf-8")

    print("🔁 Re-evaluating rewritten article...\n")
    new_report = brand_score_agent(rewritten, research, brand_tone)

    print(f"✅ NEW BRAND SCORE: {new_report['overall_score']}%")
    print("📌 NEW BREAKDOWN:")
    for k, v in new_report["breakdown"].items():
        print(f"   {k}: {v}")

    print(f"\n📁 FINAL ARTICLE SAVED → {OUTPUT_PATH}")

# ================= ENTRY =================
if __name__ == "__main__":
    run()
