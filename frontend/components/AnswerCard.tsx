import {
  Sparkles,
  Clock,
  TrendingUp,
  Shield,
  ExternalLink,
  BookOpen,
  ChevronRight,
  CheckCircle2,
} from "lucide-react";

export default function AnswerCard({
  data,
  loading,
  error,
}: {
  data: any;
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 text-center text-white">
        Generating answer...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-2xl p-6 text-red-400">
        {error}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div className="bg-violet-600 rounded-2xl p-4 text-white">
          {data.answer}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-gray-800 rounded-xl">
          <TrendingUp className="text-lime-400" />
          {(data.confidence * 100).toFixed(0)}%
        </div>
        <div className="p-3 bg-gray-800 rounded-xl">
          <Shield className="text-violet-400" />
          {((1 - data.hallucination_score) * 100).toFixed(0)}%
        </div>
        <div className="p-3 bg-gray-800 rounded-xl">
          <Clock className="text-purple-400" />
          {data.latency_ms}ms
        </div>
      </div>

      <div className="bg-gray-900 rounded-2xl border border-gray-700">
        <div className="p-4 border-b border-gray-700 flex items-center space-x-2">
          <BookOpen className="text-lime-400" />
          <span className="text-white">Sources</span>
        </div>

        <div className="p-4 space-y-3">
          {data.sources.map((src: any, i: number) => (
            <div key={src.id} className="bg-gray-800 rounded-xl p-4">
              <h4 className="text-white">{src.title}</h4>
              <p className="text-gray-400 text-xs">{src.snippet}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
