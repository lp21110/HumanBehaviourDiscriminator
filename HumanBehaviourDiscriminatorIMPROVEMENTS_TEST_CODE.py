#IMPROVEMENTS TEST_CODE 

import ollama 
import json
#import requests
import re

#initialise Ollama client 
client = ollama.Client()

#define model 
#model = 'llama3.2:3b'
#model = 'llama3.1:8b'
model = 'qwen3.5:9b'

#A dictionary of the different behaviours that we are analysing and providing as prompts for the model to use
BEHAVIOUR_CATEGORY_RUBRIC = {

    #POTENTIALLY REMOVE INTENTIONALITY AND ROUTINE?

    #INTENTIONALITY PROMPTS: intentionality of the agent's behaviour, including the presence of goals, plans, and motivations behind their actions.  Rank the intentionality on a scale from 10 (human) to 0 (generated)."
    #'INTENTIONALITY_PROMPTS' : [
    #    'Does the agent exhibit goal-directed behaviour?', #Does the behaviour build towards a larger goal? 
    #    'Does the behaviour show a hierarchy of short and long term goals?',
    #    'Do the inferred goals of the actions and tasks fit the scenario context?',
    #    'Are the agents actions coherent across time steps and do they remain so over time?'],   

    #ADAPTABILITY PROMPTS: adaptability of the agent's behaviour. Dealing with uncertainty, ability to improv, re-plan or update plans as they happen.
    'ADAPTABILITY' : [
		'Does the agent show evidence of adapting its behaviour when the environment or context changes?',
        'Does the agent suggest the use of prior experience when encountering familiar situations?',
        'Does the agent show evidence of adjusting its behaviour in response to external feedback?',
        'Does the agent revise its goals when encountering events that hinder its inferred task from its action sequence?',
        'Does the agent show evidence of flexibility in their behaviour, such as being able to switch between different strategies or approaches to achieve their goals?',
        #'Does the agent show evidence of improvisation or creativity in their actions?',   - similar to the above prompt              
		'Does the agent show evidence of re-planning or updating their plans as they happen?'
     ],

    #ROUTINE AND VARIABILITY PROMPTS: 
    ##'ROUTINE' : [
        # 'Does the agent show evidence of habitual or routinely executed actions?',   
    ##    'Does the agents behaviour show evidence of routine, automated actions and procedural familiarity with their tasks',                            
    ##    'Does the agents suggest procedural familiarity with the task?',
    ##    'If the agents actions are inferred as uncertain, does the agents behaviour suggest exploratory, investigative behaviour i.e. through trial and error?',
    ##    'Does the agent show an ability to perform routine tasks with a degree of variability, if the task is repeated can the agent complete it using different action sequences?',
    ##    'Do actions appear habitual or automatic rather than explicitly deliberative?'
    ##    'Does the agents actions contain actions that verify the progress state of the action?'
    ##],

    #IMPERFECTIONS, ERRORS, VARIABILITY
    'HUMAN_IMPERFECTIONS' : [  
        'Do the actions of the agent show uncertainty, such as hesitation, action reversal or changes of course in their carrying out of the task?',
        'Does the agent show signs of forgetfulness in their action sequences?',
        'Does the agent shows signs of distraction from the current task?',
        'Are there interruptions in behaviour and action flow, such as pauses between actions or interruptions in task flow (in contrast to a smooth flow)?'
    ],

    #ERROR RECOVERY 
    'RECOVERY' : [
        'If actions of the agent are inferred as mistakes, do the mistakes and recovery appear overly direct or artificially convenient? The more true this is, the lower the score.',
        'If the agent shows signs of mistakes, are the agents able to correct their path of action, or recover from a potential error?',
        'Does the agent show evidence of being able to detect and recognise its own mistakes?',
        'Does the behaviour show evidence of reviewing or self-checking between tasks and after mistakes?'
    ],


    #EMOTIONS
    ##'EMOTIONAL_ACTION_PROMPTS' : [
    ##    'Does the agent show behaviour and actions that are not purely rational or utility-maximising?'
    ##], #remove prompt - example model response is: 'agents behaviour shows some emotional action such as adding milk and removing the teabag


    #NON-OPTIMALITY 
    'PREFERENCES_AND_NON_OPTIMALITY' : [ #deviation from a clean task flow
        'Does the agents behaviour suggest preference-driven choices over optimal actions?',
        'Does the agent behaviour display sub-optimal behaviour?', 
        'Does the agents behaviour show signs of settling for adequate rather than optimal action flows?',
        'Does the agents behaviour show small variations in action sequences that can be inferred as routine behaviour?'
    ],
    
    #TIMING
    # 'TIMING' : [
    #     'Do the time intervals between each action/ different actions or task sequences performed show realistic variation? ',
    #     'Do the intervals between consecutive actions show human-like irregularity, including natural pauses, quicker automatic movements, and longer gaps before complex or context-dependent actions?',
    #     'Do the times taken for each action correspond with the time generally required for the actions?',
    #     'Are the times taken to perform tasks realistic rather than optimally efficient?'
    # ],

    #MICRO- remove
    'MICRO-BEHAVIOUR' : [
        'Does the agents behaviour perform any automatic, subconscious or micro-behaviours, behaviours with no outward goal? These are behaviours such as yawning, stretching, fidgeting, sighing, flinching, startling, hiccups etc.',
    ],

    #ENVIRONMENTAL CONTEXTUAL BEHAVIOUR
    'ENVIRONMENTAL_CONTEXT' : [
	    'Do the actions of the human adapt to the locations of the objects they are interacting with?',
	    'Do the agents actions show an awareness of their environmental constraints, surrounding wise?', #i.e. physically, walking around obstacles, repositioning objects, adjusting grip, changing posture
	    'Do the actions of the human show that they have been influenced by their surrounding environment?'
    ],

    #PHYSIOLOGICAL_CONTEXT
    'PHYSIOLOGICAL_CONTEXT' : [
	    'Do the agents actions show an awareness of and reflect realistic constraints of the body i.e. the likelihood of an action being able to be performed?',
	    'Do the agents actions and behaviour seem physically plausible?'
	],
	
    #ATTENTIVENESS
    'ATTENTIVENESS' : [
        'Does the agent exhibit actions that suggests it periodically monitor or reassess its environment?',
	    'Does attention shift between multiple goals or objects?',
	    'Does the agents behaviour suggest selective attention rather than perfect awareness of the environment?',
	    'Does the agents behaviour show signs that some information is overlooked?'
	],
    
    #FORESIGHT
    'FORESIGHT' : [
	    'Does the agent show signs of bundling related actions together when possible?',
	    'Does the behaviour indicate towards an awareness of anticipating future resource needs, or evidence of planning/ foresight for future tasks or actions?',
	    'Are multiple goals being pursued simultaneously?',
	    'Are some goals temporarily postponed or left in favour of other goals?'
	],
	
    #SOCIAL BEHAVIOUR
    'SOCIAL': [
        'If other agents or living beings are present, does the agents behaviour adapt to their actions?',
        'If other agents are present, does the agent coordinate its actions with the others?',
        'If other agents are present, does the agent show an adequate awareness of social expectations?'
    ]
}                              


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#FUNCTION TO ASK USER WHICH DIMENSIONS FROM THE BEHAVIOURAL RUBRIC THEY WOULD LIKE TO ASSESS:



#ASK: 
    #Which behavioural dimensions would you like to assess in you inputted text?
        #Here are the options with a summary of what they analyse for: ...

    #ELSE: would you like to add a your own prompt seperate to those provided in the behavioural rubric? 
        #type 'ALL_PROMPTS' if all provided prompts
        #type 'PROVIDED_PROMPT', then input the desired prompts below
        #type 'OWN_PROMPT: ', then input your prompt below

#USER REPLY: Names of the dimensions (exact) that they would like to test 
    ## Add these to an 'dimensions_of_interest' list 
    ## IF reply contains 'OWN PROMPT:', add their following question to the  
    ## IF any of the reply is not included in the rubric (other than entry under 'OWN_PROMPT'), return an Error 


BEHAVIOUR_DIMENSION_SUMMARIES = {
    'ADAPTABILITY_PROMPTS': 'Assesses whether behaviour changes with context, feedback, obstacles, prior experience, or revised plans.',
    'HUMAN_IMPERFECTIONS_PROMPTS': 'Assesses hesitation, forgetfulness, distraction, interruptions, and other imperfect human-like action flow.',
    'RECOVERY_PROMPTS': 'Assesses mistake detection, correction, self-checking, and whether recovery looks natural or overly convenient.',
    'PREFERENCES_AND_NON_OPTIMAL_BEHAVIOUR': 'Assesses preference-driven choices, adequate rather than optimal actions, and small routine variations.',
    'MICRO-BEHAVIOUR': 'Assesses automatic or subconscious behaviours with no outward task goal, such as fidgeting or yawning.',
    'ENVIRONMENTAL_CONTEXT_BEHAVIOUR': 'Assesses whether actions respond to objects, surroundings, and environmental constraints.',
    'PHYSIOLOGICAL_CONTEXT': 'Assesses whether actions are physically plausible and reflect realistic bodily constraints.',
    'ATTENTIVENESS': 'Assesses monitoring, attention shifts, selective awareness, and whether some information is overlooked.',
    'FORESIGHT': 'Assesses planning ahead, bundling related actions, postponing goals, and managing multiple goals.',
    'SOCIAL_BEHAVIOUR': 'Assesses adaptation, coordination, and awareness when other agents or living beings are present.'
}

def get_behaviour_dimension_options(rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Returns the behavioural dimensions available in the rubric with a short explanation of what each dimension analyses.
    '''
    options = []

    for dimension_name in rubric:
        options.append({
            'dimension': dimension_name,
            'summary': BEHAVIOUR_DIMENSION_SUMMARIES.get(
                dimension_name,
                'Assesses this behavioural category using the prompts listed in the rubric.')
        })

    return options

def display_behaviour_dimension_options(rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Prints the dimension-selection instructions for the user.
    '''
    print('Which behavioural dimensions would you like to assess in your inputted text?')
    print('Here are the options with a summary of what they analyse for:')

    for option in get_behaviour_dimension_options(rubric):
        print(f"- {option['dimension']}: {option['summary']}")

    print('\nReply using one of the following formats:')
    print("- Type 'ALL_PROMPTS' to use all provided behavioural rubric prompts.")
    print("- Type 'PROVIDED_PROMPTS', then enter the exact dimension names you want to assess.")
    print("- Type 'OWN_PROMPT:', then enter your own prompt. Seperate each own prompt with a comma, and start with 'OWN_PROMPT:' for each prompt")
    print("\nYou can also combine provided dimensions with an own prompt, for example:")
    print("PROVIDED_PROMPT: ADAPTABILITY_PROMPTS, SOCIAL_BEHAVIOUR; OWN_PROMPT: Does the agent show fatigue?")

def _split_dimension_names(text):
    '''
    Splits comma/newline/semicolon separated dimension names while preserving exact dimension names that contain underscores or hyphens.
    '''
    separators = [',', '\n', ';']
    dimension_names = [text]

    for separator in separators:
        next_names = []
        for name in dimension_names:
            next_names.extend(name.split(separator))
        dimension_names = next_names

    return [name.strip() for name in dimension_names if name.strip()]

def parse_behaviour_dimension_reply(user_reply, rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Parses the user's requested behavioural dimensions.

    Valid replies:
        - ALL_PROMPTS
        - PROVIDED_PROMPTS: DIMENSION_NAME, OTHER_DIMENSION_NAME
        - DIMENSION_NAME, OTHER_DIMENSION_NAME
        - OWN_PROMPT: custom question
        - PROVIDED_PROMPT: DIMENSION_NAME; OWN_PROMPT: custom question

    Returns:
        dimensions_of_interest: list of exact rubric dimension names, plus
            'OWN_PROMPT' if the user supplied a custom prompt.
        selected_rubric: rubric dictionary containing only selected dimensions.

    Raises:
        ValueError: if any provided dimension is not exactly in the rubric, or
            if OWN_PROMPT is present but has no prompt text.
    '''
    if not user_reply or not user_reply.strip():
        raise ValueError("No behavioural dimensions were provided.")

    reply = user_reply.strip()
    reply_upper = reply.upper()
    own_prompt_text = None

    if 'OWN_PROMPT:' in reply_upper:
        own_prompt_index = reply_upper.index('OWN_PROMPT:')
        own_prompt_text = reply[own_prompt_index + len('OWN_PROMPT:'):].strip()
        reply = reply[:own_prompt_index].strip()
        reply_upper = reply.upper()

        if not own_prompt_text:
            raise ValueError("OWN_PROMPT was included, but no custom prompt was provided after 'OWN_PROMPT:'.")

    include_all_prompts = 'ALL_PROMPTS' in reply_upper
    provided_text = reply

    if reply_upper.startswith('PROVIDED_PROMPT:'):
        provided_text = reply[len('PROVIDED_PROMPT:'):].strip()
    elif reply_upper == 'PROVIDED_PROMPT':
        provided_text = ''
    elif reply_upper.startswith('PROVIDED_PROMPT'):
        provided_text = reply[len('PROVIDED_PROMPT'):].strip(' :\n\t')

    provided_text_for_validation = re.sub('ALL_PROMPTS', '', provided_text, flags=re.IGNORECASE)
    dimension_names = _split_dimension_names(provided_text_for_validation)
    ignored_markers = {'PROVIDED_PROMPT', 'ALL_PROMPTS'}
    requested_dimensions = [name for name in dimension_names if name.upper() not in ignored_markers]

    invalid_dimensions = [name for name in requested_dimensions if name not in rubric]
    if invalid_dimensions:
        available_dimensions = ', '.join(rubric.keys())
        raise ValueError(
            "Invalid behavioural dimension(s): "
            f"{', '.join(invalid_dimensions)}. "
            "Please use exact dimension names from the rubric. "
            f"Available dimensions are: {available_dimensions}"
        )

    if include_all_prompts:
        dimensions_of_interest = list(rubric.keys())
    else:
        dimensions_of_interest = requested_dimensions

    selected_rubric = {dimension: rubric[dimension] for dimension in dimensions_of_interest}

    if own_prompt_text:
        dimensions_of_interest.append('OWN_PROMPT')
        selected_rubric['OWN_PROMPT'] = [own_prompt_text]

    if not selected_rubric:
        raise ValueError("No valid behavioural dimensions or own prompt were provided.")

    return dimensions_of_interest, selected_rubric


def ask_for_behaviour_dimensions(rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Interactive helper that asks the user which rubric dimensions to analyse.
    '''
    display_behaviour_dimension_options(rubric)
    user_reply = input('\nEnter your selected dimensions or prompt option: ')
    return user_reply
    #return parse_behaviour_dimension_reply(user_reply, rubric)

def text_to_action_log (text_input):

    '''
    Timing is depedent on the input: 
        If timing is provided alongside the text input, return an action log alongside the times at which they occurred. 
        Else, create an action log without a corresponding time record. (Can later analyse with all behaviour categories in rubric other than time.
            In this case, the timing recorded will be qualitative; if there are cues towards duration of actions or relative action times
    '''
    prompt = f"""Convert the following text input into a structured action log, recording each individual action seperately.
        
        If text input has explicit timestamps, for each action give its step in the sequence, its timestamp and short description of the action.
        Only include actions that appear in the text, and keep as much of the text_input as possible.
    
        If text input does not have explicit timestamps but does have time cues or duration cues for an action, give its steps in the sequence, the action, the time/ duration cue mentioned in the text, and a short description of the action

        If text input does not have any timestamps or time cues or duration cues, give its step in the sequence and a short description of the action.
        
        Only include and analyse what is literally given in the text input, do not make up or invent times, and leave the 'time_stamp / time_cue" response empty.
        Text input: {text_input}

        
        Return JSON: {{
            "action_log" : [ {{
                "step": 0,
                "action": ""
                }} ]
            }}""" 
    
    response = client.generate(model=model, prompt=prompt, format='json', think=False, options={'temperature':0})
    return json.loads(response['response'])['action_log']
    #response_text = response['response'].strip()
    #parsed_response = json.loads(response_text)
    #return parsed_response['action_log']

def ask_for_text_input():
    '''
    Interactive helper that asks the user which text to analyse.
    Returns the action log to be inputted into te behavioural analysis function
    '''
    user_reply = input('\nEnter your text input to be analysed (enter as one line): ')
    action_log = text_to_action_log(user_reply)
    return action_log 



# function to send the prompt to the Ollama API and get the response
def get_behaviour_analysis(text_input, rubric=BEHAVIOUR_CATEGORY_RUBRIC, user_dimension_reply=None, dimensions_of_interest = None): 
    # Add the text input to the prompt
    ''' 
        The input log is assumed to be in the form of a structured log (detailed events with timestamp for each action)
        of the simulation. 
        The function will preprocess the text input to extract the relevant information for identifying the state of the simulation at each time step. These cover Intentionality, 
        Coherence, Agency, Adaptability, Routine and Variability, Practical Know-How, Imperfection, Preferences and Non-Optimal behaviour, Emotional Expression, Error and Error
        Recovery, Temporal Realism, Micro-Behaviour presence, and Social Interactions. 
        The function will identify the state of the simulation at each time step based on the information extracted from the text input, 
        including agents actions, movements, interactions with the environment and other agents, time stamps, time taken for each action and movement, task progress, and 
        emotional state of the agent.
        The function will then use this information to identify patterns in agent behaviour and rank them on a scale from 10 (human) to 0 (generated). These patterns covered by 
        the prompts include Intentionality, Coherence, Agency, Adaptability, Routine and Variability, Practical Know-How, Imperfection, Preferences and Non-Optimal behaviour, 
        Emotional Expression, Error and Error Recovery, Temporal Realism, Micro-Behaviour presence, and Social Interactions. 

        
        #Step 1: REMOVED PROMPT FROM USER PROMPT
        #- If text_input is not already in a behavioural action-log format, literally and precisely convert it into a behavioural action log. 
        #- Record each seperate observable action taken and the timestep at which actions occur.
        #- Only include actions explicitly present in the transcript
        #- Do not invent, assume or ass actions that are not recorded
    '''

    ''' 
    Input: 
        dimensions: The behavioural dimensions the user wishes to analyse. 
            Possible dimensions include Intentionality, Coherence, Agency, Adaptability, Routine and Variability, Practical Know-How, Imperfection, Preferences and Non-Optimal 
            behaviour, Emotional Expression, Error and Error Recovery, Temporal Realism, Micro-Behaviour presence, and Social Interactions. 
        
        text_input: A description of the agents actions and movements expected in natural language format. Expected as a 
    '''
    #define prompt

    if user_dimension_reply is not None:
        dimensions_of_interest, rubric = parse_behaviour_dimension_reply(user_dimension_reply, rubric)
    elif dimensions_of_interest is None:
        dimensions_of_interest = list(rubric.keys())



    #Define the prompt for the behavior discriminator
    #the initial messages to set the context for the behaviour discriminator. 
        #Modify the 'system' role to include specific instructions or examples for the behaviour of the discriminator to follow when analyzing the behaviour transcript.
        #Modify the 'user'role by appending the text input (the behaviour transcript) to the messages list. The text input should be a description of the agents actions 
        #and movements expected in natural language format.

        #Seperate steps 1 and 2 call

    system_prompt = "You are a behaviour discriminator. Your role is to analyse behaviour using a provided behaviour rubric, and score how human-like the agents actions are on a scale from 0 to 10, where 0=generated-like and 10=clearly human-like."
    
    user_prompt = f"""Analyse the following behaviour input, using steps outlined below and the provided rubric. 

                Step 1: For each category in the behavioural rubric:
                -Answer each question in the category applied to the behavioural action log 
                - Only include actions explicitly present in the input. Do not infer or invent acions such as hidden actions, intentions, locations, emotions, mistakes, missing steps
                - Do not invent or assume  actions that are not recorded
                - Give each question a score between 0 to 10, where 0= strongly generated-like, 5=ambiguous, and 10= strongly human-like 
                - If the category is 'social_behaviour', only consider if there is a presence of another agent. Else give a a human-likeness scoring of 5.
                - If the category is 'timing', only consider inputs which have time logs for actions. If the action log does not include times, provide a scoring of 5.
                - If a behaviour has insufficient evidence, assign a score of 5 rather than assuming it is generated-like or human-like. Provide this as the evidence for the scoring.
                - Provide what from the actions in the transcript contributed to the score given, including for categories scored with insufficient evidence  
                - Calculate the average of the scores in the category
                - Classify the category as 'human-like' if the category average >= 7
                - For scores above 7 that fall under human-like provide explicit evidence from the behavioural action log that demonstrates that behaviour. If no explicit evidence exists assign it a score of 5.
                - Classify the category as 'generated-like' if the category average <7
                - For scores below 7 that fall under generated-like provide explicit evidence from the behavioural action log 

                Step 2: 
                - Calculate the overall human-likeness score for the behavioural action log: calculate the average of the average scores of the scored categories.
                - Calculate a percentge for the overall human-likeness score considering all the categories
                - Classify the inputed text as 'human' if the overall human-likeness percentage >=70
                - Classify the inputted text as 'generated' if the overall human-likeness percentage <70

                Step 3:
                -Grouped the categories by their classification, into human-like categories and generated-like categories.

                Behaviour input: 
                {text_input}

                behaviour rubric: 
                {rubric}

                Return valid JSON only:
                For "categories", return an entry for each category in the behavioural rubric. Do not skip or omit any category even if no evidence is available.
                {{"overall_human_likeness_percentage": 0, 
                "classification": "",
                "summary": "",
                "categories": [ {{
                    "category": "",
                    "average_score_of_category": 0,
                    "human_or_generated_label": "",
                    "score_reasoning": "",
                    "score_evidence": ""
                    }} ] }}
    """

    # Send the prompt to the Ollama API
    #if using 'qwen' model, include the variable 'think' (, think = False ). Else remove 
    init_response = client.generate(model=model, system = system_prompt, prompt= user_prompt, format= "json", think=False, options={"temperature": 0}) #temperature keeps the results reproducible  
    response = init_response["response"]

    parsed_response = json.loads(response)
    parsed_response['dimensions_of_interest'] = dimensions_of_interest
    
    return parsed_response


####

#ASK FOR BEHAVIOUR DIMENSIONS 
#USE INPUTTED BEHAVIOUR DIMENSIONS AS USER_DIMENSION_REPLY INPUT 


###Put this into __init__.py file 
def get_behavioural_analysis_interactive (rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    user_input_text_reply = ask_for_text_input()
    user_dimensions_REPLY = ask_for_behaviour_dimensions(rubric)
    analysis_output = get_behaviour_analysis(text_input=user_input_text_reply, rubric= rubric, user_dimension_reply=user_dimensions_REPLY)
    return analysis_output 



####



result_interactive_input = get_behavioural_analysis_interactive(rubric=BEHAVIOUR_CATEGORY_RUBRIC)
print('RESULT - INTERACTIVE USER INPUT', json.dumps(result_interactive_input, indent=2)) 


####

import pandas as pd
from pathlib import Path

#csv_path = Path(__file__).with_name("EPIC_100_validation_dataset.csv")

#df = pd.read_csv(csv_path, usecols=['start_timestamp', 'stop_timestamp', 'narration'])

#print (df)

if __name__ == "__main__": #only runs if this script is directly run instead of imported as a module


    # test_transcript_1 = """
    # [07:42:00] Agent enters kitchen.
    # [07:42:05] Agent fills kettle with water.
    # [07:42:10] Agent turns on kettle.
    # [07:42:15] Agent retrieves mug from cupboard.
    # [07:42:20] Agent places teabag in mug.
    # [07:43:20] Agent pours boiling water into mug.
    # [07:43:25] Agent adds milk.
    # [07:44:25] Agent removes teabag.
    # [07:44:30] Agent drinks tea.
    # [07:44:35] Agent places mug in sink.
    # # """

    # result_1 = get_behaviour_analysis(text_input=test_transcript_1, user_dimension_reply="ALL_PROMPTS", rubric=BEHAVIOUR_CATEGORY_RUBRIC)
    # print('RESULT 1', json.dumps(result_1, indent=2))   # pretty-print if it parsed to a dict

    #test_transcript_2 = """
    # [07:42:13] Agent walks into kitchen, flicks light switch, light doesn't come on, flicks it again.
    # [07:42:20] Agent fills kettle, slightly overfills, tips a bit back out into sink.
    # [07:42:34] Agent sets kettle to boil, leans against counter.
    # [07:42:51] Agent opens cupboard, looks for mug, moves two mugs aside, picks the one at the back.
    # [07:43:10] Agent gets distracted by phone, scrolls for about 40 seconds.
    # [07:43:55] Agent looks up as kettle clicks off, realises it boiled a while ago.
    # [07:44:02] Agent drops teabag in mug, pours water, splashes slightly.
    # [07:44:20] Agent forgets the milk, opens fridge after already pouring, adds it. 
    # [07:45:30] Agent fishes teabag out, squeezes it against the side, drops it in bin, misses, picks it up.
    # [07:46:00] Agent sips, it's too hot, sets it down, waits.
    # [07:48:30] Agent drinks slowly while staring out the window.
    # """

    # result_2 = get_behaviour_analysis(text_input=test_transcript_2, user_dimension_reply="PROVIDED_PROMPT: ALL_PROMPTS", rubric=BEHAVIOUR_CATEGORY_RUBRIC)
    # print('RESULT 2', json.dumps(result_2, indent=2))   # pretty-print if it parsed to a dict







