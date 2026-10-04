import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from memory.memory import get_lessons


lessons = get_lessons()

print("\n🧠 LEARNED LESSONS")
print("=" * 50)

for lesson in lessons:

    user_input, response, score, success, text = lesson

    print("\nUser:", user_input)
    print("Agent:", response)
    print("Score:", score)
    print("Success:", success)
    print("Lesson:", text)

print("\n" + "=" * 50)