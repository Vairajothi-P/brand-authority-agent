import os
import json
import time
import re
import openai
from dotenv import load_dotenv
from openai.error import RateLimitError

# ================= ENV =================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ================= PATH CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESEARCH_JSON_PATH = os.path.join(
    BASE_DIR,
    "agent_outputs",
    "research_brief.json"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
RATE_LIMIT_WAIT = 20

# ================= UTILS =================
def call_openai_with_retry(fn, retries=5):
    for _ in range(retries):
        try:
            return fn()
        except RateLimitError:
            print(f"⏳ Rate limit hit. Waiting {RATE_LIMIT_WAIT}s...")
            time.sleep(RATE_LIMIT_WAIT)
    raise Exception("❌ OpenAI retry limit exhausted")

def extract_json(text):
    text = re.sub(r"```json|```", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group()) if match else None

def load_research_brief():
    if not os.path.exists(RESEARCH_JSON_PATH):
        raise FileNotFoundError(f"❌ Missing research file: {RESEARCH_JSON_PATH}")
    with open(RESEARCH_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ================= STATE =================
class ArticleState:
    def __init__(self, research):
        self.research = research

        self.primary_keyword = research.get("primary_keyword", "AI tools")
        self.secondary_keywords = research.get("secondary_keywords", [])
        self.word_count = research.get("recommended_word_count", 2000)

        self.topic = research.get(
            "topic",
            f"How {self.primary_keyword.title()} Improve Productivity"
        )

        self.sections = None
        self.article = None
        self.done = False

# ================= AGENTS =================
class OutlineAgent:
    def act(self, article):
        if article.sections:
            return

        print("🧠 Generating sections automatically...")

        prompt = f"""
You are a professional content strategist.

Based on SEO research, generate a blog structure.

Topic: {article.topic}
Primary keyword: {article.primary_keyword}
Secondary keywords: {article.secondary_keywords}

Rules:
- Informational intent
- Logical learning flow
- Student + startup focus
- No fluff
- No generic headings

Return ONLY JSON:
{{
  "sections": [
    "Introduction",
    "Concept explanation",
    "Key benefits",
    "Student use cases",
    "Startup use cases",
    "Tool comparison",
    "Best practices",
    "Conclusion"
  ]
}}
"""

        res = call_openai_with_retry(lambda: openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Return clean JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        ))

        data = extract_json(res["choices"][0]["message"]["content"])
        article.sections = data["sections"]
        print("🗂 Sections created dynamically")

class WritingAgent:
    def act(self, article):
        if article.article:
            return

        print("✍️ Writing full article...")

        prompt = f"""
Write an INFORMATIONAL blog article in Markdown.

STRICT RULES:
- Active voice only
- Human, simple language
- No AI clichés
- No promotional tone
- Primary + secondary keywords max 5 times total

Blog Structure:
- H1 Title
- Introduction (2–3 short paragraphs)
- H2/H3 sections
- 2–4 paragraphs per section
- Bullet points / lists
- Examples & real use cases
- Conclusion

Topic: {article.topic}
Primary keyword: {article.primary_keyword}
Secondary keywords: {article.secondary_keywords}
Sections to cover: {article.sections}
Target length: {article.word_count} words

Mandatory:
- Student examples
- Startup productivity examples
- Comparison table (where relevant)

Return ONLY the blog content.
"""

        res = call_openai_with_retry(lambda: openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Expert informational blogger."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        ))

        article.article = res["choices"][0]["message"]["content"]
        print("📝 Article generated")

class OutputAgent:
    def act(self, article):
        if article.done:
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        path = os.path.join(OUTPUT_DIR, "article.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(article.article)

        article.done = True
        print(f"💾 Article saved → {path}")

# ================= SUPERVISOR =================
class Supervisor:
    def decide(self, article):
        if not article.sections:
            return "OUTLINE"
        if not article.article:
            return "WRITE"
        if not article.done:
            return "SAVE"
        return "DONE"

# ================= MAIN =================
def run():
    print("\n🚀 Fully Automatic Research-Based Content Pipeline Started\n")

    research_data = load_research_brief()
    print(f"📥 Loaded primary keyword → {research_data.get('primary_keyword')}")

    article = ArticleState(research_data)

    agents = {
        "OUTLINE": OutlineAgent(),
        "WRITE": WritingAgent(),
        "SAVE": OutputAgent()
    }

    supervisor = Supervisor()

    while True:
        action = supervisor.decide(article)
        if action == "DONE":
            print("\n✅ Content generation completed successfully\n")
            break
        agents[action].act(article)

# ================= ENTRY =================
if __name__ == "__main__":
    run()