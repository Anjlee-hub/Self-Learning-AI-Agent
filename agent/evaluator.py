# =========================================================
# RESPONSE EVALUATOR
# =========================================================

import re

from agent.ollama_client import chat_completion


VALID_LESSON_TYPES = {
    "TOOL_USAGE",
    "PLANNING",
    "VERIFICATION",
    "ERROR_RECOVERY",
    "ANSWER_QUALITY",
}


def evaluate_response(user_input, agent_response):
    """
    Evaluate the agent's response and extract a reusable lesson.

    Returns:
        score,
        success,
        lesson_type,
        lesson
    """

    response_lower = str(agent_response).lower()

    # -----------------------------------------------------
    # 1. EXPLICIT TOOL FAILURE DETECTION
    # -----------------------------------------------------

    failure_indicators = [
        "tool failed",
        "tool execution failed",
        "operation failed",
        "could not be completed",
        "execution failed",
        "failed while executing",
        "error occurred",
        "exception occurred",
        "unable to complete",
        "unable to execute",
    ]

    if any(
        indicator in response_lower
        for indicator in failure_indicators
    ):

        return (
            1,
            "NO",
            "ERROR_RECOVERY",
            "Retry a failed tool operation before abandoning the task.",
        )

    # -----------------------------------------------------
    # 2. VERIFIED RESULT DETECTION
    # -----------------------------------------------------
    #
    # This is deterministic information produced by our
    # verification system. The LLM should not override it.
    #

    verification_success_indicators = [
        "independent verification: passed",
        "tool result was independently verified",
        "tool result independently verified",
        "verification passed",
        "independently verified and is correct",
    ]

    if any(
        indicator in response_lower
        for indicator in verification_success_indicators
    ):

        return (
            5,
            "YES",
            "VERIFICATION",
            "Verify tool results before reporting them.",
        )

    # -----------------------------------------------------
    # 3. VERIFIED CORRECTION
    # -----------------------------------------------------

    correction_indicators = [
        "original tool result was incorrect",
        "tool result was incorrect",
        "was corrected using independent verification",
    ]

    if (
        any(
            indicator in response_lower
            for indicator in correction_indicators
        )
        and
        (
            "independently verified result"
            in response_lower
            or
            "verification"
            in response_lower
        )
    ):

        return (
            5,
            "YES",
            "VERIFICATION",
            "Verify tool results before reporting them.",
        )

    # -----------------------------------------------------
    # 4. GENERAL VERIFICATION DETECTION
    # -----------------------------------------------------

    verification_patterns = [
        "verify tool results",
        "verify the result",
        "verify results",
        "verification",
        "independently verify",
        "independent verification",
        "check the result",
        "check results",
        "validate the result",
        "validate results",
    ]

    if any(
        pattern in response_lower
        for pattern in verification_patterns
    ):

        return (
            5,
            "YES",
            "VERIFICATION",
            "Verify tool results before reporting them.",
        )

    # -----------------------------------------------------
    # 5. NORMAL LLM EVALUATION
    # -----------------------------------------------------

    prompt = f"""
You are evaluating an AI agent response.

USER TASK:
{user_input}

AGENT RESPONSE:
{agent_response}

Evaluate the response.

Rules:

1. SCORE must be an integer from 1 to 5.

2. SUCCESS must be YES or NO.

3. LESSON_TYPE must be exactly one of:

TOOL_USAGE
PLANNING
VERIFICATION
ERROR_RECOVERY
ANSWER_QUALITY

4. LESSON must be a short reusable behavioral rule.

Important classification rules:

- If the lesson involves checking, validating,
  independently checking, or verifying a result,
  use VERIFICATION.

- If the lesson involves using a calculator,
  time tool, word counter, or another tool,
  use TOOL_USAGE.

- If the lesson involves breaking a task into steps,
  use PLANNING.

- If the lesson involves recovering from a failure,
  retrying a failed operation, or handling an error,
  use ERROR_RECOVERY.

- Use ANSWER_QUALITY only for general answer
  clarity, relevance, precision, or communication.

For calculations, prefer VERIFICATION when
the lesson is about checking the result.

Return exactly:

SCORE: <1-5>
SUCCESS: <YES/NO>
LESSON_TYPE: <type>
LESSON: <short reusable behavioral rule>
"""

    try:

        content = chat_completion(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

    except Exception:

        return (
            3,
            "YES",
            "ANSWER_QUALITY",
            "Provide a clear and relevant answer.",
        )

    # -----------------------------------------------------
    # 6. PARSE EVALUATOR OUTPUT
    # -----------------------------------------------------

    score_match = re.search(
        r"SCORE:\s*([1-5])",
        content,
        re.IGNORECASE,
    )

    success_match = re.search(
        r"SUCCESS:\s*(YES|NO)",
        content,
        re.IGNORECASE,
    )

    lesson_type_match = re.search(
        r"LESSON_TYPE:\s*([A-Z_]+)",
        content,
        re.IGNORECASE,
    )

    lesson_match = re.search(
        r"LESSON:\s*(.+)",
        content,
        re.IGNORECASE,
    )

    score = (
        int(score_match.group(1))
        if score_match
        else 3
    )

    success = (
        success_match.group(1).upper()
        if success_match
        else "YES"
    )

    lesson_type = (
        lesson_type_match.group(1).upper()
        if lesson_type_match
        else "ANSWER_QUALITY"
    )

    lesson = (
        lesson_match.group(1).strip()
        if lesson_match
        else "Provide a clear and relevant answer."
    )

    if lesson_type not in VALID_LESSON_TYPES:
        lesson_type = "ANSWER_QUALITY"

    return (
        score,
        success,
        lesson_type,
        lesson,
    )