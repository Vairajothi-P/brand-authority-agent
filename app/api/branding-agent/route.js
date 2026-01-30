import { NextResponse } from 'next/server';

export async function POST(request) {
    // Extract request body (support JSON or form)
    let requestBody = {};
    try {
        const contentType = request.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            requestBody = await request.json();
        } else if (contentType && contentType.includes("application/x-www-form-urlencoded")) {
            const formData = await request.formData();
            requestBody = Object.fromEntries(formData);
        }
    } catch (e) {
        console.log("No request body provided or failed to parse body:", e?.message || e);
    }

    // Call backend using 127.0.0.1 to avoid potential localhost/IPv6 resolution issues
    const backendUrl = "http://127.0.0.1:8001/branding-agent";

    try {
        const res = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error("Backend error:", res.status, errorText);
            return NextResponse.json({ error: "Backend error", details: errorText }, { status: 502 });
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error running branding agent (fetch):", error);
        return NextResponse.json({ error: "Failed to run branding agent", details: String(error) }, { status: 500 });
    }
}
