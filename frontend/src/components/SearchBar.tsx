"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, ArrowRight, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const SUGGESTIONS = [
  "Punishment for theft under IPC",
  "Article 21 Right to Privacy",
  "BNS Section 103 vs IPC 302",
  "Corporate Tax Law exemptions"
];

export default function SearchBar() {
  const [q, setQ] = useState("");
  const [focused, setFocused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(0);
  const router = useRouter();

  // Auto-rotate suggestions
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveSuggestion((prev) => (prev + 1) % SUGGESTIONS.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  function submit(e?: React.FormEvent) {
    if (e) e.preventDefault();
    if (!q.trim()) return;
    
    setLoading(true);
    // Simulate a small "thinking" delay for effect, then route
    setTimeout(() => {
      router.push(`/search?q=${encodeURIComponent(q.trim())}`);
      setLoading(false);
    }, 400); 
  }

  return (
    <div className="w-full max-w-3xl mx-auto mt-12">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="relative group z-20"
      >
        {/* The Glow Effect */}
        <div 
          className={`absolute -inset-0.5 bg-gradient-to-r from-blue-500 via-purple-500 to-amber-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 ${focused ? 'opacity-70 duration-200' : ''}`}
        />
        
        <form 
          onSubmit={submit} 
          className="relative flex items-center bg-[#0f1523] border border-white/10 rounded-xl shadow-2xl overflow-hidden p-1"
        >
          <div className="pl-4 pr-3 text-slate-500">
            <Search className={`w-5 h-5 transition-colors ${focused ? 'text-blue-400' : ''}`} />
          </div>
          
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask a legal question..."
            className="w-full bg-transparent text-white text-lg px-1 py-4 focus:outline-none placeholder:text-slate-600 font-light tracking-wide"
            autoComplete="off"
          />
          
          <button 
            type="submit" 
            disabled={loading}
            className="bg-gradient-to-b from-slate-100 to-slate-300 text-[#050914] px-6 py-3 rounded-lg font-medium text-sm hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all flex items-center gap-2"
          >
            {loading ? (
              <Sparkles className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>Ask</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </motion.div>

      {/* Rotating Suggestion Text */}
      <div className="mt-4 h-6 flex justify-center items-center overflow-hidden relative">
        <span className="text-slate-500 text-sm mr-2">Try asking:</span>
        <AnimatePresence mode="wait">
          <motion.button
            key={activeSuggestion}
            initial={{ y: 15, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -15, opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={() => setQ(SUGGESTIONS[activeSuggestion])}
            className="text-amber-500/90 text-sm hover:underline underline-offset-4 cursor-pointer font-mono"
          >
            "{SUGGESTIONS[activeSuggestion]}"
          </motion.button>
        </AnimatePresence>
      </div>
    </div>
  );
}