from typing import List

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = (text or "").replace("\r\n","\n")
    if not text.strip():
        return []
    chunks=[]
    i=0
    n=len(text)
    step=max(1, chunk_size-overlap)
    while i < n:
        chunk=text[i:i+chunk_size]
        chunks.append(chunk)
        i += step
    return chunks
