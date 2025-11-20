"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Sparkles, Copy, RefreshCw, Scale, ChevronRight } from "lucide-react";

type QueryResponse = {
  query: string;
  chunks_used?: string[];
  answer?: string;
};

export default function JurisGPTPage() {
  const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

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

  function handleCopy() {
    navigator.clipboard.writeText(results?.answer || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <main className="min-h-screen pt-32 pb-20 px-6">
      <div className="mx-auto max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-2 mb-6">
            <Scale className="w-4 h-4 text-amber-500" />
            <span className="text-sm text-amber-500/90 font-medium">JurisGPT</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-br from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Ask About Indian Law
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Get instant answers about Constitution, IPC, and BNS backed by AI retrieval and reasoning
          </p>
        </motion.div>

        <motion.form
          onSubmit={submitQuery}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-12"
        >
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-amber-500 via-blue-500 to-amber-500 rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-300" />

            <div className="relative flex items-center bg-[#0f1523]/80 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden shadow-2xl">
              <div className="pl-5 pr-3 text-slate-500">
                <Search className="w-5 h-5" />
              </div>

              <input
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder='Try "What is Article 21?" or "Section 420 punishment"'
                className="flex-1 bg-transparent text-white text-base md:text-lg px-2 py-5 focus:outline-none placeholder:text-slate-600 font-light"
                autoComplete="off"
              />

              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="m-2 bg-gradient-to-r from-amber-500 to-amber-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg hover:shadow-amber-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Sparkles className="w-4 h-4 animate-spin" />
                    <span>Thinking</span>
                  </>
                ) : (
                  <>
                    <span>Ask</span>
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </motion.button>
            </div>
          </div>

          <p className="text-center text-sm text-slate-500 mt-4">
            Include exact article/section numbers for precise results
          </p>
        </motion.form>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  Answer
                </h2>

                {results && (
                  <div className="flex gap-2">
                    <motion.button
                      onClick={handleCopy}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex items-center gap-2 text-sm bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-2 rounded-lg transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      {copied ? "Copied!" : "Copy"}
                    </motion.button>

                    <motion.button
                      onClick={() => { setQuery(""); setResults(null); setError(null); }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex items-center gap-2 text-sm bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-2 rounded-lg transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Clear
                    </motion.button>
                  </div>
                )}
              </div>

              <div className="min-h-[240px]">
                <AnimatePresence mode="wait">
                  {isLoading && (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center py-12"
                    >
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        className="w-12 h-12 border-4 border-amber-500/20 border-t-amber-500 rounded-full mb-4"
                      />
                      <p className="text-slate-400">Analyzing legal documents...</p>
                    </motion.div>
                  )}

                  {!isLoading && error && (
                    <motion.div
                      key="error"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-400"
                    >
                      Error: {error}
                    </motion.div>
                  )}

                  {!isLoading && results && (
                    <motion.article
                      key="results"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="space-y-4"
                    >
                      <div className="bg-amber-500/5 border border-amber-500/10 rounded-lg p-4">
                        <p className="text-sm text-slate-400 mb-1">Question:</p>
                        <p className="text-white font-medium">{results.query}</p>
                      </div>

                      <div className="bg-white/5 border border-white/10 rounded-lg p-6 text-slate-200 leading-relaxed">
                        {results.answer}
                      </div>
                    </motion.article>
                  )}

                  {!isLoading && !results && !error && (
                    <motion.div
                      key="empty"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center py-12 text-center"
                    >
                      <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center mb-4">
                        <Scale className="w-8 h-8 text-amber-500" />
                      </div>
                      <p className="text-slate-400 max-w-md">
                        Ask a question to get started. JurisGPT will retrieve relevant Articles and Sections to provide a comprehensive answer.
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          <aside>
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl sticky top-24">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                Retrieved Laws
              </h3>

              <AnimatePresence mode="wait">
                {isLoading && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-2"
                  >
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="bg-white/5 rounded-lg p-3 animate-pulse h-16" />
                    ))}
                  </motion.div>
                )}

                {!isLoading && results && results.chunks_used && (
                  <motion.ol
                    key="chunks"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-3"
                  >
                    {results.chunks_used.map((chunk, idx) => (
                      <motion.li
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-slate-300 hover:bg-white/10 transition-colors"
                      >
                        <span className="text-amber-500 font-semibold mr-2">#{idx + 1}</span>
                        {chunk.substring(0, 100)}...
                      </motion.li>
                    ))}
                  </motion.ol>
                )}

                {!isLoading && (!results || !results.chunks_used) && (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-sm text-slate-500 text-center py-8"
                  >
                    Source documents will appear here after your query
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </aside>
        </motion.section>

        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 text-center text-sm text-slate-500 space-y-2"
        >
          <p>Built with AI for academic research. Dataset: Constitution of India, IPC, BNS</p>
          <p>Powered by BM25 retrieval + Llama-3 reasoning</p>
        </motion.footer>
      </div>
    </main>
  );
}
