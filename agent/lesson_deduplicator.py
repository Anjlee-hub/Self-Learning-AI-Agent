import re


def normalize_lesson(text):
    """
    Normalize lesson text for comparison.
    """

    if not text:
        return ""

    text = text.lower().strip()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_behavior_signature(lesson, lesson_type):
    """
    Convert a lesson into a reusable behavioral signature.

    The goal is semantic deduplication at the level of
    learned behavior rather than exact wording.
    """

    if not lesson:
        return None

    text = normalize_lesson(lesson)
    lesson_type = (lesson_type or "").upper().strip()

    # --------------------------------------------------------
    # ERROR RECOVERY
    # --------------------------------------------------------

    if lesson_type == "ERROR_RECOVERY":

        retry_words = [
            "retry",
            "try again",
            "attempt again",
            "repeat"
        ]

        failure_words = [
            "fail",
            "failed",
            "failure",
            "error",
            "unsuccessful"
        ]

        has_retry = any(
            word in text
            for word in retry_words
        )

        has_failure = any(
            word in text
            for word in failure_words
        )

        if has_retry and has_failure:
            return (
                "ERROR_RECOVERY",
                "RETRY_FAILED_OPERATION"
            )

    # --------------------------------------------------------
    # TOOL USAGE — CALCULATOR
    # --------------------------------------------------------

    if lesson_type == "TOOL_USAGE":

        calculator_words = [
            "calculator",
            "arithmetic",
            "calculation",
            "calculate",
            "multiplication",
            "addition",
            "subtraction",
            "division"
        ]

        if any(
            word in text
            for word in calculator_words
        ):
            return (
                "TOOL_USAGE",
                "CALCULATOR"
            )

        # ----------------------------------------------------
        # TOOL USAGE — WORD COUNTER
        # ----------------------------------------------------

        word_counter_words = [
            "word counter",
            "word count",
            "count words",
            "count the words"
        ]

        if any(
            word in text
            for word in word_counter_words
        ):
            return (
                "TOOL_USAGE",
                "WORD_COUNTER"
            )

        # ----------------------------------------------------
        # TOOL USAGE — CURRENT TIME
        # ----------------------------------------------------

        time_words = [
            "current time",
            "get the time",
            "time tool"
        ]

        if any(
            word in text
            for word in time_words
        ):
            return (
                "TOOL_USAGE",
                "CURRENT_TIME"
            )

    # --------------------------------------------------------
    # PLANNING
    # --------------------------------------------------------

    if lesson_type == "PLANNING":

        planning_words = [
            "plan",
            "planning",
            "break the task",
            "steps",
            "multi step"
        ]

        if any(
            word in text
            for word in planning_words
        ):
            return (
                "PLANNING",
                "TASK_PLANNING"
            )

    # --------------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------------

    if lesson_type == "VERIFICATION":

        verification_words = [
            "verify",
            "verification",
            "check the result",
            "check results",
            "validate the result"
        ]

        if any(
            word in text
            for word in verification_words
        ):
            return (
                "VERIFICATION",
                "VERIFY_RESULTS"
            )

    # --------------------------------------------------------
    # ANSWER QUALITY
    # --------------------------------------------------------

    if lesson_type == "ANSWER_QUALITY":

        answer_words = [
            "answer",
            "response",
            "explanation",
            "clear",
            "precise",
            "accurate"
        ]

        if any(
            word in text
            for word in answer_words
        ):
            return (
                "ANSWER_QUALITY",
                text
            )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return (
        lesson_type,
        text
    )


def are_same_task_type(type_a, type_b):
    """
    Check whether two lessons have the same category.
    """

    if not type_a or not type_b:
        return False

    return (
        type_a.upper().strip()
        ==
        type_b.upper().strip()
    )


def are_same_lesson(
    lesson_a,
    lesson_type_a,
    lesson_b,
    lesson_type_b
):
    """
    Determine whether two lessons represent the same
    reusable behavior.
    """

    if not are_same_task_type(
        lesson_type_a,
        lesson_type_b
    ):
        return False

    signature_a = get_behavior_signature(
        lesson_a,
        lesson_type_a
    )

    signature_b = get_behavior_signature(
        lesson_b,
        lesson_type_b
    )

    return signature_a == signature_b


def deduplicate_lessons(lessons):
    """
    Remove duplicate learned behaviors while preserving
    different behaviors.

    Expected tuple structure:

    (
        user_input,
        agent_response,
        score,
        success,
        lesson,
        lesson_type
    )
    """

    unique_lessons = []

    seen_signatures = set()

    for lesson in lessons:

        if len(lesson) < 6:
            unique_lessons.append(lesson)
            continue

        lesson_text = lesson[4]
        lesson_type = lesson[5]

        signature = get_behavior_signature(
            lesson_text,
            lesson_type
        )

        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)

        unique_lessons.append(lesson)

    return unique_lessons