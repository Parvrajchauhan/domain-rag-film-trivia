"use client";

import React, { useState } from "react";
import QueryBox from "@/components/QueryBox";
import AnswerCard from "@/components/AnswerCard";
import Box from "@/components/box";

export default function Page() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="text-center py-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-violet-400 via-purple-400 to-lime-400 bg-clip-text text-transparent">
            Film Trivia RAG
          </h1>
          <p className="text-gray-400 text-sm">
            AI-powered answers with verified sources
          </p>
        </div>

        <Box>
          <QueryBox
            onResult={setData}
            onLoading={setLoading}
            onError={setError}
          />
          <AnswerCard data={data} loading={loading} error={error} />
        </Box>
      </div>
    </div>
  );
}
