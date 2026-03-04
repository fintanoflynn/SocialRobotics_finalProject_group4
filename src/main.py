from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText
import random 
import time 
import os

import movements
import face_tracking
import audio_config

from openai import OpenAI
from dotenv import load_dotenv


audio_processor = SpeechToText()
audio_processor.silence_time = 0.5 
audio_processor.silence_threshold2 = 100
audio_processor.logging = False


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize the OpenAI client
role = None # Director or Guesser
time_limit = 50000 # A way to end the game (for testing it was set to 8 seconds)
cards = ["pizza", "bicycle", "football", "basketball", "phone"] 
rules = """
This game has two roles, a Director and a Guesser. The Director chooses a word and describes it 
without saying the word itself. The Guesser tries to figure out the word from the description. If the 
Guesser makes a correct guess and the Director confirms it by saying "correct", the Guesser wins. 
The Guesser has 3 minutes to guess the word.
"""
# chat history:
user_chat = [] 
llm_chat = []


def generate_llm_response(prompt):
    """
    The response from OpenAI is recorded here.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150  
    )
    return response.choices[0].message.content



@inlineCallbacks
def director_role(session):
    """
    This function executes when the role of the robot is the Director.
    """
    
    chosen_word = random.choice(cards)
    start_time = time.time() # timer starts
    llm_chat = [] 
    movements.nod_head(session)
    yield audio_config.TTS_2(session, "Alright I will be the director then. Let me think of a word!", audio_processor)
    response = generate_llm_response(f"""
                                        Play With Other Words (guessing game) with me. Give me a description of 
                                        secret word I do not know. Don't use the word in the sentence ofcourse.
                                        The secret word I dont know is {chosen_word}.
                                        When playing, give a very short explanation like you are playing a guessing game. The goal
                                          is for the user to make multiple guesses and work towards the answer based on your description. Leave the explanation vague but 
                                        not too vague that no guesses can be made however it should be hard. 
                                        If the user doesn't get close, give them more hints. Don't repeat your previous description, make a new one and adjust the difficulty. 
                                        Create a different description but keep it short still. If the user asks for the secret word, you should encourage 
                                        them to guess again like "try to guess again!".""")
    user_chat.append(f"""
                                        Play With Other Words (guessing game) with me. Give me a description of 
                                        secret word I do not know. Don't use the word in the sentence ofcourse.
                                        The secret word I dont know is {chosen_word}. 
                                        When playing, give a very short explanation like you are playing a guessing game. The goal
                                          is for the user to make multiple guesses and work towards the answer based on your description. Leave the explanation vague but 
                                        not too vague that no guesses can be made however it should be hard. 
                                        If the user doesn't get close, give them more hints. Don't repeat your previous description, make a new one and adjust the difficulty. 
                                        Create a different description but keep it short still. If the user asks for the secret word, you should encourage 
                                        them to guess again like "try to guess again!".""")
    llm_chat.append(response)
    yield audio_config.TTS_2(session, response, audio_processor)

    while True:
        if time.time() - start_time > time_limit:
            movements.shake_head(session)
            yield session.call("rie.dialogue.say",text=f"The time's up! The word was {chosen_word}")
            return
        
        user = yield audio_config.STT(audio_processor)
        user_chat.append(user)

        if "exit" in user:
            yield movements.shake_head(session)
            movements.wave_right_arm(session)
            yield audio_config.TTS_2(session, "Ok, I will leave you then.", audio_processor)
            break
        if chosen_word in user:
            movements.raise_hands(session)
            yield audio_config.TTS_2(session, "Congratulations! You have guessed the word.", audio_processor)
            break
        
        response = generate_llm_response(f"""
                                                    Your past response: {llm_chat}.
                                                    Our past responses: {user_chat}
                                                    Give us your new description for the {chosen_word} for 
                                                    the guessing game. 
                                                    """)
        
        llm_chat.append(response)
        movements.shake_head(session)
        yield audio_config.TTS_2(session, response, audio_processor)


@inlineCallbacks
def guesser_role(session):
    """
    This function executes when the role of the robot is the Guesser.
    """    
    chosen_word = random.choice(cards)
    print(chosen_word) # print word into terminal for user
    start_time = time.time() 
    llm_chat = [] 
    response = generate_llm_response("""   
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
    movements.nod_head(session)
    yield audio_config.TTS_2(session, "Alright you are the director. Think of a word and I will try to guess it.", audio_processor)
    
    while True:
        if time.time() - start_time > time_limit:
            movements.raise_hands(session)
            yield audio_config.TTS_2(session, "The time's up. You win!", audio_processor)
            return
        
        user = yield audio_config.STT(audio_processor)
        user_chat.append(user)

        if "exit" in user:
            yield movements.shake_head(session)
            movements.wave_right_arm(session)
            yield audio_config.TTS_2(session, "Ok, I will leave you then!", audio_processor)
            break
        
        if "correct" in user:
            movements.raise_hands(session)
            yield audio_config.TTS_2(session, "I have won!", audio_processor)
            break 
        else:
            response = generate_llm_response(f"""
                                                    Your past response: {llm_chat}.
                                                    Our past responses: {user_chat}
                                                    Give us your guess for the guessing game.
                                                    """)

            llm_chat.append(response)
            movements.nod_head(session)
            yield audio_config.TTS_2(session, response, audio_processor)


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

    yield face_tracking.track_face(session)
    yield sleep(1.0)

    yield session.call("rom.sensor.hearing.sensitivity", 1650) 
    yield session.call("rie.dialogue.config.language", lang="en")
    

    print('Listening now')
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream") 
    yield session.call("rom.sensor.hearing.stream")
    
    movements.wave_right_arm(session)
    yield audio_config.TTS_2(session, """
                            Let's play With Other Words. Do you know the game or would you like to
                            hear the rules? Say yes if you want the rules.
                        """, audio_processor)
    yield session.call("rom.sensor.hearing.stream")
    user = yield audio_config.STT(audio_processor)

    if "yes" in user:
        movements.nod_head(session)
        yield audio_config.TTS_2(session, f"{rules}", audio_processor)
    
    yield audio_config.TTS_2(session, """
                            Let's start the game and if you want to leave the game say exit. 
                            Would you like to be the director or the guesser?
                        """, audio_processor)

    while True:
        user = yield audio_config.STT(audio_processor)
        if "exit" in user:
            yield movements.shake_head(session)
            movements.wave_right_arm(session)
            yield audio_config.TTS_2(session, "Ok, I will leave you then.", audio_processor)
            yield leave_program(session)
        if "director" in user: # if user is director then the role of the robot is Guesser
            role = "guesser"
            yield guesser_role(session)
            role = None
        elif "guesser" in user: 
            role = "director"
            yield director_role(session)
            role = None

        yield audio_config.TTS_2(session, "Say director or guesser to choose your role or you can say exit to leave the game. ", audio_processor)
        yield sleep(0.05) 


wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.69a823d2b788cadff345a589"
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])