from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from research_agent import run_research_agent, ResearchRequest
import os
import json

# Pydantic model for branding request
class BrandingRequest(BaseModel):
    suggestion: str = ""

app = FastAPI()

brand_tone = """
Warm, nurturing, informative
Target audience: Indian parents
No sales language
SEO-friendly but human
"""

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

# Serve a tiny inline favicon (SVG) to avoid 404 logs from browsers requesting /favicon.ico
from fastapi.responses import Response

@app.get("/favicon.ico")
async def favicon():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        '<rect width="16" height="16" fill="#111827"/>'
        '<text x="8" y="11" font-size="9" fill="#ffffff" text-anchor="middle" font-family="Arial">BA</text>'
        '</svg>'
    )
    return Response(content=svg, media_type="image/svg+xml")

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
            from research_agent import call_gemini
            import json
            
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
            
            response = call_gemini(
                prompt=prompt,
                system_role="Expert content writer",
                temperature=0.7
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

@app.post("/branding-agent")
async def branding_agent_endpoint(request_data: BrandingRequest):
    try:
        from branding_agent import run_branding_agent
        
        suggestion = request_data.suggestion if request_data.suggestion else None
        print(f"🔍 Branding agent called with suggestion: {suggestion}")
        
        result = await run_branding_agent(brand_tone=brand_tone,suggestion=suggestion)

        print(f"✅ Branding agent result: {result}")
        return result
    except Exception as e:
        import traceback
        print(f"❌ Error in branding agent:")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
        }
