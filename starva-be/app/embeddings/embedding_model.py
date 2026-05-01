from sentence_transformers import SentenceTransformer

# =========================
# CONFIG
# =========================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

# =========================
# GLOBAL MODEL
# =========================

_model = None


def get_model():
    global _model

    if _model is None:
        print("🔄 Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def embed_text(text: str):
    model = get_model()

    # BGE instruction (IMPORTANT)
    text = "Represent this sentence for retrieval: " + text

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()