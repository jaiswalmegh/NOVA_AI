
import re
import threading
import unicodedata
import queue

import pyttsx3


class TextToSpeech:

    def __init__(self, rate=175, volume=1.0, voice_index=1):

        self.rate = max(80, min(300, int(rate)))
        self.volume = max(0.0, min(1.0, float(volume)))
        self.voice_index = int(voice_index)

        self.engine = None
        self.is_initialized = False
        self.is_speaking = False

        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._closed = False

        self._worker = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="NOVA-TTS-Worker"
        )

        self._worker.start()
        self._ready.wait(timeout=10)

    def _initialize_engine(self):

        try:

            self.engine = pyttsx3.init("sapi5")

            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)

            voices = self.engine.getProperty("voices")

            if voices:
                index = max(
                    0,
                    min(self.voice_index, len(voices) - 1)
                )

                self.engine.setProperty(
                    "voice",
                    voices[index].id
                )

            self.is_initialized = True
            return True

        except Exception as error:

            print(f"NOVA TTS Initialization Error: {error}")

            self.engine = None
            self.is_initialized = False

            return False

    def _reinitialize_engine(self):

        try:

            if self.engine:
                self.engine.stop()

        except Exception:
            pass

        self.engine = None
        self.is_initialized = False

        return self._initialize_engine()

    def _worker_loop(self):

        self._initialize_engine()
        self._ready.set()

        if not self.is_initialized:
            return

        while True:

            task = self._queue.get()

            if task is None:
                self._queue.task_done()
                break

            action, value, event, result = task

            try:

                if action == "speak":

                    self.is_speaking = True

                    self.engine.say(value)
                    self.engine.runAndWait()

                    self.is_speaking = False

                    result["value"] = True

                    # Fresh SAPI5 engine for the next speech.
                    if not self._reinitialize_engine():
                        print("NOVA TTS: Engine restart failed.")

                elif action == "stop":

                    self.engine.stop()
                    self.is_speaking = False
                    result["value"] = True

                elif action == "rate":

                    self.rate = value
                    self.engine.setProperty("rate", value)
                    result["value"] = True

                elif action == "volume":

                    self.volume = value
                    self.engine.setProperty("volume", value)
                    result["value"] = True

                elif action == "voice":

                    voices = self.engine.getProperty("voices")

                    if 0 <= value < len(voices):

                        self.engine.setProperty(
                            "voice",
                            voices[value].id
                        )

                        self.voice_index = value
                        result["value"] = True

                    else:
                        result["value"] = False

                elif action == "get_voices":

                    voices = self.engine.getProperty("voices")

                    result["value"] = [
                        {
                            "id": voice.id,
                            "name": voice.name,
                            "index": index
                        }
                        for index, voice in enumerate(voices)
                    ]

                elif action == "close":

                    self.engine.stop()
                    self.is_speaking = False
                    result["value"] = True
                    break

            except Exception as error:

                self.is_speaking = False
                result["value"] = False

                print(f"NOVA TTS Error ({action}): {error}")

                if action == "speak":
                    self._reinitialize_engine()

            finally:

                if event:
                    event.set()

                self._queue.task_done()

        try:
            if self.engine:
                self.engine.stop()
        except Exception:
            pass

        self.engine = None
        self.is_initialized = False

    def _clean_text_for_speech(self, text):

        if not isinstance(text, str):
            return ""

        cleaned = []

        for char in text:

            category = unicodedata.category(char)

            if category in ("So", "Sk", "Cf"):
                continue

            if char in ("\ufe0e", "\ufe0f"):
                continue

            cleaned.append(char)

        text = "".join(cleaned)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)

        return text.strip()

    def _submit(self, action, value=None, wait=True):

        if not self.is_initialized or self._closed:
            return False

        event = threading.Event() if wait else None
        result = {"value": False}

        self._queue.put((action, value, event, result))

        if not wait:
            return True

        if not event.wait(timeout=30):
            return False

        return result["value"]

    def speak(self, text):

        speech_text = self._clean_text_for_speech(text)

        if not speech_text:
            return False

        return self._submit("speak", speech_text, wait=False)

    def stop(self):

        return self._submit("stop")

    def set_rate(self, rate):

        try:
            rate = max(80, min(300, int(rate)))
            return self._submit("rate", rate)
        except Exception as error:
            print(f"NOVA TTS Rate Error: {error}")
            return False

    def set_volume(self, volume):

        try:
            volume = max(0.0, min(1.0, float(volume)))
            return self._submit("volume", volume)
        except Exception as error:
            print(f"NOVA TTS Volume Error: {error}")
            return False

    def set_voice(self, voice_index):

        try:
            return self._submit("voice", int(voice_index))
        except Exception as error:
            print(f"NOVA TTS Voice Error: {error}")
            return False

    def get_available_voices(self):

        result = self._submit("get_voices")

        return result if isinstance(result, list) else []

    def close(self):

        if self._closed:
            return True

        self._closed = True

        if self._worker.is_alive():

            self._queue.put(None)

            if threading.current_thread() != self._worker:
                self._worker.join(timeout=5)

        self.is_initialized = False
        self.is_speaking = False

        return True
