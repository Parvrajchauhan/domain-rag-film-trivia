from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_MODEL_NAME = "llama-3.3-70b-versatile"
_client = None


def get_llm():
    global _client
    if _client is None:
        _client = Groq()
    return _client


def generate_answer(
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.1,  
) -> str:

    client = get_llm()

    system_prompt = """
You are a strict retrieval-based assistant.

Rules:
- Answer ONLY using the provided context.
- Do NOT use prior knowledge.
- If the answer is not in the context, say: "I could not find the answer in the provided context."
- Keep answers concise and factual.
- Do NOT mix information from different movies.
"""

    response = client.chat.completions.create(
        model=_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content.strip()