# # HumanBehaviourDiscriminator

### Project Overview:  
Distinguishing between generated vs human behaviour for a given text input. The text input is assumed to entail an action sequence or a description of such. 

### Behaviour Analysis Rubric:
The following are the behavioural dimensions covered in the pre-defined rubric and a summary of what they assess.

 > - **ADAPTABILITY**: Assesses whether behaviour changes with context, feedback, obstacles, prior experience, or revised plans.  
 > - **HUMAN_IMPERFECTIONS**: Assesses for hesitation, forgetfulness, distraction, interruptions, and other imperfections in the action flow.  
 > - **RECOVERY**: Assesses ability to identify mistakes, correct mistakes, self-checking, and whether recovery from mistakes looks natural or overly convenient.  
 > - **PREFERENCES_AND_NON_OPTIMALITY**: Assesses if choices are driven by preference, if just adequate rather than optimal actions are taken, and small routine variations are shown.
>  - **TIMING**: Assesses realism of the timing for each action and between actions.  
 > - **MICRO-BEHAVIOUR**: Assesses automatic or subconscious behaviours that have no clear goal, such as fidgeting or yawning.  
 > - **ENVIRONMENTAL_CONTEXT**: Assesses whether actions respond to and are aligned with objects, surroundings, and environmental constraints.  
 > - **PHYSIOLOGICAL_CONTEXT**: Assesses whether actions are physically plausible and accurately reflect realistic bodily constraints.  
 > - **ATTENTIVENESS**: Assesses monitoring the current scenario, attention shifts, selective awareness, and whether some information is overlooked.  
 > - **FORESIGHT**: Assesses planning, ability to bundle related actions (i.e. taking multiple items out of the drawer at the same time for varying tasks), postponing goals, and managing multiple goals.  
 > - **SOCIAL**: Assesses adaptation, coordination, and awareness when other agents or living beings are present.  

  Other dimensions considered include: INTENTIONALITY, ROUTINE, EMOTIONS, TIMING  

## Usage requirements/ Dependencies:

**For Ollama Model (default)**  
LLM: Ollama  
Ollama model: qwen3.5:9b

**For Deepseek Model**
LLM: DeepSeek
OpenAI Deepseek model: deepseek-v4-flash  
(requires API key)  

**For Private API**  
LLM: Assumed OpenAI model.  
Personalise by setting the model and base_url environment variables.  

Default model: jetson/qwen3.5-9b-q8_0  
(requires API key)

FOR VIDEO INPUTS (additionally required to one of the above):  
**Gemini**  
LLM: Gemini  
Gemini model: gemini-3.7-flash  
(requires API key - free)  

## How to call through terminal:  

**For Ollama (default):**  
1. Call the user interface.  
`py .\gradio_user_interface.py`  

**For Private API:**  
1. Set the environment variable 'HBD_MODEL_PROVIDER' to "private_api". This variable selects from where to call the large language model.
2. IF you wish to connect to a specific API, set the environment variable 'HBD_API_BASE_URL' to your API base URL
4. Assign the environment variable 'HDB_API_KEY' your API key.  
`$env:HBD_MODEL_PROVIDER="private_api"`  
`$env:HBD_API_BASE_URL="yourAPIbaseURL"`      
`$env:HBD_API_KEY="yourAPIkey"`  

6. To call a model other than the default model from the private API, set the environment variable 'HBD_API_MODEL' to either of the following.    
`$env:HBD_API_MODEL="jetson/qwen3.5-27b"`  
OR  
`$env:HBD_API_MODEL="jetson/qwen3.5-35b"`

This outputs a link to access either a local or online host for the (gradio) discriminator user interface.  

## Using the Interface

**The User inputs:**  
Input Options:  
- Text: Enter into textbox on screen  
- Video: file upload, or URL  
- Analysis Categories: Can select the behavioural categories from the defined rubric, and can input their own prompt. 

**The User can see the following output:**  
- Overall human-likeness percentage for chosen categories  
- Classification (Human-like or Generated-like)  
- Classification reasoning summary  
- For each chosen behavioural category, its classification, its independent scores, and in-depth score reasoning  
