from agent.ollama_client import get_ollama_client


def reflect_and_improve(
    user_input,
    agent_response,
    lesson
):

    prompt = f"""
You are the reflection module of an AI agent.

USER REQUEST:
{user_input}

AGENT RESPONSE:
{agent_response}

LEARNED LESSON:
{lesson}

The agent response may contain an error.

Your job is to explain what went wrong and suggest
how the agent should improve.

==================================================
CRITICAL SAFETY RULE
==================================================

The agent may only report results that are explicitly
present in the AGENT RESPONSE.

NEVER invent:

- calculation results
- timestamps
- dates
- tool outputs
- completed steps
- execution status
- successful operations

NEVER pretend a failed operation succeeded.

If a tool operation failed, the improved answer
MUST clearly acknowledge the failure.

Do not create replacement results.

==================================================
IMPORTANT
==================================================

Return exactly:

REFLECTION: <short explanation>

IMPROVED_ANSWER: <corrected answer based ONLY on available evidence>

Do not add any other sections.
"""

    try:
        response = get_ollama_client().chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.message.content.strip()
    except Exception:
        return (
            "REFLECTION: The local LLM was unavailable, so no new claim was invented. "
            "The agent must report only the evidence already present in the response.\n"
            f"IMPROVED_ANSWER: {agent_response}"
        )