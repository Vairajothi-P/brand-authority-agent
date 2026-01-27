export async function POST(request) {
    try {
        const formData = await request.formData();
        const brief = formData.get("brief");

        if (!brief) {
            return Response.json(
                { error: "Brief is required" },
                { status: 400 }
            );
        }

        const backendFormData = new FormData();
        backendFormData.append("brief", brief);

        const res = await fetch("http://localhost:8001/writing-agent", {
            method: "POST",
            body: backendFormData,
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error("Backend error:", errorText);
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
