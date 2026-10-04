import os

import ollama


OLLAMA_TIMEOUT_SECONDS = 5.0


def get_ollama_client():
    return ollama.Client(
        host=os.getenv("OLLAMA_BASE_URL"),
        timeout=OLLAMA_TIMEOUT_SECONDS,
    )