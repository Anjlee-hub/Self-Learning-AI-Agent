import re

from agent.ollama_client import get_ollama_client


# ==================================================
# RULE-BASED REUSABILITY CHECK
# ==================================================

def has_reusable_behavior(lesson):

    if not lesson:
        return False

    text = lesson.strip().lower()

    # ------------------------------------------
    # Obviously bad / descriptive phrases
    # ------------------------------------------

    rejected_patterns = [
        "the response was correct",
        "the answer was correct",
        "the response was clear",
        "the answer was clear",
        "the task was completed",
        "provided the correct result",
        "provided the correct answer",
        "correct calculation result",
        "correctly provided",
        "successfully completed",
        "stated the correct",
        "calculation was done manually",
        "manually calculated",
        "old timestamp"
    ]

    for pattern in rejected_patterns:

        if pattern in text:
            return False


    # ------------------------------------------
    # Strong reusable-behavior indicators
    # ------------------------------------------

    behavior_patterns = [
        r"\buse\b",
        r"\bavoid\b",
        r"\bprefer\b",
        r"\bverify\b",
        r"\bcheck\b",
        r"\bensure\b",
        r"\bbreak\b",
        r"\bseparate\b",
        r"\bretrieve\b",
        r"\bexecute\b",
        r"\bvalidate\b",
        r"\bstore\b",
        r"\bselect\b",
        r"\bchoose\b",
        r"\bhandle\b",
        r"\bretry\b",
        r"\bwhen\b",
        r"\bif\b",
        r"\bshould\b",
        r"\bmust\b"
    ]

    matches = 0

    for pattern in behavior_patterns:

        if re.search(
            pattern,
            text
        ):
            matches += 1


    # At least one strong behavioral
    # indicator is enough for this baseline.
    return matches >= 1


# ==================================================
# LLM VALIDATION
# ==================================================

def llm_validate_learning(
    user_input,
    agent_response,
    score,
    success,
    lesson
):

    prompt = f"""
You are validating a proposed learning rule.

USER REQUEST:
{user_input}

AGENT RESPONSE:
{agent_response}

PROPOSED LESSON:
{lesson}

Determine whether the PROPOSED LESSON itself
describes reusable behavior.

Do NOT invent a new strategy.

A reusable behavioral rule tells the agent
HOW to behave in future situations.

Examples of valid rules:

"Use the calculator tool for arithmetic."

"Break multi-step requests into separate tool calls."

"Verify tool output before reporting results."

Examples of invalid lessons:

"The answer was correct."

"The response was clear."

"The agent completed the task."

Return exactly:

VALID: YES or NO
REASON: <short reason>
"""

    response = get_ollama_client().chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    output = response.message.content.strip()

    valid_match = re.search(
        r"VALID:\s*(YES|NO)",
        output,
        re.IGNORECASE
    )

    reason_match = re.search(
        r"REASON:\s*(.+)",
        output,
        re.IGNORECASE
    )

    valid = (
        valid_match.group(1).upper()
        if valid_match
        else "NO"
    )

    reason = (
        reason_match.group(1).strip()
        if reason_match
        else "LLM validation failed."
    )

    return valid, reason


# ==================================================
# HYBRID VALIDATOR
# ==================================================

def validate_learning(
    user_input,
    agent_response,
    score,
    success,
    lesson
):

    # ------------------------------------------
    # First: deterministic rule check
    # ------------------------------------------

    rule_based_result = has_reusable_behavior(
        lesson
    )


    # ------------------------------------------
    # Clearly invalid lesson
    # ------------------------------------------

    if not rule_based_result:

        return (
            "NO",
            "Lesson does not contain a clear reusable behavioral rule."
        )


    # ------------------------------------------
    # Clearly behavioral lesson
    #
    # We accept it without another LLM call.
    # This reduces latency and avoids LLM
    # misclassification of obvious strategies.
    # ------------------------------------------

    return (
        "YES",
        "Lesson contains an explicit reusable behavioral rule."
    )