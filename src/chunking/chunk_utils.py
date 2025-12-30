from typing import List

def clean_award_text(text: str) -> str:
    text = text.replace("||.", "||")
    text = text.replace("|| ||", "||")
    return text.strip("| ").strip()


def sentence_split(text: str) -> List[str]:
    sentences = []
    buf = ""

    for part in text.split(". "):
        if buf:
            buf += ". " + part
        else:
            buf = part

        if buf.endswith("."):
            sentences.append(buf.strip())
            buf = ""

    if buf:
        sentences.append(buf.strip())

    return sentences


def recursive_split(text: str, max_chars: int) -> List[str]:
    chunks = []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for para in paragraphs:
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            for sent in sentence_split(para):
                if len(sent) <= max_chars:
                    chunks.append(sent)
                else:
                    for i in range(0, len(sent), max_chars):
                        chunks.append(sent[i:i + max_chars])

    return chunks


def sentence_overlap(prev: str, overlap_chars: int) -> str:
    sentences = sentence_split(prev)
    buf = ""

    for s in reversed(sentences):
        if len(buf) + len(s) <= overlap_chars:
            buf = s + ". " + buf
        else:
            break

    return buf.strip()
