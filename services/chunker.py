import re

def chunk_text(raw: str, min_chars: int = 40, max_chars: int = 600) -> list[str]:
    # Split on double newlines, numbered list items, or separator lines
    chunks = re.split(r'\n{2,}|(?=\d+\.\s)|---|\*{3,}', raw)
    result = []
    for chunk in chunks:
        chunk = chunk.strip()
        chunk = re.sub(r'^\d+\.\s*', '', chunk)   # strip leading '1. '
        if len(chunk) < min_chars:
            continue                                   # too short, skip
        if len(chunk) > max_chars:
            # Split long chunks by sentence
            sentences = re.split(r'(?<=[.!?])\s+', chunk)
            result.extend(s for s in sentences if len(s) >= min_chars)
        else:
            result.append(chunk)
    return result