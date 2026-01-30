"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function BrandingPage() {
    const [loading, setLoading] = useState(false);
    const [article, setArticle] = useState("");
    const [brandedArticle, setBrandedArticle] = useState("");
    const [brandScore, setBrandScore] = useState(null);
    const [suggestion, setSuggestion] = useState("");
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [showScoreDetails, setShowScoreDetails] = useState(false);

    useEffect(() => {
        // Auto-run branding agent on page load
        runBrandingAgent();
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

    async function runBrandingAgent(suggestionText = null) {
        setLoading(true);
        setError("");
        setMessage("");
        setBrandScore(null);

        try {
            const res = await fetch("/api/branding-agent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({}),
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error("Response error:", errorText);
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const data = await res.json();
            console.log("Backend response:", data);

            if (data.error) {
                setError(data.error);
            } else if (data.status === "success") {
                setBrandedArticle(data.article);
                setBrandScore(data.brand_score);
                setMessage("✅ Article evaluated successfully!");
                setShowScoreDetails(true);
            } else {
                console.log("Unexpected response status:", data.status);
                setError(`Unexpected response: ${data.status}`);
            }
        } catch (err) {
            setError(`Error: ${err.message}`);
            console.error("Fetch error:", err);
        } finally {
            setLoading(false);
        }
    }

    async function rewriteWithSuggestion(suggestionText = null) {
        setLoading(true);
        setError("");
        setMessage("");

        try {
            const suggestionToSend = suggestionText !== null ? suggestionText : suggestion;
            
            const res = await fetch("/api/branding-agent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    suggestion: suggestionToSend || "",
                }),
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
                setMessage("✅ Article rewritten successfully!");
                setShowScoreDetails(true);
                setSuggestion("");
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
                <div className="max-w-4xl mx-auto bg-white/5 p-8 rounded-xl prose prose-invert max-w-none mb-8">
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

            {/* Suggestion box + Rewrite and Download buttons (bottom) - show only after article exists AND score < 50 */}
            {brandedArticle && brandScore && brandScore.overall_score < 50 && (
            <div className="max-w-4xl mx-auto mb-16">
                <div className="bg-yellow-500/20 border border-yellow-500 p-4 rounded-lg mb-4">
                    <p className="text-yellow-300 font-semibold">⚠️ Score below 50 - Improvements needed</p>
                </div>
                
                <label className="block text-sm font-semibold mb-2">Suggestion / Feedback:</label>
                <textarea
                    value={suggestion}
                    onChange={(e) => setSuggestion(e.target.value)}
                    placeholder="Add suggestions to improve brand alignment and rewrite the article..."
                    className="w-full min-h-[100px] p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-300 mb-4"
                />

                <div className="flex gap-4">
                    <button
                        onClick={() => rewriteWithSuggestion(suggestion)}
                        disabled={loading || !suggestion}
                        className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold"
                    >
                        {loading ? "⏳ Rewriting..." : "🔁 Rewrite with Suggestions"}
                    </button>

                    <button
                        onClick={() => setSuggestion("")}
                        className="bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-xl font-semibold"
                    >
                        ✖️ Clear Suggestion
                    </button>
                </div>
            </div>
            )}

            {/* Download button - show when score >= 50 or after successful rewrite */}
            {brandedArticle && (!brandScore || brandScore.overall_score >= 50) && (
            <div className="max-w-4xl mx-auto mb-16">
                <button
                    onClick={downloadBrandedArticle}
                    disabled={!brandedArticle}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-3 rounded-xl font-semibold w-full"
                >
                    ⬇️ Download MD
                </button>
            </div>
            )}
        </div>
    );
}
