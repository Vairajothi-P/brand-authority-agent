"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

export default function WritingPage() {
    const [loading, setLoading] = useState(false);
    const [article, setArticle] = useState("");
    const [metadata, setMetadata] = useState({});
    const [suggestion, setSuggestion] = useState("");
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        // Auto-run writing agent on page load
        runWritingAgent();
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

    async function runWritingAgent(suggestionText = null) {
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
            // include optional suggestion/feedback for refinement
            const suggestionToSend = suggestionText ?? suggestion;
            if (suggestionToSend) {
                formData.append("suggestion", suggestionToSend);
            }

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
        const file = new Blob([article], {type: "text/markdown"});
        element.href = URL.createObjectURL(file);
        element.download = `article_${Date.now()}.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    function clearArticle() {
        setArticle("");
        setMetadata({});
        setMessage("");
        setError("");
        setSuggestion("");
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-purple-900 to-indigo-900 text-white p-10">
            <h1 className="text-4xl font-bold text-center mb-8">📝 Writing Agent</h1>

            

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
                            h1: ({node, ...props}) => <h1 className="text-3xl font-bold my-4 text-white" {...props} />,
                            h2: ({node, ...props}) => <h2 className="text-2xl font-bold my-3 text-indigo-300" {...props} />,
                            h3: ({node, ...props}) => <h3 className="text-xl font-semibold my-2 text-indigo-200" {...props} />,
                            p: ({node, ...props}) => <p className="my-2 text-gray-200 leading-relaxed" {...props} />,
                            li: ({node, ...props}) => <li className="my-1 text-gray-200 ml-4" {...props} />,
                            code: ({node, ...props}) => <code className="bg-black/50 px-2 py-1 rounded text-yellow-300" {...props} />,
                            blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-purple-500 pl-4 my-2 italic text-gray-300" {...props} />,
                        }}
                    >
                        {article}
                    </ReactMarkdown>
                </div>
            )}

            {/* Suggestion box + Re-run and Download buttons (bottom) - show only after article exists */}
            {article && (
            <div className="max-w-4xl mx-auto mt-6 mb-16">
                <label className="block text-sm font-semibold mb-2">Suggestion / Feedback (optional):</label>
                <textarea
                    value={suggestion}
                    onChange={(e) => setSuggestion(e.target.value)}
                    placeholder="Add a suggestion or edits for the writing agent..."
                    className="w-full min-h-[100px] p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-300 mb-4"
                />

                <div className="flex gap-4">
                    <button
                        onClick={() => runWritingAgent(suggestion)}
                        disabled={loading}
                        className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold"
                    >
                        {loading ? "⏳ Running..." : "🔁 Re-run with Suggestions"}
                    </button>

                    <button
                        onClick={downloadArticle}
                        disabled={!article}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold"
                    >
                        ⬇️ Download MD
                    </button>

                    <button
                        onClick={() => setSuggestion("")}
                        className="bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-xl font-semibold"
                    >
                        ✖️ Clear Suggestion
                    </button>
                        <Link
                            href="/branding"
                            className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-xl font-semibold inline-block"
                        >
                            📝 Run Branding Agent
                        </Link>
                </div>
            </div>
            )}
        </div>
    );
}
