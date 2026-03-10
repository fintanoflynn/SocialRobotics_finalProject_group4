from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize the OpenAI client

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