"use client";

import { useState } from "react";
import QueryBox from "@/components/QueryBox";
import AnswerCard from "@/components/AnswerCard";
import ProTips from "@/components/ProTips";
import { QueryResponse } from "@/types";
import InfoPanel from "@/components/Info";

export default function Page() {
  const [data, setData] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="w-full px-4">
      <InfoPanel />
      {/* Header */}
      <div className="text-center py-10">
        <h1 className="gradient-heading text-4xl font-bold mb-2">
          Film Trivia RAG
        </h1>
        <p className="text-gray-400 text-sm">
          AI-powered answers with verified sources
        </p>
      </div>

      {/* === MAIN LAYOUT === */}
      <div
        className="
          grid
          grid-cols-1
          lg:grid-cols-[1fr_320px]
          gap-7
          items-start
          max-w-[1400px]
          mx-auto
        "
      >
        {/* ===== MAIN DIALOG (FULL WIDTH AREA) ===== */}
        <div className="relative">
          {/* Glow */}
          <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 via-purple-600 to-lime-400 rounded-3xl blur-lg opacity-20" />

          {/* Card */}
          <div className="relative bg-gradient-to-br from-gray-900 to-black rounded-3xl border border-gray-800 overflow-hidden">
            {/* Top Bar */}
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-2 border-b border-gray-700">
              <span className="text-xs text-gray-400">
                AI Response System
              </span>
            </div>

            {/* Content */}
            <div className="max-h-[60vh] overflow-y-auto p-6 space-y-6 custom-scrollbar">
              <QueryBox
                onResult={(res: QueryResponse) => setData(res)}
                onLoading={setLoading}
                onError={setError}
                hasAnswer={data !== null}
              />

              <AnswerCard
                data={data}
                loading={loading}
                error={error || undefined}
              />
            </div>

            {/* Footer */}
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-2 border-t border-gray-700 text-xs text-gray-500 text-right">
              Powered by Groq
            </div>
          </div>
        </div>

        {/* ===== PRO TIPS SIDEBAR ===== */}
        <ProTips />
      </div>
    </div>
  );
}
