"use client";

import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  async function runAgent(e) {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.target);

    const res = await fetch("http://127.0.0.1:8000/run-agent", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResults(data);
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 to-black text-white p-10">
      <h1 className="text-4xl font-bold mb-8 text-center">
        🔍 SERP Research Agent
      </h1>

      <form
        onSubmit={runAgent}
        className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto bg-white/10 p-6 rounded-xl"
      >
        <input name="topic" placeholder="Topic" required className="input" />
        <input
          name="target_audience"
          placeholder="Target Audience"
          required
          className="input"
        />

        <select name="content_goal" className="input">
          <option>Educational</option>
          <option>Informational</option>
          <option>Commercial</option>
          <option>Brand Authority</option>
        </select>

        <input name="brand" placeholder="Brand" className="input" />
        <input name="region" placeholder="Region" className="input" />
        <input
          name="blog_count"
          type="number"
          min="1"
          max="5"
          defaultValue="1"
          className="input"
        />

        <button
          type="submit"
          className="col-span-1 md:col-span-2 bg-indigo-600 hover:bg-indigo-700 py-3 rounded-xl font-semibold"
        >
          🚀 Run Research Agent
        </button>
      </form>

      {loading && (
        <p className="text-center mt-6 text-indigo-300">
          ⏳ Analyzing SERP & competitors...
        </p>
      )}

      <div className="mt-10 space-y-6 max-w-5xl mx-auto">
        {results.map((b, i) => (
          <div
            key={i}
            className="bg-white/10 p-6 rounded-xl border border-white/20"
          >
            <h2 className="text-2xl font-semibold mb-1">
              Blog {b.blog_number}
            </h2>
            <p className="text-indigo-300 mb-3">{b.blog_angle}</p>

            <p><b>Primary Keyword:</b> {b.primary_keyword}</p>
            <p><b>Word Count:</b> {b.recommended_word_count}</p>

            <p className="mt-3 text-sm opacity-90">
              {b.writing_instructions}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
