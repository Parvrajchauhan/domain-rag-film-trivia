export interface AskRequest {
  query: string;
}

export interface SourceDoc {
  id: string;
  title: string;
  source: string;
  section: string;
  snippet: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDoc[];
  hallucination_score: number;
  latency_ms: number;
  confidence: number;
}
