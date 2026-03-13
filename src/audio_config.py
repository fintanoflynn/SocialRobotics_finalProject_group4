from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText

import movements

@inlineCallbacks
def STT(audio_processor, response, session):
    """
    Wait until SpeechToText has a new final utterance and return it.
    """

    while True:
        audio_processor.loop()
        
        if audio_processor.new_words:
            text = " ".join(map(str, audio_processor.words)).strip().lower()
            if response in text:
                text = text.replace(response, "").strip()

            yield movements.nod_head(session)
            audio_processor.words = []
            audio_processor.new_words = False
            print(text)
            return text
        
        yield sleep(0.05)


@inlineCallbacks
def TTS(session, text):
    """
    The robot produces speech without listening to itself.
    """
    yield session.call("rie.dialogue.say", text=text)