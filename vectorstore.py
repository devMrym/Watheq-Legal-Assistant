import chromadb


class VectorStore:
    def __init__(self, db_path="chroma_db_watheq"):
        self.client = chromadb.PersistentClient(path=db_path)

        # ✅ CORRECT COLLECTION NAME
        self.collection = self.client.get_collection("saudi_laws")

    def search(self, query_embedding, top_k=5):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        return [
            {
                "text": doc,
                "metadata": meta,
                "score": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]