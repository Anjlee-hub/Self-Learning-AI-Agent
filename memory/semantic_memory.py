import sqlite3
import numpy as np

from sentence_transformers import SentenceTransformer


DB_NAME = "memory.db"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model

    if _model is None:
        print("🧠 Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def create_embedding(text):
    if not text or not str(text).strip():
        return np.zeros(384, dtype=np.float32)

    model = get_model()
    embedding = model.encode(str(text), convert_to_numpy=True)
    return embedding.astype(np.float32)


def cosine_similarity(vector_a, vector_b):
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(vector_a, vector_b) / (norm_a * norm_b))


def _fetch_durable_memory_rows(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'explicit',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    rows = connection.execute(
        """
        SELECT id, content
        FROM semantic_memories
        WHERE content IS NOT NULL AND TRIM(content) != ''
        ORDER BY id DESC
        """
    ).fetchall()

    if rows:
        return [(row[0], "system", row[1]) for row in rows]

    rows = connection.execute(
        """
        SELECT id, lesson
        FROM lessons
        WHERE lesson IS NOT NULL AND TRIM(lesson) != ''
        ORDER BY id DESC
        """
    ).fetchall()

    return [(row[0], "lesson", row[1]) for row in rows]


def search_semantic_memory(query, limit=5, threshold=0.50):
    if not query or not str(query).strip():
        return []

    connection = sqlite3.connect(DB_NAME)

    try:
        rows = _fetch_durable_memory_rows(connection)
    except Exception:
        rows = []
    finally:
        connection.close()

    if not rows:
        return []

    query_embedding = create_embedding(query)
    results = []

    for memory_id, role, content in rows:
        if not content:
            continue

        message_embedding = create_embedding(content)
        similarity = cosine_similarity(query_embedding, message_embedding)

        if similarity >= threshold:
            results.append(
                {
                    "id": memory_id,
                    "role": role,
                    "content": content,
                    "similarity": similarity,
                }
            )

    results.sort(key=lambda item: item["similarity"], reverse=True)
    return results[:limit]


def get_semantic_context(query, limit=5, threshold=0.50):
    memories = search_semantic_memory(query=query, limit=limit, threshold=threshold)

    if not memories:
        return ""

    return "\n".join(f"user: {memory['content']}" for memory in memories)
