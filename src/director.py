from twisted.internet.defer import inlineCallbacks
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
def director_role(session, audio_processor):
    """
    This function executes when the role of the robot is the Director.
    """
    
    chosen_word = random.choice(cards.card)
    start_time = time.time() # timer starts
    llm_chat = [] 

    yield movements.nod_head(session)
    yield audio_config.TTS(session, "Alright I will be the director then. Let me think of a word!")
    yield movements.thinking(session)
    prompt = prompts.generate_director_prompt(chosen_word)
    response = llm.generate_llm_response(prompt)
    user_chat.append(prompt)
    llm_chat.append(response)
    yield audio_config.TTS(session, response)

    while True:
        if time.time() - start_time > time_limit:
            yield movements.shake_head(session)
            yield session.call("rie.dialogue.say",text=f"The time's up! The word was {chosen_word}")
            return
        
        yield movements.breathing(session)
        user = yield audio_config.STT(audio_processor, response)
        print("here in director")
        user_chat.append(user)

        if "exit" in user:
            yield movements.shake_head(session)
            yield movements.wave_right_arm(session)
            yield audio_config.TTS(session, "Ok, I will leave you then.")
            break
        if chosen_word in user:
            yield movements.raise_hands(session)
            yield audio_config.TTS(session, "Congratulations! You have guessed the word.")
            break
        
        yield movements.thinking(session)
        response = llm.generate_llm_response(f"""
                                                    Your past response: {llm_chat}.
                                                    Our past responses: {user_chat}
                                                    Give us your new description for the {chosen_word} for 
                                                    the guessing game. 
                                                    """)
        
        llm_chat.append(response)
        yield audio_config.TTS(session, response)