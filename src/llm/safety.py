def postprocess_answer(answer: str) -> str:
    answer = answer.strip()

    if not answer:
        return "I don't know based on the given context."

    return answer
