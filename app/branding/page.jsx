"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function BrandingPage() {
    const [loading, setLoading] = useState(false);
    const [article, setArticle] = useState("");
    const [brandedArticle, setBrandedArticle] = useState("");
    const [brandScore, setBrandScore] = useState(null);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [showScoreDetails, setShowScoreDetails] = useState(false);

    useEffect(() => {
        // Load existing branded article on page load
        loadBrandedArticle();
    }, []);

    async function loadBrandedArticle() {
        try {
            const res = await fetch("/api/article-output");
            const data = await res.json();
            if (data.status === "found" && data.article) {
                setBrandedArticle(data.article);
            }
        } catch (err) {
            console.error("Error loading article:", err);
        }
    }

    async function runBrandingAgent() {
        setLoading(true);
        setError("");
        setMessage("");
        setBrandScore(null);

        try {
            const res = await fetch("/api/branding-agent", {
                method: "POST",
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
                setBrandedArticle(data.article);
                setBrandScore(data.brand_score);
                setMessage("✅ Article branded successfully!");
                setShowScoreDetails(true);
            }
        } catch (err) {
            setError(`Error: ${err.message}`);
            console.error("Fetch error:", err);
        } finally {
            setLoading(false);
        }
    }

    async function downloadBrandedArticle() {
        if (!brandedArticle) return;

        const element = document.createElement("a");
        const file = new Blob([brandedArticle], { type: "text/markdown" });
        element.href = URL.createObjectURL(file);
        element.download = `article_branded_${Date.now()}.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-orange-900 to-red-900 text-white p-10">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold">🎨 Branding Agent</h1>
                <Link href="/writing" className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-xl font-semibold">
                    ← Back to Writing Agent
                </Link>
            </div>

            <div className="grid grid-cols-3 gap-4 max-w-6xl mx-auto mb-8">
                <button
                    onClick={runBrandingAgent}
                    disabled={loading}
                    className="col-span-1 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold transition"
                >
                    {loading ? "⏳ Processing..." : "🚀 Run Branding Agent"}
                </button>

                <button
                    onClick={downloadBrandedArticle}
                    disabled={!brandedArticle}
                    className="col-span-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold transition"
                >
                    ⬇️ Download Branded MD
                </button>

                <button
                    onClick={loadBrandedArticle}
                    className="col-span-1 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-xl font-semibold transition"
                >
                    🔄 Reload
                </button>
            </div>

            {loading && <p className="text-center mt-4 text-lg">⏳ Evaluating brand alignment and rewriting...</p>}
            {error && <p className="text-red-400 text-center mt-4 font-semibold">{error}</p>}
            {message && <p className="text-green-400 text-center mt-4 font-semibold">{message}</p>}

            {brandScore && showScoreDetails && (
                <div className="max-w-6xl mx-auto bg-white/10 p-6 rounded-xl mb-8">
                    <h2 className="text-2xl font-bold mb-4">📊 Brand Score Report</h2>

                    <div className="mb-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-lg font-semibold">Overall Score:</span>
                            <span
                                className={`text-3xl font-bold px-4 py-2 rounded-lg ${brandScore.overall_score >= 80
                                        ? "bg-green-500/30 text-green-300"
                                        : brandScore.overall_score >= 60
                                            ? "bg-yellow-500/30 text-yellow-300"
                                            : "bg-red-500/30 text-red-300"
                                    }`}
                            >
                                {brandScore.overall_score}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-4">
                            <div
                                className={`h-4 rounded-full transition-all ${brandScore.overall_score >= 80
                                        ? "bg-green-500"
                                        : brandScore.overall_score >= 60
                                            ? "bg-yellow-500"
                                            : "bg-red-500"
                                    }`}
                                style={{ width: `${brandScore.overall_score}%` }}
                            ></div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-white/5 p-4 rounded-lg">
                            <h3 className="font-semibold text-orange-300 mb-3">Breakdown:</h3>
                            {brandScore.breakdown && Object.entries(brandScore.breakdown).map(([key, value]) => (
                                <div key={key} className="flex justify-between py-1 capitalize">
                                    <span>{key.replace(/_/g, " ")}:</span>
                                    <span className="font-bold text-yellow-300">{value}/100</span>
                                </div>
                            ))}
                        </div>

                        {brandScore.issues && brandScore.issues.length > 0 && (
                            <div className="bg-white/5 p-4 rounded-lg">
                                <h3 className="font-semibold text-red-300 mb-3">Issues Found:</h3>
                                <ul className="list-disc ml-5 space-y-1">
                                    {brandScore.issues.map((issue, idx) => (
                                        <li key={idx} className="text-sm text-gray-200">
                                            {issue}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {brandedArticle && (
                <div className="max-w-4xl mx-auto bg-white/5 p-8 rounded-xl prose prose-invert max-w-none">
                    <h2 className="text-2xl font-bold mb-6 text-white">📄 Branded Article</h2>
                    <ReactMarkdown
                        components={{
                            h1: ({ node, ...props }) => (
                                <h1 className="text-3xl font-bold my-4 text-white" {...props} />
                            ),
                            h2: ({ node, ...props }) => (
                                <h2 className="text-2xl font-bold my-3 text-orange-300" {...props} />
                            ),
                            h3: ({ node, ...props }) => (
                                <h3 className="text-xl font-semibold my-2 text-orange-200" {...props} />
                            ),
                            p: ({ node, ...props }) => (
                                <p className="my-2 text-gray-200 leading-relaxed" {...props} />
                            ),
                            li: ({ node, ...props }) => (
                                <li className="my-1 text-gray-200 ml-4" {...props} />
                            ),
                            code: ({ node, ...props }) => (
                                <code
                                    className="bg-black/50 px-2 py-1 rounded text-yellow-300"
                                    {...props}
                                />
                            ),
                            blockquote: ({ node, ...props }) => (
                                <blockquote
                                    className="border-l-4 border-orange-500 pl-4 my-2 italic text-gray-300"
                                    {...props}
                                />
                            ),
                        }}
                    >
                        {brandedArticle}
                    </ReactMarkdown>
                </div>
            )}
        </div>
    );
}
