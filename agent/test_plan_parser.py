import sys
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)

from plan_parser import parse_plan


plan = """
Based on the user request, I created the following plan:

1. Calculate 250 * 4
2. Get the current time

These are the executable operations.
"""


print("\n" + "=" * 60)
print("PLAN PARSER TEST")
print("=" * 60)

print("\nOriginal planner output:")
print(plan)

steps = parse_plan(plan)

print("\nParsed steps:")

for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")


print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

if steps == [
    "Calculate 250 * 4",
    "Get the current time"
]:

    print("\n✅ PLAN PARSER: PASS")

else:

    print("\n❌ PLAN PARSER: FAIL")

    print(
        "\nActual:",
        steps
    )