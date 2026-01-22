"use client";

import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

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
    } catch (err) {
      setError("Backend not reachable");
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-black text-white p-10">
      <h1 className="text-4xl font-bold mb-8 text-center">
        🔍 SERP Research Agent
      </h1>

      <form
        onSubmit={runAgent}
        className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto bg-white/10 p-6 rounded-xl"
      >
        <input name="topic" placeholder="Topic" required className="input" />
        <input name="target_audience" placeholder="Audience" required className="input" />

        <select name="content_goal" required className="input">
          <option value="">Select Goal</option>
          <option>Educational</option>
          <option>Informational</option>
          <option>Commercial</option>
          <option>Brand Authority</option>
        </select>

        <input name="brand" placeholder="Brand" className="input" />
        <input name="region" placeholder="Region" className="input" />
        <input name="blog_count" type="number" defaultValue="1" className="input" />

        <button className="col-span-2 bg-indigo-600 py-3 rounded-xl">
          🚀 Run Agent
        </button>
      </form>

      {loading && <p className="text-center mt-4">⏳ Running...</p>}
      {error && <p className="text-red-400 text-center mt-4">{error}</p>}

      <div className="mt-8 max-w-5xl mx-auto space-y-4">
        {results.map((b, i) => (
          <div key={i} className="bg-white/10 p-4 rounded">
            <h3 className="text-xl font-bold">Blog {b.blog_number}</h3>
            <p>{b.blog_angle}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
