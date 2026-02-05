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
    const [showInstructions, setShowInstructions] = useState(false);
    const [showFullOutput, setShowFullOutput] = useState(false);


    // 🔥 NEW: suggestion input state
    const [suggestion, setSuggestion] = useState("");

    // Results state (unchanged)
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
            formData.append("blog_count", blogCount);

            // 🔥 NEW: send suggestion text
            if (suggestion) {
                formData.append("suggestion", suggestion);
            }

            // existing file upload
            if (uploadedFile) {
                formData.append("file", uploadedFile);
            }

            const res = await fetch("/api/research-agent", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

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
            </div>

            {/* FORM */}
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


                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">
                        Suggestions for AI (optional):
                    </label>
                    <textarea
                        value={suggestion}
                        onChange={(e) => setSuggestion(e.target.value)}
                        className="w-full px-4 py-2 bg-white/20 border border-indigo-400 rounded-lg text-white"
                        placeholder="Eg: Focus on newborn care, include Indian cultural beliefs"
                    />
                </div>

                {/* existing file upload */}
                <div className="col-span-2">
                    <label className="block text-sm font-semibold mb-2">
                        Upload PDF or TXT (optional):
                    </label>
                    <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
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

            {/* OUTPUT (unchanged) */}
            {researchBrief && (
                <div className="max-w-5xl mx-auto">
                    <div className="bg-white/10 p-6 rounded-xl max-h-[70vh] overflow-y-auto">
                        <h2 className="text-2xl font-bold mb-6">
                            📊 Research Brief (Writing Agent Input)
                        </h2>

                        {/* Primary Keyword */}
                        <div className="mb-5">
                            <p className="font-semibold mb-1">🎯 Primary Keyword</p>
                            <p className="pl-4">{researchBrief.primary_keyword}</p>
                        </div>

                        {/* Secondary Keywords */}
                        <div className="mb-5">
                            <p className="font-semibold mb-1">🔑 Secondary Keywords</p>
                            <ul className="list-disc pl-8 space-y-1">
                                {researchBrief.secondary_keywords.map((kw, i) => (
                                    <li key={i}>{kw}</li>
                                ))}
                            </ul>
                        </div>

                        {/* Question Keywords */}
                        <div className="mb-5">
                            <p className="font-semibold mb-1">❓ Question Keywords</p>
                            <ul className="list-disc pl-8 space-y-1">
                                {researchBrief.question_keywords.map((q, i) => (
                                    <li key={i}>{q}</li>
                                ))}
                            </ul>
                        </div>

                        {/* Content Angle */}
                        <div className="mb-5">
                            <p className="font-semibold mb-1">🧠 Content Angle</p>
                            <p className="pl-4 leading-relaxed">{researchBrief.content_angle}</p>
                        </div>

                        {/* Ranking Feasibility */}
                        <div className="mb-5">
                            <p className="font-semibold mb-1">🚀 Ranking Feasibility</p>
                            <p className="pl-4">{researchBrief.ranking_feasibility}</p>
                        </div>

                        {/* Writing Instructions */}
                        <div className="mb-5">
                            <p className="font-semibold mb-2">✍️ Writing Instructions</p>
                            <div className="whitespace-pre-wrap bg-white/5 p-4 rounded-lg leading-relaxed">
                                {researchBrief.writing_instructions}
                            </div>
                        </div>
                    </div>
                    {/* Writing Agent Button */}
                    <div className="mt-6 text-center">
                        <Link
                            href="/writing"
                            className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-xl font-semibold inline-block"
                        >
                            📝 Run Writing Agent
                        </Link>
                    </div>
                </div>
            )}


        </div>
    );
}
