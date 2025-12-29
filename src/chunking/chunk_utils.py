import re
from typing import List


def split_on_bullets(text: str) -> List[str]:
    bullets = re.split(r"\n\s*•\s*", text)
    return [b.strip() for b in bullets if b.strip()]


def recursive_split(text: str, max_chars: int) -> List[str]:
    if len(text) <= max_chars:
        return [text.strip()]

    if "•" in text:
        chunks = []
        buf = ""
        for bullet in split_on_bullets(text):
            if len(buf) + len(bullet) < max_chars:
                buf += " • " + bullet
            else:
                chunks.append(buf.strip())
                buf = bullet
        if buf:
            chunks.append(buf.strip())
        return chunks

    parts = text.split("\n\n")
    chunks, buf = [], ""
    for p in parts:
        if len(buf) + len(p) < max_chars:
            buf += "\n\n" + p
        else:
            chunks.append(buf.strip())
            buf = p
    if buf:
        chunks.append(buf.strip())

    final = []
    for c in chunks:
        if len(c) <= max_chars:
            final.append(c)
        else:
            for i in range(0, len(c), max_chars):
                final.append(c[i : i + max_chars])
    return final
