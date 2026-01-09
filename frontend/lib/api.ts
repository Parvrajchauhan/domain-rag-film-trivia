import { QueryResponse, AskRequest } from "@/types";

export async function askQuestion(
  query: AskRequest
): Promise<QueryResponse> {
  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch response");
  }

  return res.json();
}
