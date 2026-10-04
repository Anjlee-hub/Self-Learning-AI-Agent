def is_useful_lesson(
    user_input,
    agent_response,
    score,
    success,
    lesson
):
    """
    Decide whether an evaluated experience contains
    useful information for future learning.

    This is intentionally rule-based for now.
    We want a transparent baseline before using
    another LLM to judge learning quality.
    """

    # ------------------------------------------
    # Basic validation
    # ------------------------------------------

    if not lesson:
        return False

    lesson = lesson.strip()

    if len(lesson) < 10:
        return False

    # ------------------------------------------
    # Reject obviously weak lessons
    # ------------------------------------------

    rejected_phrases = [
        "no lesson",
        "no information",
        "nothing learned",
        "no useful",
        "previous answer was correct"
    ]

    lesson_lower = lesson.lower()

    for phrase in rejected_phrases:

        if phrase in lesson_lower:
            return False

    # ------------------------------------------
    # Successful experiences
    # ------------------------------------------

    if success == "YES" and score >= 4:

        return True

    # ------------------------------------------
    # Failed experiences
    #
    # Failed experiences can still contain
    # valuable learning, but only if the lesson
    # describes an actual improvement.
    # ------------------------------------------

    improvement_indicators = [
        "should",
        "must",
        "avoid",
        "instead",
        "improve",
        "use",
        "when",
        "ensure",
        "separate",
        "check",
        "verify"
    ]

    if any(
        word in lesson_lower
        for word in improvement_indicators
    ):

        return True

    return False