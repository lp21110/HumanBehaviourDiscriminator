#API configurations
import os 
import httpx 
import json
#Using 'provider adapters':
#Recieves the request from the user via the  and sends it to the LLM API for processing. The response is then sent back to the user.

# #OLLAMA API configuration: 
# import ollama 

# #initialise Ollama client 
# client = ollama.Client()

# #define model 
# #model = 'llama3.2:3b'
# #model = 'llama3.1:8b'
# model = 'qwen3.5:9b'

class model_provider:
    
    def __init__(self, client, model_name):
        self.model = model_name #change model name to the model provider of choice
        self.client = client #change the cleint intitialisation according to the model provider of choice

    def generate_response(self, system_prompt, prompt, format = "json", think=False, options=None):
        response = self.client.generate(
            model=self.model,
            system=system_prompt,
            prompt=prompt,
            format=format,
            think=think,
            options=options
        )
        return response
    

 # when called: 
 # init_response = provider.generate_response(model=model, system = system_prompt, prompt= user_prompt, format= "json", think=False, options={"temperature": 0}) #temperature keeps the results reproducible

#OLLAMA API configuration:
def call_ollama():
    import ollama
    #define client and model for the ollama provider
    ollama_client = ollama.Client()
    ollama_model = 'qwen3.5:9b'
    #create an instance of the model_provider class for the ollama provider
    ollama_provider = model_provider(ollama_client, ollama_model)

#PROVIDED API CONFIGURATION: 
#store variable values into environment variables in powershell/bash terminal before running the code:
#BASE URL under HBD_API_BASE_URL
#API Key under HBD_API_KEY
#Model name under HBD_MODEL_NAME

class API_provider:

    def __init__(self):
        self.base_url = os.environ["HBD_API_BASE_URL"].strip()
        self.api_key = os.environ["HBD_API_KEY"]
        self.model = os.environ["HBD_MODEL_NAME"]
        #can include a 'timeout' variable in the call to httpx.Client() below to limit time taken to establish a connection to the API server. 
        #i.e. timeout = 120 
        self.client = httpx.Client(base_url=self.base_url, headers={"Authorization": f"Bearer {self.api_key}"})

    def generate_response(self, system_prompt, prompt, format = "json", think=False, options=None):
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": prompt,
            "temperature": 0,
            "response_format": format,
            "temperature": 0,
        }
        response = self.client.post("/generate", json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        gateway_response = response.json()
        generated_response = gateway_response.get("response", "")

        if isinstance(generated_response, ):
            # If the response is a dictionary, convert it to a JSON string
            generated_response = json.dumps(generated_response)
        return response