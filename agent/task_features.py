import re


def extract_task_features(text):
    """
    Extract simple task-level features from a user request.

    These features describe WHAT kind of task the user wants,
    rather than the exact values or wording.
    """

    text = text.lower()

    features = set()

    # -------------------------------
    # Calculation
    # -------------------------------

    calculation_patterns = [
        r"\d+\s*[\+\-\*\/]\s*\d+",
        r"\bcalculate\b",
        r"\bcompute\b",
        r"\bmultiply\b",
        r"\badd\b",
        r"\bsubtract\b",
        r"\bdivide\b",
        r"\bplus\b",
        r"\bminus\b",
        r"\btimes\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in calculation_patterns
    ):
        features.add("calculation")


    # -------------------------------
    # Current time / date
    # -------------------------------

    time_keywords = [
        "current time",
        "what time",
        "current date",
        "today's date",
        "date today"
    ]

    if any(
        keyword in text
        for keyword in time_keywords
    ):
        features.add("time")


    # -------------------------------
    # Word counting
    # -------------------------------

    word_count_keywords = [
        "count words",
        "count the words",
        "number of words",
        "how many words",
        "word count"
    ]

    if any(
        keyword in text
        for keyword in word_count_keywords
    ):
        features.add("word_count")


    # -------------------------------
    # Multi-step task
    # -------------------------------

    multi_step_indicators = [
        " and ",
        " then ",
        "also",
        "after that",
        "first",
        "next"
    ]

    if any(
        indicator in text
        for indicator in multi_step_indicators
    ):
        features.add("multi_step")


    return features