from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText

import movements
import audio_config
import guesser
import director
import camera_vision
import cv2
import numpy as np
audio_processor = SpeechToText()
audio_processor.silence_time = int(0.5)
audio_processor.silence_threshold2 = 40
audio_processor.logging = False

role = None # Director or Guesser
time_limit = 50000 # A way to end the game (for testing it was set to 8 seconds)
rules = """
This game has two roles, a Director and a Guesser. The Director chooses a word and describes it 
without saying the word itself. The Guesser tries to figure out the word from the description. If the 
Guesser makes a correct guess and the Director confirms it by saying "correct", the Guesser wins. 
The Guesser has 3 minutes to guess the word.
"""

@inlineCallbacks
def leave_program(session):
    """
    Function to leave the program.
    """
    yield session.call("rom.sensor.hearing.close")
    session.leave()

# Callback function to handle incoming camera frames
def on_camera_frame(frame):
    """
    Callback function to process and display the camera frames.

    Args:
        frame: The frame data received from the robot's camera stream.
    """
    try:
        # Assuming the frame is received as a byte array
        np_frame = np.frombuffer(frame, dtype=np.uint8)
        image = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

        # Display the frame using OpenCV
        if image is not None:
            cv2.imshow("Robot Camera Feed", image)
        else:
            print("Failed to decode the camera frame.")

        # Close the window when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    except Exception as e:
        print("Error processing camera frame:", e)

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
    
    # Subscribe to the camera stream
    print("Subscribing to the camera stream...")
    yield session.subscribe(on_camera_frame, "rie.vision.face.stream")
    yield session.call("rie.vision.face.stream")

    # Call the find_face function here
    print("Looking for a face...")
    face_found = yield camera_vision.find_face(session, active=True)
    if face_found:
        print("Face detected!")
        yield audio_config.TTS(session, "I see you!")
    else:
        print("No face detected.")
        yield audio_config.TTS(session, "I can't see anyone.")


    yield movements.wave_right_arm(session)

    yield audio_config.TTS(session, """
                            Let's play With Other Words. Do you know the game or would you like to
                            hear the rules?
                        """)
    yield movements.pause_movement(session)
    yield audio_config.TTS(session, "Say yes if you want the rules.")
    yield session.call("rom.sensor.hearing.stream") 
    response = ""
    user = yield audio_config.STT(audio_processor, response)

    if "yes" in user:
        yield movements.nod_head(session)
        yield sleep(5)
        yield movements.one_hand_raise(session)

        yield audio_config.TTS(session, "This game has two roles, a Director and a Guesser.")
    
        yield movements.turn_head(session)
        yield audio_config.TTS(session, """
                                            The Director chooses a word and describes it without saying the word itself.
                                            The Guesser tries to figure out the word from the description.
                                        """)
        yield movements.turn_head_back(session) 
        yield audio_config.TTS(session, """
                                            If the Guesser makes a correct guess and the Director 
                                            confirms it by saying "correct", the Guesser wins. The Guesser 
                                            has 3 minutes to guess the word.
                                        """)
           

    yield movements.breathing(session)
    yield audio_config.TTS(session, """
                            Let's start the game and if you want to leave the game say exit. 
                            Would you like to be the director or the guesser?
                        """)

    while True:
        user = yield audio_config.STT(audio_processor, response)
        if "exit" in user:
            yield movements.shake_head(session)
            yield movements.wave_right_arm(session)
            yield audio_config.TTS(session, "Ok, I will leave you then.")
            yield leave_program(session)
        if "director" in user: 
            role = "guesser"
            yield guesser.guesser_role(session, audio_processor)
            role = None
        elif "guesser" in user: 
            role = "director"
            yield director.director_role(session, audio_processor)
            role = None

        yield movements.breathing(session)
        yield audio_config.TTS(session, "Say director or guesser to choose your role or you can say exit to leave the game. ")
        yield sleep(0.05) 


wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.69b3e3009a57f4e5d77b11ed"
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])