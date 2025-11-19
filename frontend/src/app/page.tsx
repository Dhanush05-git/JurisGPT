"use client";

import React, { useState } from "react";

// NOTE: This file is a single-file Next.js App Router page (src/app/page.tsx).
// It uses Tailwind CSS and shadcn/ui style patterns. Adjust imports if you use different component libraries.

type QueryResponse = {
  query: string;
  chunks_used?: string[];
  answer?: string;
};

export default function JurisGPTPage(): JSX.Element {
  const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submitQuery(e?: React.FormEvent) {
    e?.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await fetch(`${BACKEND}/api/query/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server returned ${res.status}: ${text}`);
      }

      const data = (await res.json()) as QueryResponse;
      setResults(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Unknown error");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 p-6 md:p-12">
      <div className="mx-auto max-w-4xl">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold">JurisGPT</h1>
            <p className="text-slate-500 mt-1">Hybrid legal assistant — search or chat about Indian law.</p>
          </div>
          <div className="text-right text-sm text-slate-500">
            <div>Backend: <span className="font-mono">{BACKEND}</span></div>
            <div className="mt-1">Mode: <span className="font-medium">BM25 + Llama-3</span></div>
          </div>
        </header>

        <form onSubmit={submitQuery} className="space-y-4">
          <label className="sr-only" htmlFor="query">Ask JurisGPT</label>

          <div className="flex gap-3">
            <input
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Try: "What is Article 21?" or "Section 420 punishment"`}
              className="flex-1 rounded-lg border border-slate-200 px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-sky-400"
            />

            <button
              type="submit"
              disabled={isLoading}
              className={`rounded-lg px-4 py-2 font-semibold shadow-sm transition disabled:opacity-60 bg-sky-600 text-white hover:bg-sky-700`}
            >
              {isLoading ? "Thinking…" : "Ask"}
            </button>
          </div>

          <div className="text-sm text-slate-500">Tip: include exact article/section numbers for best results.</div>
        </form>

        <section className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-white rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold mb-3">Answer</h2>

            <div className="min-h-[140px]">
              {isLoading && (
                <div className="flex items-center gap-3 text-slate-500">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <span>Generating answer from retrieved laws...</span>
                </div>
              )}

              {!isLoading && error && (
                <div className="text-red-600">Error: {error}</div>
              )}

              {!isLoading && results && (
                <article className="prose max-w-none">
                  <div className="mb-4 text-slate-600 text-sm">Question: <span className="font-medium">{results.query}</span></div>
                  <div className="bg-slate-50 rounded-md p-4 shadow-inner">{results.answer}</div>
                </article>
              )}

              {!isLoading && !results && !error && (
                <div className="text-slate-400">Ask a question to get started — JurisGPT will retrieve relevant Articles/Sections and produce a concise answer.</div>
              )}
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={() => { setQuery(""); setResults(null); setError(null); }}
                className="text-sm text-slate-600 underline"
              >Clear</button>

              {results && (
                <button
                  onClick={() => navigator.clipboard.writeText(results.answer || "")}
                  className="ml-auto text-sm bg-slate-100 px-3 py-1 rounded"
                >Copy Answer</button>
              )}
            </div>
          </div>

          <aside className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-md font-semibold mb-2">Relevant Laws (retrieved)</h3>

            {isLoading && <div className="text-slate-500">Searching documents…</div>}

            {!isLoading && results && results.chunks_used && (
              <ol className="list-decimal pl-5 space-y-2 text-sm text-slate-700">
                {results.chunks_used.map((c, idx) => (
                  <li key={idx} className="break-words">{c}</li>
                ))}
              </ol>
            )}

            {!isLoading && (!results || !results.chunks_used) && (
              <div className="text-sm text-slate-400">Retrieved chunks will appear here after a query.</div>
            )}
          </aside>
        </section>

        <footer className="mt-10 text-sm text-slate-500">
          <div>Built for academic project — JurisGPT. Data used: constitution, IPC, BNS (sample).</div>
          <div className="mt-2">Pro tip: include article/section numbers to get precise, citation-backed answers.</div>
        </footer>
      </div>
    </main>
  );
}
