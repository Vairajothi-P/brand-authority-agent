export async function POST(request) {
    try {
        const res = await fetch("http://localhost:8001/writing-agent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!res.ok) {
            throw new Error(`Backend error: ${res.status}`);
        }

        const data = await res.json();
        return Response.json(data);
    } catch (error) {
        console.error("Error running writing agent:", error);
        return Response.json(
            { error: "Failed to run writing agent", details: error.message },
            { status: 500 }
        );
    }
}
