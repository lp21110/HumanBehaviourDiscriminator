"""Switchable model access for local Ollama or a private API gateway."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any


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
        self.model = os.getenv("HBD_OLLAMA_MODEL", "qwen3.5:9b") #establish model used for the ollama provider. qwen3.5:9b is used as default 

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
        self.model = "deepseek-v4-flash"

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]: 
        response = self.client.chat.completions.create(
            model=self.model,messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},],
            max_tokens=8192,
            temperature=0,
            extra_body={"thinking": {"type": "disabled"}},)

        generated_response = response.choices[0].message.content

        return generated_response


#PRIVATE API CONFIGURATION 
class PrivateAPI:
    """
    Generate JSON through the private API model gateway.
    """

    name = "private_api"

    def __init__(self):
        from openai import OpenAI


        base_url = os.getenv("HBD_API_BASE_URL","https://agx1-1.taildbf607.ts.net/v1",)
        api_key = os.getenv("HBD_API_KEY","1237899") #get the API key from $env:HBD_API_KEY

        default_model = "jetson/qwen3.5-9b-q8_0" #here can alter the defaut model
        self.model = os.getenv("HBD_API_MODEL", default_model,) #access the model specific in environment to run, if none specified run default model

        self.client = OpenAI(api_key = api_key, base_url = base_url,)

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
            raise ModelProviderError("The Private API gateway request failed") from exc 
        
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
        self.model = "gemini-3.6-flash"
        self.time = time

    def generate_json(self, video_input_type : str, video_input, system_prompt: str) -> dict[str, Any]:

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
    
    #Using Gemini API - youtube URL's


#@lru_cache(maxsize=1)
def get_model_provider() -> Ollama | PrivateAPI:

    """
    Returns and calls/uses the selected backend (either Ollama or Private API).
    If neither are chosen, returns an error message.
    """

    provider_name = os.getenv("HBD_MODEL_PROVIDER", "ollama").strip().lower() #specify private_api befor calling, or will use ollama provider as default

    if provider_name == "ollama":
        return Ollama() 
    if provider_name == "deepseek":
        return Deepseek()
    if provider_name == "private_api":
        return PrivateAPI()
    
    raise ModelProviderError("HBD_MODEL_PROVIDER must be 'ollama', 'deepseek' or 'private_api'.")



# OLD CODE -----------------------------------------------------------------------------------------------------------------------------------

# PRIVATE API CONFIGURATION 
# class PrivateAPI:
#     """
#     Generate JSON through the private API model gateway.
#     """

#     name = "private API gateway"

#     def __init__(self):
#         from openai import OpenAI

#         try:
#             import httpx 
#         #raise error if the user does not have httpx package installed in terminal
#         except ImportError as exc:
#             raise ModelProviderError("The private API provider requires the 'httpx' package.") from exc


#         #base_url = os.getenv("HBD_API_BASE_URL", "").rstrip("/") #use this line if you want to implement another private API/ input API environment in terminal instead of the specific gateway used in this case
#         base_url = "https://agx1-1.taildbf607.ts.net/v1"
#         #models = os.getenv("HBD_API_MODEL", "") #provide the model in gitbash/ terminal under $env:HBD_API_MODEL - use to be able to implement another API 
#         models = "/models" #access the different models the API can run
#         default_model = "jetson/qwen3.5-9b-q8_0" #here can alter the defaut model
        
#         #USE BELOW CODE IF ENTERING THE BASE_URL AND THE API_MODEL VIA TERMINAL (INSTEAD OF THE ONE SET HERE)
#         #if not base_url: #raise error if the base_url is not provided under $HBD_API_BASE_URL
#         #    raise ModelProviderError("HBD_API_BASE_URL is required for private_api.")
#         #if not model: #raise error if the API model is not provided under $env:HBD_API_MODEL
#         #    raise ModelProviderError("HBD_API_MODEL is required for private_api.")

#         #endpoint = os.getenv("HBD_API_ENDPOINT", "/v1/generate") #uses the provided HBD_API_ENDPOINT variable if provided in terminal, otherwise uses provided endpoint 
#         #endpoint = os.getenv(endpoint_get_url)
#         #self.url = f"{base_url}/{endpoint.lstrip('/')}" #append endpoint to the base URL and define as the URL for the API / model to use
        

#         endpoint_get_url = f"{base_url}/{models.lstrip('/')}/{default_model.lstrip('/')}" 
        
#         self.url = endpoint_get_url
#         self.model = default_model 

#         #headers = {"Accept": "application/json"} IDK WHAT THIS CODE DOES
#         api_key = os.getenv("HBD_API_KEY") #get the API key from $env:HBD_API_KEY

#         #IDK WHAT THE BELOW LINES DO 
#         # if api_key:
#         #     header_name = os.getenv("HBD_API_AUTH_HEADER", "Authorization")
#         #     auth_scheme = os.getenv("HBD_API_AUTH_SCHEME", "Bearer")
#         #     headers[header_name] = f"{auth_scheme} {api_key}".strip()

#         timeout = float(os.getenv("HBD_API_TIMEOUT", "120")) #limit the amount of time allowed for this function to run 

#         self.client = OpenAI(api_key = api_key, base_url = base_url,)



#     def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
#         #generate json function that is specific to the Private API model output
#         payload = {
#             "model": self.model,
#             "system_prompt": system_prompt,
#             "prompt": user_prompt,
#             #"temperature": 0, - default/ recommended is set to 0.2 already
#             "response_format": "json",
#         }

#         #THE DIFFERENT WAYS TO CALL FOR THE RESONSE FROM THE API - MAKE IT SPECIFIC TO THE WHAT THE API YOU HAVE REQUIRES 
#         try:
#             response = client.chat.completions.create(self.url, json=payload)
#             response.raise_for_status()
#         except Exception as exc:
#             status_code = getattr(getattr(exc, "response", None), "status_code", None)
#             status_text = f" (HTTP {status_code})" if status_code else ""
#             raise ModelProviderError(f"The private API gateway request failed{status_text}.") from exc

#         #TRIES TO EXTRACT THE RESPONSE AS A JSON (AS THE SYSTEM / USER PROMPT REQUESTED)
#         try:
#             gateway_response = response.json()
#         except ValueError as exc:
#             raise ModelProviderError("The private API gateway did not return JSON.") from exc

#         if "response" not in gateway_response:
#             raise ModelProviderError("The private API gateway response has no 'response' field.")

#         generated_content = gateway_response["response"]
#         return _decode_json_object(generated_content)



# @lru_cache(maxsize=1)
# def get_model_provider() -> OllamaProvider | PrivateAPIProvider:
#     """Return the selected backend and reuse it for the whole pipeline."""
#     provider_name = os.getenv("HBD_MODEL_PROVIDER", "ollama").strip().lower()

#     if provider_name == "ollama":
#         return OllamaProvider()
#     if provider_name == "private_api":
#         return PrivateAPIProvider()

#     raise ModelProviderError(
#         "HBD_MODEL_PROVIDER must be 'ollama' or 'private_api'."
#     )
