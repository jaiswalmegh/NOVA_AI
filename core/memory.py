
import json
from datetime import datetime
from pathlib import Path

from config.settings import MEMORY_DIR


class MemoryManager:

    def __init__(self):
        self.memory_file = Path(MEMORY_DIR) / "nova_memory.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memories = self._load_memories()

    def _load_memories(self):
        if not self.memory_file.exists():
            return []

        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            return []

    def _save_memories(self):
        try:
            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump(
                    self.memories,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except OSError as error:
            print(f"Memory Save Error: {error}")
            return False

    def remember(self, information, category="general"):
        if not isinstance(information, str) or not information.strip():
            return False

        memory = {
            "id": len(self.memories) + 1,
            "information": information.strip(),
            "category": category,
            "created_at": datetime.now().isoformat()
        }

        self.memories.append(memory)

        if self._save_memories():
            return True

        self.memories.pop()
        return False

    def get_all_memories(self):
        return self.recall()

    def recall(self, category=None):
        if category is None:
            return self.memories.copy()

        return [
            memory for memory in self.memories
            if memory.get("category") == category
        ]

    def forget(self, memory_id):
        for index, memory in enumerate(self.memories):
            if memory.get("id") == memory_id:
                deleted = self.memories.pop(index)

                if self._save_memories():
                    return True

                self.memories.insert(index, deleted)
                return False

        return False

    def clear_all(self):
        previous_memories = self.memories.copy()
        self.memories = []

        if self._save_memories():
            return True

        self.memories = previous_memories
        return False
