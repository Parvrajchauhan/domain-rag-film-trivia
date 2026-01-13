INTENT_INSTRUCTIONS = {

    "fact": (
        "You are a STRICT context-bound extraction system.\n"
        "Use ONLY exact words or short phrases that appear verbatim in the provided context.\n"
        "Do NOT use prior knowledge.\n"
        "Do NOT explain, justify, compare, summarize, or reason.\n"
        "Do NOT reference chunks, chunk numbers, sources, or context structure.\n"
        "Do NOT say phrases like 'as mentioned above', 'in another chunk', or similar.\n"
        "Return EXACTLY ONE short sentence OR ONE entity name.\n"
        "If the answer is NOT explicitly stated, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),

    "director": (
        "You are a STRICT entity extraction system.\n"
        "Extract ONLY the director’s full name if it appears verbatim in the context.\n"
        "Do NOT add titles, explanations, or extra words.\n"
        "Do NOT infer from other movies or general knowledge.\n"
        "Do NOT reference chunks, chunk numbers, or other sources.\n"
        "If the director is NOT explicitly mentioned, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),

    "plot": (
        "You are a STRICT plot reconstruction system.\n"
        "Use ONLY events explicitly stated in the provided context.\n"
        "Write 4–6 short sentences describing concrete actions involving named characters.\n"
        "Follow the chronological order as written in the context.\n"
        "Do NOT infer motivations, themes, or unstated events.\n"
        "Do NOT reference chunks, chunk numbers, or external information.\n"
        "If fewer than 4 concrete plot events are present, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),

    "ending": (
        "You are a STRICT movie-ending extraction system.\n"
        "Review ALL provided context silently.\n"
        "Describe ONLY the FINAL resolution explicitly stated in the context.\n"
        "Write 2–3 short sentences.\n"
        "Each sentence MUST describe a concrete final outcome\n"
        "(e.g., escape, death, arrest, reunion, parole).\n"
        "Do NOT summarize earlier events.\n"
        "Do NOT explain or justify the answer.\n"
        "Do NOT reference chunks, chunk numbers, or context structure.\n"
        "If NO final outcome is explicitly stated, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),

    "explanation": (
        "You are a STRICT cause–effect extraction system.\n"
        "Use ONLY explicit actions and outcomes stated in the context.\n"
        "Write 3–5 short sentences.\n"
        "Each sentence MUST reference a concrete action or event.\n"
        "Include at least ONE explicit cause–effect relationship stated in the context.\n"
        "Do NOT infer, generalize, or add unstated reasoning.\n"
        "Do NOT reference chunks, chunk numbers, or other sources.\n"
        "If ANY requirement is missing, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),

    "general": (
        "You are a STRICT grounded-response system.\n"
        "Answer ONLY using information explicitly stated in the context.\n"
        "Be concise and factual.\n"
        "Do NOT explain uncertainty or provide reasoning.\n"
        "Do NOT reference chunks, chunk numbers, or context structure.\n"
        "If the answer is not directly stated, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),

    "summary": (
        "You are a STRICT context-grounded summarization system.\n"
        "Summarize the main events explicitly stated in the context.\n"
        "Write 3–5 concise sentences.\n"
        "Each sentence MUST reference a concrete event or named character.\n"
        "Do NOT infer themes, motivations, symbolism, or unstated outcomes.\n"
        "Do NOT reference chunks, chunk numbers, or external knowledge.\n"
        "If the context does not contain enough information, output EXACTLY:\n"
        "I don't know based on the given context.\n"
        "STOP immediately after the answer."
    ),
}



def build_prompt(
    query: str,
    chunks: list[dict],
    query_intent: str,
    movie: str,
) -> str:
    
    system_instruction = INTENT_INSTRUCTIONS.get(
        query_intent,
        INTENT_INSTRUCTIONS["general"]
    )

    context_blocks = []
    for i, c in enumerate(chunks, start=1):
        block = (
            f"[Chunk {i} | score={c['rerank_score']:.3f} | "
            f"source={c.get('source')} | movie: {c['title']} | section={c.get('section')}]\n"
            f"{c['text']}"
        )
        context_blocks.append(block)

    context = "\n\n".join(context_blocks)

    prompt = (
        f"{system_instruction}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\n"
        f"movie:\n{movie}\n\n"
        f"query intent:\n{query_intent}\n\n"
        f"Answer:"
    )

    return prompt
