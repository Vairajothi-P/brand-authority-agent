import os
import json
from dotenv import load_dotenv
import openai

# =========================
# ENV SETUP
# =========================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# =========================
# CONFIG
# =========================
ARTICLE_PATH = "outputs/article.md"
ACCEPTED_MD_PATH = "outputs/accepted_article.md"
TONE_THRESHOLD = 50
MAX_REWRITE_ATTEMPTS = 3

# =========================
# FIXED BRAND TONE SUMMARY
# =========================
BRAND_TONE_SUMMARY = """
The AstroKids brand voice is calm, compassionate, and parent-supportive.
The tone is reassuring and emotionally sensitive, never urgent, fearful,
or sales-driven. Content speaks directly to parents using "you" and "we".
Language is simple, nurturing, and free from hype or jargon.
Astrology is framed as guidance, not prediction or medical advice.
The goal is to reduce parental anxiety and encourage patience and understanding.
"""

# =========================
# READ ARTICLE
# =========================
def read_article(path):
    if not os.path.exists(path):
        raise FileNotFoundError("Article file not found at outputs/article.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# =========================
# SCORE TONE
# =========================
def score_tone(article):
    prompt = f"""
You are a strict Branding Evaluation Agent.

Evaluate the article against the brand tone summary.

Brand Tone Summary:
{BRAND_TONE_SUMMARY}

Rules:
- Score from 0 to 100
- Penalize hype, fear, sales language, AI-generic phrasing
- Reward calm, compassionate, parent-supportive tone

Return ONLY valid JSON:
{{
  "tone_match_score": number,
  "analysis": "short explanation"
}}

Article:
{article}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You evaluate brand tone alignment."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)

# =========================
# REWRITE ARTICLE
# =========================
def rewrite_article(article):
    prompt = f"""
Rewrite the article below so that it strictly matches the brand tone summary.

Brand Tone Summary:
{BRAND_TONE_SUMMARY}

Instructions:
- Maintain original meaning
- Remove hype, fear, and sales language
- Use calm, compassionate, parent-supportive tone
- Avoid AI-generic phrases

Return ONLY the rewritten article.

Article:
{article}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You rewrite content to match brand tone."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# =========================
# SAVE ACCEPTED ARTICLE AS MD
# =========================
def save_as_markdown(article):
    os.makedirs("outputs", exist_ok=True)
    with open(ACCEPTED_MD_PATH, "w", encoding="utf-8") as f:
        f.write(article)

# =========================
# MAIN AGENT LOOP
# =========================
def run_brand_agent():
    print("\n--- Branding Agent Started ---\n")

    article = read_article(ARTICLE_PATH)

    for attempt in range(1, MAX_REWRITE_ATTEMPTS + 1):
        result = score_tone(article)
        score = result["tone_match_score"]
        analysis = result["analysis"]

        print(f"Attempt {attempt}")
        print(f"Tone Match Score: {score}")
        print(f"Analysis: {analysis}\n")

        if score >= TONE_THRESHOLD:
            save_as_markdown(article)
            print("✅ Article ACCEPTED and saved as outputs/accepted_article.md")
            return

        print("❌ Tone mismatch — rewriting article...\n")
        article = rewrite_article(article)

    print("⚠️ Max rewrite attempts reached.")
    final_result = score_tone(article)

    if final_result["tone_match_score"] >= TONE_THRESHOLD:
        save_as_markdown(article)
        print("✅ Final improved version accepted and saved as .md")
    else:
        print("❌ Article failed brand tone. No output saved.")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_brand_agent()
