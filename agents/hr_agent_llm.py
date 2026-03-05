import os
from google import genai
from google.genai import types
from prompts.llm_planner_prompt import planner_system_instruction
from data_base_connection import get_organization_hierarchy_date
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def llm_planner(user_query: str,chat_history:list):
    organization_hierarchy = get_organization_hierarchy_date()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=planner_system_instruction(chat_history=chat_history,employees_data=organization_hierarchy),
            response_mime_type="application/json",
        ),
        contents=user_query,
    )
    return response.text

# def llm_action(user_query: str,chat_history:list,hierarchy:list):
#     response = client.models.generate_content(
#         model="gemini-3-flash-preview",
#         config=types.GenerateContentConfig(
#             system_instruction=planner_system_instruction(chat_history=chat_history,employees_data=hierarchy),
#             response_mime_type="application/json",
#         ),
#         contents=user_query,
#     )
#     return response.text