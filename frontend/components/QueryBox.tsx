"use client";

import { useState } from "react";
import { askQuestion } from "@/lib/api";
import { QueryResponse } from "@/types";

interface QueryBoxProps {
  onResult: (data: QueryResponse) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string | null) => void;
}

export default function QueryBox({
  onResult,
  onLoading,
  onError,
}: QueryBoxProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = async () => {
    if (!query.trim()) return;

    try {
      onLoading(true);
      onError(null);

      const data = await askQuestion(query);
      onResult(data);
    } catch (err: any) {
      onError(err.message || "Something went wrong");
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="border rounded p-4 space-y-2">
      <textarea
        className="w-full border rounded p-2"
        rows={3}
        placeholder="Ask a question about a movie..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <button
        onClick={handleSubmit}
        className="px-4 py-2 bg-black text-white rounded disabled:opacity-50"
        disabled={!query.trim()}
      >
        Ask
      </button>
    </div>
  );
}
