import { readFile } from "fs/promises";
import { join } from "path";
import { existsSync } from "fs";

export const GET = async (req) => {
    try {
        const filePath = join(process.cwd(), "app", "agent_outputs", "research_briefs.json");
        
        if (!existsSync(filePath)) {
            return Response.json(
                {
                    status: "error",
                    message: "No research briefs found. Run the research agent first.",
                    research_briefs: [],
                },
                { status: 404 }
            );
        }
        
        const content = await readFile(filePath, "utf-8");
        const research_briefs = JSON.parse(content);
        
        return Response.json({
            status: "success",
            research_briefs: research_briefs,
        });
    } catch (error) {
        console.error("API Route Error:", error);
        return Response.json(
            {
                status: "error",
                message: error.message,
            },
            { status: 500 }
        );
    }
};

export const POST = async (req) => {
    try {
        const formData = await req.formData();

        // Extract form fields
        const topic = formData.get("topic");
        const target_audience = formData.get("target_audience");
        const content_goal = formData.get("content_goal");
        const brand = formData.get("brand") || "Brand Authority Agent";
        const region = formData.get("region");
        const blog_count = formData.get("blog_count") || "1";

        // Create new FormData for backend
        const backendFormData = new FormData();
        backendFormData.append("topic", topic);
        backendFormData.append("target_audience", target_audience);
        backendFormData.append("content_goal", content_goal);
        backendFormData.append("brand", brand);
        backendFormData.append("region", region);
        backendFormData.append("blog_count", blog_count);

        // Add file if present
        const file = formData.get("file");
        if (file) {
            backendFormData.append("file", file);
        }

        // Call backend API
        const backendUrl = process.env.BACKEND_URL || "http://localhost:8001";
        const response = await fetch(`${backendUrl}/run-research-agent`, {
            method: "POST",
            body: backendFormData,
        });

        const data = await response.json();

        if (!response.ok) {
            return Response.json(
                {
                    status: "error",
                    message: data.detail || data.message || "Backend error",
                },
                { status: response.status }
            );
        }

        return Response.json(data);
    } catch (error) {
        console.error("API Route Error:", error);
        return Response.json(
            {
                status: "error",
                message: error.message,
            },
            { status: 500 }
        );
    }
};
