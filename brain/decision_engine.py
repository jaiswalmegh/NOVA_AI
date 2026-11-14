
class DecisionEngine:

    def __init__(self):

        self.available_actions = {
            "conversation",
            "tool_execution",
            "clarification",
            "confirmation",
            "unsupported"
        }

    def make_decision(self, intent_data):

        if not isinstance(intent_data, dict):
            return self._decision(
                "clarification",
                "Invalid intent information."
            )

        intent = intent_data.get("intent", "unknown")
        confidence = intent_data.get("confidence", 0.0)

        if not isinstance(confidence, (int, float)):
            confidence = 0.0

        if intent == "unknown" or confidence < 0.3:
            return self._decision(
                "clarification",
                "I need more information to understand your request."
            )

        if intent == "general_conversation":
            return self._decision(
                "conversation",
                "Send the request to the AI engine."
            )

        if intent in ("greeting", "question"):
            return self._decision(
                "conversation",
                "Generate a conversational AI response."
            )

        if intent in ("system_action", "file_action"):
            return self._decision(
                "confirmation",
                "Check the requested action and its safety before execution."
            )

        if intent in ("productivity", "information"):
            return self._decision(
                "tool_execution",
                "Find an appropriate registered tool for the request."
            )

        return self._decision(
            "conversation",
            "Handle the request through the AI engine."
        )

    def _decision(self, action, reason):

        return {
            "action": action,
            "reason": reason
        }

    def is_action_supported(self, action):

        return action in self.available_actions
