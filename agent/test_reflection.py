import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from reflection import reflect_and_improve


user_input = "What is 25 * 40?"

agent_response = "The result is 1000."

lesson = "The answer should clearly state the calculation result."

result = reflect_and_improve(
    user_input,
    agent_response,
    lesson
)

print("\n🔍 REFLECTION")
print("=" * 50)
print(result)