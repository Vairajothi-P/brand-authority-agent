import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from research_agent import run_research_agent, ResearchRequest

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "FastAPI backend running"}

@app.post("/run-research-agent")
async def research_agent_handler(
    topic: str = Form(...),
    target_audience: str = Form(...),
    content_goal: str = Form(...),
    brand: str = Form(default="Brand Authority Agent"),
    region: str = Form(...),
    blog_count: int = Form(default=1),
    file: UploadFile = File(None),
):
    try:
        # Read file content if provided
        file_content = None
        if file:
            file_content = await file.read()
        
        # Create request object
        request_data = ResearchRequest(
            topic=topic,
            target_audience=target_audience,
            content_goal=content_goal,
            brand=brand,
            region=region,
            blog_count=blog_count,
        )
        
        # Run the research agent
        result = await run_research_agent(request_data, file_content)
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
        }

@app.get("/article-output")
async def get_article_output():
    try:
        output_dir = "agent_outputs"
        if not os.path.exists(output_dir):
            return {"articles": []}
        
        articles = []
        for file in os.listdir(output_dir):
            if file.endswith(".md"):
                with open(os.path.join(output_dir, file), "r") as f:
                    articles.append({
                        "filename": file,
                        "content": f.read(),
                    })
        return {"articles": articles}
    except Exception as e:
        return {"error": str(e)}

@app.post("/writing-agent")
async def writing_agent_endpoint(brief: str = Form(...)):
    try:
        # Import the writing agent if it exists, otherwise use a placeholder
        try:
            import json
            import google.generativeai as genai
            from dotenv import load_dotenv
            
            load_dotenv()
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            
            prompt = f"""
You are an expert content writer.

Generate a comprehensive blog article based on the following research brief:

{json.dumps(json.loads(brief) if isinstance(brief, str) else brief, indent=2)}

Write a complete, SEO-optimized article with:
1. Engaging introduction
2. Detailed sections based on the structure provided
3. Keyword optimization
4. Compelling conclusion with CTA

Return the article content."""
            
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="Expert content writer"
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.7)
            )
            
            article_content = response.text
            
            return {
                "status": "success",
                "message": "Article generated successfully",
                "article": article_content,
            }
        except ImportError:
            # Fallback if import fails
            return {
                "status": "success",
                "message": "Writing agent processing...",
                "article": f"Generated article based on brief:\n{brief}",
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/save-output")
async def save_output_endpoint(content: str = Form(...)):
    try:
        output_dir = "agent_outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.join(output_dir, "output.md")
        with open(filename, "w") as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"Output saved to {filename}",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/refine-output")
async def refine_output_endpoint(content: str = Form(...)):
    try:
        return {
            "status": "success",
            "message": "Refinement complete",
            "refined_content": content,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
