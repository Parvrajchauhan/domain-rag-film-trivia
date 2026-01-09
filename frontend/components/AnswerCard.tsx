import { QueryResponse, SourceDoc } from "@/types";

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
  if (loading) {
    return (
      <div className="border rounded p-4 animate-pulse">
        Generating answer...
      </div>
    );
  }

  if (error) {
    return (
      <div className="border rounded p-4 text-red-600">
        {error}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="border rounded p-4 space-y-4">
      {/* Answer */}
      <div>
        <h2 className="font-semibold text-lg mb-1">Answer</h2>
        <p className="text-gray-800">{data.answer}</p>
      </div>

      {/* Metrics */}
      <div className="flex gap-4 text-sm text-gray-600">
        <span>Confidence: {data.confidence.toFixed(2)}</span>
        <span>Hallucination: {data.hallucination_score.toFixed(2)}</span>
        <span>Latency: {data.latency_ms} ms</span>
      </div>

      {/* Sources */}
      <div>
        <h3 className="font-semibold mb-2">Sources</h3>
        <ul className="space-y-2">
          {data.sources.map((src: SourceDoc) => (
            <li
              key={src.id}
              className="border rounded p-2 text-sm"
            >
              <div className="font-medium">{src.title}</div>
              <div className="text-gray-600">
                {src.source} · {src.section}
              </div>
              <p className="mt-1">{src.snippet}</p>
              <div className="text-xs text-gray-500 mt-1">
                Score: {src.score.toFixed(2)}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
