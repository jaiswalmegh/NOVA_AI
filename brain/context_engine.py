
from collections import deque


class ContextEngine:

    def __init__(self, max_context_messages=20):

        self.max_context_messages = max_context_messages
        self.context = deque(maxlen=max_context_messages)

    def add_context(self, role, message):

        if role not in ("user", "assistant"):
            return False

        if not isinstance(message, str) or not message.strip():
            return False

        self.context.append({
            "role": role,
            "content": message.strip()
        })

        return True

    def get_context(self):

        return list(self.context)

    def get_recent_context(self, count=5):

        if count <= 0:
            return []

        return list(self.context)[-count:]

    def get_context_for_ai(self):

        return [
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in self.context
        ]

    def clear_context(self):

        self.context.clear()

    def get_context_size(self):

        return len(self.context)

    def search_context(self, keyword):

        if not isinstance(keyword, str) or not keyword.strip():
            return []

        keyword = keyword.lower()

        return [
            item for item in self.context
            if keyword in item["content"].lower()
        ]
    