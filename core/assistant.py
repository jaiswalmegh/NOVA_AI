
import threading

from core.ai_engine import AIEngine
from core.conversation import ConversationManager
from core.memory import MemoryManager
from core.prompt_manager import PromptManager
from core.response_handler import ResponseHandler

from config.settings import USER_NAME

from services.settings_manager import SettingsManager
from voice.voice_manager import VoiceManager

from tools.tool_setup import ToolSetup


class NOVAAssistant:

    def __init__(self, settings_manager=None, tool_setup=None):

        self.settings_manager = settings_manager or SettingsManager()

        self.ai_engine = AIEngine()
        self.conversation_manager = ConversationManager()
        self.memory_manager = MemoryManager()

        self.prompt_manager = PromptManager(
            settings_manager=self.settings_manager
        )

        self.response_handler = ResponseHandler()
        self.voice_manager = VoiceManager()

        self.tool_setup = tool_setup or ToolSetup()
        self.tool_registry = self.tool_setup.get_registry()

        self.tools_initialized = False
        self.is_initialized = False
        self.is_shutdown = False

        self.current_conversation_id = (
            self.conversation_manager.conversation_id
        )

        self._lock = threading.RLock()

        self._apply_voice_settings()

    # =========================================
    # VOICE SETTINGS
    # =========================================

    def _apply_voice_settings(self):

        settings = self.settings_manager.get_all_settings()

        if settings.get("voice_enabled", True):
            self.voice_manager.enable()
        else:
            self.voice_manager.disable()

    # =========================================
    # INITIALIZATION
    # =========================================

    def initialize(self):

        with self._lock:

            if self.is_shutdown:
                return {
                    "success": False,
                    "message": "NOVA has already been shut down."
                }

            if self.is_initialized:
                return {
                    "success": True,
                    "message": "NOVA is already initialized.",
                    "tools": {
                        "success": True,
                        "total": self.get_tool_count()
                    }
                }

            try:

                tool_result = self.tool_setup.register_all_tools()

                self.tools_initialized = tool_result.get(
                    "success",
                    False
                )

                if not self.tools_initialized:
                    raise RuntimeError(
                        f"Tool registration failed: "
                        f"{tool_result.get('failed', [])}"
                    )

                configured = self.ai_engine.initialize()

                if not configured:

                    self.is_initialized = False

                    return {
                        "success": False,
                        "message": (
                            "NOVA tools are ready, but the AI connection "
                            "could not be initialized. Check your local "
                            ".env configuration and Groq API key."
                        ),
                        "tools": tool_result
                    }

                self.is_initialized = True

                return {
                    "success": True,
                    "message": f"NOVA is ready, {USER_NAME}!",
                    "tools": tool_result
                }

            except Exception as error:

                print(f"NOVA Initialization Error: {error}")

                self.is_initialized = False

                return {
                    "success": False,
                    "message": str(error)
                }

    # =========================================
    # MEMORY CONTEXT
    # =========================================

    def _build_memory_context(self):

        settings = self.settings_manager.get_all_settings()

        if not settings.get("memory_enabled", True):
            return ""

        try:

            memories = self.memory_manager.get_all_memories()

            if not memories:
                return ""

            memory_lines = []

            for memory in memories[-20:]:

                if isinstance(memory, dict):

                    information = memory.get(
                        "information",
                        memory.get("content", "")
                    )

                    if information:
                        memory_lines.append(str(information))

                elif memory:
                    memory_lines.append(str(memory))

            if not memory_lines:
                return ""

            return (
                "\n\nRelevant saved user memories:\n"
                + "\n".join(memory_lines)
            )

        except Exception as error:

            print(f"NOVA Memory Context Error: {error}")
            return ""

    # =========================================
    # MESSAGE PROCESSING
    # =========================================

    def process_message(self, user_message):

        if not self.is_initialized:
            return "NOVA is not initialized."

        if not isinstance(user_message, str):
            return "Please enter a valid message."

        user_message = user_message.strip()

        if not user_message:
            return "Please enter a message."

        with self._lock:

            if not self.is_initialized or self.is_shutdown:
                return "NOVA is not currently available."

            try:

                self.conversation_manager.add_message(
                    "user",
                    user_message
                )

                system_prompt = (
                    self.prompt_manager.get_system_prompt()
                )

                system_prompt += self._build_memory_context()

                history = (
                    self.conversation_manager.get_history()
                )

                response = (
                    self.ai_engine.generate_response_with_tools(
                        user_message=user_message,
                        system_prompt=system_prompt,
                        conversation_history=history,
                        tool_registry=self.tool_registry
                    )
                )

                response = (
                    self.response_handler.process_response(
                        response
                    )
                )

                self.conversation_manager.add_message(
                    "assistant",
                    response
                )

                # Voice is deliberately NOT started here.
                # The UI displays the response first.

                return response

            except Exception as error:

                print(f"NOVA Assistant Error: {error}")

                return self.response_handler.format_error(error)

    # =========================================
    # VOICE INPUT
    # =========================================

    def listen_for_command(self, language="en-IN"):

        if not self.is_initialized:
            return {
                "success": False,
                "text": "",
                "error": "NOVA is not initialized."
            }

        settings = self.settings_manager.get_all_settings()

        if not settings.get("voice_enabled", True):
            return {
                "success": False,
                "text": "",
                "error": "Voice input is disabled in settings."
            }

        try:

            return self.voice_manager.listen_once(
                language=language
            )

        except Exception as error:

            print(f"NOVA Voice Input Error: {error}")

            return {
                "success": False,
                "text": "",
                "error": "Unable to process voice input."
            }

    # =========================================
    # VOICE OUTPUT
    # =========================================

    def speak_response(self, text):

        settings = self.settings_manager.get_all_settings()

        if not settings.get("voice_enabled", True):
            return False

        if not settings.get("auto_speak", False):
            return False

        if not isinstance(text, str) or not text.strip():
            return False

        if self.is_shutdown:
            return False

        try:

            return self.voice_manager.speak(text)

        except Exception as error:

            print(f"NOVA Voice Output Error: {error}")
            return False

    def stop_speaking(self):

        try:
            return self.voice_manager.stop_speaking()

        except Exception as error:

            print(f"NOVA Stop Speaking Error: {error}")
            return False

    # =========================================
    # CONVERSATION MANAGEMENT
    # =========================================

    def get_conversation_history(self):

        with self._lock:
            return self.conversation_manager.get_history()

    def clear_conversation(self):

        with self._lock:

            if self.is_shutdown:
                return False

            try:

                self.current_conversation_id = (
                    self.conversation_manager.create_conversation()
                )

                self.ai_engine.reset_conversation()

                return True

            except Exception as error:

                print(f"NOVA Conversation Reset Error: {error}")
                return False

    # =========================================
    # MEMORY MANAGEMENT
    # =========================================

    def get_memory(self):
        return self.memory_manager.get_all_memories()

    def remember(self, content, category="general"):

        settings = self.settings_manager.get_all_settings()

        if not settings.get("memory_enabled", True):
            return False

        if not isinstance(content, str) or not content.strip():
            return False

        return self.memory_manager.remember(
            content.strip(),
            category
        )

    def forget(self, memory_id):
        return self.memory_manager.forget(memory_id)

    # =========================================
    # TOOL MANAGEMENT
    # =========================================

    def get_available_tools(self):
        return self.tool_registry.get_all_tools()

    def get_tool_count(self):
        return self.tool_registry.get_tool_count()

    def execute_tool(self, tool_name, arguments):

        if not self.tools_initialized:
            return {
                "success": False,
                "error": "Tools are not initialized."
            }

        if self.is_shutdown:
            return {
                "success": False,
                "error": "NOVA has been shut down."
            }

        return self.tool_registry.execute_tool(
            tool_name,
            arguments
        )

    # =========================================
    # SETTINGS
    # =========================================

    def get_settings(self):
        return self.settings_manager.get_all_settings()

    def update_setting(self, key, value):

        result = self.settings_manager.update_setting(
            key,
            value
        )

        if result and key == "voice_enabled":
            self._apply_voice_settings()

        return result

    # =========================================
    # STATUS
    # =========================================

    def get_status(self):

        return {
            "initialized": self.is_initialized,
            "tools_initialized": self.tools_initialized,
            "tool_count": self.get_tool_count(),
            "voice_enabled": self.settings_manager.get_setting(
                "voice_enabled",
                True
            ),
            "memory_enabled": self.settings_manager.get_setting(
                "memory_enabled",
                True
            ),
            "notifications_enabled": self.settings_manager.get_setting(
                "notifications_enabled",
                True
            ),
            "shutdown": self.is_shutdown
        }

    # =========================================
    # SHUTDOWN
    # =========================================

    def shutdown(self):

        with self._lock:

            if self.is_shutdown:
                return True

            self.is_initialized = False
            self.is_shutdown = True

            shutdown_components = [
                ("Voice", self.voice_manager.close),
                ("AI Engine", self.ai_engine.close),
                ("Tool System", self.tool_setup.shutdown)
            ]

            for component_name, shutdown_method in shutdown_components:

                try:
                    shutdown_method()

                except Exception as error:

                    print(
                        f"NOVA {component_name} Shutdown Error: {error}"
                    )

            return True
