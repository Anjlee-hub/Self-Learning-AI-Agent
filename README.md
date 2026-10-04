# Self-Learning AI Agent

A lightweight portfolio project for a self-learning AI agent that can:

- detect deterministic requests such as calculator, time, and word-count tasks
- route them to the appropriate tool before invoking the model
- store reusable lessons in SQLite memory
- retrieve similar prior lessons and adapt future behavior
- fall back safely when Ollama is unavailable
- expose a small FastAPI backend and a simple React frontend

## Features

- Deterministic tool routing for arithmetic and simple task execution
- Durable lesson memory with semantic-style retrieval for relevant experience
- Graceful offline behavior when the local LLM is not running
- FastAPI endpoints for root, health, and chat
- Frontend API configuration via Vite environment variables

## Local development

The backend defaults to:

- http://127.0.0.1:8000

The frontend reads the backend URL from VITE_API_URL and falls back to the same local default when unset.

Example environment file:

- .env.example

Key variables:

- VITE_API_URL=http://127.0.0.1:8000
- CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
- LLM_PROVIDER=ollama
- OLLAMA_BASE_URL=http://127.0.0.1:11434
- OPENAI_MODEL=gpt-4o-mini

For Render, set `LLM_PROVIDER=openai` and configure `OPENAI_API_KEY` in the
backend service's environment settings. The backend reads the key directly;
do not use a `VITE_`-prefixed variable or add the key to frontend configuration.
`OPENAI_MODEL` is optional and defaults to `gpt-4o-mini`. Local development
continues to use Ollama by default.

## Run the backend

From the project root:

python app/main.py

or run the FastAPI app with your preferred ASGI server.

## Render production dependencies

Set the Render build command to:

```bash
pip install -r requirements-render.txt
```

The Render dependency list excludes the optional embedding stack. Semantic
memory loads sentence-transformers lazily when installed; otherwise, semantic
queries fall back to keyword matches from the SQLite memory database. Local
development can continue using `requirements.txt` to enable embedding-based
retrieval.

## Run the frontend

From the frontend folder:

npm install
npm run dev

## API endpoints

- GET / returns basic service metadata
- GET /health reports backend health and the configured model provider status
- POST /chat accepts a message and returns a response plus activity metadata

## Learning and memory

The agent stores lessons in SQLite and retrieves relevant past experiences before generating a response. These lessons are intended to support behavior reuse, failure recovery, and tool selection without pretending that the model was always available.

## Important operational note

The system is designed to continue working when Ollama is offline. In that case, the agent uses deterministic logic and truthful fallback responses instead of crashing or inventing results.

## Validation

The project is validated with:

- python -m compileall agent tools memory app
- pytest when the repository contains actual pytest-based tests

The script-style files under the agent folder are demonstration harnesses and are not always recognized as pytest tests by default.
