from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText
import random 
import time 

import movements
import audio_config
import llm

cards = ["pizza", "bicycle", "football", "basketball", "phone"] 

# chat history:
user_chat = [] 
llm_chat = []
time_limit = 50000 # A way to end the game (for testing it was set to 8 seconds)

@inlineCallbacks
def guesser_role(session, audio_processor):
    """
    This function executes when the role of the robot is the Guesser.
    """    
    chosen_word = random.choice(cards)
    print(chosen_word)
    start_time = time.time() 
    llm_chat = [] 
    yield movements.thinking(session)
    response = llm.generate_llm_response("""   
                                    Play With Other Words with me. Guess the word I am thinking of. 
                                    I will give you a short description of it without saying the
                                    actual words of course. You can ask me questions if you are unsure but
                                    keep them short. You can only make one guess at a time.
                                        """)
    user_chat.append("""   
                                    Play With Other Words with me. Guess the word I am thinking of. 
                                    I will give you a short description of it without saying the
                                    actual words of course. You can ask me questions if you are unsure but
                                    keep them short. You can only make one guess at a time.
                                        """)
    llm_chat.append(response)
    yield sleep(2)
    yield audio_config.TTS(session, "Alright you are the director. Think of a word and I will try to guess it.")
    
    while True:
        if time.time() - start_time > time_limit:
            yield movements.raise_hands(session)
            yield audio_config.TTS(session, "The time's up. You win!")
            return
        
        yield movements.breathing(session)
        print("i am in guesser")
        user = yield audio_config.STT(audio_processor, response)
        user_chat.append(user)

        if "exit" in user:
            yield movements.shake_head(session)
            yield movements.wave_right_arm(session)
            yield audio_config.TTS(session, "Ok, I will leave you then!")
            break
        
        if "correct" in user:
            yield movements.raise_hands(session)
            yield sleep(3)
            yield audio_config.TTS(session, "I have won!")
            break 
        else:
            yield movements.thinking(session)
            response = llm.generate_llm_response(f"""
                                                    Your past response: {llm_chat}.
                                                    Our past responses: {user_chat}
                                                    Give us your guess for the guessing game.
                                                    """)

            llm_chat.append(response)
            yield audio_config.TTS(session, response)