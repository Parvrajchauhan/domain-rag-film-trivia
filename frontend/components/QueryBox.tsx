"use client";

import { useState } from "react";
import { askQuestion } from "@/lib/api";
import { QueryResponse } from "@/types";
import { 
  Send, 
  Loader2, 
  Search
} from "lucide-react";

interface QueryBoxProps {
  onResult: (data: QueryResponse) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string | null) => void;
  hasAnswer: boolean;
}


export default function QueryBox({
  onResult,
  onLoading,
  onError,
  hasAnswer,
}: QueryBoxProps) {
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

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const exampleQuestions = [
    "What is the summary of The Shawshank Redemption?",
    "Who directed The Godfather?",
    "What is the name of the main character in The Matrix?",
  ];

  return (
    <div className="space-y-3">
      {/* Input */}
      <div className="relative">
        <textarea
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isSubmitting}
          placeholder="Ask anything about movies, plots, actors..."
          className="w-full resize-none rounded-2xl p-4 pr-14
            text-white placeholder-gray-400
            bg-gradient-to-br from-gray-800 to-gray-900
            border border-gray-700
            focus:border-violet-500 focus:outline-none
            transition-all"
        />

        <button
          onClick={handleSubmit}
          disabled={!query.trim() || isSubmitting}
          className={`absolute bottom-3 right-3 p-3 rounded-xl transition-all
            ${
              isSubmitting || !query.trim()
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "bg-gradient-to-r from-violet-600 to-purple-600 text-white hover:from-violet-700 hover:to-purple-700 shadow-lg shadow-violet-500/30"
            }`}
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Examples */}
      {/* Example Questions */}
{!query && !isSubmitting && !hasAnswer && (
  <div className="space-y-2">
    {exampleQuestions.map((example, index) => (
      <button key={index} onClick={() => setQuery(example)}
              className="w-full text-left px-4 py-3 rounded-xl
          bg-gradient-to-br from-gray-800 to-gray-900
          border border-gray-700 hover:border-lime-500
          transition-all duration-200 flex items-center space-x-3 group">
        <Search className="w-4 h-4 text-gray-500 group-hover:text-lime-400" />
        <span className="text-sm text-gray-300 group-hover:text-white">
          {example}
        </span>
      </button>
    ))}
  </div>
)}


    </div>
  );
}