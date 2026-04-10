#!/usr/bin/env python3
"""
Vector Memory Indexer — RAG for Sig Botti memory.
Indexes MEMORY.md, daily logs, lessons, and skills using nomic-embed-text.
"""
import faiss
import numpy as np
import os
import json
import time
import urllib.request
import urllib.error
import glob

WORKSPACE = "/Users/sigbotti/.openclaw/workspace"
INDEX_FILE = os.path.join(WORKSPACE, "data", "memory.index")
META_FILE = os.path.join(WORKSPACE, "data", "memory_meta.json")
OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
DIM = 768  # nomic-embed-text dimension


def embed_texts(texts: list) -> list:
    """Get embeddings from Ollama nomic-embed-text."""
    embeddings = []

    for i, text in enumerate(texts):
        payload = {"model": EMBED_MODEL, "prompt": text[:4000]}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA}/api/embeddings",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                emb = result.get("embedding", result.get("embeddings", []))
                if emb:
                    embeddings.append(emb)
                else:
                    embeddings.append([0.0] * DIM)
        except Exception as e:
            print(f"Error embedding '{text[:30]}...': {e}")
            embeddings.append([0.0] * DIM)

        if (i + 1) % 20 == 0:
            print(f"  Embedded {i+1}/{len(texts)}...")

    return embeddings


def load_memory_files():
    """Load all memory source files."""
    texts = []
    metadata = []

    sources = {
        "MEMORY.md": os.path.join(WORKSPACE, "MEMORY.md"),
        "daily_logs": os.path.join(WORKSPACE, "memory", "*.md"),
        "lessons": os.path.join(WORKSPACE, "memory", "*.md"),
    }

    # MEMORY.md
    mem_path = os.path.join(WORKSPACE, "MEMORY.md")
    if os.path.exists(mem_path):
        with open(mem_path) as f:
            content = f.read()
        # Split into paragraphs/sections
        chunks = [c.strip() for c in content.split("\n##") if c.strip()]
        for chunk in chunks:
            if len(chunk) > 20:
                texts.append(chunk[:2000])  # Truncate very long chunks
                metadata.append({"source": "MEMORY.md", "type": "curated", "preview": chunk[:100]})

    # Daily logs
    log_dir = os.path.join(WORKSPACE, "memory")
    for log_file in sorted(glob.glob(os.path.join(log_dir, "*.md"))):
        fname = os.path.basename(log_file)
        with open(log_file) as f:
            content = f.read()
        # Split by day
        chunks = content.split("\n## ")
        for chunk in chunks:
            if len(chunk) > 30:
                texts.append(chunk[:1500])
                metadata.append({"source": fname, "type": "daily_log", "preview": chunk[:80]})

    # Skills
    skill_dir = os.path.join(WORKSPACE, "skills")
    if os.path.exists(skill_dir):
        for skill_file in glob.glob(os.path.join(skill_dir, "**", "SKILL.md"), recursive=True):
            with open(skill_file) as f:
                content = f.read()
            # Take first 500 chars of each skill
            if len(content) > 50:
                texts.append(content[:1500])
                metadata.append({
                    "source": os.path.relpath(skill_file, WORKSPACE),
                    "type": "skill",
                    "preview": content[:80]
                })

    print(f"Loaded {len(texts)} chunks from {len(metadata)} sources")
    return texts, metadata


def build_index():
    """Build FAISS index from memory chunks."""
    print("Loading memory files...")
    texts, metadata = load_memory_files()

    if not texts:
        print("No texts to index!")
        return

    print(f"Embedding {len(texts)} chunks...")
    start = time.time()
    embeddings = embed_texts(texts)
    elapsed = time.time() - start
    print(f"Embedded in {elapsed:.1f}s ({len(texts)/elapsed:.1f} embeds/sec)")

    # Convert to numpy array
    emb_array = np.array(embeddings).astype("float32")
    if emb_array.ndim == 1:
        emb_array = emb_array.reshape(-1, 1)

    # Normalize for cosine similarity
    norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
    norms[norms == 0] = 1
    emb_array = emb_array / norms

    # Build FAISS index (Inner Product for normalized vectors = cosine sim)
    index = faiss.IndexFlatIP(DIM)
    index.add(emb_array)

    # Save index
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    faiss.write_index(index, INDEX_FILE)

    # Save metadata
    with open(META_FILE, "w") as f:
        json.dump(metadata, f)

    print(f"✅ Index built: {index.ntotal} vectors saved to {INDEX_FILE}")
    print(f"   Meta saved: {len(metadata)} entries")


def retrieve(query: str, top_k: int = 5, min_score: float = 0.3) -> list:
    """Retrieve relevant memory chunks for a query."""
    if not os.path.exists(INDEX_FILE):
        print("No index found — run build-index first")
        return []

    # Load index and metadata
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE) as f:
        metadata = json.load(f)

    # Embed query
    emb = embed_texts([query])[0]
    query_vec = np.array([emb]).astype("float32")
    norms = np.linalg.norm(query_vec)
    if norms > 0:
        query_vec = query_vec / norms

    # Search
    scores, indices = index.search(query_vec, min(top_k * 2, index.ntotal))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(metadata) and score >= min_score:
            results.append({
                "score": round(float(score), 3),
                "source": metadata[idx]["source"],
                "type": metadata[idx]["type"],
                "preview": metadata[idx]["preview"],
            })

    return results[:top_k]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print("Building vector memory index...")
        build_index()
    elif len(sys.argv) > 1 and sys.argv[1] == "query":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "What have I learned?"
        print(f"Query: {query}\n")
        results = retrieve(query)
        for r in results:
            print(f"[{r['score']}] {r['source']} ({r['type']})")
            print(f"  {r['preview']}")
            print()
    else:
        print("Usage:")
        print("  build-vector-index.py build   # Build/rebuild index")
        print("  build-vector-index.py query <text>  # Retrieve")
