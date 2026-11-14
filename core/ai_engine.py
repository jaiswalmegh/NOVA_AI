
import json

from groq import Groq

from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    USER_NAME,
    ASSISTANT_NAME
)


class AIEngine:

    MAX_TOOL_ROUNDS = 5
    MAX_HISTORY_MESSAGES = 30
    MAX_COMPLETION_TOKENS = 2048

    def __init__(self):

        self.client = (
            Groq(api_key=GROQ_API_KEY)
            if GROQ_API_KEY
            else None
        )

        self.conversation_history = []

        self.system_prompt = f"""
You are {ASSISTANT_NAME}, an intelligent personal desktop AI assistant.

The user's name is {USER_NAME}.

IDENTITY AND COMMUNICATION:
- Understand Hindi, English and Hinglish.
- Respond naturally in the language used by the user.
- Be helpful, intelligent, accurate and conversational.
- Keep responses clear and appropriately concise.
- Maintain context from previous messages.

TOOL USAGE:
- - You have access to tools for calculations, web searches, weather, Wikipedia, news and reminders.
- Decide when a tool is genuinely needed.
- Use tools instead of guessing when a tool can provide the required information.
- You may call multiple tools when necessary.
- Never invent tool results.
- Never claim a tool action succeeded unless its result confirms success.
- If a tool fails, explain the failure honestly.

SAFETY:
- Never execute actions that are not provided through registered tools.
- Never claim to access files, applications or system resources without a connected tool.
- Ask for confirmation before destructive or sensitive actions.
- Never reveal API keys, passwords or private configuration.

You are NOVA, the user's intelligent desktop companion.
""".strip()

    # -----------------------------------------
    # INITIALIZATION
    # -----------------------------------------

    def initialize(self):

        return self.is_configured()

    def is_configured(self):

        return bool(
            self.client
            and GROQ_MODEL
        )

    # -----------------------------------------
    # CONVERSATION MANAGEMENT
    # -----------------------------------------

    def reset_conversation(self):

        self.conversation_history.clear()

    def _prepare_messages(
        self,
        user_message,
        system_prompt=None,
        conversation_history=None
    ):

        history = (
            conversation_history
            if conversation_history is not None
            else self.conversation_history
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt or self.system_prompt
            }
        ]

        if isinstance(history, list):

            messages.extend(
                history[-self.MAX_HISTORY_MESSAGES:]
            )

        # Avoid duplicating the latest user message.
        if (
            not messages
            or messages[-1].get("role") != "user"
            or messages[-1].get("content") != user_message
        ):

            messages.append({
                "role": "user",
                "content": user_message
            })

        return messages

    # -----------------------------------------
    # TOOL SCHEMA CONVERSION
    # -----------------------------------------

    def _prepare_tools(self, tool_registry):

        if tool_registry is None:
            return []

        registered_tools = tool_registry.get_all_tools()

        groq_tools = []

        for tool in registered_tools:

            name = tool.get("name")
            description = tool.get("description", "")
            parameters = tool.get("parameters", {})

            if not name:
                continue

            groq_tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            })

        return groq_tools

    # -----------------------------------------
    # TOOL RESULT FORMATTING
    # -----------------------------------------

    def _format_tool_result(self, result):

        try:

            return json.dumps(
                result,
                ensure_ascii=False,
                default=str
            )

        except Exception:

            return json.dumps({
                "success": False,
                "message": "Tool result could not be serialized."
            })

    # -----------------------------------------
    # TOOL EXECUTION
    # -----------------------------------------

    def _execute_tool_call(
        self,
        tool_call,
        tool_registry
    ):

        function_data = tool_call.function

        tool_name = function_data.name

        try:

            arguments = json.loads(
                function_data.arguments or "{}"
            )

            if not isinstance(arguments, dict):
                raise ValueError(
                    "Tool arguments must be a JSON object."
                )

        except (json.JSONDecodeError, ValueError) as error:

            return {
                "success": False,
                "message": f"Invalid tool arguments: {error}",
                "result": None
            }

        if tool_registry is None:

            return {
                "success": False,
                "message": "Tool registry is unavailable.",
                "result": None
            }

        result = tool_registry.execute_tool(
            tool_name,
            arguments
        )

        return result

    # -----------------------------------------
    # NORMAL AI RESPONSE
    # -----------------------------------------

    def generate_response(
        self,
        user_message,
        system_prompt=None,
        conversation_history=None
    ):

        if (
            not isinstance(user_message, str)
            or not user_message.strip()
        ):
            return "Please enter a message."

        if not self.is_configured():

            return (
                "NOVA's AI connection is not configured. "
                "Please check GROQ_API_KEY and GROQ_MODEL "
                "in your local .env file."
            )

        user_message = user_message.strip()

        messages = self._prepare_messages(
            user_message,
            system_prompt,
            conversation_history
        )

        try:

            completion = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=self.MAX_COMPLETION_TOKENS
            )

            response = completion.choices[0].message.content

            return (
                response.strip()
                if response
                else "I couldn't generate a response."
            )

        except Exception as error:

            print(f"Groq API Error: {error}")

            return (
                "I'm having trouble connecting to my AI engine. "
                "Please check your internet connection, API key "
                "and model configuration."
            )

    # -----------------------------------------
    # AI-DRIVEN TOOL CALLING
    # -----------------------------------------

    def generate_response_with_tools(
        self,
        user_message,
        system_prompt=None,
        conversation_history=None,
        tool_registry=None
    ):

        if (
            not isinstance(user_message, str)
            or not user_message.strip()
        ):
            return "Please enter a message."

        if not self.is_configured():

            return (
                "NOVA's AI connection is not configured. "
                "Please check your local .env file."
            )

        user_message = user_message.strip()

        messages = self._prepare_messages(
            user_message,
            system_prompt,
            conversation_history
        )

        try:

            groq_tools = self._prepare_tools(
                tool_registry
            )

            # If no tools are registered, use normal chat.
            if not groq_tools:

                return self.generate_response(
                    user_message,
                    system_prompt,
                    conversation_history
                )

            for round_number in range(self.MAX_TOOL_ROUNDS):

                completion = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    tools=groq_tools,
                    tool_choice="auto",
                    temperature=0.7,
                    max_completion_tokens=self.MAX_COMPLETION_TOKENS
                )

                assistant_message = completion.choices[0].message

                tool_calls = assistant_message.tool_calls

                # No tool requested. Return the final AI response.
                if not tool_calls:

                    response = assistant_message.content

                    if response and response.strip():
                        return response.strip()

                    return (
                        "I couldn't generate a response. "
                        "Please try again."
                    )

                # Preserve the assistant's tool-call message.
                messages.append(
                    assistant_message.model_dump(
                        exclude_none=True
                    )
                )

                # Execute every requested tool call.
                for tool_call in tool_calls:

                    tool_result = self._execute_tool_call(
                        tool_call,
                        tool_registry
                    )

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": self._format_tool_result(
                            tool_result
                        )
                    })

            # Stop uncontrolled or endless tool-call loops.
            # Ask the model for a final response without tools.
            final_completion = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=self.MAX_COMPLETION_TOKENS
            )

            final_response = (
                final_completion.choices[0].message.content
            )

            return (
                final_response.strip()
                if final_response
                else "I reached the tool execution limit. Please try again."
            )

        except Exception as error:

            print(f"NOVA Tool Calling Error: {error}")

            return (
                "I encountered a problem while processing your request. "
                "Please check your AI connection and try again."
            )

    # -----------------------------------------
    # CONNECTION STATUS
    # -----------------------------------------

    def get_status(self):

        return {
            "configured": self.is_configured(),
            "provider": "Groq",
            "model": GROQ_MODEL,
            "conversation_messages": len(
                self.conversation_history
            )
        }

    # -----------------------------------------
    # SHUTDOWN
    # -----------------------------------------

    def close(self):

        self.reset_conversation()

        if self.client:

            try:
                self.client.close()
            except Exception as error:
                print(f"Groq Client Shutdown Error: {error}")
