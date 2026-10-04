import sqlite3
import os


# =========================================
# DATABASE PATH
# =========================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "instance",
    "finpilot.db"
)


# =========================================
# CHECK DATABASE
# =========================================

if not os.path.exists(DATABASE_PATH):

    raise FileNotFoundError(
        f"Database not found:\n{DATABASE_PATH}"
    )


print(
    "FinPilot database found:"
)

print(
    DATABASE_PATH
)


# =========================================
# CONNECT TO SQLITE
# =========================================

connection = sqlite3.connect(
    DATABASE_PATH
)

cursor = connection.cursor()


# =========================================
# CHECK EXISTING COLUMNS
# =========================================

cursor.execute(
    "PRAGMA table_info(chat_messages)"
)

columns = [
    row[1]
    for row in cursor.fetchall()
]


print(
    "\nExisting columns:"
)

for column in columns:

    print(
        f"  ✓ {column}"
    )


# =========================================
# ADD FEEDBACK COLUMN
# =========================================

if "feedback" not in columns:

    print(
        "\nAdding feedback column..."
    )

    cursor.execute(
        """
        ALTER TABLE chat_messages
        ADD COLUMN feedback VARCHAR(20)
        """
    )

    print(
        "✓ feedback added"
    )

else:

    print(
        "\n✓ feedback already exists"
    )


# =========================================
# ADD FEEDBACK TIME COLUMN
# =========================================

if "feedback_at" not in columns:

    print(
        "\nAdding feedback_at column..."
    )

    cursor.execute(
        """
        ALTER TABLE chat_messages
        ADD COLUMN feedback_at DATETIME
        """
    )

    print(
        "✓ feedback_at added"
    )

else:

    print(
        "\n✓ feedback_at already exists"
    )


# =========================================
# SAVE CHANGES
# =========================================

connection.commit()


# =========================================
# VERIFY MIGRATION
# =========================================

cursor.execute(
    "PRAGMA table_info(chat_messages)"
)

updated_columns = [
    row[1]
    for row in cursor.fetchall()
]


print(
    "\nUpdated chat_messages columns:"
)

for column in updated_columns:

    print(
        f"  ✓ {column}"
    )


# =========================================
# CLOSE DATABASE
# =========================================

connection.close()


print(
    "\n========================================="
)

print(
    "✅ Step 16B migration completed!"
)

print(
    "Existing chat history was preserved."
)

print(
    "========================================="
)