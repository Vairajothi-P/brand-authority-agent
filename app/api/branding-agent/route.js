export async function POST(request) {
    try {
        const res = await fetch("http://localhost:8001/branding-agent", {
            method: "POST",
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error("Backend error:", errorText);
            throw new Error(`Backend error: ${res.status}`);
        }

        const data = await res.json();
        return Response.json(data);
    } catch (error) {
        console.error("Error running branding agent:", error);
        return Response.json(
            { error: "Failed to run branding agent", details: error.message },
            { status: 500 }
        );
    }
}
