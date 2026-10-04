from agent.task_features import extract_task_features


# =========================================================
# SIMILARITY
# =========================================================

def calculate_similarity(
    current_features,
    lesson_features
):
    """
    Calculate Jaccard-style similarity between
    two task feature sets.
    """

    if not current_features or not lesson_features:
        return 0.0

    intersection = (
        current_features
        & lesson_features
    )

    union = (
        current_features
        | lesson_features
    )

    return len(intersection) / len(union)


# =========================================================
# PREFERRED LESSON TYPES
# =========================================================

def get_preferred_lesson_types(user_input):
    """
    Determine which lesson types are relevant
    to the current task.

    ERROR_RECOVERY is included for tool-based
    tasks because a learned recovery strategy
    may be directly useful if a tool fails.
    """

    features = extract_task_features(
        user_input
    )

    preferred_types = []

    # -----------------------------------------------------
    # Multi-step tasks
    # -----------------------------------------------------

    if "multi_step" in features:

        preferred_types.extend([
            "PLANNING",
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ])

    # -----------------------------------------------------
    # Calculation
    # -----------------------------------------------------

    if "calculation" in features:

        preferred_types.extend([
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ])

    # -----------------------------------------------------
    # Time
    # -----------------------------------------------------

    if "time" in features:

        preferred_types.extend([
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ])

    # -----------------------------------------------------
    # Word count
    # -----------------------------------------------------

    if "word_count" in features:

        preferred_types.extend([
            "TOOL_USAGE",
            "VERIFICATION",
            "ERROR_RECOVERY"
        ])

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    preferred_types = list(
        dict.fromkeys(
            preferred_types
        )
    )

    return preferred_types


# =========================================================
# LESSON SIGNATURE
# =========================================================

def get_lesson_signature(lesson):
    """
    Create a lightweight behavioral signature
    so repeated lessons do not dominate retrieval.
    """

    if len(lesson) < 6:

        return (
            lesson[0],
            lesson[4] if len(lesson) > 4 else ""
        )

    lesson_type = (
        lesson[5]
        or "ANSWER_QUALITY"
    )

    lesson_text = (
        lesson[4]
        or ""
    )

    return (
        lesson_type.upper().strip(),
        lesson_text.lower().strip()
    )


# =========================================================
# RETRIEVE SIMILAR LESSONS
# =========================================================

def retrieve_similar_lessons(
    user_input,
    lessons,
    top_k=5
):
    """
    Retrieve relevant previous lessons.

    Retrieval strategy:

    1. Extract current task features.
    2. Identify relevant lesson types.
    3. Prefer relevant lesson types.
    4. Rank by task similarity.
    5. Prevent identical lessons from dominating
       the result.
    6. Use structural fallback when necessary.
    """

    current_features = (
        extract_task_features(
            user_input
        )
    )

    if not current_features:

        return []


    preferred_types = (
        get_preferred_lesson_types(
            user_input
        )
    )


    # =====================================================
    # REMOVE DUPLICATE LESSONS FOR RETRIEVAL
    # =====================================================

    unique_lessons = []

    seen_signatures = set()

    for lesson in lessons:

        signature = (
            get_lesson_signature(
                lesson
            )
        )

        if signature in seen_signatures:

            continue

        seen_signatures.add(
            signature
        )

        unique_lessons.append(
            lesson
        )


    # =====================================================
    # STAGE 1 — RELEVANT LESSON TYPES
    # =====================================================

    preferred_lessons = []

    for lesson in unique_lessons:

        if len(lesson) >= 6:

            lesson_type = (
                lesson[5]
                or "ANSWER_QUALITY"
            )

        else:

            lesson_type = (
                "ANSWER_QUALITY"
            )


        lesson_type = (
            lesson_type
            .upper()
            .strip()
        )


        if lesson_type not in preferred_types:

            continue


        previous_input = lesson[0]

        previous_features = (
            extract_task_features(
                previous_input
            )
        )


        similarity = (
            calculate_similarity(
                current_features,
                previous_features
            )
        )


        if similarity > 0:

            preferred_lessons.append(
                (
                    similarity,
                    lesson
                )
            )


    # =====================================================
    # STAGE 1 RESULT
    # =====================================================

    if preferred_lessons:

        # -------------------------------------------------
        # Rank by:
        #
        # 1. Similarity
        # 2. Lesson type relevance
        #
        # ERROR_RECOVERY receives a small relevance
        # boost for tool-based tasks.
        # -------------------------------------------------

        def ranking_key(item):

            similarity, lesson = item

            if len(lesson) >= 6:

                lesson_type = (
                    lesson[5]
                    or "ANSWER_QUALITY"
                )

            else:

                lesson_type = (
                    "ANSWER_QUALITY"
                )


            lesson_type = (
                lesson_type
                .upper()
                .strip()
            )


            type_priority = 0

            if lesson_type == "ERROR_RECOVERY":

                type_priority = 3

            elif lesson_type == "TOOL_USAGE":

                type_priority = 2

            elif lesson_type == "VERIFICATION":

                type_priority = 1


            return (
                similarity,
                type_priority
            )


        preferred_lessons.sort(
            key=ranking_key,
            reverse=True
        )


        return [
            lesson
            for similarity, lesson
            in preferred_lessons[:top_k]
        ]


    # =====================================================
    # STAGE 2 — STRUCTURAL FALLBACK
    # =====================================================

    fallback_lessons = []

    for lesson in unique_lessons:

        previous_input = lesson[0]

        previous_features = (
            extract_task_features(
                previous_input
            )
        )


        similarity = (
            calculate_similarity(
                current_features,
                previous_features
            )
        )


        if similarity > 0:

            fallback_lessons.append(
                (
                    similarity,
                    lesson
                )
            )


    fallback_lessons.sort(
        key=lambda item: item[0],
        reverse=True
    )


    return [
        lesson
        for similarity, lesson
        in fallback_lessons[:top_k]
    ]
