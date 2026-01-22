"use client";

import { useState } from "react";

export default function Home() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const [error, setError] = useState("");

    function renderValue(value) {
        if (!value) return null;

        if (typeof value === "string") {
            return <p className="text-sm">{value}</p>;
        }

        if (Array.isArray(value)) {
            return (
                <ul className="list-disc list-inside text-sm">
                    {value.map((v, i) => (
                        <li key={i}>{v}</li>
                    ))}
                </ul>
            );
        }

        if (typeof value === "object") {
            return (
                <div className="text-sm space-y-1">
                    {Object.entries(value).map(([k, v]) => (
                        <p key={k}>
                            <b>{k}:</b> {String(v)}
                        </p>
                    ))}
                </div>
            );
        }

        return null;
    }

    async function runAgent(e) {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const formData = new FormData(e.target);

            const res = await fetch("http://127.0.0.1:8000/research-agent", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (data.error) {
                setError(data.error);
                setResults([]);
            } else {
                setResults(data);
            }
        } catch {
            setError("Backend not reachable");
        }

        setLoading(false);
    }

    return (
<div className="min-h-screen bg-gradient-to-b from-blue-900 to-indigo-900 text-white p-10">
            <h1 className="text-4xl font-bold mb-8 text-center">
                🔍 SERP Research Agent
            </h1>

            <form
                onSubmit={runAgent}
                className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto bg-white/10 p-6 rounded-xl"
            >
                <input name="topic" placeholder="Topic" required className="input" />
                <input name="target_audience" placeholder="Target Audience" required className="input" />

                <select name="content_goal" required className="input">
                    <option value="">Select Goal</option>
                    <option>Educational</option>
                    <option>Informational</option>
                    <option>Commercial</option>
                    <option>Brand Authority</option>
                </select>

                <input name="region" placeholder="Region" required className="input" />
                <input name="blog_count" type="number" min="1" max="5" defaultValue="1" className="input" />

                <button className="col-span-2 bg-indigo-600 py-3 rounded-xl font-semibold">
                    🚀 Run Research Agent
                </button>
            </form>

            {loading && <p className="text-center mt-4">⏳ Running...</p>}
            {error && <p className="text-red-400 text-center mt-4">{error}</p>}

            <div className="mt-8 max-w-5xl mx-auto space-y-6">
                {results.map((b, i) => (
                    <div key={i} className="bg-white/10 p-6 rounded-xl space-y-2">
                        <h3 className="text-xl font-bold">
                            Blog {b.blog_number}
                        </h3>

                        <p className="text-indigo-300">{b.blog_angle}</p>

                        <div>
                            <b>Primary keyword:</b>
                            {renderValue(b.primary_keyword)}
                        </div>

                        <div>
                            <b>Secondary keywords:</b>
                            {renderValue(b.secondary_keywords)}
                        </div>

                        <div>
                            <b>Question keywords:</b>
                            {renderValue(b.question_keywords)}
                        </div>

                        <div>
                            <b>Content angle:</b>
                            {renderValue(b.content_angle)}
                        </div>

                        <div>
                            <b>Recommended structure:</b>
                            {renderValue(b.recommended_structure)}
                        </div>

                        <div>
                            <b>Word count:</b>
                            {renderValue(b.recommended_word_count)}
                        </div>

                        <div>
                            <b>Ranking feasibility:</b>
                            {renderValue(b.ranking_feasibility)}
                        </div>

                        <div>
                            <b>Writing instructions:</b>
                            {renderValue(b.writing_instructions)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
