
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


def generate_id():
    return str(uuid.uuid4())


def current_timestamp():
    return datetime.now().isoformat()


@dataclass
class Conversation:
    title: str = "New Conversation"
    conversation_id: str = field(default_factory=generate_id)
    created_at: str = field(default_factory=current_timestamp)
    updated_at: str = field(default_factory=current_timestamp)
    is_active: bool = True

    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active
        }


@dataclass
class Message:
    role: str
    content: str
    conversation_id: str
    message_id: str = field(default_factory=generate_id)
    timestamp: str = field(default_factory=current_timestamp)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):

        if self.role not in ("user", "assistant", "system", "tool"):
            raise ValueError("Invalid message role")

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class Memory:
    content: str
    category: str = "general"
    memory_id: str = field(default_factory=generate_id)
    created_at: str = field(default_factory=current_timestamp)
    updated_at: str = field(default_factory=current_timestamp)
    importance: int = 1

    def __post_init__(self):

        if not 1 <= self.importance <= 5:
            raise ValueError("Importance must be between 1 and 5")

    def to_dict(self):
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "importance": self.importance
        }


@dataclass
class Reminder:
    title: str
    scheduled_at: str
    reminder_id: str = field(default_factory=generate_id)
    description: str = ""
    created_at: str = field(default_factory=current_timestamp)
    completed: bool = False

    def to_dict(self):
        return {
            "reminder_id": self.reminder_id,
            "title": self.title,
            "description": self.description,
            "scheduled_at": self.scheduled_at,
            "created_at": self.created_at,
            "completed": self.completed
        }


@dataclass
class UserSettings:
    user_id: str = "default_user"
    language: str = "Auto Detect"
    response_style: str = "Balanced"
    voice_enabled: bool = True
    auto_speak: bool = True
    memory_enabled: bool = True
    notifications_enabled: bool = True
    updated_at: str = field(default_factory=current_timestamp)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "language": self.language,
            "response_style": self.response_style,
            "voice_enabled": self.voice_enabled,
            "auto_speak": self.auto_speak,
            "memory_enabled": self.memory_enabled,
            "notifications_enabled": self.notifications_enabled,
            "updated_at": self.updated_at
        }
