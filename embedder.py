from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")


def get_embedding(text: str, is_query=True):
    """
    BGE-M3 requires proper prompting style for best retrieval
    """

    if is_query:
        text = f"query: {text}"
    else:
        text = f"passage: {text}"

    return model.encode(text, normalize_embeddings=True).tolist()