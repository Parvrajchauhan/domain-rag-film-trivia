"use client";

import { useState } from "react";
import QueryBox from "@/components/QueryBox";
import AnswerCard from "@/components/AnswerCard";
import { QueryResponse } from "@/types";

export default function Home() {
  const [data, setData] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">
        🎬 Film Trivia RAG
      </h1>

      {/* Query Input */}
      <QueryBox
        onResult={(res) => setData(res)}
        onLoading={(val) => setLoading(val)}
        onError={(err) => setError(err)}
      />

      {/* Answer */}
      <AnswerCard
        data={data}
        loading={loading}
        error={error || undefined}
      />
    </main>
  );
}
