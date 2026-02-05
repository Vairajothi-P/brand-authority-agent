 "use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function WritingPage() {
    const [loading, setLoading] = useState(false);
    const [article, setArticle] = useState("");
    const [metadata, setMetadata] = useState({});
    const [suggestion, setSuggestion] = useState("");
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [lastResponse, setLastResponse] = useState(null);

    useEffect(() => {
        runWritingAgent();
    }, []);

    async function runWritingAgent(suggestionText = null) {
        setLoading(true);
        setError("");
        setMessage("");

        try {
            // 🔹 STEP 1: Fetch research agent output
            const briefRes = await fetch("/api/research-agent", { method: "GET" });

            if (!briefRes.ok) {
                throw new Error("Failed to fetch research agent");
            }

            const briefData = await briefRes.json();
            console.debug("Research Agent Response:", briefData);

            // 🔥 UNIVERSAL RESEARCH EXTRACTION
            let briefObject = null;

            if (Array.isArray(briefData?.research_briefs)) {
                briefObject = briefData.research_briefs[0];
            } else if (briefData?.brief) {
                briefObject = briefData.brief;
            } else if (briefData?.data) {
                briefObject = briefData.data;
            } else if (typeof briefData === "object") {
                briefObject = briefData;
            }

            if (!briefObject) {
                throw new Error("Research brief not found in backend response");
            }

            // 🔹 STEP 2: Send research → writing agent
            const formData = new FormData();
            formData.append("brief", JSON.stringify(briefObject));

            const suggestionToSend = suggestionText ?? suggestion;
            if (suggestionToSend) {
                formData.append("suggestion", suggestionToSend);
            }

            const res = await fetch("/api/writing-agent", {
                method: "POST",
                body: formData,
            });

            let data = null;
            try {
                data = await res.json();
            } catch (e) {
                const text = await res.text();
                data = { __raw: text };
            }

            console.debug("Writing Agent Response:", data);
            setLastResponse(data);

            if (!res.ok) {
                throw new Error(data?.error || data?.message || "Writing agent failed");
            }

            if (data?.article) {
                setArticle(data.article);
            }

            setMetadata({
                topic: data?.topic || "",
                primary_keyword: data?.primary_keyword || "",
                secondary_keywords: data?.secondary_keywords || [],
            });

            setMessage("✅ Article generated successfully!");
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    async function downloadArticle() {
        if (!article) return;

        const element = document.createElement("a");
        const file = new Blob([article], { type: "text/markdown" });
        element.href = URL.createObjectURL(file);
        element.download = `article_${Date.now()}.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-purple-900 to-indigo-900 text-white p-10">
            <h1 className="text-4xl font-bold text-center mb-8">📝 Writing Agent</h1>

            {loading && <p className="text-center text-lg">⏳ Generating article...</p>}
            {error && <p className="text-red-400 text-center font-semibold">{error}</p>}
            {message && <p className="text-green-400 text-center font-semibold">{message}</p>}

            {metadata.primary_keyword && (
                <div className="max-w-6xl mx-auto bg-white/10 p-6 rounded-xl mb-8">
                    <h2 className="text-xl font-bold mb-4">📌 Article Metadata</h2>
                    <p><b>Topic:</b> {metadata.topic}</p>
                    <p><b>Primary Keyword:</b> {metadata.primary_keyword}</p>
                    <p><b>Secondary Keywords:</b> {metadata.secondary_keywords?.join(", ")}</p>
                </div>
            )}

            {article && (
                <div className="max-w-4xl mx-auto bg-white/5 p-8 rounded-xl prose prose-invert max-w-none">
                    <ReactMarkdown>{article}</ReactMarkdown>
                </div>
            )}

            {article && (
                <div className="max-w-4xl mx-auto mt-6">
                    <textarea
                        value={suggestion}
                        onChange={(e) => setSuggestion(e.target.value)}
                        placeholder="Optional refinement suggestion..."
                        className="w-full min-h-[100px] p-4 bg-white/5 rounded-lg mb-4"
                    />

                    <div className="flex gap-4">
                        <button
                            onClick={() => runWritingAgent(suggestion)}
                            className="bg-purple-600 px-6 py-3 rounded-xl font-semibold"
                        >
                            🔁 Re-run
                        </button>

                        <button
                            onClick={downloadArticle}
                            className="bg-blue-600 px-6 py-3 rounded-xl font-semibold"
                        >
                            ⬇️ Download
                        </button>

                        <Link
                            href="/branding"
                            className="bg-indigo-600 px-6 py-3 rounded-xl font-semibold"
                        >
                            🧠 Branding Agent
                        </Link>
                    </div>
                </div>
            )}

            {!article && lastResponse && (
                <pre className="max-w-4xl mx-auto mt-6 bg-black/40 p-4 rounded text-sm">
                    {JSON.stringify(lastResponse, null, 2)}
                </pre>
            )}
        </div>
    );
}
