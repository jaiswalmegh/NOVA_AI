
import speech_recognition as sr


class WakeWordDetector:

    def __init__(self, wake_words=None):

        self.wake_words = wake_words or [
            "hey nova",
            "hello nova",
            "okay nova",
            "nova"
        ]

        self.recognizer = sr.Recognizer()
        self.is_active = False

    def detect(self, audio):

        try:

            text = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            ).lower().strip()

            for wake_word in self.wake_words:

                if wake_word in text:

                    return {
                        "detected": True,
                        "wake_word": wake_word,
                        "recognized_text": text
                    }

            return {
                "detected": False,
                "wake_word": None,
                "recognized_text": text
            }

        except sr.UnknownValueError:

            return {
                "detected": False,
                "wake_word": None,
                "recognized_text": ""
            }

        except sr.RequestError:

            return {
                "detected": False,
                "wake_word": None,
                "recognized_text": "",
                "error": "Speech recognition service unavailable."
            }

    def set_active(self, status):

        self.is_active = bool(status)

    def add_wake_word(self, word):

        if not isinstance(word, str) or not word.strip():
            return False

        word = word.strip().lower()

        if word not in self.wake_words:
            self.wake_words.append(word)

        return True

    def remove_wake_word(self, word):

        word = word.strip().lower()

        if word in self.wake_words:
            self.wake_words.remove(word)
            return True

        return False

    def get_wake_words(self):

        return self.wake_words.copy()
