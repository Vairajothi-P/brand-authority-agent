export async function POST(request) {
    try {
        const res = await fetch("http://localhost:8001/save-output", {
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
        console.error("Error saving output:", error);
        return Response.json(
            { error: "Failed to save output", details: error.message },
            { status: 500 }
        );
    }
}
