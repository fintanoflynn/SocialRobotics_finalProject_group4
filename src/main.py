from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText

import movements
import audio_config
import guesser
import director
import camera_vision

audio_processor = SpeechToText()
audio_processor.silence_time = int(1.2)
audio_processor.silence_threshold2 = 10
audio_processor.logging = False

role = None # Director or Guesser
time_limit = 50000 # A way to end the game (for testing it was set to 8 seconds)

@inlineCallbacks
def leave_program(session):
    """
    Function to leave the program.
    """
    yield session.call("rom.sensor.hearing.close")
    session.leave()

@inlineCallbacks
def main(session, wamp):
    """
    Plays game WOW with user.
    """
    global role

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    yield sleep(1)

    yield session.call("rom.sensor.hearing.sensitivity", 1650) 
    yield session.call("rie.dialogue.config.language", lang="en")
    
    print('Listening now')
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream") 
    yield session.call("rom.sensor.hearing.stream")
    
    yield camera_vision.find_face(session, active=True)

    yield movements.wave_right_arm(session)

    yield movements.breathing(session)
    yield audio_config.TTS(session, "Let's play With Other Words. Do you know the game or would you like to hear the rules?", audio_processor)
    
    yield movements.pause_movement(session)
    yield session.call("rom.sensor.hearing.stream") 
    response = ""
    user = yield audio_config.speak_then_capture(
        session,
        audio_processor,
        "Say yes if you want the rules.",
        response=response,
        grace_period=1.0,
        timeout=8
    )

    if "yes" in user:
        yield movements.nod_head(session)
        yield sleep(5)
        yield movements.one_hand_raise(session)

        yield audio_config.TTS(session, "This game has two roles, a Director and a Guesser.", audio_processor)
    
        yield movements.turn_head(session)
        yield audio_config.TTS(session, """
                                            The Director chooses a word and describes it without saying the word itself.
                                            The Guesser tries to figure out the word from the description.
                                        """, audio_processor)
        yield movements.turn_head_back(session) 
        yield audio_config.TTS(session, """
                                            If the Guesser makes a correct guess and the Director 
                                            confirms it by saying "correct", the Guesser wins. The Guesser 
                                            has 3 minutes to guess the word.
                                        """, audio_processor)
           

    yield movements.breathing(session)
    audio_config.clear_audio_state(audio_processor)
    user = yield audio_config.speak_then_capture(
        session,
        audio_processor,
        """
                            Let's start the game and if you want to leave the game say exit. 
                            Would you like to be the director or the guesser?
                        """,
        response=response,
        grace_period=1.0,
        timeout=8
    )

    while True:
        if "exit" in user:
            yield movements.shake_head(session)
            yield movements.wave_right_arm(session)
            yield audio_config.TTS(session, "Ok, I will leave you then.", audio_processor)
            yield leave_program(session)
        if "director" in user: 
            role = "guesser"
            audio_config.clear_audio_state(audio_processor)
            yield guesser.guesser_role(session, audio_processor)
            role = None
        elif "guesser" in user or "guess" in user: 
            role = "director"
            audio_config.clear_audio_state(audio_processor)
            yield director.director_role(session, audio_processor)
            role = None

        audio_config.clear_audio_state(audio_processor)
        yield movements.breathing(session)
        user = yield audio_config.speak_then_capture(
        session,
        audio_processor,
        "Say director or guesser to choose your role or you can say exit to leave the game. ",
        response=response,
        grace_period=1.0,
        timeout=8
    )


wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.69b3e01c9a57f4e5d77b11d9"
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])