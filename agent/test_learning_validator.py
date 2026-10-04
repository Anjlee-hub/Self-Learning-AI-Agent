from learning_validator import validate_learning


# ==================================================
# TEST 1 — BAD LESSON
# ==================================================

bad_lesson = (
    "The agent correctly combined the results "
    "and stated the calculation was done manually "
    "due to lack of tool result."
)


print("\n🧪 TEST 1 — BAD LESSON")
print("=" * 50)


valid, reason = validate_learning(
    user_input=(
        "Calculate 50 * 20, get the current time, "
        "and count the words in 'AI is amazing'"
    ),
    agent_response=(
        "The product is 1000 and the current time "
        "is 2026-09-06 22:22:14."
    ),
    score=5,
    success="YES",
    lesson=bad_lesson
)


print(f"VALID: {valid}")
print(f"REASON: {reason}")


# ==================================================
# TEST 2 — GOOD LESSON
# ==================================================

good_lesson = (
    "Break independent multi-step requests "
    "into separate executable tool operations."
)


print("\n🧪 TEST 2 — GOOD LESSON")
print("=" * 50)


valid, reason = validate_learning(
    user_input=(
        "Calculate 25 * 40, get the current time, "
        "and count the words in 'I am learning AI'"
    ),
    agent_response=(
        "1. 25 × 40 = 1000\n"
        "2. Current time retrieved from the tool\n"
        "3. Word count = 4"
    ),
    score=5,
    success="YES",
    lesson=good_lesson
)


print(f"VALID: {valid}")
print(f"REASON: {reason}")