from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import time
import movements


def clear_audio_state(audio_processor):
    """
    Clears any leftover speech detected.
    """
    audio_processor.words = []
    audio_processor.new_words = False


@inlineCallbacks
def finalize_pending_speech(audio_processor, grace_period=1.0):
    """
    Processes speech that was during robots speech.
    """
    start = time.time()
    while time.time() - start < grace_period:
        audio_processor.loop()
        if audio_processor.new_words:
            return
        yield sleep(0.05)


@inlineCallbacks
def STT(audio_processor, response, session, timeout=None):
    """
    Processes speech to text. And removes the robots intended speech from the text. 
    """
    start = time.time()

    while True:
        audio_processor.loop()

        if audio_processor.new_words:
            text = " ".join(map(str, audio_processor.words)).strip().lower()

            if response and response in text:
                text = text.replace(response, "").strip()

            clear_audio_state(audio_processor)

            if text:
                yield movements.nod_head(session)
                print(text)
                return text

        if timeout is not None and (time.time() - start) > timeout:
            return ""

        yield sleep(0.05)


@inlineCallbacks
def TTS(session, text, audio_processor):
    """
    Converts text to speech.
    """
    yield session.call("rie.dialogue.say", text=text)


@inlineCallbacks
def speak_then_capture(session, audio_processor, text, response="", grace_period=1.0, timeout=5):
    """
    Processes speech and user utterance in the correct order. 
    """
    yield TTS(session, text, audio_processor)

    # Let speech said during robot speech finalize
    yield finalize_pending_speech(audio_processor, grace_period=grace_period)

    # If something is already ready, process the speech now
    if audio_processor.new_words:
        user = yield STT(audio_processor, response, session, timeout=0.1)
        return user

    # Otherwise keep listening normally
    user = yield STT(audio_processor, response, session, timeout=timeout)
    return user