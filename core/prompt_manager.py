
from config.settings import USER_NAME, ASSISTANT_NAME
from services.settings_manager import SettingsManager


class PromptManager:

    def __init__(self, settings_manager=None):

        self.settings_manager = (
            settings_manager or SettingsManager()
        )

        self.custom_instructions = []

    def get_system_prompt(self):

        settings = self.settings_manager.get_all_settings()

        response_style = settings.get(
            "response_style", "Balanced"
        )

        language = settings.get(
            "language", "Auto Detect"
        )

        prompt = f"""
You are {ASSISTANT_NAME}, an intelligent personal desktop AI assistant.

USER PROFILE:
- User name: {USER_NAME}
- You are a personal AI assistant.
- Understand natural language, Hindi, English and Hinglish.
- Maintain context throughout the conversation.

CORE BEHAVIOUR:
- Be helpful, intelligent, accurate and conversational.
- Understand the user's actual intention.
- Ask clarifying questions when necessary.
- Never pretend that an action was completed.
- Never invent tool results.
- Respect user privacy.
- Ask for confirmation before destructive or sensitive actions.

RESPONSE STYLE:
{self._get_style_instruction(response_style)}

LANGUAGE:
{self._get_language_instruction(language)}

CUSTOM INSTRUCTIONS:
{self._get_custom_instructions()}
"""

        return prompt.strip()

    def _get_style_instruction(self, style):

        styles = {
            "Balanced": (
                "Use a natural balance of detail and conciseness. "
                "Explain important points clearly."
            ),

            "Concise": (
                "Prefer short, direct and useful responses. "
                "Avoid unnecessary explanations."
            ),

            "Detailed": (
                "Provide detailed explanations, examples and "
                "step-by-step guidance when useful."
            ),

            "Creative": (
                "Use imaginative, engaging and expressive language "
                "while keeping information accurate."
            )
        }

        return styles.get(style, styles["Balanced"])

    def _get_language_instruction(self, language):

        languages = {
            "Auto Detect": (
                "Detect the language used by the user and respond "
                "naturally in the same language."
            ),

            "English": (
                "Always respond in English unless the user requests "
                "another language."
            ),

            "Hindi": (
                "Respond in natural Hindi."
            ),

            "Hinglish": (
                "Respond in natural conversational Hinglish using "
                "Roman Hindi and English."
            )
        }

        return languages.get(
            language,
            languages["Auto Detect"]
        )

    def _get_custom_instructions(self):

        if not self.custom_instructions:
            return "No additional instructions."

        return "\n".join(
            f"- {instruction}"
            for instruction in self.custom_instructions
        )

    def add_instruction(self, instruction):

        if not isinstance(instruction, str):
            return False

        instruction = instruction.strip()

        if not instruction:
            return False

        self.custom_instructions.append(instruction)
        return True

    def remove_instruction(self, instruction):

        if instruction in self.custom_instructions:
            self.custom_instructions.remove(instruction)
            return True

        return False

    def clear_instructions(self):

        self.custom_instructions.clear()
        return True

    def update_settings_manager(self, settings_manager):

        self.settings_manager = settings_manager
