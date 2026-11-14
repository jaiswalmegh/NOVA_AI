
class IntentEngine:

    def __init__(self):

        self.intent_categories = {
            "greeting": [
                "hello", "hi", "hey", "good morning",
                "good evening", "good afternoon"
            ],
            "question": [
                "what", "why", "how", "when",
                "where", "who", "which", "explain"
            ],
            "system_action": [
                "open", "launch", "start", "close",
                "shutdown", "restart"
            ],
            "file_action": [
                "create file", "delete file", "find file",
                "open file", "rename file"
            ],
            "productivity": [
                "remind me", "set reminder", "schedule",
                "timer", "task", "todo"
            ],
            "information": [
                "weather", "news", "search", "calculate",
                "wikipedia"
            ]
        }

    def detect_intent(self, message):

        if not isinstance(message, str) or not message.strip():
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "message": message
            }

        text = message.lower().strip()
        scores = {}

        for intent, keywords in self.intent_categories.items():

            score = sum(
                1 for keyword in keywords
                if keyword in text
            )

            if score:
                scores[intent] = score

        if not scores:
            return {
                "intent": "general_conversation",
                "confidence": 0.5,
                "message": message
            }

        best_intent = max(scores, key=scores.get)

        total_matches = sum(scores.values())
        confidence = scores[best_intent] / total_matches

        return {
            "intent": best_intent,
            "confidence": round(confidence, 2),
            "message": message
        }

    def get_supported_intents(self):

        return list(self.intent_categories.keys())
