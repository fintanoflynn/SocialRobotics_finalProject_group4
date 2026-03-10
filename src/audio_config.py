# from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug.speech_to_text import SpeechToText


@inlineCallbacks
def STT(audio_processor):
    """
    Wait until SpeechToText has a new final utterance and return it.
    """

    while True:
        audio_processor.loop() 
        
        if audio_processor.new_words:
            print("listening")
            text = " ".join(map(str, audio_processor.words)).strip().lower()
            audio_processor.words = []
            audio_processor.new_words = False
            return text
        
        yield sleep(0.05)
        

@inlineCallbacks
def TTS(session, text, audio_processor):
    """
    Unsubscribes from STT here. 
    The robot produces speech without listening to itself.
    """
    
    audio_processor.do_speech = False
    yield session.call("rie.dialogue.say", text=text) 
    audio_processor.do_speech = True

