
import threading

import speech_recognition as sr

from voice.text_to_speech import TextToSpeech


class VoiceManager:

    def __init__(self):

        self.recognizer = sr.Recognizer()
        self.speaker = TextToSpeech()

        self.is_listening = False
        self.is_enabled = True

        self._lock = threading.Lock()

        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5

    def listen_once(
        self,
        timeout=5,
        phrase_time_limit=12,
        language="en-IN"
    ):
        """
        Listen to one voice command and convert it into text.
        Microphone is accessed only when this method is called.
        """

        if not self.is_enabled:
            return {
                "success": False,
                "text": "",
                "error": "Voice input is disabled."
            }

        if not self._lock.acquire(blocking=False):
            return {
                "success": False,
                "text": "",
                "error": "Voice input is already active."
            }

        try:

            self.is_listening = True

            with sr.Microphone() as source:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.6
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            try:

                recognized_text = self.recognizer.recognize_google(
                    audio,
                    language=language
                )

                return {
                    "success": True,
                    "text": recognized_text.strip(),
                    "error": None
                }

            except sr.UnknownValueError:

                return {
                    "success": False,
                    "text": "",
                    "error": "I couldn't understand that. Please try again."
                }

            except sr.RequestError as error:

                return {
                    "success": False,
                    "text": "",
                    "error": f"Speech recognition service error: {error}"
                }

        except sr.WaitTimeoutError:

            return {
                "success": False,
                "text": "",
                "error": "No speech detected. Please try again."
            }

        except Exception as error:

            return {
                "success": False,
                "text": "",
                "error": str(error)
            }

        finally:

            self.is_listening = False
            self._lock.release()

    def speak(self, text):

        if not self.is_enabled:
            return False

        if not isinstance(text, str) or not text.strip():
            return False

        try:
            self.speaker.speak(text.strip())
            return True

        except Exception as error:
            print(f"NOVA Voice Error: {error}")
            return False

    def stop_speaking(self):

        try:
            self.speaker.stop()
            return True

        except Exception as error:
            print(f"NOVA Voice Stop Error: {error}")
            return False

    def enable(self):
        self.is_enabled = True
        return True

    def disable(self):

        self.is_enabled = False
        self.stop_speaking()

        return True

    def set_rate(self, rate):
        return self.speaker.set_rate(rate)

    def set_volume(self, volume):
        return self.speaker.set_volume(volume)

    def set_voice(self, voice_id):
        return self.speaker.set_voice(voice_id)

    def get_available_voices(self):
        return self.speaker.get_available_voices()

    def close(self):

        self.is_enabled = False
        self.stop_speaking()

        try:
            self.speaker.close()
        except Exception as error:
            print(f"NOVA Voice Shutdown Error: {error}")

        return True
    