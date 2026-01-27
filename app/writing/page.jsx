"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function WritingPage() {
    const [loading, setLoading] = useState(false);
    const [article, setArticle] = useState("");
    const [metadata, setMetadata] = useState({});
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        // Load existing article on page load
        loadArticle();
    }, []);

    async function loadArticle() {
        try {
            const res = await fetch("/api/article-output");
            const data = await res.json();
            if (data.status === "found" && data.article) {
                setArticle(data.article);
            }
        } catch (err) {
            console.error("Error loading article:", err);
        }
    }

    async function runWritingAgent() {
        setLoading(true);
        setError("");
        setMessage("");

        try {
            // Load the latest research brief
            const briefRes = await fetch("/api/research-agent", {
                method: "GET",
            });

            let brief = "No brief available";
            if (briefRes.ok) {
                try {
                    const briefData = await briefRes.json();
                    if (briefData.research_briefs && briefData.research_briefs.length > 0) {
                        brief = JSON.stringify(briefData.research_briefs[0]);
                    }
                } catch (e) {
                    console.log("Could not load brief from research-agent endpoint");
                }
            }

            const formData = new FormData();
            formData.append("brief", brief);

            const res = await fetch("/api/writing-agent", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error("Response error:", errorText);
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const data = await res.json();

            if (data.error) {
                setError(data.error);
            } else if (data.status === "success") {
                setArticle(data.article);
                setMetadata({
                    topic: data.topic,
                    primary_keyword: data.primary_keyword,
                    secondary_keywords: data.secondary_keywords
                });
                setMessage("✅ Article generated successfully!");
            }
        } catch (err) {
            setError(`Error: ${err.message}`);
            console.error("Fetch error:", err);
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
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold">📝 Writing Agent</h1>
                <Link href="/research" className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold">
                    ← Back to Research
                </Link>
            </div>

            <div className="grid grid-cols-4 gap-4 max-w-6xl mx-auto mb-8">
                <button
                    onClick={runWritingAgent}
                    disabled={loading}
                    className="col-span-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold"
                >
                    {loading ? "⏳ Generating..." : "🚀 Generate Article"}
                </button>

                <button
                    onClick={downloadArticle}
                    disabled={!article}
                    className="col-span-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold"
                >
                    ⬇️ Download MD
                </button>

                <button
                    onClick={loadArticle}
                    className="col-span-1 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-xl font-semibold"
                >
                    🔄 Reload
                </button>

                <Link href="/branding" className="col-span-1 bg-orange-600 hover:bg-orange-700 px-6 py-3 rounded-xl font-semibold text-center">
                    🎨 Go to Branding Agent
                </Link>
            </div>

            {loading && <p className="text-center mt-4 text-lg">⏳ Generating article...</p>}
            {error && <p className="text-red-400 text-center mt-4 font-semibold">{error}</p>}
            {message && <p className="text-green-400 text-center mt-4 font-semibold">{message}</p>}

            {metadata.primary_keyword && (
                <div className="max-w-6xl mx-auto bg-white/10 p-6 rounded-xl mb-8">
                    <h2 className="text-xl font-bold mb-4">📌 Article Metadata</h2>
                    <p><b>Topic:</b> {metadata.topic}</p>
                    <p><b>Primary Keyword:</b> {metadata.primary_keyword}</p>
                    <p><b>Secondary Keywords:</b> {metadata.secondary_keywords?.join(", ") || "N/A"}</p>
                </div>
            )}

            {article && (
                <div className="max-w-4xl mx-auto bg-white/5 p-8 rounded-xl prose prose-invert max-w-none">
                    <ReactMarkdown
                        components={{
                            h1: ({ node, ...props }) => <h1 className="text-3xl font-bold my-4 text-white" {...props} />,
                            h2: ({ node, ...props }) => <h2 className="text-2xl font-bold my-3 text-indigo-300" {...props} />,
                            h3: ({ node, ...props }) => <h3 className="text-xl font-semibold my-2 text-indigo-200" {...props} />,
                            p: ({ node, ...props }) => <p className="my-2 text-gray-200 leading-relaxed" {...props} />,
                            li: ({ node, ...props }) => <li className="my-1 text-gray-200 ml-4" {...props} />,
                            code: ({ node, ...props }) => <code className="bg-black/50 px-2 py-1 rounded text-yellow-300" {...props} />,
                            blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-purple-500 pl-4 my-2 italic text-gray-300" {...props} />,
                        }}
                    >
                        {article}
                    </ReactMarkdown>
                </div>
            )}
        </div>
    );
}
