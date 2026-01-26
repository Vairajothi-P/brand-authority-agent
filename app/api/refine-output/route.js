export async function POST(request) {
    try {
        const body = await request.formData();
        const suggestion = body.get("suggestion");

        const formData = new FormData();
        formData.append("suggestion", suggestion);

        const res = await fetch("http://localhost:8001/refine-output", {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            throw new Error(`Backend error: ${res.status}`);
        }

        const data = await res.json();
        return Response.json(data);
    } catch (error) {
        console.error("Error refining output:", error);
        return Response.json(
            { error: "Failed to refine output", details: error.message },
            { status: 500 }
        );
    }
}
