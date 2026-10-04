import sqlite3

DB_NAME = "memory.db"


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    connection = sqlite3.connect(DB_NAME)

    # -----------------------------------------------------
    # Conversations
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # Lessons
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            agent_response TEXT NOT NULL,
            score INTEGER,
            success TEXT,
            lesson TEXT NOT NULL,
            lesson_type TEXT NOT NULL DEFAULT 'ANSWER_QUALITY'
        )
    """)

    # -----------------------------------------------------
    # DATABASE MIGRATION
    # -----------------------------------------------------

    cursor = connection.execute(
        "PRAGMA table_info(lessons)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "lesson_type" not in columns:

        connection.execute("""
            ALTER TABLE lessons
            ADD COLUMN lesson_type TEXT NOT NULL
            DEFAULT 'ANSWER_QUALITY'
        """)

    connection.commit()

    connection.close()


# =========================================================
# CONVERSATION MEMORY
# =========================================================

def save_message(role, content):

    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        """
        INSERT INTO conversations
        (role, content)
        VALUES (?, ?)
        """,
        (
            role,
            content
        )
    )

    connection.commit()

    connection.close()


def get_messages():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        SELECT role, content
        FROM conversations
        ORDER BY id
        """
    )

    messages = [
        {
            "role": role,
            "content": content
        }
        for role, content in cursor.fetchall()
    ]

    connection.close()

    return messages


# =========================================================
# LESSON MEMORY
# =========================================================

def save_lesson(
    user_input,
    agent_response,
    score,
    success,
    lesson_type,
    lesson
):

    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        """
        INSERT INTO lessons
        (
            user_input,
            agent_response,
            score,
            success,
            lesson_type,
            lesson
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_input,
            agent_response,
            score,
            success,
            lesson_type,
            lesson
        )
    )

    connection.commit()

    connection.close()


# =========================================================
# GET ALL LESSONS
# =========================================================

def get_lessons():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        SELECT
            user_input,
            agent_response,
            score,
            success,
            lesson,
            lesson_type
        FROM lessons
        ORDER BY id
        """
    )

    lessons = cursor.fetchall()

    connection.close()

    return lessons


# =========================================================
# GET RECENT LESSONS
# =========================================================

def get_recent_lessons(limit=5):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        SELECT
            user_input,
            lesson,
            score,
            lesson_type
        FROM lessons
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            limit,
        )
    )

    lessons = cursor.fetchall()

    connection.close()

    return lessons


# =========================================================
# SEARCH LESSONS
# =========================================================

def search_lessons(
    keyword,
    limit=5
):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        SELECT
            user_input,
            agent_response,
            score,
            success,
            lesson,
            lesson_type
        FROM lessons
        WHERE user_input LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            f"%{keyword}%",
            limit
        )
    )

    lessons = cursor.fetchall()

    connection.close()

    return lessons


# =========================================================
# GET LESSONS BY TYPE
# =========================================================

def get_lessons_by_type(
    lesson_type,
    limit=10
):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        SELECT
            user_input,
            agent_response,
            score,
            success,
            lesson,
            lesson_type
        FROM lessons
        WHERE lesson_type = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            lesson_type,
            limit
        )
    )

    lessons = cursor.fetchall()

    connection.close()

    return lessons


# =========================================================
# REPAIR LEGACY LESSON TYPES
# =========================================================

def repair_lesson_types():

    connection = sqlite3.connect(DB_NAME)

    # -----------------------------------------------------
    # TOOL_USAGE
    # -----------------------------------------------------
    # Repair old lessons whose actual text clearly describes
    # selecting or using a tool.
    # -----------------------------------------------------

    connection.execute("""
        UPDATE lessons
        SET lesson_type = 'TOOL_USAGE'
        WHERE
            LOWER(lesson) LIKE '%use the calculator tool%'
            OR LOWER(lesson) LIKE '%use the word counter tool%'
            OR LOWER(lesson) LIKE '%use the current time tool%'
            OR LOWER(lesson) LIKE '%use the time tool%'
    """)

    # -----------------------------------------------------
    # PLANNING
    # -----------------------------------------------------

    connection.execute("""
        UPDATE lessons
        SET lesson_type = 'PLANNING'
        WHERE
            LOWER(lesson) LIKE '%break%multi-step%'
            OR LOWER(lesson) LIKE '%break%task%'
            OR LOWER(lesson) LIKE '%separate%tool%'
            OR LOWER(lesson) LIKE '%order%steps%'
    """)

    # -----------------------------------------------------
    # VERIFICATION
    # -----------------------------------------------------

    connection.execute("""
        UPDATE lessons
        SET lesson_type = 'VERIFICATION'
        WHERE
            LOWER(lesson) LIKE '%verify%tool%'
            OR LOWER(lesson) LIKE '%verify%result%'
            OR LOWER(lesson) LIKE '%check%result%'
            OR LOWER(lesson) LIKE '%validate%result%'
    """)

    # -----------------------------------------------------
    # ERROR RECOVERY
    # -----------------------------------------------------

    connection.execute("""
        UPDATE lessons
        SET lesson_type = 'ERROR_RECOVERY'
        WHERE
            LOWER(lesson) LIKE '%retry%'
            OR LOWER(lesson) LIKE '%recover%'
            OR LOWER(lesson) LIKE '%handle%failure%'
            OR LOWER(lesson) LIKE '%failed operation%'
    """)

    connection.commit()

    connection.close()
# =========================================================
# =========================================================
# SEARCH CONVERSATION MEMORY
# =========================================================

def search_messages(keyword, limit=5):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        SELECT
            role,
            content
        FROM conversations
        WHERE
            content LIKE ?
            AND role IN ('user', 'assistant')
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            f"%{keyword}%",
            limit
        )
    )

    messages = [
        {
            "role": role,
            "content": content
        }
        for role, content in cursor.fetchall()
    ]

    connection.close()

    return messages


