"use client";

import { useState } from "react";
import Link from "next/link";

export default function ResearchPage() {
    // State management (unchanged)
    const [topic, setTopic] = useState("AI for school students");
    const [targetAudience, setTargetAudience] = useState("Kids aged 10-14");
    const [contentGoal, setContentGoal] = useState("Educational");
    const [brand, setBrand] = useState("AstroKids");
    const [blogCount, setBlogCount] = useState("1"); // kept for UI consistency
    const [region, setRegion] = useState("India");
    const [uploadedFile, setUploadedFile] = useState(null);

    // Results state (MODIFIED)
    const [loading, setLoading] = useState(false);
    const [researchBrief, setResearchBrief] = useState(null);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    // Handler
    const handleRunAgent = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setMessage("");
        setResearchBrief(null);

        try {
            const formData = new FormData();
            formData.append("topic", topic);
            formData.append("target_audience", targetAudience);
            formData.append("content_goal", contentGoal);
            formData.append("brand", brand);
            formData.append("region", region);
            formData.append("blog_count", blogCount); // harmless, ignored by backend
            if (uploadedFile) {
                formData.append("file", uploadedFile);
            }

            const res = await fetch("/api/research-agent", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            // 🔑 STRICT OUTPUT HANDLING
            setResearchBrief(data);
            setMessage("✅ Research brief generated successfully");

        } catch (err) {
            setError(err.message);
            console.error("Error:", err);
        } finally {
            setLoading(false);
        }
    };

    const renderValue = (value) => {
        if (Array.isArray(value)) return value.join(", ");
        return String(value);
    };

    const generateResourceLink = (query) =>
        `https://www.google.com/search?q=${query.replace(/ /g, "+")}`;

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-700 to-blue-700 text-white p-10">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold text-center flex-1">
                    🔍 SERP Research Agent
                </h1>
                <Link
                    href="/writing"
                    className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-xl font-semibold"
                >
                    📝 Writing Agent
                </Link>
            </div>

            {/* FORM (UNCHANGED) */}
            <form
                onSubmit={handleRunAgent}
                className="grid grid-cols-2 gap-4 max-w-4xl mx-auto bg-white/10 p-6 rounded-xl mb-8"
                suppressHydrationWarning
            >
                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Context:</label>
                    <input
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                    />
                </div>

                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Target Audience:</label>
                    <input
                        value={targetAudience}
                        onChange={(e) => setTargetAudience(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                    />
                </div>

                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">Content Goal:</label>
                    <select
                        value={contentGoal}
                        onChange={(e) => setContentGoal(e.target.value)}
                        className="w-full px-4 py-2 bg-black/20 border border-indigo-400 rounded-lg text-white"
                    >
                        <option>Educational</option>
                        <option>Informational</option>
                        <option>Commercial</option>
                        <option>Brand Authority</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2">Brand:</label>
                    <input
                        value={brand}
                        onChange={(e) => setBrand(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                    />
                </div>

                <div>
                    <label className="block text-sm font-semibold mb-2">Region:</label>
                    <input
                        value={region}
                        onChange={(e) => setRegion(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="col-span-2 bg-indigo-600 hover:bg-indigo-700 py-3 rounded-xl font-semibold text-lg"
                >
                    {loading ? "⏳ Analyzing SERP & competitors..." : "🚀 Run SERP Research Agent"}
                </button>
            </form>

            {error && <p className="text-red-400 text-center mb-4">❌ {error}</p>}
            {message && <p className="text-green-400 text-center mb-4">{message}</p>}

            {/* 🔥 FINAL STRICT OUTPUT */}
            {researchBrief && (
                <div className="max-w-5xl mx-auto">
                    <div className="bg-white/10 p-6 rounded-xl">
                        <h2 className="text-2xl font-bold mb-4">
                            📊 Research Brief (Writing Agent Input)
                        </h2>

                        <p className="mb-2">
                            <strong>🎯 Primary Keyword:</strong>{" "}
                            <a
                                href={generateResourceLink(researchBrief.primary_keyword)}
                                className="text-blue-300 underline"
                                target="_blank"
                            >
                                {researchBrief.primary_keyword}
                            </a>
                        </p>

                        <p className="mb-2">
                            <strong>🔑 Secondary Keywords:</strong>{" "}
                            {renderValue(researchBrief.secondary_keywords)}
                        </p>

                        <p className="mb-2">
                            <strong>❓ Question Keywords:</strong>{" "}
                            {renderValue(researchBrief.question_keywords)}
                        </p>

                        <p className="mb-2">
                            <strong>🧠 Content Angle:</strong>{" "}
                            {researchBrief.content_angle}
                        </p>

                        <p className="mb-2">
                            <strong>🚀 Ranking Feasibility:</strong>{" "}
                            {researchBrief.ranking_feasibility}
                        </p>

                        <p>
                            <strong>✍️ Writing Instructions:</strong>{" "}
                            {researchBrief.writing_instructions}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
