"use client";
import { useState } from "react";

export default function Home() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.target);

    const res = await fetch("http://localhost:8000/run-serp-agent", {
      method: "POST",
      body: formData,
    });

    const json = await res.json();
    setData(json);
    setLoading(false);
  }

  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🔍 SERP Research Agent</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          name="topic"
          placeholder="Topic (Eg: AI for school students)"
          className="border p-2 w-full"
        />

        <input
          name="target_audience"
          placeholder="Target Audience (Eg: Kids aged 10–14)"
          className="border p-2 w-full"
        />

        <select name="content_goal" className="border p-2 w-full">
          <option>Educational</option>
          <option>Informational</option>
          <option>Commercial</option>
          <option>Brand Authority</option>
        </select>

        <input
          name="brand"
          placeholder="Brand (optional)"
          className="border p-2 w-full"
        />

        <input
          name="region"
          placeholder="Region (Eg: India)"
          className="border p-2 w-full"
        />

        <input
          type="number"
          name="blog_count"
          defaultValue={1}
          min={1}
          max={5}
          className="border p-2 w-full"
        />

        <input type="file" name="file" />

        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded"
        >
          {loading ? "Running..." : "🚀 Run SERP Research Agent"}
        </button>
      </form>

      {data && (
        <div className="mt-10 space-y-6">
          {data.research_briefs.map((brief) => (
            <div
              key={brief.blog_number}
              className="border rounded p-4"
            >
              <h2 className="text-xl font-bold">
                📝 Blog {brief.blog_number}
              </h2>

              <p><b>Angle:</b> {brief.blog_angle}</p>
              <p><b>Primary Keyword:</b> {brief.primary_keyword}</p>
              <p><b>Word Count:</b> {brief.recommended_word_count}</p>
              <p><b>Ranking Feasibility:</b> {brief.ranking_feasibility}</p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
