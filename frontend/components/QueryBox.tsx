import React, { useState } from "react";
import { Send, Loader2, Search } from "lucide-react";

const askQuestion = async (query: string) => {
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return {
    answer:
      "The Shawshank Redemption follows Andy Dufresne, a banker wrongly convicted of murdering his wife and her lover...",
    confidence: 0.92,
    hallucination_score: 0.08,
    latency_ms: 342,
    sources: [
      {
        id: "1",
        title: "The Shawshank Redemption Plot Summary",
        source: "IMDb",
        section: "Plot Overview",
        score: 0.95,
        snippet:
          "Andy Dufresne, a successful banker, is arrested for the murders of his wife...",
      },
    ],
  };
};

export default function QueryBox({
  onResult,
  onLoading,
  onError,
}: {
  onResult: (data: any) => void;
  onLoading: (v: boolean) => void;
  onError: (e: string | null) => void;
}) {
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim() || isSubmitting) return;
    try {
      setIsSubmitting(true);
      onLoading(true);
      onError(null);
      const data = await askQuestion(query);
      onResult(data);
      setQuery("");
    } catch (err: any) {
      onError(err.message || "Something went wrong");
    } finally {
      onLoading(false);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <textarea
          className="w-full resize-none rounded-2xl p-4 pr-14 text-white bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700"
          rows={3}
          placeholder="Ask anything about movies..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="absolute bottom-3 right-3 p-3 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
    </div>
  );
}
