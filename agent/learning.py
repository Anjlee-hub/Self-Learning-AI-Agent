from agent.ollama_client import chat_completion


# =========================================================
# DETERMINE CURRENT TASK TYPE
# =========================================================

def get_current_task_type(user_input):
    """
    Determine which lesson types are most relevant to
    the current request.

    This prevents the LLM from selecting an unrelated
    lesson simply because it appears in memory.
    """

    text = user_input.lower().strip()

    # -----------------------------------------------------
    # EXPLICIT ERROR / FAILURE / RECOVERY REQUEST
    # -----------------------------------------------------

    recovery_keywords = [
        "failed",
        "failure",
        "error",
        "retry",
        "try again",
        "attempt again",
        "previous failure",
        "previous attempt",
        "failed attempt",
        "after failure",
        "after a failure",
        "operation failed",
        "tool failed",
        "calculator failed",
        "calculator failure",
        "tool failure",
        "execution failed",
        "recover",
        "recovery",
    ]

    if any(
        keyword in text
        for keyword in recovery_keywords
    ):
        return [
            "ERROR_RECOVERY",
            "VERIFICATION",
            "TOOL_USAGE",
            "PLANNING",
        ]

    # -----------------------------------------------------
    # MULTI-STEP TASK
    # -----------------------------------------------------

    operation_keywords = [
        "calculate",
        "compute",
        "multiply",
        "add",
        "subtract",
        "divide",
        "current time",
        "get the time",
        "what time",
        "word count",
        "count words",
        "count the words"
    ]

    operation_count = sum(
        keyword in text
        for keyword in operation_keywords
    )

    has_conjunction = (
        " and " in text
        or " then " in text
        or "," in text
    )

    if operation_count >= 2 and has_conjunction:

        return [
            "PLANNING",
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ]

    # -----------------------------------------------------
    # CALCULATION
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "calculate",
            "compute",
            "multiply",
            "add ",
            "subtract",
            "divide"
        ]
    ):

        return [
            "VERIFICATION",
            "TOOL_USAGE",
            "ERROR_RECOVERY"
        ]

    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "current time",
            "what time",
            "get the time"
        ]
    ):

        return [
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ]

    # -----------------------------------------------------
    # WORD COUNT
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "word count",
            "count words",
            "count the words"
        ]
    ):

        return [
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ]

    # -----------------------------------------------------
    # GENERAL REQUEST
    # -----------------------------------------------------

    return [
        "ANSWER_QUALITY",
        "TOOL_USAGE",
        "PLANNING",
        "VERIFICATION",
        "ERROR_RECOVERY"
    ]


# =========================================================
# EXTRACT LEARNING STRATEGY
# =========================================================

def fallback_learning_strategy(user_input, lessons):
    if not lessons:
        return "NO_USEFUL_LEARNING"

    preferred_types = get_current_task_type(user_input)
    preferred_set = set(preferred_types)

    best_lesson = None
    best_rank = None

    for lesson_data in lessons:
        if len(lesson_data) < 6:
            continue

        _, _, _, _, lesson, lesson_type = lesson_data
        lesson_type = (lesson_type or "").upper().strip()
        lesson_text = (lesson or "").strip()
        if not lesson_text:
            continue

        rank = 0
        if lesson_type in preferred_set:
            rank += 10
        if "retry" in lesson_text.lower() or "failed" in lesson_text.lower() or "error" in lesson_text.lower():
            rank += 5
        if "verify" in lesson_text.lower() or "check" in lesson_text.lower():
            rank += 4
        if "tool" in lesson_text.lower() and "use" in lesson_text.lower():
            rank += 2

        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_lesson = lesson_text

    if not best_lesson:
        return "NO_USEFUL_LEARNING"

    return f"LEARNED_STRATEGY: {best_lesson}"


def extract_learning_strategy(
    user_input,
    lessons
):
    """
    Convert previous experiences into one useful
    behavioral strategy for the current task.
    """

    if not lessons:
        return ""

    # -----------------------------------------------------
    # DETERMINE RELEVANT LESSON TYPES
    # -----------------------------------------------------

    preferred_types = get_current_task_type(
        user_input
    )

    # -----------------------------------------------------
    # FILTER LESSONS
    # -----------------------------------------------------

    relevant_lessons = []

    for lesson_data in lessons:

        if len(lesson_data) < 6:
            continue

        (
            previous_input,
            previous_response,
            score,
            success,
            lesson,
            lesson_type
        ) = lesson_data

        lesson_type = (
            lesson_type or ""
        ).upper().strip()

        if lesson_type in preferred_types:

            relevant_lessons.append(
                lesson_data
            )

    # -----------------------------------------------------
    # NO RELEVANT LEARNING
    # -----------------------------------------------------

    if not relevant_lessons:

        return "NO_USEFUL_LEARNING"

    # -----------------------------------------------------
    # BUILD EXPERIENCE CONTEXT
    # -----------------------------------------------------

    lesson_text = ""

    for (
        previous_input,
        previous_response,
        score,
        success,
        lesson,
        lesson_type
    ) in relevant_lessons:

        lesson_text += f"""
Previous task:
{previous_input}

Previous response:
{previous_response}

Score:
{score}/5

Success:
{success}

Lesson type:
{lesson_type}

Lesson:
{lesson}

-------------------------
"""

    preferred_type_text = ", ".join(
        preferred_types
    )

    # -----------------------------------------------------
    # LLM STRATEGY EXTRACTION
    # -----------------------------------------------------

    prompt = f"""
You are the learning module of a self-learning AI agent.

Your job is to select ONE reusable behavioral strategy
from previous experiences that is relevant to the
CURRENT user request.

CURRENT USER REQUEST:
{user_input}

RELEVANT LESSON TYPES:
{preferred_type_text}

PREVIOUS RELEVANT EXPERIENCES:

{lesson_text}

==================================================
SELECTION RULES
==================================================

1. Choose ONLY from the relevant lesson types listed above.

2. The strategy must directly apply to the current request.

3. Prefer a specific behavioral rule over vague advice.

4. Do not select ERROR_RECOVERY merely because the task
   uses a tool.

5. Select ERROR_RECOVERY when the current task explicitly
   involves a failure, error, retry, failed attempt,
   recovery, or a situation strongly resembling a
   previously learned failure.

6. Select VERIFICATION when previous experience teaches
   checking or independently verifying a result.

7. Select TOOL_USAGE when previous experience teaches
   which tool to use or how to use it.

8. Select PLANNING for genuinely multi-step tasks.

9. Do not combine multiple unrelated strategies.

10. Do not copy previous answers.

11. Do not copy old numerical results.

12. Do not copy old timestamps.

13. Do not invent information.

==================================================
FAILURE / ERROR RECOVERY RULE
==================================================

If the CURRENT USER REQUEST contains or describes:

- a failure
- an error
- a failed attempt
- a previous failure
- a tool failure
- a calculator failure
- a retry
- trying again
- recovery from failure
- an unsuccessful operation

then strongly prefer a relevant ERROR_RECOVERY lesson.

Example:

CURRENT USER REQUEST:
"Calculate 900 * 7 after a calculator failure."

Previous lesson:
"Retry the Calculator tool when the first execution fails."

Correct strategy:

LEARNED_STRATEGY: Retry the Calculator tool when the first execution fails.

Do NOT choose a normal verification strategy
when the current task is explicitly about recovering
from a failure.

==================================================
CALCULATION RULE
==================================================

For a NORMAL calculation request with NO explicit
failure or recovery context:

If a relevant VERIFICATION lesson exists,
prefer the VERIFICATION lesson over an
ERROR_RECOVERY lesson.

Example:

CURRENT USER REQUEST:
"Calculate 600 * 9."

Lesson:
"Verify tool results before reporting them."

Correct strategy:

LEARNED_STRATEGY: Verify tool results before reporting them.

Do NOT choose:

"Retry the Calculator tool when the first execution fails."

unless the current task actually involves
a calculator failure.

==================================================
OUTPUT
==================================================

If there is no useful strategy:

NO_USEFUL_LEARNING

Otherwise:

LEARNED_STRATEGY: <one short actionable strategy>

Keep the strategy under 30 words.

Return ONLY the strategy.
"""

    try:

        strategy = chat_completion(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        strategy = strategy.strip()

    except Exception as error:

        print(
            f"⚠️ Learning strategy extraction failed: {error}"
        )

        return fallback_learning_strategy(user_input, relevant_lessons)

    # -----------------------------------------------------
    # BASIC OUTPUT CLEANING
    # -----------------------------------------------------

    if not strategy:

        return "NO_USEFUL_LEARNING"

    if strategy.upper() == "NO_USEFUL_LEARNING":

        return strategy

    # -----------------------------------------------------
    # ENSURE LEARNED_STRATEGY PREFIX
    # -----------------------------------------------------

    if not strategy.upper().startswith(
        "LEARNED_STRATEGY:"
    ):

        strategy = (
            "LEARNED_STRATEGY: "
            + strategy
        )

    return strategy