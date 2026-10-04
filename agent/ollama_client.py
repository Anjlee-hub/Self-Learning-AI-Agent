import os

import ollama


OLLAMA_TIMEOUT_SECONDS = 5.0
OPENAI_TIMEOUT_SECONDS = 5.0


def get_llm_provider():
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def get_ollama_client():
    return ollama.Client(
        host=os.getenv("OLLAMA_BASE_URL"),
        timeout=OLLAMA_TIMEOUT_SECONDS,
    )


def is_llm_available():
    provider = get_llm_provider()
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY", "").strip())
    if provider != "ollama":
        return False

    try:
        get_ollama_client().list()
        return True
    except Exception:
        return False


def chat_completion(model, messages):
    provider = get_llm_provider()

    if provider == "ollama":
        response = get_ollama_client().chat(model=model, messages=messages)
        return response.message.content or ""

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        from openai import OpenAI

        client = OpenAI(api_key=api_key, timeout=OPENAI_TIMEOUT_SECONDS)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
        )
        return response.choices[0].message.content or ""

    raise ValueError("LLM_PROVIDER must be 'ollama' or 'openai'.")