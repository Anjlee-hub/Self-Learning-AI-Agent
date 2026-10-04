from verification import (
    independently_verify,
    verify_result
)


print("=" * 60)
print("VERIFICATION TOOL TEST")
print("=" * 60)


# =========================================================
# TEST 1 — INDEPENDENT CALCULATION
# =========================================================

print("\nTEST 1 — Independent calculation")

result = independently_verify(
    "600 * 9"
)

print(
    "600 * 9 =",
    result
)


# =========================================================
# TEST 2 — CORRECT RESULT
# =========================================================

print("\nTEST 2 — Correct result")

verification = verify_result(
    "600 * 9",
    5400
)

print(
    verification
)


# =========================================================
# TEST 3 — INCORRECT RESULT
# =========================================================

print("\nTEST 3 — Incorrect result")

verification = verify_result(
    "600 * 9",
    5300
)

print(
    verification
)


# =========================================================
# FINAL
# =========================================================

if (
    result == 5400
    and verification["verified"] is False
    and verification["verified_result"] == 5400
):

    print(
        "\n✅ VERIFICATION TOOL: PASS"
    )

else:

    print(
        "\n❌ VERIFICATION TOOL: FAIL"
    )