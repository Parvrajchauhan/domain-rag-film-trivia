INTENT_INSTRUCTIONS = {

    "fact": (
        "You are a strict information extraction system.\n"
        "Answer ONLY using words or short phrases that appear in the provided context.\n"
        "Do NOT use prior knowledge.\n"
        "Return ONE short sentence or ONE entity name.\n"
        "Do NOT add explanations or extra details.\n"
        "If the answer is not explicitly stated in the context, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "director": (
        "You are a strict entity extraction system.\n"
        "Answer ONLY using the provided context.\n"
        "Return ONLY the director's full name.\n"
        "Do NOT include titles, explanations, or additional words.\n"
        "If the director is not explicitly mentioned in the context, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "plot": (
        "You are a movie plot summarization assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Write a CLEAR and COHERENT summary in 4–6 sentences.\n"
        "Each sentence MUST describe a concrete event involving named characters.\n"
        "Follow the chronological order of events.\n"
        "Do NOT include interpretation, themes, motivations, or opinions.\n"
        "If the provided context does not contain enough plot events to form a summary, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "ending": (
        "You are a movie ending explanation assistant.\n"
        "Review ALL provided chunks before answering.\n"
        "Answer ONLY using the provided context.\n"
        "Describe ONLY the FINAL resolution of the story in 2–3 sentences.\n"
        "Each sentence MUST reference a concrete final outcome (e.g., escape, death, arrest, reunion, parole).\n"
        "Do NOT summarize earlier plot events.\n"
        "If at least ONE final outcome is explicitly described in the context, you MUST answer.\n"
        "Only say 'I don't know based on the given context.' if NO final outcome is mentioned."
    ),

    "explanation": (
        "You are an explanatory reasoning assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Explain HOW and WHY something happens in 3–5 sentences.\n"
        "Your answer MUST include:\n"
        "- at least TWO concrete actions explicitly described in the context\n"
        "- at least ONE explicit cause–effect relationship grounded in the context\n"
        "Do NOT add background knowledge or interpretation beyond the context.\n"
        "If ANY required element is missing, say exactly:\n"
        "'I don't know based on the given context.'"
    ),

    "general": (
        "You are a grounded factual assistant.\n"
        "Answer ONLY using the provided context.\n"
        "Be concise and specific.\n"
        "Your answer MUST reference at least ONE explicit action, event, or object from the context.\n"
        "Do NOT generalize or infer unstated information.\n"
        "If the answer is not directly supported by the context, say exactly:\n"
        "'I don't know based on the given context.'"
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
