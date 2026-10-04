import re

from agent.ollama_client import chat_completion, is_llm_available


def _fallback_plan(user_input):
    text = (user_input or "").strip()
    if not text:
        return ""

    lower = text.lower()
    steps = []

    if re.search(r"\d\s*(?:\*\*|[\+\-\*\/x%])\s*\d|calculate|compute|multiply|add|subtract|divide", lower):
        calc_match = re.search(r"-?\d+(?:\.\d+)?\s*(?:\*\*|[\+\-\*\/x%])\s*-?\d+(?:\.\d+)?", lower)
        if calc_match:
            steps.append(f"Calculate {calc_match.group(0).replace('x', '*')}")

    if "current time" in lower or "what time" in lower or "get the time" in lower or "tell me the time" in lower:
        steps.append("Get the current time")

    if "word count" in lower or "count the words" in lower or "count words" in lower:
        quoted = re.search(r"['\"](.+?)['\"]", text)
        if quoted:
            steps.append(f"Count the words in '{quoted.group(1)}'")
        else:
            steps.append("Count the words in the provided text")

    if not steps:
        return "1. " + text

    return "\n".join(f"{index}. {step}" for index, step in enumerate(steps, 1))


def create_plan(
    user_input,
    learning_strategy=""
):

    try:
        if not is_llm_available():
            return _fallback_plan(user_input)
    except Exception:
        return _fallback_plan(user_input)

    prompt = f"""
You are the planning module of an AI agent.

Your job is to break the user's request into
simple executable tool operations.

USER REQUEST:
{user_input}

AVAILABLE TOOLS:

1. Calculator
2. Current Time
3. Word Counter

PREVIOUS LEARNED STRATEGY:
{learning_strategy}

==================================================
CRITICAL DISTINCTION
==================================================

The learned strategy describes HOW the agent should
behave.

It is NOT a task step.

NEVER convert a learned strategy into a numbered
plan step.

For example, if the learned strategy says:

"Retry a failed tool operation before abandoning the task."

DO NOT create:

"Retry the failed tool operation."

The executor already handles retry behavior.

==================================================
PLAN RULES
==================================================

1. Create ONLY executable tool operations.

2. Every numbered step MUST be directly executable
   by exactly one available tool.

3. The number of plan steps MUST match the number
   of operations explicitly requested by the user.

4. NEVER add an operation merely because it appears
   in an example in this prompt.

5. NEVER add an operation that is not explicitly
   requested in the USER REQUEST.

6. Do NOT create steps for:
   - retrying
   - learning
   - remembering
   - evaluating
   - reflecting
   - verifying
   - combining results
   - summarizing results
   - explaining results

7. Do NOT create a step describing the learned strategy.

8. Independent operations should be separate steps.

9. Use the learned strategy only to improve HOW
   the operations are executed.

10. Do not copy old numerical results.

11. Do not invent information.

12. Do not add demonstration, testing, or example
    operations that the user did not request.

13. If the user requests two operations, return
    exactly two operations.

14. If the user requests three operations, return
    exactly three operations.

==================================================
AVAILABLE TOOL FORMATS
==================================================

Calculator examples:

Calculate 25 * 40

Multiply 25 by 40

Calculate 100 + 50

Current Time:

Get the current time

Word Counter:

Count the words in 'I am learning AI'

==================================================
IMPORTANT EXAMPLE
==================================================

USER REQUEST:

Calculate 25 * 40 and get the current time.

LEARNED STRATEGY:

Retry a failed tool operation before abandoning
the task.

CORRECT PLAN:

1. Calculate 25 * 40
2. Get the current time

WRONG PLAN:

1. Calculate 25 * 40
2. Get the current time
3. Count the words in 'I am learning AI'

The third step is WRONG because the user did not
request word counting.

The retry strategy is also NOT a step because retry
behavior belongs to the executor.

==================================================
ANOTHER EXAMPLE
==================================================

USER REQUEST:

Calculate 25 * 40, get the current time,
and count the words in 'I am learning AI'.

CORRECT PLAN:

1. Calculate 25 * 40
2. Get the current time
3. Count the words in 'I am learning AI'

Do not add any fourth operation.

==================================================
FINAL REQUIREMENT
==================================================

Return ONLY the numbered executable plan.

Do not return:
- introductions
- explanations
- conclusions
- learning instructions
- retry instructions
- verification instructions
- reflection instructions
- extra example operations
- unrelated operations

The plan must contain ONLY operations explicitly
requested by the user.

USER REQUEST:
{user_input}
"""

    try:
        response = chat_completion(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.strip()
    except Exception:
        return _fallback_plan(user_input)
