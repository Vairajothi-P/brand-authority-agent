# import os
# import json
# import time
# import re
# import openai
# from dotenv import load_dotenv
# from openai.error import RateLimitError

# # ================= ENV =================
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# if not openai.api_key:
#     raise Exception("❌ OPENAI_API_KEY set pannala")

# # ================= PATH CONFIG =================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# RESEARCH_JSON_PATH = os.path.join(
#     BASE_DIR,
#     "agent_outputs",
#     "research_briefs.json"
# )

# OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
# RATE_LIMIT_WAIT = 20

# # ================= UTILS =================
# def call_openai_with_retry(fn, retries=5):
#     for _ in range(retries):
#         try:
#             return fn()
#         except RateLimitError:
#             print(f"⏳ Rate limit hit. Waiting {RATE_LIMIT_WAIT}s...")
#             time.sleep(RATE_LIMIT_WAIT)
#     raise Exception("❌ OpenAI retry limit exhausted")

# def extract_json(text):
#     text = re.sub(r"```json|```", "", text)
#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     if not match:
#         raise ValueError("❌ JSON not found in model response")
#     return json.loads(match.group())

# def load_research_briefs():
#     if not os.path.exists(RESEARCH_JSON_PATH):
#         raise FileNotFoundError(f"❌ Missing research file: {RESEARCH_JSON_PATH}")

#     with open(RESEARCH_JSON_PATH, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     # 🔥 MAIN FIX HERE
#     if isinstance(data, list):
#         return data[0]   # first research brief

#     return data

# # ================= STATE =================
# class ArticleState:
#     def __init__(self, research):
#         self.research = research

#         self.primary_keyword = research.get("primary_keyword")
#         self.secondary_keywords = research.get("secondary_keywords", [])
#         self.word_count = research.get("recommended_word_count", 1500)

#         self.topic = research.get(
#             "topic",
#             f"{self.primary_keyword.title()} Explained for Students and Startups"
#         )

#         self.sections = None
#         self.article = None
#         self.done = False

# # ================= AGENTS =================
# class OutlineAgent:
#     def act(self, article):
#         if article.sections:
#             return

#         print("🧠 Generating sections automatically...")

#         prompt = f"""
# Create a clear educational blog outline.

# Topic: {article.topic}
# Primary keyword: {article.primary_keyword}
# Secondary keywords: {article.secondary_keywords}

# Rules:
# - Informational
# - Logical learning flow
# - Student + startup focus
# - No generic headings

# Return ONLY JSON:
# {{
#   "sections": []
# }}
# """

#         res = call_openai_with_retry(lambda: openai.ChatCompletion.create(
#             model="gpt-4.1-mini",
#             messages=[
#                 {"role": "system", "content": "Return clean JSON only"},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.4
#         ))

#         data = extract_json(res["choices"][0]["message"]["content"])
#         article.sections = data["sections"]
#         print("🗂 Sections created")

# class WritingAgent:
#     def act(self, article):
#         if article.article:
#             return

#         print("✍️ Writing full article...")

#         prompt = f"""
# Write an INFORMATIONAL blog article in Markdown.

# Rules:
# - Simple human language
# - No promotional tone
# - Active voice
# - Real examples
# - SEO optimized

# Topic: {article.topic}
# Primary keyword: {article.primary_keyword}
# Secondary keywords: {article.secondary_keywords}
# Sections: {article.sections}
# Target length: {article.word_count} words

# Return ONLY article content.
# """

#         res = call_openai_with_retry(lambda: openai.ChatCompletion.create(
#             model="gpt-4.1-mini",
#             messages=[
#                 {"role": "system", "content": "Expert informational blogger"},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7
#         ))

#         article.article = res["choices"][0]["message"]["content"]
#         print("📝 Article generated")

# class OutputAgent:
#     def act(self, article):
#         if article.done:
#             return

#         os.makedirs(OUTPUT_DIR, exist_ok=True)

#         output_path = os.path.join(OUTPUT_DIR, "article.md")
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(article.article)

#         article.done = True
#         print(f"💾 Article saved → {output_path}")

# # ================= SUPERVISOR =================
# class Supervisor:
#     def decide(self, article):
#         if not article.sections:
#             return "OUTLINE"
#         if not article.article:
#             return "WRITE"
#         if not article.done:
#             return "SAVE"
#         return "DONE"

# # ================= MAIN =================
# def run():
#     print("\n🚀 Fully Automatic Research-Based Content Pipeline Started\n")

#     research = load_research_briefs()
#     print(f"📥 Loaded primary keyword → {research.get('primary_keyword')}")

#     article = ArticleState(research)

#     agents = {
#         "OUTLINE": OutlineAgent(),
#         "WRITE": WritingAgent(),
#         "SAVE": OutputAgent()
#     }

#     supervisor = Supervisor()

#     while True:
#         step = supervisor.decide(article)
#         if step == "DONE":
#             print("\n✅ Content generation completed successfully\n")
#             break
#         agents[step].act(article)

# # ================= ENTRY =================
# if __name__ == "__main__":
#     run()

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

if not openai.api_key:
    raise Exception("❌ OPENAI_API_KEY set pannala")

# ================= PATH CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESEARCH_JSON_PATH = os.path.join(
    BASE_DIR, "agent_outputs", "research_briefs.json"
)

SUMMARY_JSON_PATH = os.path.join(
    BASE_DIR, "agent_outputs", "summary.json"
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
    if not match:
        raise ValueError("❌ JSON not found in model response")
    return json.loads(match.group())

def load_json(path, name):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Missing {name}: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0] if isinstance(data, list) else data

# ================= STATE =================
class ArticleState:
    def __init__(self, research, summary):
        self.research = research
        self.summary = summary

        # SEO side
        self.primary_keyword = research.get("primary_keyword")
        self.secondary_keywords = research.get("secondary_keywords", [])
        self.word_count = research.get("recommended_word_count", 1500)

        # Topic priority:
        self.topic = research.get(
            "topic",
            summary.get("topic_override") if summary else None
        ) or f"{self.primary_keyword.title()} Explained Clearly"

        # Context from summary
        self.context = summary.get("context", "")
        self.key_points = summary.get("key_points", [])
        self.tone_guidelines = summary.get("tone", "Informational")

        self.sections = None
        self.article = None
        self.done = False

# ================= AGENTS =================
class OutlineAgent:
    def act(self, article):
        if article.sections:
            return

        print("🧠 Generating sections using research + summary...")

        prompt = f"""
Create a blog outline by COMBINING SEO research and content context.

Topic: {article.topic}

Primary keyword: {article.primary_keyword}
Secondary keywords: {article.secondary_keywords}

Context summary:
{article.context}

Important points to cover:
{article.key_points}

Rules:
- Informational
- Context-aware (not generic SEO)
- Logical learning flow
- No marketing fluff

Return ONLY JSON:
{{
  "sections": []
}}
"""

        res = call_openai_with_retry(lambda: openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Return clean JSON only"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        ))

        data = extract_json(res["choices"][0]["message"]["content"])
        article.sections = data["sections"]
        print("🗂 Sections created (context-aware)")

class WritingAgent:
    def act(self, article):
        if article.article:
            return

        print("✍️ Writing article using research + summary...")

        prompt = f"""
Write an INFORMATIONAL blog article in Markdown.

Tone:
{article.tone_guidelines}

Context to respect:
{article.context}

Important focus points:
{article.key_points}

SEO Requirements:
Primary keyword: {article.primary_keyword}
Secondary keywords: {article.secondary_keywords}

Sections:
{article.sections}

Target length: {article.word_count} words

Rules:
- Human natural writing
- No AI fillers
- Context > keyword stuffing
- Examples where relevant

Return ONLY article content.
"""

        res = call_openai_with_retry(lambda: openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Expert contextual SEO writer"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.65
        ))

        article.article = res["choices"][0]["message"]["content"]
        print("📝 Article generated (research + summary aligned)")

class OutputAgent:
    def act(self, article):
        if article.done:
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, "article.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(article.article)

        article.done = True
        print(f"💾 Article saved → {output_path}")

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
    print("\n🚀 Research + Summary Based Content Pipeline Started\n")

    research = load_json(RESEARCH_JSON_PATH, "research_briefs.json")
    summary = load_json(SUMMARY_JSON_PATH, "summary.json")

    print(f"📥 SEO Keyword → {research.get('primary_keyword')}")
    print(f"📘 Summary Context Loaded")

    article = ArticleState(research, summary)

    agents = {
        "OUTLINE": OutlineAgent(),
        "WRITE": WritingAgent(),
        "SAVE": OutputAgent()
    }

    supervisor = Supervisor()

    while True:
        step = supervisor.decide(article)
        if step == "DONE":
            print("\n✅ Context-aware content generated successfully\n")
            break
        agents[step].act(article)

# ================= ENTRY =================
if __name__ == "__main__":
    run()
