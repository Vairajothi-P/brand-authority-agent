"use client";

import { useState } from "react";
import Link from "next/link";

export default function ResearchPage() {
    // State management (same as Streamlit)
    const [topic, setTopic] = useState("AI for school students");
    const [targetAudience, setTargetAudience] = useState("Kids aged 10-14");
    const [contentGoal, setContentGoal] = useState("Educational");
    const [brand, setBrand] = useState("AstroKids");
    const [blogCount, setBlogCount] = useState("1");
    const [region, setRegion] = useState("India");
    const [uploadedFile, setUploadedFile] = useState(null);

    // Results state
    const [loading, setLoading] = useState(false);
    const [researchBriefs, setResearchBriefs] = useState(null);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    // Handler for Run SERP Research Agent (same as Streamlit button logic)
    const handleRunAgent = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setMessage("");

        try {
            const formData = new FormData();
            formData.append("topic", topic);
            formData.append("target_audience", targetAudience);
            formData.append("content_goal", contentGoal);
            formData.append("brand", brand);
            formData.append("region", region);
            formData.append("blog_count", blogCount);
            if (uploadedFile) {
                formData.append("file", uploadedFile);
            }

            const res = await fetch("/api/research-agent", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (data.status === "success") {
                setResearchBriefs(data.research_briefs);
                setMessage(data.message);
            } else {
                setError(data.message || "An error occurred");
            }
        } catch (err) {
            setError(err.message);
            console.error("Error:", err);
        } finally {
            setLoading(false);
        }
    };

    // Helper function to render values (same as Streamlit)
    const renderValue = (value) => {
        if (Array.isArray(value)) {
            return value.join(", ");
        }
        return String(value);
    };

    // Helper function to generate resource link (same as Python function)
    const generateResourceLink = (query) => {
        return `https://www.google.com/search?q=${query.replace(/ /g, "+")}`;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900 text-white p-10">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold">🔍 SERP Research Agent</h1>
                <Link href="/" className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-xl font-semibold">
                    ← Back to Home
                </Link>
            </div>

            {/* Form Section (same as Streamlit form) */}
            <form onSubmit={handleRunAgent} className="grid grid-cols-2 gap-4 max-w-4xl mx-auto bg-white/10 p-6 rounded-xl mb-8" suppressHydrationWarning>
                {/* Provide context manually */}
                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Context:</label>
                    <input
                        type="text"
                        placeholder="Eg: AI for school students"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white placeholder-gray-300"
                        suppressHydrationWarning
                    />
                </div>

                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Target Audience:</label>
                    <input
                        type="text"
                        placeholder="Eg: Kids aged 10–14"
                        value={targetAudience}
                        onChange={(e) => setTargetAudience(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white placeholder-gray-300"
                        suppressHydrationWarning
                    />
                </div>

                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Content Goal:</label>
                    <select
                        value={contentGoal}
                        onChange={(e) => setContentGoal(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                        suppressHydrationWarning
                    >
                        <option value="Educational">Educational</option>
                        <option value="Informational">Informational</option>
                        <option value="Commercial">Commercial</option>
                        <option value="Brand Authority">Brand Authority</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2">Brand:</label>
                    <input
                        type="text"
                        placeholder="Eg: AstroKids"
                        value={brand}
                        onChange={(e) => setBrand(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white placeholder-gray-300"
                        suppressHydrationWarning
                    />
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2">Region:</label>
                    <input
                        type="text"
                        placeholder="Eg: India"
                        value={region}
                        onChange={(e) => setRegion(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white placeholder-gray-300"
                        suppressHydrationWarning
                    />
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2">Number of Blogs to Generate:</label>
                    <select
                        value={blogCount}
                        onChange={(e) => setBlogCount(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                        suppressHydrationWarning
                    >
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                    </select>
                </div>

                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Upload PDF or TXT document (optional):</label>
                    <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                        suppressHydrationWarning
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="col-span-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 py-3 rounded-xl font-semibold text-lg"
                    suppressHydrationWarning
                >
                    {loading ? "⏳ Analyzing SERP & competitors..." : "🚀 Run SERP Research Agent"}
                </button>
            </form>

            {/* Error and Success Messages */}
            {error && <p className="text-red-400 text-center mb-4">❌ {error}</p>}
            {message && <p className="text-green-400 text-center mb-4">{message}</p>}

            {/* Research Briefs Output (same as Streamlit expander) */}
            {researchBriefs && researchBriefs.length > 0 && (
                <div className="max-w-5xl mx-auto">
                    <div className="bg-white/10 p-6 rounded-xl mb-8">
                        <h2 className="text-2xl font-bold mb-4">📊 Research Briefs (Output for Writing Agent)</h2>

                        {researchBriefs.map((brief, idx) => (
                            <div key={idx} className="bg-white/5 p-6 rounded-lg mb-6 border-l-4 border-indigo-500">
                                <h3 className="text-xl font-bold mb-2">📝 Blog {brief.blog_number}</h3>
                                <p className="text-indigo-300 mb-4"><strong>Angle:</strong> {brief.blog_angle}</p>

                                {/* Primary Keyword */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">🎯 Primary Keyword</h4>
                                    <p>
                                        <strong>{brief.primary_keyword}</strong>{" "}
                                        <a
                                            href={generateResourceLink(brief.primary_keyword)}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-blue-400 hover:underline"
                                        >
                                            [🔗]
                                        </a>
                                    </p>
                                </div>

                                {/* Secondary Keywords */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">🔑 Secondary Keywords</h4>
                                    <p><strong>Secondary:</strong> {renderValue(brief.secondary_keywords)}</p>
                                </div>

                                {/* Question Keywords */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">❓ Question Keywords</h4>
                                    <p><strong>Questions:</strong> {renderValue(brief.question_keywords)}</p>
                                </div>

                                {/* Content Angle */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">🧠 Content Angle</h4>
                                    <p>{brief.content_angle}</p>
                                </div>

                                {/* Recommended Structure */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">🧱 Recommended Structure</h4>
                                    <p><strong>Structure:</strong> {renderValue(brief.recommended_structure)}</p>
                                </div>

                                {/* Word Count */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">📏 Word Count</h4>
                                    <p>{brief.recommended_word_count}</p>
                                </div>

                                {/* Ranking Feasibility */}
                                <div className="mb-4">
                                    <h4 className="font-semibold mb-2">🚀 Ranking Feasibility</h4>
                                    <p>{brief.ranking_feasibility}</p>
                                </div>

                                {/* Writing Instructions */}
                                <div>
                                    <h4 className="font-semibold mb-2">✍️ Writing Instructions</h4>
                                    <p><strong>Instructions:</strong> {renderValue(brief.writing_instructions)}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
