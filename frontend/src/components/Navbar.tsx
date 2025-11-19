"use client";

import { useState, useEffect } from "react";
import { Scale } from "lucide-react";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import Link from "next/link";

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 20);
  });

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b ${
        isScrolled 
          ? "bg-[#050914]/80 backdrop-blur-md border-white/10 py-4 shadow-lg" 
          : "bg-transparent border-transparent py-6"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
        {/* Logo Section */}
        <Link href="/" className="flex items-center gap-3 group cursor-pointer">
          <div className="relative">
            <div className="absolute inset-0 bg-amber-500 blur-lg opacity-20 group-hover:opacity-40 transition-opacity" />
            <div className="relative bg-gradient-to-tr from-amber-600 to-amber-400 p-2 rounded-lg text-white shadow-lg">
              <Scale size={24} strokeWidth={2.5} />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-serif font-bold tracking-wide text-white leading-none">
              Juris<span className="text-amber-500 font-sans">GPT</span>
            </span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-medium">
              Legal Intelligence
            </span>
          </div>
        </Link>

        {/* Navigation Links (Hidden on mobile) */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <Link href="#" className="hover:text-white transition-colors">About</Link>
          <Link href="#" className="hover:text-white transition-colors">Methodology</Link>
          
          <button className="px-5 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-medium transition-all backdrop-blur-sm text-white hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]">
            Sign In
          </button>
        </div>
      </div>
    </motion.nav>
  );
}