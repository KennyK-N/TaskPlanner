from flask import current_app
import os
import json
from google import genai
from .gemini_text_prompt import TEMPLATE_PROMPT
from .config import *


def gemini_init():
    """
    Initializes and returns a Gemini API client using the GEMINI_API_KEY environment variable.
    Returns:
        genai.Client: A configured Gemini client, or exits the process if initialization fails.
    """
    try:
        key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=key)

        return client
    except Exception as e:
        print("Error ", e)
        exit()


def generate_tasks(task_list, location):
    """
    Sends a prompt to Gemini with the user's tasks and location, and returns the generated schedule as a dict.
    Args:
        task_list (list): The list of tasks the user wants scheduled.
        location (str): The user's location to give Gemini regional context.
    Returns:
        dict | None: The parsed JSON schedule from Gemini, or None if generation fails.
    """
    try:
        task_prompt = (
            TEMPLATE_PROMPT
            + "location: "
            + location
            + "\n"
            + "task_list: "
            + str(task_list)
        )
        client = current_app.extensions["gemini_CLIENT"]

        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=task_prompt, config=GEMINI_CONFIG
        )

        task_json = json.loads(response.text)

        return task_json
    except Exception as e:
        print("Error ", e)
        return None
