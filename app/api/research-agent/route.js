export async function POST(request) {
    try {
        const body = await request.json();

        const res = await fetch("http://localhost:8001/research-agent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            throw new Error(`Backend error: ${res.status}`);
        }

        const data = await res.json();
        return Response.json(data);
    } catch (error) {
        console.error("Error running research agent:", error);
        return Response.json(
            { error: "Failed to run research agent", details: error.message },
            { status: 500 }
        );
    }
}
