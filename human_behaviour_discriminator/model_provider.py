"""Switchable model access for local Ollama or a private API gateway."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

#FOR TEXT ANALYSIS - TEXTS DIRECTLY INPUTTED, OR CAPTIONS OF INPUTTED VIDEOS --------------------------------------------------------------

#ERROR FOR MODEL OUTPUTS IF NOT IN/ CANNOT BE CONVERTED TO A JSON FORMAT 
class ModelProviderError(RuntimeError): 
    """
    Raised when the configured model service cannot return usable JSON.
    - Returns the output as it is if the model directly returns a dictionary 
    - Converts the output into a dictionary if the model returns a string 
    - If the model does not return a string or a dictionary, return an error message 
    - If the model returns a string that cannot be converted to valid JSON, return an error message
    
    Role: call to return the error message (inputted to replace default RuntimeError message) when the exception is raised
    
    Runtime: built-in exception that is raised when an unexpected error (an error that does not fall under any specific category) is detected 
    """
def _decode_json_object(content: Any) -> dict[str, Any]: 
    
    """
    Ensures the model has returned a valid Python dictionary, in json format.
    '->' : specifies the expected return type of the function 
    """
    if isinstance(content, dict): #if the model returns a dictionary, return it as it is
        return content

    if not isinstance(content, str): #if the model's response is not in string (or dict) format, raise an Error
         raise ModelProviderError("The model returned content that was neither JSON text nor an object.")

    try:
        decoded = json.loads(content) #convert the string into a Python dictionary
    except json.JSONDecodeError as exc: #If the content is not valid JSON raise an error
        #'raise ... from exc' - raise a new exception and keeps the original exception as the cause of the exception
        raise ModelProviderError("The model returned incomplete or invalid JSON.") from exc

    if not isinstance(decoded, dict): #if the models response is not or cannot be converted into a dictionary, raise an error
        raise ModelProviderError("The model JSON response must be an object.")

    return decoded


#OLLAMA CONFIGURATION:
class Ollama:
    """
    Generate JSON through a locally running Ollama server.
    """

    name = "ollama"

    def __init__(self):
        import ollama

        self.client = ollama.Client(host=os.getenv("OLLAMA_HOST") or None) #establish connection to the ollama server running on local machine or remote server
        self.model = os.getenv("OLLAMA_MODEL", "qwen3.5:9b") #establish model used for the ollama provider. qwen3.5:9b is used as default 

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]: 
        '''
        Function to generate JSON file specific to the output layout of the Ollama server
        '''
        response = self.client.generate(
            model=self.model,
            system=system_prompt,
            prompt=user_prompt,
            format="json",
            think=False,
            options={"temperature": 0},
        )
        return _decode_json_object(response["response"])


#DEEPSEEK CONFIGURATION 
class Deepseek:
    """
    Generate JSON through the deepseek API model gateway.
    """
    name = "deepseek"

    def __init__(self):
        from openai import OpenAI
        
        self.client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]: 
        response = self.client.chat.completions.create(
            model=self.model,messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},],
            max_tokens=8192,
            temperature=0,
            extra_body={"thinking": {"type": "disabled"}},)

        generated_response = response.choices[0].message.content

        return _decode_json_object(generated_response)


#PRIVATE API CONFIGURATION 
class Private:
    """
    Generate JSON through the private API model gateway.
    """

    name = "private"

    def __init__(self):
        from openai import OpenAI


        base_url = os.getenv("PRIVATE_BASE_URL","https://agx1-1.taildbf607.ts.net/v1",) #PRIVATE API base URL set to the one provided 
        api_key = os.getenv("PRIVATE_API_KEY") #get the API key from $env:PRIVATE_API_KEY

        default_model = "jetson/qwen3.5-9b-q8_0" #here can alter the defaut model
        self.model = os.getenv("PRIVATE_MODEL", default_model) #access the model specific in environment to run, if none specified run default model

        self.client = OpenAI(api_key = api_key, base_url = base_url)

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        
        try: 

            response = self.client.chat.completions.create(
                model = self.model, 
                messages = [
                    {"role":"system",
                     "content": system_prompt},
                     {"role":"user",
                      "content": user_prompt}
                    ],
                    stream = False,
                    max_tokens = 8192,
                    temperature = 0,
                    extra_body= {"think":False, "num_ctx":32768},
                    )

        except Exception as exc: 
            raise ModelProviderError("The Private gateway request failed") from exc 
        
        if isinstance(response, str):
            generated_response = response
        else: 
            generated_response = response.choices[0].message.content
        
        print("RESPONSE TYPE:", type(response))
        
        print("RESPONSE VALUE:", repr(response)[:500])

        if isinstance(response, str):
            generated_response = response
        else:
            generated_response = response.choices[0].message.content

        print("CONTENT TYPE:", type(generated_response))
        print("CONTENT VALUE:", repr(generated_response)[:1000])

        return _decode_json_object(generated_response) 
    


#-FOR VIDEO INPUTS----------------------------------------------------------------------------------------------------

#Using Gemini API - file APIS
#gemini: 1FramePerSecond sampling rate so might lose accuracy - slow down clips?
    
import base64

class Gemini:
    """
    Analyse and create an action log via Gemini API model gateway 

    Default model : gemini-3.7-flash
    Issues with model choice: Frequently becomes too 'high demand' when used in Free Tier. Can replace with previous models:
            'gemini-3.6-flash'
            'gemini-3.5-flash'
            'gemini-3.5-flash-lite'
            But, might loose accuracy quality in video captioning.
    """

    name = "Gemini"

    def __init__(self):
        from google import genai
        import time as time 

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ModelProviderError(
                "GEMINI_API_KEY is not set. Configure a valid Gemini API key before analysing video."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.7-flash"
        self.time = time

    def generate_json(self, video_input_type : str, video_input, system_prompt: str) -> str:

        if video_input_type == "file_upload":
            myfile = self.client.files.upload(file=video_input)

            while not myfile.state or myfile.state.name != "ACTIVE":
                self.time.sleep(5)
                myfile = self.client.files.get(name=myfile.name)

            contents = [system_prompt, myfile]


        elif video_input_type == "url":
            contents = [system_prompt, video_input]


        response = self.client.models.generate_content(
                model= self.model,
                contents = contents)
            
        generated_response = response.text

        return generated_response
    

class Qwen:
    """
    Suggested to be more accurate at identifying human actions from a video. 
    Requirements: To be run locally, requires NVIDIA GPU and CUDA. Hence, run non-locally.
    Non-local options: (not free)
        -OpenRouter 
        -DashScope API Key 

    !!! IF SWITCHING TO QWEN, NEED TO UPDATE/ INCORPORATE INTO video_to_action_log in video_analysis.py 

    """
    
    name = "Qwen"

    def __init__(self):
        from openai import OpenAI
        import time as time

        base_url = os.getenv("QWEN_API_BASE_URL", "https://openrouter.ai/api/v1") #BASE URL for QWEN (for better video analysis) set to OpenRouter
        api_key = os.getenv("QWEN_API_KEY")

        if not api_key:
            raise ModelProviderError(
                "QWEN_API_KEY is not set. Configure a valid Gemini API key before analysing video.")
        
        self.model = "qwen/qwen3.7-flash"
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.time = time
        self.base = base64

    def generate_json(self, video_input_type : str, video_input, system_prompt: str) -> str:

        if video_input_type == "file_upload":

            with open(video_input, "rb") as video_file:
                encoded_video = self.base64.b64encode(video_file.read()).decode("utf-8")

            video_content = {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{encoded_video}"}}

        elif video_input_type == "url":
        
            video_content = {
                "type": "video_url",
                "video_url": {
                    "url": video_input}
            }
         
        messages = [
            {"role": "user",
            "content": [
                {"type": "text",
                "text": system_prompt},
                video_content,
                ],
            }
        ]

        completion = self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            max_tokens = 2048,
        )
        return completion.choices[0].message.content


#--------------------------------------------------------------------------------------------------------------------------------------


def get_model_provider() -> Ollama | Deepseek | Private:

    """
    Returns and calls/uses the selected backend (either Ollama, Deepseek or Private).
    If neither are chosen, returns an error message.

    Ollama is set as the default.
    """

    provider_name = os.getenv("MODEL_PROVIDER", "ollama").strip().lower() #specify private before calling, or Ollama will be used by default

    if provider_name == "ollama":
        return Ollama() 
    if provider_name == "deepseek":
        return Deepseek()
    if provider_name == "private":
        return Private()
    
    raise ModelProviderError("MODEL_PROVIDER must be 'ollama', 'deepseek' or 'private'.")
