from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement
from alpha_mini_rug.speech_to_text import SpeechToText


# Audio configurations:



@inlineCallbacks
def STT(audio_processor):
    """
    Wait until SpeechToText has a new final utterance and return it.
    """
    while True:
        audio_processor.loop() 
        
        if audio_processor.new_words:
            text = " ".join(map(str, audio_processor.words)).strip().lower()
            audio_processor.words = []
            audio_processor.new_words = False
            return text
        
        yield sleep(0.05)


@inlineCallbacks
def TTS_2(session, text, audio_processor):
    """
    Unsubscribes from STT here. 
    The robot produces speech without listening to itself.
    """
    audio_processor.do_speech_recognition = False 
    yield session.call("rie.dialogue.say", text=text) 
    num = len(text)
    yield sleep(num/200)
    audio_processor.do_speech_recognition = True
