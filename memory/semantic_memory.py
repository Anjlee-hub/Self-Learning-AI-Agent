import sqlite3
import math
import re


DB_NAME = "memory.db"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_embedding_module_missing = False


def get_model():
    global _model, _embedding_module_missing

    if _model is None:
        if _embedding_module_missing:
            raise ImportError("sentence-transformers is not installed")

        print("🧠 Loading embedding model...")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            _embedding_module_missing = True
            raise

        _model = SentenceTransformer(MODEL_NAME)

    return _model


def create_embedding(text):
    if not text or not str(text).strip():
        return [0.0] * 384

    model = get_model()
    embedding = model.encode(str(text), convert_to_numpy=True)
    return embedding


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(float(a) * float(b) for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(float(value) ** 2 for value in vector_a))
    norm_b = math.sqrt(sum(float(value) ** 2 for value in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def _keyword_search(query, rows, limit, threshold):
    stop_words = {"and", "for", "from", "have", "into", "the", "this", "what", "with", "your"}
    query_tokens = {
        token
        for token in re.findall(r"\b[a-z0-9]+\b", query.lower())
        if len(token) > 2 and token not in stop_words
    }
    if not query_tokens:
        return []

    results = []
    for memory_id, role, content in rows:
        content_tokens = set(re.findall(r"\b[a-z0-9]+\b", content.lower()))
        similarity = len(query_tokens & content_tokens) / len(query_tokens)
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

    try:
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
    except Exception as error:
        print(f"Semantic embeddings unavailable; using keyword memory search: {error}")
        return _keyword_search(query, rows, limit, threshold)

    results.sort(key=lambda item: item["similarity"], reverse=True)
    return results[:limit]


def get_semantic_context(query, limit=5, threshold=0.50):
    memories = search_semantic_memory(query=query, limit=limit, threshold=threshold)

    if not memories:
        return ""

    return "\n".join(f"user: {memory['content']}" for memory in memories)
