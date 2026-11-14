
from datetime import datetime
import uuid


class ConversationManager:
    def __init__(self, max_messages=30):
        self.messages = []
        self.max_messages = max_messages
        self.conversation_id = None
        self.create_conversation()

    def create_conversation(self):
        self.conversation_id = str(uuid.uuid4())
        self.messages.clear()
        return self.conversation_id

    def add_message(self, role, content):
        if role not in ("user", "assistant", "system"):
            raise ValueError("Invalid conversation role.")

        if not isinstance(content, str) or not content.strip():
            return False

        self.messages.append({
            "role": role,
            "content": content.strip(),
            "timestamp": datetime.now().isoformat(),
        })

        self._trim_history()
        return True

    def _trim_history(self):
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_history(self):
        return [
            {"role": message["role"], "content": message["content"]}
            for message in self.messages
        ]

    def clear_history(self):
        self.messages.clear()

    def clear(self):
        self.clear_history()

    def get_message_count(self):
        return len(self.messages)
