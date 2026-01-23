"use client";

import { useState } from "react";

export default function Home() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const [error, setError] = useState("");
    const [showSuggest, setShowSuggest] = useState(false);
    const [suggestion, setSuggestion] = useState("");
    const [message, setMessage] = useState("");

    function renderValue(v) {
        if (v === null || v === undefined) return null;
        if (typeof v === "string" || typeof v === "number") return <span> {v}</span>;
        if (Array.isArray(v)) return <ul className="list-disc ml-5">{v.map((x,i)=><li key={i}>{x}</li>)}</ul>;
        return null;
    }

    async function runAgent(e) {
        e.preventDefault();
        setLoading(true);
        setError("");
        setMessage("");

        const res = await fetch("http://127.0.0.1:8000/research-agent", {
            method: "POST",
            body: new FormData(e.target),
        });

        const data = await res.json();
        setResults(data);
        setLoading(false);
    }

    async function saveOutput() {
        const res = await fetch("http://127.0.0.1:8000/save-output", { method: "POST" });
        const data = await res.json();
        if (data.status === "saved") setMessage("✅ Output saved successfully");
    }

    async function submitSuggestion() {
        const fd = new FormData();
        fd.append("suggestion", suggestion);

        const res = await fetch("http://127.0.0.1:8000/refine-output", {
            method: "POST",
            body: fd,
        });

        const data = await res.json();
        setResults(data.data);
        setSuggestion("");
        setShowSuggest(false);
        setMessage("🔁 Output refined");
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-900 to-indigo-900 text-white p-10">
            <h1 className="text-4xl font-bold text-center mb-8">🔍 SERP Research Agent</h1>

            <form onSubmit={runAgent} className="grid grid-cols-2 gap-4 max-w-4xl mx-auto bg-white/10 p-6 rounded-xl">
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
                <button className="col-span-2 bg-indigo-600 py-3 rounded-xl">🚀 Run Agent</button>
            </form>

            {loading && <p className="text-center mt-4">⏳ Running...</p>}
            {message && <p className="text-green-400 text-center mt-4">{message}</p>}

            <div className="mt-8 space-y-6 max-w-5xl mx-auto">
                {results.map((b,i)=>(
                    <div key={i} className="bg-white/10 p-6 rounded-xl">
                        <h3 className="text-xl font-bold">Blog {b.blog_number}</h3>
                        <p className="text-indigo-300">{b.blog_angle}</p>
                        <p><b>Primary:</b>{renderValue(b.primary_keyword)}</p>
                        <p><b>Secondary:</b>{renderValue(b.secondary_keywords)}</p>
                        <p><b>Questions:</b>{renderValue(b.question_keywords)}</p>
                        <p><b>Structure:</b>{renderValue(b.recommended_structure)}</p>
                        <p><b>Instructions:</b>{renderValue(b.writing_instructions)}</p>
                    </div>
                ))}
            </div>

            {results.length > 0 && (
                <div className="mt-10 bg-white/10 p-6 rounded-xl max-w-4xl mx-auto">
                    <h2 className="text-xl font-semibold mb-3">Do you want to add any suggestions?</h2>
                    <div className="flex gap-4">
                        <button onClick={()=>setShowSuggest(true)} className="bg-blue-600 px-6 py-2 rounded">Yes</button>
                        <button onClick={saveOutput} className="bg-green-600 px-6 py-2 rounded">No</button>
                    </div>

                    {showSuggest && (
                        <>
                            <textarea
                                className="w-full mt-4 p-3 text-black rounded"
                                rows="4"
                                value={suggestion}
                                onChange={e=>setSuggestion(e.target.value)}
                                placeholder="Enter your suggestions..."
                            />
                            <button onClick={submitSuggestion} className="mt-3 bg-indigo-600 px-6 py-2 rounded">
                                Submit
                            </button>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
