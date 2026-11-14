
import sqlite3
import json

from pathlib import Path
from contextlib import contextmanager

from config.settings import DATA_DIR


class DatabaseManager:

    def __init__(self, database_name="nova.db"):

        self.database_path = Path(DATA_DIR) / database_name

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.initialize_database()

    @contextmanager
    def get_connection(self):

        connection = sqlite3.connect(
            self.database_path,
            timeout=10
        )

        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def initialize_database(self):

        with self.get_connection() as connection:

            cursor = connection.cursor()

            # Conversations

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Messages

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(conversation_id)
                        ON DELETE CASCADE
                )
            """)

            # Memories

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    importance INTEGER DEFAULT 1
                )
            """)

            # Reminders

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    reminder_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    scheduled_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed INTEGER DEFAULT 0
                )
            """)

            # User Settings

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id TEXT PRIMARY KEY,
                    settings_data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_category
                ON memories(category)
            """)

    # CONVERSATIONS

    def save_conversation(self, conversation):

        data = conversation.to_dict()

        with self.get_connection() as connection:

            connection.execute("""
                INSERT OR REPLACE INTO conversations
                (conversation_id, title, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data["conversation_id"],
                data["title"],
                data["created_at"],
                data["updated_at"],
                int(data["is_active"])
            ))

        return True

    def get_conversations(self):

        with self.get_connection() as connection:

            rows = connection.execute("""
                SELECT * FROM conversations
                ORDER BY updated_at DESC
            """).fetchall()

            return [dict(row) for row in rows]

    def delete_conversation(self, conversation_id):

        with self.get_connection() as connection:

            connection.execute("PRAGMA foreign_keys = ON")

            connection.execute("""
                DELETE FROM conversations
                WHERE conversation_id = ?
            """, (conversation_id,))

        return True

    # MESSAGES

    def save_message(self, message):

        data = message.to_dict()

        with self.get_connection() as connection:

            connection.execute("""
                INSERT OR REPLACE INTO messages
                (message_id, conversation_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["message_id"],
                data["conversation_id"],
                data["role"],
                data["content"],
                data["timestamp"],
                json.dumps(data["metadata"])
            ))

            connection.execute("""
                UPDATE conversations
                SET updated_at = ?
                WHERE conversation_id = ?
            """, (
                data["timestamp"],
                data["conversation_id"]
            ))

        return True

    def get_messages(self, conversation_id):

        with self.get_connection() as connection:

            rows = connection.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,)).fetchall()

            results = []

            for row in rows:

                item = dict(row)

                try:
                    item["metadata"] = json.loads(
                        item["metadata"]
                    )
                except (json.JSONDecodeError, TypeError):
                    item["metadata"] = {}

                results.append(item)

            return results

    # MEMORIES

    def save_memory(self, memory):

        data = memory.to_dict()

        with self.get_connection() as connection:

            connection.execute("""
                INSERT OR REPLACE INTO memories
                (memory_id, content, category, created_at, updated_at, importance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["memory_id"],
                data["content"],
                data["category"],
                data["created_at"],
                data["updated_at"],
                data["importance"]
            ))

        return True

    def get_memories(self, category=None):

        with self.get_connection() as connection:

            if category:

                rows = connection.execute("""
                    SELECT * FROM memories
                    WHERE category = ?
                    ORDER BY importance DESC, updated_at DESC
                """, (category,)).fetchall()

            else:

                rows = connection.execute("""
                    SELECT * FROM memories
                    ORDER BY importance DESC, updated_at DESC
                """).fetchall()

            return [dict(row) for row in rows]

    def delete_memory(self, memory_id):

        with self.get_connection() as connection:

            connection.execute("""
                DELETE FROM memories
                WHERE memory_id = ?
            """, (memory_id,))

        return True

    # REMINDERS

    def save_reminder(self, reminder):

        data = reminder.to_dict()

        with self.get_connection() as connection:

            connection.execute("""
                INSERT OR REPLACE INTO reminders
                (reminder_id, title, description, scheduled_at, created_at, completed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["reminder_id"],
                data["title"],
                data["description"],
                data["scheduled_at"],
                data["created_at"],
                int(data["completed"])
            ))

        return True

    def get_reminders(self, pending_only=False):

        with self.get_connection() as connection:

            if pending_only:

                rows = connection.execute("""
                    SELECT * FROM reminders
                    WHERE completed = 0
                    ORDER BY scheduled_at ASC
                """).fetchall()

            else:

                rows = connection.execute("""
                    SELECT * FROM reminders
                    ORDER BY scheduled_at ASC
                """).fetchall()

            return [dict(row) for row in rows]

    def complete_reminder(self, reminder_id):

        with self.get_connection() as connection:

            cursor = connection.execute("""
                UPDATE reminders
                SET completed = 1
                WHERE reminder_id = ?
            """, (reminder_id,))

            return cursor.rowcount > 0

    # USER SETTINGS

    def save_user_settings(self, settings):

        data = settings.to_dict()

        user_id = data.pop("user_id")
        updated_at = data.pop("updated_at")

        with self.get_connection() as connection:

            connection.execute("""
                INSERT OR REPLACE INTO user_settings
                (user_id, settings_data, updated_at)
                VALUES (?, ?, ?)
            """, (
                user_id,
                json.dumps(data),
                updated_at
            ))

        return True

    def get_user_settings(self, user_id="default_user"):

        with self.get_connection() as connection:

            row = connection.execute("""
                SELECT settings_data
                FROM user_settings
                WHERE user_id = ?
            """, (user_id,)).fetchone()

            if row is None:
                return {}

            try:
                return json.loads(row["settings_data"])
            except (json.JSONDecodeError, TypeError):
                return {}

    def get_database_path(self):

        return str(self.database_path)
