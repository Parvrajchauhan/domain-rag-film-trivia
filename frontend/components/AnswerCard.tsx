import React from "react";
import {
  Sparkles,
  Clock,
  TrendingUp,
  Shield,
  BookOpen,
  ChevronRight,
  CheckCircle2,
} from "lucide-react";

// Types
interface SourceDoc {
  id: string;
  title: string;
  source: string;
  section: string;
  score: number;
  snippet: string;
}

interface QueryResponse {
  answer: string;
  confidence: number;
  hallucination_score: number;
  latency_ms: number;
  sources: SourceDoc[];
}

interface AnswerCardProps {
  data: QueryResponse | null;
  loading: boolean;
  error?: string;
}

export default function AnswerCard({
  data,
  loading,
  error,
}: AnswerCardProps) {
  /* Loading */
  if (loading) {
    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl border border-gray-700 p-8">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-gray-700 rounded-full" />
            <div className="w-16 h-16 border-4 border-lime-400 rounded-full animate-spin border-t-transparent absolute inset-0" />
          </div>
          <p className="text-gray-400 text-sm">Generating answer…</p>
        </div>
      </div>
    );
  }

  /* Error */
  if (error) {
    return (
      <div className="bg-gradient-to-br from-red-900/20 to-gray-900 rounded-2xl border border-red-500/50 p-6">
        <h3 className="text-red-400 font-semibold mb-1">Error</h3>
        <p className="text-red-300/70 text-sm">{error}</p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-4">
      {/* Answer bubble */}
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 flex-shrink-0 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
  <Sparkles className="w-4 h-4 text-white" />
</div>


        <div className="bg-gradient-to-br from-violet-600 to-purple-600 rounded-2xl rounded-tl-sm p-4 shadow-lg">
          <p className="text-white text-sm whitespace-pre-wrap">
            {data.answer}
          </p>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3">
        <Metric
          icon={<TrendingUp className="w-4 h-4 text-lime-400" />}
          label="Confidence"
          value={`${Math.round(data.confidence * 100)}%`}
        />
        <Metric
          icon={<Shield className="w-4 h-4 text-violet-400" />}
          label="Reliability"
          value={`${Math.round((1 - Math.exp(-data.sources.length)) * 100)}%`}
        />
        <Metric
          icon={<Clock className="w-4 h-4 text-purple-400" />}
          label="Time"
          value={`${data.latency_ms}ms`}
        />
      </div>

      {/* Sources */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700 flex justify-between">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-lime-400" />
            <span className="text-white font-semibold">Sources</span>
          </div>
          <span className="text-lime-400 font-bold">
            {data.sources.length}
          </span>
        </div>

        <div className="p-4 space-y-3">
          {data.sources.map((src, i) => (
            <div
              key={src.id}
              className="bg-gray-900/50 border border-gray-700 rounded-xl p-4"
            >
              <div className="flex justify-between mb-2">
                <h4 className="text-white text-sm font-semibold">
                  {i + 1}. {src.title}
                </h4>
                <span className="text-xs text-lime-400 font-bold">
                  {Math.round(src.score * 100)}%
                </span>
              </div>

              <p className="text-gray-300 text-xs mb-3">
                {src.snippet}
              </p>

              <div className="flex justify-between text-xs text-gray-400">
                <span>
                  {src.source} <ChevronRight className="inline w-3 h-3" />{" "}
                  {src.section}
                </span>
                <CheckCircle2 className="w-4 h-4 text-lime-400" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* Small metric card */
function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-3 border border-gray-700">
      <div className="flex items-center space-x-2">
        {icon}
        <div>
          <p className="text-xs text-gray-400">{label}</p>
          <p className="text-lg font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}
