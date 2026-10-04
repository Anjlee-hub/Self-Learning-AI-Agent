import os
import sys
import re
import ollama

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# MEMORY
# =========================================================

from memory.memory import (
    init_db,
    save_message,
    get_messages,
    save_lesson,
    get_lessons,
    get_recent_lessons,
    search_lessons,
    search_messages,
    get_lessons_by_type
    
)


# =========================================================
# TOOLS
# =========================================================

from tools.calculator import calculate
from tools.time_tool import get_current_time
from tools.text_tool import count_words


# =========================================================
# AGENT MODULES
# =========================================================

from agent.evaluator import evaluate_response
from agent.reflection import reflect_and_improve
from agent.planner import create_plan
from agent.plan_executor import execute_plan, execute_tool_step
from agent.agent_state import AgentState

from agent.learning_validator import validate_learning
from agent.lesson_deduplicator import get_behavior_signature
from agent.learning import extract_learning_strategy
from agent.lesson_retriever import retrieve_similar_lessons
from agent.task_features import extract_task_features
from agent.plan_parser import parse_plan


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()

messages = []


# =========================================================
# REQUEST DETECTION
# =========================================================

def is_multi_step_request(user_input):

    text = user_input.lower()

    operation_patterns = [

        r"\bcalculate\b",
        r"\bcompute\b",
        r"\bmultiply\b",
        r"\badd\b",
        r"\bsubtract\b",
        r"\bdivide\b",

        r"\bget the current time\b",
        r"\bcurrent time\b",

        r"\bcount the words\b",
        r"\bword count\b"
    ]

    matches = 0

    for pattern in operation_patterns:

        if re.search(
            pattern,
            text
        ):
            matches += 1

    conjunctions = [
        " and ",
        ",",
        " then "
    ]

    has_conjunction = any(
        item in text
        for item in conjunctions
    )

    return (
        matches >= 2
        and has_conjunction
    )


def is_calculation_request(user_input):

    text = user_input.lower()

    return (
        "calculate" in text
        or "compute" in text
        or "multiply" in text
        or "add " in text
        or "subtract" in text
        or "divide" in text
    )


def is_time_request(user_input):

    text = user_input.lower()

    return (
        "current time" in text
        or "what time" in text
        or "get the time" in text
    )


def is_word_count_request(user_input):

    text = user_input.lower()

    return (
        "word count" in text
        or "count the words" in text
        or "count words" in text
    )


# =========================================================
# LESSON RETRIEVAL
# =========================================================

def get_relevant_lessons(
    user_input,
    limit=5
):

    try:

        # -------------------------------------------------
        # Extract current task features
        # -------------------------------------------------

        features = extract_task_features(
            user_input
        )

        # -------------------------------------------------
        # Load previous lessons from memory
        # -------------------------------------------------

        lessons = get_lessons()

        if not lessons:
            return []

        # -------------------------------------------------
        # Retrieve structurally similar lessons
        # -------------------------------------------------

        relevant_lessons = (
            retrieve_similar_lessons(
                user_input,
                lessons,
                top_k=limit
            )
        )

        return relevant_lessons

    except Exception as e:

        print(
            f"⚠️ Lesson retrieval failed: {e}"
        )

        return []


# =========================================================
# LEARNING STRATEGY
# =========================================================

def get_learning_strategy(user_input):

    lessons = get_relevant_lessons(
        user_input,
        limit=5
    )

    if not lessons:

        return "", []

    print(
        f"🔎 Retrieved {len(lessons)} similar lesson(s)."
    )

    try:

        strategy = (
            extract_learning_strategy(
                user_input,
                lessons
            )
        )

    except Exception as e:

        print(
            f"⚠️ Learning strategy extraction failed: {e}"
        )

        strategy = ""

    return strategy, lessons


# =========================================================
# DIRECT TOOL EXECUTION
# =========================================================

def execute_direct_tool(user_input):

    # -----------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------

    if is_calculation_request(
        user_input
    ):

        try:

            result = calculate(
                user_input
            )

            return str(result)

        except Exception as e:

            return (
                "Tool execution failed: "
                + str(e)
            )


    # -----------------------------------------------------
    # TIME TOOL
    # -----------------------------------------------------

    if is_time_request(
        user_input
    ):

        try:

            result = get_current_time()

            return str(result)

        except Exception as e:

            return (
                "Tool execution failed: "
                + str(e)
            )


    # -----------------------------------------------------
    # WORD COUNTER
    # -----------------------------------------------------

    if is_word_count_request(
        user_input
    ):

        try:

            result = count_words(
                user_input
            )

            return str(result)

        except Exception as e:

            return (
                "Tool execution failed: "
                + str(e)
            )


    return None


# =========================================================
# MULTI-STEP ANSWER
# =========================================================

def build_multi_step_answer(
    user_input,
    results,
    plan
):

    answer_lines = []

    for index, result in enumerate(
        results,
        1
    ):

        step = ""

        if index <= len(plan):

            step = plan[
                index - 1
            ]

        step_lower = step.lower()


        # -------------------------------------------------
        # CALCULATION
        # -------------------------------------------------

        if "calculate" in step_lower:

            answer_lines.append(
                f"{index}. Calculation result = {result}"
            )


        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        elif (
            "current time" in step_lower
            or "get the time" in step_lower
        ):

            answer_lines.append(
                f"{index}. Current date and time = {result}"
            )


        # -------------------------------------------------
        # WORD COUNT
        # -------------------------------------------------

        elif "word" in step_lower:

            answer_lines.append(
                f"{index}. Number of words = {result}"
            )


        # -------------------------------------------------
        # GENERIC
        # -------------------------------------------------

        else:

            answer_lines.append(
                f"{index}. {result}"
            )

    return "\n".join(
        answer_lines
    )


# =========================================================
# REFLECTION SAFETY
# =========================================================

def reflection_is_safe(
    original_response,
    improved_response
):

    if not original_response:

        return False

    original_lower = (
        original_response.lower()
    )


    failure_indicators = [

        "tool execution failed",
        "tool failed",
        "operation failed",
        "execution failed",
        "could not be completed",
        "unable to execute",
        "error occurred",
        "exception occurred"
    ]


    original_failed = any(
        indicator in original_lower
        for indicator in failure_indicators
    )


    # -----------------------------------------------------
    # No failure detected
    # -----------------------------------------------------

    if not original_failed:

        return True


    improved_lower = (
        improved_response or ""
    ).lower()


    success_indicators = [

        "successful",
        "completed successfully",
        "result =",
        "result:",
        "calculation result"
    ]


    claims_success = any(
        indicator in improved_lower
        for indicator in success_indicators
    )


    if claims_success:

        print(
            "⚠️ Reflection safety blocked "
            "a possible fabricated success claim."
        )

        return False


    return True


# =========================================================
# PROCESS LEARNING
# =========================================================

def process_learning(
    user_input,
    reply,
    score,
    success,
    lesson_type,
    lesson
):

    learning_valid, validation_reason = (
        validate_learning(
            user_input,
            reply,
            score,
            success,
            lesson
        )
    )


    print(
        f"🧠 Learning valid: {learning_valid}"
    )

    print(
        f"🔎 Validation reason: "
        f"{validation_reason}"
    )


    save_learning = False


    # -----------------------------------------------------
    # SUCCESSFUL HIGH-QUALITY LEARNING
    # -----------------------------------------------------

    if (
        learning_valid == "YES"
        and success == "YES"
        and score >= 4
    ):

        save_learning = True


    # -----------------------------------------------------
    # FAILURE RECOVERY LEARNING
    # -----------------------------------------------------

    elif (
        learning_valid == "YES"
        and success == "NO"
        and lesson_type == "ERROR_RECOVERY"
    ):

        save_learning = True


    # -----------------------------------------------------
    # REJECT
    # -----------------------------------------------------

    if not save_learning:

        print(
            "🚫 Learning rejected."
        )

        return learning_valid


    # -----------------------------------------------------
    # BEHAVIOR SIGNATURE
    # -----------------------------------------------------

    candidate_signature = (
        get_behavior_signature(
            lesson,
            lesson_type
        )
    )


    # -----------------------------------------------------
    # CHECK EXISTING LESSONS
    # -----------------------------------------------------

    existing_lessons = get_lessons()

    duplicate_found = False


    for existing in existing_lessons:

        if len(existing) < 6:

            continue


        existing_lesson = existing[4]

        existing_type = existing[5]


        existing_signature = (
            get_behavior_signature(
                existing_lesson,
                existing_type
            )
        )


        if (
            candidate_signature is not None
            and candidate_signature
            == existing_signature
        ):

            duplicate_found = True

            break


    # -----------------------------------------------------
    # DUPLICATE
    # -----------------------------------------------------

    if duplicate_found:

        print(
            "♻️ Duplicate behavioral lesson "
            "— learning not stored again."
        )


    # -----------------------------------------------------
    # NEW LEARNING
    # -----------------------------------------------------

    else:

        save_lesson(
            user_input,
            reply,
            score,
            success,
            lesson,
            lesson_type
        )

        print(
            "💾 New behavioral learning saved."
        )


    return learning_valid


# =========================================================
# EVALUATION + LEARNING
# =========================================================

def evaluate_and_learn(
    user_input,
    reply
):

    print(
        "\n🔍 Evaluating response..."
    )

    # -----------------------------------------------------
    # NORMALIZE EXECUTION RESULT
    # -----------------------------------------------------

    evaluation_reply = reply

    if isinstance(reply, dict):

        execution_success = reply.get(
            "success"
        )

        execution_error = reply.get(
            "error"
        )

        execution_result = reply.get(
            "result"
        )

        verified = reply.get(
            "verified"
        )

        corrected = reply.get(
            "corrected"
        )

        # -------------------------------------------------
        # EXPLICIT TOOL FAILURE
        # -------------------------------------------------

        if execution_success is False:

            evaluation_reply = (
                "Tool execution failed: "
                f"{execution_error}"
            )

        # -------------------------------------------------
        # VERIFIED TOOL RESULT
        # -------------------------------------------------

        elif verified is True:

            evaluation_reply = (
                f"Tool result: {execution_result}\n"
                "Independent verification: PASSED\n"
                "The tool result was independently verified "
                "and is correct."
            )

        # -------------------------------------------------
        # TOOL RESULT WAS WRONG BUT CORRECTED
        # -------------------------------------------------

        elif corrected is True:

            evaluation_reply = (
                f"Original tool result: "
                f"{reply.get('result')}\n"
                f"Independently verified result: "
                f"{reply.get('result')}\n"
                "The original tool result was incorrect "
                "and was corrected using independent verification."
            )

        # -------------------------------------------------
        # NORMAL SUCCESSFUL TOOL RESULT
        # -------------------------------------------------

        elif execution_success is True:

            evaluation_reply = (
                f"Tool execution succeeded.\n"
                f"Result: {execution_result}"
            )

        else:

            evaluation_reply = str(
                reply
            )

    # -----------------------------------------------------
    # EVALUATE
    # -----------------------------------------------------

    try:

        score, success, lesson_type, lesson = (
            evaluate_response(
                user_input,
                evaluation_reply
            )
        )

    except Exception as e:

        print(
            f"⚠️ Evaluation failed: {e}"
        )

        return {
            "score": 0,
            "success": "NO",
            "lesson_type": "ANSWER_QUALITY",
            "lesson": "",
            "learning_valid": "NO"
        }

    # -----------------------------------------------------
    # DISPLAY EVALUATION
    # -----------------------------------------------------

    print(
        f"📈 Score: {score}/5"
    )

    print(
        f"✅ Success: {success}"
    )

    print(
        f"🧩 Lesson type: {lesson_type}"
    )

    print(
        f"🧠 Lesson: {lesson}"
    )

    # -----------------------------------------------------
    # PROCESS LEARNING
    # -----------------------------------------------------

    learning_valid = process_learning(

        user_input,

        evaluation_reply,

        score,

        success,

        lesson_type,

        lesson
    )

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return {
        "score": score,
        "success": success,
        "lesson_type": lesson_type,
        "lesson": lesson,
        "learning_valid": learning_valid
    }
    # -----------------------------------------------------
    # DISPLAY EVALUATION
    # -----------------------------------------------------

    print(
        f"📈 Score: {score}/5"
    )

    print(
        f"✅ Success: {success}"
    )

    print(
        f"🧩 Lesson type: {lesson_type}"
    )

    print(
        f"🧠 Lesson: {lesson}"
    )

    # -----------------------------------------------------
    # PROCESS LEARNING
    # -----------------------------------------------------

    learning_valid = process_learning(

        user_input,

        evaluation_reply,

        score,

        success,

        lesson_type,

        lesson
    )

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return {

        "score": score,

        "success": success,

        "lesson_type": lesson_type,

        "lesson": lesson,

        "learning_valid": learning_valid
    }


    print(
        f"📈 Score: {score}/5"
    )

    print(
        f"✅ Success: {success}"
    )

    print(
        f"🧩 Lesson type: {lesson_type}"
    )

    print(
        f"🧠 Lesson: {lesson}"
    )


    learning_valid = process_learning(

        user_input,

        reply,

        score,

        success,

        lesson_type,

        lesson
    )


    return {

        "score": score,

        "success": success,

        "lesson_type": lesson_type,

        "lesson": lesson,

        "learning_valid": learning_valid
    }


# =========================================================
# SAVE CONVERSATION
# =========================================================

def save_conversation(
    user_input,
    reply
):

    try:
        save_message("user", user_input)
        save_message("assistant", reply)

    except Exception as e:

        print(
            f"⚠️ Conversation save failed: {e}"
        )


# =========================================================

# =========================================================
# =========================================================
# =========================================================
# CONVERSATIONAL MEMORY RETRIEVAL
# =========================================================

def retrieve_conversation_memory(user_input, limit=5):

    normalized_input = user_input.lower().strip()

    # -----------------------------------------------------
    # PERSONAL MEMORY: NAME
    # -----------------------------------------------------

    if (
        "what is my name" in normalized_input
        or "what's my name" in normalized_input
        or "who am i" in normalized_input
    ):

        results = search_messages(
            "my name is",
            limit=limit
        )

        return results[:limit]

    # -----------------------------------------------------
    # PERSONAL MEMORY: "I AM"
    # -----------------------------------------------------

    if (
        normalized_input.startswith("who am i")
        or normalized_input.startswith("tell me about me")
    ):

        results = search_messages(
            "I am",
            limit=limit
        )

        return results[:limit]

    # -----------------------------------------------------
    # GENERAL MEMORY
    # -----------------------------------------------------

    stop_words = {
        "what",
        "what's",
        "when",
        "where",
        "which",
        "who",
        "whom",
        "why",
        "how",
        "is",
        "are",
        "was",
        "were",
        "the",
        "this",
        "that",
        "my",
        "your",
        "you",
        "me",
        "can",
        "could",
        "would",
        "should",
        "tell",
        "please"
    }

    words = [
        word.strip(".,!?;:()[]{}\"'")
        for word in normalized_input.split()
    ]

    meaningful_words = [
        word
        for word in words
        if len(word) >= 5 and word not in stop_words
    ]

    memories = []

    for word in meaningful_words:

        try:

            results = search_messages(
                word,
                limit=limit
            )

            for message in results:

                if message not in memories:
                    memories.append(message)

        except Exception as error:

            print(
                f"?? Conversation memory search failed: {error}"
            )

    return memories[:limit]

# MAIN AGENT
# =========================================================

def run_agent(
    user_input
):

    user_input = user_input.strip()


    if not user_input:

        return ""


    # =====================================================
    # STEP 1 — RETRIEVE LEARNING
    # =====================================================

    learning_strategy, lessons = (
        get_learning_strategy(
            user_input
        )
    )


    if lessons:

        print(
            "📚 Previous learning found!"
        )

        print(
            f"🔎 Retrieved "
            f"{len(lessons)} similar lesson(s)."
        )

    else:

        print(
            "📚 No previous learning found."
        )


    if learning_strategy:

        print(
            "\n🧠 LEARNED STRATEGY:"
        )

        print(
            learning_strategy
        )


    # =====================================================
    # STEP 2 — MULTI-STEP TASK
    # =====================================================

    if is_multi_step_request(
        user_input
    ):

        print(
            "\n🧠 Planning required..."
        )


        try:

            plan_text = create_plan(
                user_input,
                learning_strategy
            )

        except Exception as e:

            print(
                f"⚠️ Planner failed: {e}"
            )

            plan_text = ""


        print(
            "\n📋 RAW PLAN:"
        )

        print(
            plan_text
        )


        plan_steps = parse_plan(
            plan_text
        )


        print(
            "\n📋 PARSED PLAN:"
        )


        for index, step in enumerate(
            plan_steps,
            1
        ):

            print(
                f"{index}. {step}"
            )


        # -------------------------------------------------
        # INVALID PLAN
        # -------------------------------------------------

        if not plan_steps:

            reply = (
                "I could not create a valid "
                "executable plan for this request."
            )


            evaluate_and_learn(
                user_input,
                reply
            )


            save_conversation(
                user_input,
                reply
            )


            return reply


        # -------------------------------------------------
        # CREATE AGENT STATE
        # -------------------------------------------------

        state = AgentState(
            user_input,
            plan_steps
        )


        state.start()


        print(
            "\n🧠 AGENT STATE STARTED"
        )


        print(
            state.show_state()
        )


        # -------------------------------------------------
        # EXECUTE PLAN
        # -------------------------------------------------

        state = execute_plan(

            plan_steps,

            state,

            learning_strategy=learning_strategy
        )


        print(
            "\n📦 PLAN RESULTS:"
        )

        print(
            state.results
        )


        print(
            "\n🏁 AGENT STATE:"
        )

        print(
            state.show_state()
        )


        # -------------------------------------------------
        # EXECUTION FAILURE
        # -------------------------------------------------

        if state.status != "completed":

            reply = (
                "Tool execution failed: "
                f"{state.error}"
            )


            try:

                reflection = (
                    reflect_and_improve(
                        user_input,
                        reply,
                        "Retry failed operations "
                        "before abandoning the task."
                    )
                )


                if reflection_is_safe(
                    reply,
                    reflection
                ):

                    print(
                        "\n🪞 REFLECTION:"
                    )

                    print(
                        reflection
                    )


            except Exception as e:

                print(
                    f"⚠️ Reflection failed: {e}"
                )


            evaluate_and_learn(
                user_input,
                reply
            )


            save_conversation(
                user_input,
                reply
            )


            return reply


        # -------------------------------------------------
        # BUILD FINAL ANSWER
        # -------------------------------------------------

        reply = build_multi_step_answer(

            user_input,

            state.results,

            plan_steps
        )


        evaluate_and_learn(

            user_input,

            reply
        )


        save_conversation(

            user_input,

            reply
        )


        return reply


    # =====================================================
    # STEP 3 — DIRECT TOOL / LLM
    # =====================================================

    direct_result = None

    # -----------------------------------------------------
    # CALCULATOR THROUGH VERIFICATION-AWARE EXECUTOR
    # -----------------------------------------------------
    # Single-step calculations use the same executor as
    # planned tasks so learned verification can affect
    # behavior.
    # -----------------------------------------------------

    if is_calculation_request(user_input):

        try:

            execution = execute_tool_step(
                user_input,
                learning_strategy=learning_strategy
            )

            if execution["success"]:

                direct_result = str(
                    execution["result"]
                )

            else:

                direct_result = (
                    "Tool execution failed: "
                    + str(execution["error"])
                )

        except Exception as e:

            direct_result = (
                "Tool execution failed: "
                + str(e)
            )

    # -----------------------------------------------------
    # TIME TOOL
    # -----------------------------------------------------

    elif is_time_request(user_input):

        try:

            result = get_current_time()
            direct_result = str(result)

        except Exception as e:

            direct_result = (
                "Tool execution failed: "
                + str(e)
            )

    # -----------------------------------------------------
    # WORD COUNTER
    # -----------------------------------------------------

    elif is_word_count_request(user_input):

        try:

            result = count_words(user_input)
            direct_result = str(result)

        except Exception as e:

            direct_result = (
                "Tool execution failed: "
                + str(e)
            )

    # -----------------------------------------------------
    # LLM FALLBACK
    # -----------------------------------------------------

    if direct_result is not None:

        reply = direct_result

    else:

        try:

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Relevant previous conversation:\n"
                            + "\n".join(
                                [
                                    f"{m.get('role', 'unknown')}: "
                                    f"{m.get('content', '')}"
                                    for m in retrieve_conversation_memory(
                                        user_input,
                                        limit=5
                                    )
                                    if m.get("role") in ["user", "assistant"]
                                ]
                            )
                            + "\n\nCurrent user request:\n"
                            + user_input
                        )
                    }
                ]
            )

            reply = (
                response.message.content.strip()
            )

        except Exception as e:

            reply = (
                "I encountered an error "
                "while processing the request: "
                + str(e)
            )

    # =====================================================
    # STEP 4 — EVALUATE + LEARN
    # =====================================================

    evaluation = evaluate_and_learn(

        user_input,

        reply
    )


    # =====================================================
    # STEP 5 — REFLECTION
    # =====================================================

    if evaluation[
        "success"
    ] == "NO":

        try:

            reflection = (
                reflect_and_improve(
                    user_input,
                    reply,
                    evaluation[
                        "lesson"
                    ]
                )
            )


            if reflection_is_safe(
                reply,
                reflection
            ):

                print(
                    "\n🪞 REFLECTION:"
                )

                print(
                    reflection
                )


        except Exception as e:

            print(
                f"⚠️ Reflection failed: {e}"
            )


    # =====================================================
    # STEP 6 — SAVE
    # =====================================================

    save_conversation(

        user_input,

        reply
    )


    return reply


# =========================================================
# INTERACTIVE MODE
# =========================================================

def main():

    print(
        "=" * 60
    )

    print(
        "SELF-LEARNING AI AGENT"
    )

    print(
        "=" * 60
    )

    print(
        "\nType 'exit' to stop."
    )


    while True:

        try:

            user_input = input(
                "\nYou: "
            ).strip()


        except (
            KeyboardInterrupt,
            EOFError
        ):

            print(
                "\n\nAgent stopped."
            )

            break


        if user_input.lower() == "exit":

            print(
                "\nAgent stopped."
            )

            break


        if not user_input:

            continue


        try:

            response = run_agent(
                user_input
            )

            print(
                "\nAgent:",
                response
            )


        except Exception as e:

            print(
                "\n❌ Agent error:",
                e
            )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()








