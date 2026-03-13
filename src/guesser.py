from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import random 
import time 

import movements
import audio_config
import llm
import prompts
import cards


# chat history:
user_chat = [] 
llm_chat = []
time_limit = 50000 # A way to end the game (for testing it was set to 8 seconds)

@inlineCallbacks
def guesser_role(session, audio_processor):
    """
    This function executes when the role of the robot is the Guesser.
    """    
    chosen_word = random.choice(cards.card)
    print(chosen_word)
    start_time = time.time() 
    llm_chat = [] 
    prompt = prompts.generate_guesser_prompt()
    response = llm.generate_llm_response(prompt)
    user_chat.append(prompt)
    llm_chat.append(response)
    yield sleep(2)
    yield audio_config.TTS(session, "Alright you are the director. Think of a word and I will try to guess it.", audio_processor)
    
    while True:
        if time.time() - start_time > time_limit:
            yield movements.raise_hands(session)
            yield audio_config.TTS(session, "The time's up. You win!", audio_processor)
            return

        user = yield audio_config.STT(audio_processor)
        user_chat.append(user)

        if "exit" in user:
            yield movements.shake_head(session)
            yield movements.wave_right_arm(session)
            yield audio_config.TTS(session, "Ok, I will leave you then!", audio_processor)
            break
        
        if "correct" in user:
            yield movements.raise_hands(session)
            yield sleep(3)
            yield audio_config.TTS(session, "I have won!", audio_processor)
            break 
        else:
            response = llm.generate_llm_response(f"""
                                                    Your past response: {llm_chat}.
                                                    Our past responses: {user_chat}
                                                    Give us your guess for the guessing game.
                                                    """)

            llm_chat.append(response)
            movements.nod_head(session)
            yield audio_config.TTS(session, response, audio_processor)