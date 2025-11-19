"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { askJurisGPT } from "@/lib/api";
import { ArrowLeft, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

function SearchContent() {
  const params = useSearchParams();
  const q = params?.get("q") ?? "";

  const [loading, setLoading] = useState(true);
  const [answer, setAnswer] = useState("");

  useEffect(() => {
    async function getData() {
      try {
        const response = await askJurisGPT(q);
        setAnswer(response.answer);
      } catch (err) {
        setAnswer("Error contacting backend");
      }
      setLoading(false);
    }

    if (q) getData();
  }, [q]);

  return (
    <div className="pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => history.back()}
          className="flex items-center gap-2 text-sm text-amber-500 hover:text-amber-400 mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </motion.button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-bold text-white mb-3">Your Query</h2>
          <p className="text-lg text-slate-300 bg-white/5 border border-white/10 rounded-lg p-4">{q}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl"
        >
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-500" />
            Answer
          </h3>

          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-12 h-12 border-4 border-amber-500/20 border-t-amber-500 rounded-full mb-4"
              />
              <p className="text-slate-400">Analyzing legal documents...</p>
            </div>
          ) : (
            <div className="bg-white/5 border border-white/10 rounded-lg p-6 text-slate-200 leading-relaxed">
              {answer}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="pt-32 pb-20 px-6 flex items-center justify-center">
        <div className="text-slate-400">Loading...</div>
      </div>
    }>
      <SearchContent />
    </Suspense>
  );
}
