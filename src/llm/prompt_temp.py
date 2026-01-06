INTENT_INSTRUCTIONS = {
    "fact": (
        "You are a strict information extraction system.\n"
    "Answer ONLY using words that appear in the provided context.\n"
    "Do NOT use prior knowledge.\n"
    "Your answer must be copied or minimally paraphrased from the context.\n"
    "Answer in ONE short sentence or ONE entity name.\n"
    "If the answer is not explicitly stated in the context, say exactly:\n"
    "'I don't know based on the given context.'"
    ),

    "director": (
        "You are a factual question-answering assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Give a SHORT, direct answer (1 sentence).\n"
        "If the answer is missing, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "plot": (
        "You are a movie plot summarization assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Give a CLEAR and COHERENT summary (4–6 sentences).\n"
        "Do NOT add interpretation or opinions.\n"
        "If the plot is incomplete, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "ending": (
        "You are a movie ending explanation assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Explain the ending clearly (3–5 sentences).\n"
        "Focus only on final events.\n"
        "If the ending is missing, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "explanation": (
        "You are an explanatory assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Explain HOW or WHY something happens (3–5 sentences).\n"
        "Be factual and grounded.\n"
        "If the explanation is missing, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "general": (
        "You are a factual question-answering assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Be concise and factual.\n"
        "If the answer is missing, say exactly:\n"
        "'I don't know based on the given context.'"
    ),
}

def build_prompt(
    query: str,
    chunks: list[dict],
    query_intent: str
) -> str:
    
    system_instruction = INTENT_INSTRUCTIONS.get(
        query_intent,
        INTENT_INSTRUCTIONS["general"]
    )

    context_blocks = []
    for i, c in enumerate(chunks, start=1):
        block = (
            f"[Chunk {i} | score={c['rerank_score']:.3f} | "
            f"source={c.get('source')} | section={c.get('section')}]\n"
            f"{c['text']}"
        )
        context_blocks.append(block)

    context = "\n\n".join(context_blocks)

    prompt = (
        f"{system_instruction}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\n"
        f"Answer:"
    )

    return prompt
