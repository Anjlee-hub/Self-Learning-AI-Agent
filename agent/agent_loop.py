import os
import sys
import re

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# MEMORY
# =========================================================

from memory.semantic_memory import search_semantic_memory
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
from tools.weather_tool import format_weather_response, get_weather


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
from agent.ollama_client import chat_completion, is_llm_available
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
        r"\bwhat time\b",
        r"\btell me the time\b",
        r"\bcurrent time\b",
        r"\bget the time\b",
        r"\bweather\b",
        r"\btemperature\b",
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
        " then ",
        ";"
    ]

    has_conjunction = any(
        item in text
        for item in conjunctions
    )

    return (
        matches >= 2
        and has_conjunction
    )


def is_weather_request(user_input):
    if not user_input:
        return False

    text = user_input.lower().strip()
    if "weather" in text or "temperature" in text or "forecast" in text:
        if re.search(r"\b(?:in|for|at|of)\b", text):
            return True
        if "weather" in text:
            return True
    return False


def extract_weather_location(user_input):
    if not user_input:
        return ""

    text = user_input.strip()
    patterns = [
        r"(?:weather|temperature|forecast)(?:\s+in|\s+for|\s+at|\s+of)?\s+([A-Za-z][A-Za-z\s'-]+?)(?:\?|\.|!|$)",
        r"(?:in|for|at|of)\s+([A-Za-z][A-Za-z\s'-]+?)(?:\?|\.|!|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            if location and location.lower() not in {"the", "today", "tomorrow"}:
                return location

    return ""


def is_learning_summary_request(user_input):
    text = (user_input or "").lower().strip()
    learning_phrases = [
        "what have you learned",
        "what have you learnt",
        "what did you learn",
        "show me what you learned",
        "what lessons have you learned",
        "what lessons have you learnt",
        "what have you learned from previous tasks",
    ]
    return any(phrase in text for phrase in learning_phrases)


def summarize_lessons_from_memory():
    lessons = get_lessons()
    seen = set()
    cleaned = []

    for _, _, _, _, lesson, _ in lessons:
        if not lesson:
            continue
        label = lesson.strip()
        if label.lower() in seen:
            continue
        seen.add(label.lower())
        cleaned.append(label)

    if not cleaned:
        return "I have not learned any reusable lessons yet."

    bullet_list = "\n".join(f"• {lesson}" for lesson in cleaned[:5])
    return (
        "Here are some lessons I have learned from previous tasks:\n\n"
        f"{bullet_list}\n\n"
        "These lessons are stored as reusable experience and can influence future tasks."
    )


def is_calculation_request(user_input):

    if not user_input:
        return False

    text = user_input.lower().strip()

    if any(
        keyword in text
        for keyword in [
            "calculate",
            "compute",
            "multiply",
            "add ",
            "subtract",
            "divide",
            "what is ",
            "what's ",
        ]
    ):
        if re.search(r"-?\d+(?:\.\d+)?\s*(?:\*\*|[\+\-\*\/x%])\s*-?\d+(?:\.\d+)?", text):
            return True
        if "calculate" in text or "compute" in text or "multiply" in text:
            return True

    if re.search(r"-?\d+(?:\.\d+)?\s*(?:\*\*|[\+\-\*\/x%])\s*-?\d+(?:\.\d+)?", text):
        return True

    return False


def is_time_request(user_input):

    text = user_input.lower()

    return (
        "current time" in text
        or "what time" in text
        or "get the time" in text
        or "tell me the time" in text
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

        if "calculate" in step_lower or "multiply" in step_lower or "add" in step_lower or "subtract" in step_lower or "divide" in step_lower:

            answer_lines.append(
                f"{index}. Calculation: {result}"
            )


        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        elif (
            "current time" in step_lower
            or "get the time" in step_lower
            or "what time" in step_lower
        ):

            answer_lines.append(
                f"{index}. Current time: {result}"
            )


        # -------------------------------------------------
        # WEATHER
        # -------------------------------------------------

        elif "weather" in step_lower or "temperature" in step_lower:
            answer_lines.append(
                f"{index}. Weather: {result}"
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
    user_input,
    return_activity=False,
):

    user_input = user_input.strip()
    activity = []

    if not user_input:
        return ("", activity) if return_activity else ""

    activity.append("Received user request")


    if is_learning_summary_request(user_input):
        summary = summarize_lessons_from_memory()
        activity.append("Retrieved stored lessons from the learning memory")
        if return_activity:
            return summary, activity
        return summary

    # =====================================================
    # STEP 1 — RETRIEVE LEARNING
    # =====================================================

    learning_strategy, lessons = (
        get_learning_strategy(
            user_input
        )
    )


    if lessons:
        activity.append("Retrieved relevant learning")
        print(
            "📚 Previous learning found!"
        )

        print(
            f"🔎 Retrieved "
            f"{len(lessons)} similar lesson(s)."
        )

    else:
        activity.append("No relevant learning found")
        print(
            "📚 No previous learning found."
        )


    if learning_strategy:
        activity.append("Applied learned strategy")
        print(
            "\n🧠 LEARNED STRATEGY:"
        )

        print(
            learning_strategy
        )


    if is_weather_request(user_input):
        location = extract_weather_location(user_input)
        activity.append("Detected weather task")
        if location:
            activity.append(f"Resolved location: {location}")
        try:
            weather_result = get_weather(location or user_input)
            if weather_result.get("success"):
                activity.append("Executed Weather tool")
                activity.append("Retrieved live weather data")
                reply = format_weather_response(weather_result)
                save_conversation(user_input, reply)
                if return_activity:
                    return reply, activity
                return reply
            activity.append("Weather tool failed gracefully")
            reply = weather_result.get("error", "Weather information is unavailable.")
            save_conversation(user_input, reply)
            if return_activity:
                return reply, activity
            return reply
        except Exception as error:
            reply = f"Weather tool failed gracefully: {error}"
            activity.append("Weather tool failed gracefully")
            save_conversation(user_input, reply)
            if return_activity:
                return reply, activity
            return reply

    # =====================================================
    # STEP 2 — MULTI-STEP TASK
    # =====================================================

    if is_multi_step_request(
        user_input
    ):

        activity.append("Detected multi-step task")
        activity.append("Created execution plan")
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

        for step in plan_steps:
            if "calculate" in step.lower():
                activity.append("Executed Calculator tool")
            elif "current time" in step.lower() or "what time" in step.lower() or "get the time" in step.lower():
                activity.append("Executed Time tool")
            elif "weather" in step.lower() or "temperature" in step.lower():
                activity.append("Executed Weather tool")
            elif "word" in step.lower():
                activity.append("Executed Word Counter tool")


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
            activity.append("Execution failed")


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


        if return_activity:
            return reply, activity
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

        activity.append("Detected calculation task")

        try:

            execution = execute_tool_step(
                user_input,
                learning_strategy=learning_strategy
            )

            if execution["success"]:
                activity.append("Executed Calculator tool")
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
        activity.append("Detected time task")

        try:

            result = get_current_time()
            activity.append("Executed Time tool")
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
        activity.append("Detected word-count task")

        try:

            result = count_words(user_input)
            activity.append("Executed Word Counter tool")
            direct_result = str(result)

        except Exception as e:

            direct_result = (
                "Tool execution failed: "
                + str(e)
            )

    elif is_weather_request(user_input):
        location = extract_weather_location(user_input)
        activity.append("Detected weather task")
        if location:
            activity.append(f"Resolved location: {location}")
        try:
            weather_result = get_weather(location or user_input)
            if weather_result.get("success"):
                activity.append("Executed Weather tool")
                activity.append("Retrieved live weather data")
                direct_result = format_weather_response(weather_result)
            else:
                direct_result = weather_result.get("error", "Weather information is unavailable.")
        except Exception as error:
            direct_result = f"Weather tool failed gracefully: {error}"

        # -----------------------------------------------------
    # LLM FALLBACK
    # -----------------------------------------------------

    if direct_result is not None:
        activity.append("Evaluated response")
        if "Tool execution failed" not in direct_result:
            activity.append("Stored learning")
        reply = direct_result
        if return_activity:
            return reply, activity
        return reply

    else:

        try:

            # -------------------------------------------------
            # KEYWORD CONVERSATIONAL MEMORY
            # -------------------------------------------------

            keyword_memories = retrieve_conversation_memory(
                user_input,
                limit=5
            )

            # -------------------------------------------------
            # SEMANTIC CONVERSATIONAL MEMORY
            # -------------------------------------------------

            semantic_memories = search_semantic_memory(
                user_input,
                limit=5,
                threshold=0.35
            )

            # -------------------------------------------------
            # COMBINE MEMORY RESULTS
            # -------------------------------------------------

            combined_memories = []

            seen_memory_ids = set()

            # Add semantic memories first because they
            # represent meaning-based matches.

            for memory in semantic_memories:

                memory_id = memory.get("id")

                if memory_id not in seen_memory_ids:

                    combined_memories.append(
                        {
                            "role": memory.get("role"),
                            "content": memory.get("content"),
                            "source": "semantic",
                            "similarity": memory.get("similarity", 0.0)
                        }
                    )

                    seen_memory_ids.add(memory_id)

            # Add keyword memories that were not already
            # retrieved semantically.

            for memory in keyword_memories:

                memory_id = memory.get("id")

                # Older keyword memories may not contain IDs.
                # In that case use role + content as a fallback.

                fallback_id = (
                    memory_id
                    if memory_id is not None
                    else (
                        memory.get("role", "")
                        + "|"
                        + memory.get("content", "")
                    )
                )

                if fallback_id not in seen_memory_ids:

                    combined_memories.append(
                        {
                            "role": memory.get("role"),
                            "content": memory.get("content"),
                            "source": "keyword",
                            "similarity": 0.0
                        }
                    )

                    seen_memory_ids.add(fallback_id)

            # Keep only valid conversation roles.

            valid_memories = [
                memory
                for memory in combined_memories
                if memory.get("role") in ["user", "assistant"]
            ]

            # Limit total context sent to the LLM.

            valid_memories = valid_memories[:8]

            # -------------------------------------------------
            # BUILD MEMORY CONTEXT
            # -------------------------------------------------

            if valid_memories:

                memory_context = "\n".join(
                    [
                        (
                            f"{memory['role']}: "
                            f"{memory['content']}"
                        )
                        for memory in valid_memories
                    ]
                )

            else:

                memory_context = (
                    "No relevant previous conversation found."
                )

            # -------------------------------------------------
            # SEND MEMORY + CURRENT REQUEST TO LLM
            # -------------------------------------------------

            if not is_llm_available():
                reply = (
                    "I cannot reach the configured language model right now. "
                    "Deterministic tools like the calculator, time tool, and word counter remain available."
                )
            else:
                reply = chat_completion(
                    model="llama3.2",
                    messages=[
                        {
                            "role": "user",
                            "content": (
                                "You are a helpful AI agent.\n\n"
                                "Relevant previous conversation "
                                "memory:\n"
                                + memory_context
                                + "\n\n"
                                "Use the previous memory when it is "
                                "relevant to the current request. "
                                "Do not invent information that is "
                                "not supported by the memory.\n\n"
                                "Current user request:\n"
                                + user_input
                            )
                        }
                    ]
                )

                reply = reply.strip()

        except Exception as e:

            reply = (
                "I encountered a temporary LLM error while processing the request. "
                "Deterministic tools such as the calculator, time tool, and word counter can still be used."
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








