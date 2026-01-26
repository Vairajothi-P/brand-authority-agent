export async function GET(request) {
    try {
        const res = await fetch("http://localhost:8001/article-output");
        const data = await res.json();
        return Response.json(data);
    } catch (error) {
        console.error("Error fetching article:", error);
        return Response.json(
            { error: "Failed to fetch article", details: error.message },
            { status: 500 }
        );
    }
}
