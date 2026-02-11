from flask import current_app
import os
import json
from google import genai
from .gemini_text_prompt import TEMPLATE_PROMPT
from .config import *

def gemini_init():
    try:
        key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=key)

        return client
    except Exception as e:
        print(e)
        exit()

def generate_tasks(task_list, location):
    try:   
        task_prompt = TEMPLATE_PROMPT + "location: " + location + "\n" + "task_list: " + str(task_list)
        client = current_app.extensions["gemini_CLIENT"]
        
        response = client.models.generate_content(
            model= GEMINI_MODEL, 
            contents= task_prompt,
            config = GEMINI_CONFIG 
        )
        
        task_json = json.loads(response.text)
        
        return task_json
    except Exception as e:
        print(e)
        return None
