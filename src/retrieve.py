from sentence_transformers import SentenceTransformer
import chromadb
from ingest import build_chunks

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")


def build_index(max_words: int, docs_dir: str = "data/docs"):
    name = f"docs_{max_words}"

    # delete the old collection if it exists, so rebuilding starts clean
    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name, metadata={"hnsw:space": "cosine"}
    )

    chunks = build_chunks(docs_dir, max_words)
    texts = [c.text for c in chunks]

    embeddings = model.encode(
        texts, normalize_embeddings=True, show_progress_bar=True
    )

    batch = 500
    for i in range(0, len(chunks), batch):
        part = chunks[i:i + batch]
        collection.add(
            ids=[c.chunk_id for c in part],
            documents=[c.text for c in part],
            embeddings=embeddings[i:i + batch].tolist(),
            metadatas=[{"file": c.file, "heading": c.heading} for c in part],
        )

    print(f"Indexed {len(chunks)} chunks into {name}")


def search(question: str, k: int = 5, max_words: int = 300):
    collection = client.get_collection(f"docs_{max_words}")

    q_emb = model.encode([question], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=q_emb, n_results=k)

    results = []
    for i in range(len(res["ids"][0])):
        results.append({
            "file": res["metadatas"][0][i]["file"],
            "heading": res["metadatas"][0][i]["heading"],
            "text": res["documents"][0][i],
            "score": 1 - res["distances"][0][i],   # similarity, higher = better
        })
    return results


if __name__ == "__main__":
    build_index(300)
    for q in ["how do I validate request body?",
              "how to read headers?",
              "what is dependency injection?"]:
        print("\nQ:", q)
        for r in search(q, 3):
            print(f"  {r['score']:.3f}  {r['file']}  |  {r['heading']}")