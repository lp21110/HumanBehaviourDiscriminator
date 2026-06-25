# HumanBehaviourDiscriminator

### Project Overview:  
Distinguishing between generated vs human behaviour for a given text input. The text input is assumed to entail an action sequence or a description of such. 

### Behaviour Analysis Rubric:
The following are the behavioural dimensions covered in the pre-defined rubric and a summary of what they assess for.

 > - **ADAPTABILITY**: Assesses whether behaviour changes with context, feedback, obstacles, prior experience, or revised plans.  
 > - **HUMAN_IMPERFECTIONS**: Assesses for hesitation, forgetfulness, distraction, interruptions, and other imperfections in the action flow.  
 > - **RECOVERY**: Assesses ability to identify mistakes, correct mistakes, self-checking, and whether recovery from mistakes looks natural or overly convenient.  
 > - **PREFERENCES_AND_NON_OPTIMALITY**: Assesses if choices are driven by preference, if just adequate rather than optimal actions are taken, and small routine variations are shown.  
 > - **MICRO-BEHAVIOUR**: Assesses automatic or subconscious behaviours that have no clear goal, such as fidgeting or yawning.  
 > - **ENVIRONMENTAL_CONTEXT**: Assesses whether actions respond and are aligned to objects, surroundings, and environmental constraints.  
 > - **PHYSIOLOGICAL_CONTEXT**: Assesses whether actions are physically plausible and accurately reflect realistic bodily constraints.  
 > - **ATTENTIVENESS**: Assesses monitoring current scenario, attention shifts, selective awareness, and whether some information is overlooked.  
 > - **FORESIGHT**: Assesses planning ahead, ability to bundle related actions (i.e. taking multiple items out the drawer at the same time for varying tasks), postponing goals, and managing multiple goals.  
 > - **SOCIAL**: Assesses adaptation, coordination, and awareness when other agents or living beings are present.  

  Other dimensions considered include:  
  INTENTIONALITY    
  ROUTINE  
  EMOTIONS  
  TIMING  

## Usage requirements/ Dependencies:
LLM: Ollama  
Ollama model: qwen3.5:9b

## How to use:

### If running directly through python:
The relevant function to call is:
> ` get_behvaiour_analysis (text_input, rubric=BEHAVIOUR_CATEGORY_RUBRIC, user_dimension_reply = None, dimensions_of_interest = None) `

where  
- *text_input* is the desired text to analyse behaviour for. Pre-define in script before calling.  
- *dimensions_of_interest* is a list of the specific dimensions to analyse text on if the user does not want all the dimensions scored. Pre-define in script before calling 

example code:  
    ` result = get_behavior_analysis(text_input=test_transcript_input, rubric=BEHAVIOUR_CATEGORY_RUBRIC) #this will result with analysing the test_transcript_input with all the dimensions in the rubric  
    print('RESULT 1', json.dumps(result_1, indent=2)) `

### If running through terminal:
The relevant function to call is:
> ` get_behavioural_analysis_interactive(rubric=BEHAVIOUR_CATEGORY_RUBRIC) `

This will:
1. Prompt user to input their text to be analysed. Enter the text as one line.
2. Prompt user to choose which behavioural dimensions they wish to analyse. User can reply using one of the following formats:
   
#### Prompt Options:
- **ALL_PROMPTS** - Evaluates the text input containing behaviour to be analysed on all the dimensions defined in the behavioural rubric   
- **'PROVIDED_PROMPTS'**: ... - Evaluates the text input on only the selected behavioural dimensions from the rubric. Selected and defined by the user  
- **'OWN_PROMPT'**: ... - Evaluates the text input on a prompt given by the user, not from the pre-defined behavioural rubric  
  or  
- **'PROVIDED PROMPTS': ...; 'OWN_PROMPT'...** - Evaluate the text input on both selected behavioural dimensions from the rubric, as well as user-specific prompts   

Any prompts entered that do not follow the above will return as Error

3. Returns the behavioural analysis of the text input.

example code:  
    `result_interactive_input = get_behavioural_analysis_interactive(rubric=BEHAVIOUR_CATEGORY_RUBRIC)
     print('RESULT - INTERACTIVE USER INPUT', json.dumps(result_interactive_input, indent=2)) `
