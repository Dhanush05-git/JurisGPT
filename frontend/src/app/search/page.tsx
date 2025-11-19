"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { askJurisGPT } from "@/lib/api";
import { ArrowLeft } from "lucide-react";

export default function SearchPage() {
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
    <div className="mt-8 max-w-3xl mx-auto">
      <button
        onClick={() => history.back()}
        className="flex items-center gap-2 text-sm text-blue-600 mb-4"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <h2 className="text-2xl font-semibold mb-2">Search for:</h2>
      <p className="mb-6 text-lg text-gray-700 dark:text-gray-200">{q}</p>

      <div className="rounded-lg border p-6 bg-white dark:bg-[#07121a]">
        {loading ? (
          <p className="text-gray-500">Thinking...</p>
        ) : (
          <p className="text-gray-800 dark:text-gray-100">{answer}</p>
        )}
      </div>
    </div>
  );
}
