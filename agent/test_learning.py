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

from memory.memory import init_db, save_lesson
from evaluator import evaluate_response


# Initialize database
init_db()


# Test input
user_input = "What is 25 * 40?"

agent_response = "The answer is 1000."


# Evaluate the response
score, success, lesson_type, lesson = evaluate_response(
    user_input,
    agent_response
)


# Save the lesson
save_lesson(
    user_input,
    agent_response,
    score,
    success,
    lesson,
    lesson_type
)


print("\nEvaluation:")
print("Score:", score)
print("Success:", success)
print("Lesson:", lesson)

print("\n✅ Lesson saved to memory!")