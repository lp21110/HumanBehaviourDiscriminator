
'''
Author: xxx email
 
File: xxx.py
 
Description:
'''
import ollama 
import json
#import requests


#initialise Ollama client 
client = ollama.Client()

#define model 
#model = 'llama3.2:3b'
model = 'llama3.1:8b'
#Input: a text input describing the agents actions and movements expected in natural language format. 
    #The text input is expected to be in the form of a transcript (captures everything that happens, a raw recording of the simulation) 
    # OR a structured log (mainly specific, data-rich events) of the simulation.
#Extract relevant information from the text input to identify the state of the simulation at each time step, 
    #this includes agents actions, movements, interactions with the environment and other agents, time stamps, time taken for each action and movement, task progress, 
    #and emotional state of the agent
#Using the extracted information on the states of the agent behaviour at each time step, rank the human-ness of the behaviour on a scale from 10 (human) to 0 (generated)
        #The ranking should be for each given prompt, which overall cover the behavioural dimensions of Intentionality, Coherence, Agency, Adaptability, Routine and 
        # Variability, Practical Know-How, Imperfection, Preferences and Non-Optimal behaviour, Emotional Expression, Error and Error Recovery, Temporal Realism, 
        # Micro-Behaviour presence, and Social Interactions.



#1. Define the different Dimensions and the prompts for each dimension - OBSERVABLE AND BEHAVIOUR-FOCUSED 
    #DO we want these inputs as questions or statements? (currently questions)
    # (questions might be more effective for the model to follow and answer, but statements might be more effective for the model to follow and identify the relevant information in the text input)

#A dictionary of the different behaviours that we are analysing and providing as prompts for the model to use
BEHAVIOUR_CATEGORY_RUBRIC = {
    #INTENTIONALITY PROMPTS: intentionality of the agent's behaviour, including the presence of goals, plans, and motivations behind their actions.  Rank the intentionality on a scale from 10 (human) to 0 (generated)."
    'INTENTIONALITY_PROMPTS' : ['Is there a presence of reason or motivation behind the agents actions and movements?', 
                          'Does the agent exhibit goal-directed behavior?', #Does the behaviour build towards a larger goal? 
                          'Does the goal fit the scenario context?', 
                          'Are the agents actions coherent across time steps?', 
                          'Does the agent show evidence of planning or foresight in their actions, any long-term goals?', 
                          'Does the agent exhibit behavior that contributes towards short-term goals?',
                          'Does the agent exhibit behavior that contributes towards long-term goals?'
    ],   


    #ADAPTABILITY PROMPTS: adaptability of the agent's behaviour. Dealing with uncertainty, ability to improv, re-plan or update plans as they happen.
    'ADAPTABILITY_PROMPTS' : ['Does the agent show evidence of adapting their behavior in response to changes in the environment or unexpected events?',
                        'Does the agent change its behaviour if it has previously already encountered a similar experience?',#Does the agent show evidence of learning from past experiences and applying that learning to new situations?
                        'Does the agent show evidence of adjusting their behavior based on feedback from the environment or other agents?',
                        'Does the agent show evidence of flexibility in their behavior, such as being able to switch between different strategies or approaches to achieve their goals?',
                        'Does the agent show evidence of adjusting or modifying its behaviour as the context and situation changes?',
                        'Does the agent show evidence of improvisation or creativity in their actions?', 
                        'Does the agent show evidence of re-planning or updating their plans as they happen?',
                        'Does the agent show evidence of updating goals when encountering new information or context?', #Real-time decision-making and goal updating
    ],


    #ROUTINE AND VARIABILITY PROMPTS: routine and variability in the agent's behaviour. Testing for repetitive actions or patterns, as well as the ability for variability in their behaviour.
    #Is there the appropriate proportion of both routine and variable behaviours present?
    'ROUTINE_PROMPTS' : ['Does the agent show evidence of repetitive actions or patterns in their behavior, that might indicate routine behaviour?', # double check the wording of this one 
                   #i.e. danger of this prompt is that it might be picking up on routine behaviour, which can be a sign of human and non-human behaviour.Reword this prompt to be more specify what kind of routine behaviour we are looking for.
                   'Does the agent show competence in performing routine tasks?', 
                    'Does the agents actions show familiarity and intrinsic knowledge of how to perform routine, daily tasks, or does it show evidence of learning how to perform routine tasks through trial and error?',
                    'Does the agent show an ability to perform routine tasks with a degree of variability, such as being able to perform the same task in different action sequences or under different conditions?',
                    'Does the agent exhibit variability in their behavior and does not show reliance on repetitive actions or patterns?',
                    'Do any of the actions or sequence of actions seem like automated action?'
    ],

    #IMPERFECTIONS, ERRORS, VARIABILITY
    ##Does 'imperfect', 'perfect', 'hesitation', 'forgetting' etc need to be explicitely defined? i.e. how do you differentiate forgetting with distraction
    'HUMAN_IMPERFECTIONS_PROMPTS' : ['Does the agent make any mistakes, undertake imperfect action?', #what classifies as a 'mistake'?
                                 'Is there any deviation from the initial, desired task or is it a perfect exection of the inferred task?', # potential issue - the task could be inferred wrong, and then the execution wrongly determined as 'correct'
                                 'Are there signs of hesisation in their carrying out of the task',#specific examples of deviation
                                 'Does the agent show signs of forgetfulness in their action sequences?',
                                 'Does the agent show signs of changing their minds or their initial course of action?',
                                 'If the agent did perform mistakes, is there a range in their scale of mistakes?',
                                 'Does the agent shows signs of getting realistically distracted from the inferred initial course of action?',
                                 're there interruptions in behaviour and action flow (in contrast to a smooth flow)?'
    ],

    #EMOTIONS
    'PRESENCE_OF_EMOTION_PROMPTS' : ['Does the agent demonstrate behaviour that is emotionally-charged?',#does the agent show behaviour that is not fully explainable, but rather due to feelings/ vibes?
                                     'Does the agent show behaviour that is not purely rational?',
                                     'Does the agent show behavioural choices that are not fully explainable?',
    
    ],

    'PREFERENCES_AND_NON_OPTIMAL_BEHAVIOUR' : ['Does the agents behaviour show proof of choosing preference over the rule-binding, optimal actions?',
                                               'Does the agent behaviour display sub-optimal behavior?',
                                               #'Does the agent have multiple competing goals?'
                                               'Does the agent show any personal indivuality/ quirks that are not of a typical human?', #what defines a 'typical human'?  
                                               'Does the agents behaviour show small variations in action sequences that can be inferred as routine behaviour?'
    ],

    'RECOVERY_PROMPTS' : ['If the agent shows behaviour that falls under mistakes, do the mistakes appear too curated?',
                          'If the agent shows signs of mistakes, are the agents able to recorect their path of action, are they able to revover from a potential error?', #'relatively quickly'? how fast is quick - define if including feed as a prompt
                          'If the agent shows behaviour suggestive of mistake, does the recovery from their mistake seen curated?'
    ],

    'TIMING' : ['Is there a realistic variation in the times between actions; is there enough variation in timing or is it too evenly spaced out?',
                'Does the timing of the actions and time taken for each action show a realistic depiction of sporadicity?',
                'Do the times taken for each action correspond with the time generally required for the actions?',
                'Are the times taken to perform tasks optimised times or realistic?'
    ],

    'MICRO-BEHAVIOUR' : ['Does the agents behaviour perform any automatic, subconscious or micro-behaviours, behaviours with no outward goal? Some examples include yawning, stretching, fidgeting, sighing, flinching, startling, hiccups etc.',
    ]
}
                                

# function to send the prompt to the Ollama API and get the response
def get_behavior_analysis(text_input, rubric): # can later incorporate a dimensions input where you can choose which dimensions you wish to analyse 
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

    '''

    ''' 
    Input: 
        dimensions: The behavioural dimensions the user wishes to analyse. 
            Possible dimensions include Intentionality, Coherence, Agency, Adaptability, Routine and Variability, Practical Know-How, Imperfection, Preferences and Non-Optimal 
            behaviour, Emotional Expression, Error and Error Recovery, Temporal Realism, Micro-Behaviour presence, and Social Interactions. 
        
        text_input: A description of the agents actions and movements expected in natural language format. Expected as a 
    '''
    #define prompt
    #Define the prompt for the behavior discriminator
    #the initial messages to set the context for the behaviour discriminator. 
        #Modify the 'system' role to include specific instructions or examples for the behaviour of the discriminator to follow when analyzing the behaviour transcript.
        #Modify the 'user'role by appending the text input (the behaviour transcript) to the messages list. The text input should be a description of the agents actions 
        #and movements expected in natural language format.
    system_prompt = "You are a behavior discriminator, recognising patterns in agent behaviour and ranking them on a scale from 10 (human) to 0 (generated)."
    user_prompt = f"""Analyse the following behaviour transcript, using the provided rubric and steps outlined below. 

                First, if not already in a transcript format, literally and precisely convert the transcript into a behavioural action log. 
                Record each seperate action taken and the timestep at which each action occurs.

                Secondly, use the following prompts for each category in the behaviour rubric, using the behavioural action log: 
                - answer and provide a score between 0 (completely generated) to 10 (human behaviour) for each question in this category
                - provide clear evidence from the transcript as to why this score was given for this category
                - calculate and return the average of all the scores within the category 
                - If the average category score is above 6, classify it as a human input. Else, if category average is under 6 then classify it as generated input
                        
                Only consider actions that have been literally recorded in the transcript, and do not make up new actions. If a behaviour is not present, score it accordingly. 
                Third, combine and find the average of all overall category scores for an overall human-likeness percentage. 
                If the overall percentage is less than 60%, classify the input as generated  
                If the overall percentage is greater than 60%, classify the input as human 

                Output the categories, grouped into two: categories scoring agent-like and the categories scoring human-like

                Behaviour transcript: 
                {text_input}

                behaviour rubric: 
                {rubric}

                Return JSON:
                {{'overall_human_score': 0, 
                'classification': '',
                   'summary': '',
                   'categories': [ {{
                        'category': '',
                        'average_score': 0,
                        'human_or_generated_label': '',
                        'label_evidence_reasoning': ''
                    }} ] }}
    """

    # Send the prompt to the Ollama API
    response = client.generate(model=model, system = system_prompt, prompt= user_prompt, format= 'json', options={'temperature': 0}) #temperature keeps the results reproducible  
    return json.loads(response['response'])

#------------------------------------------------------------------------------------
#TEST TRANSCRIPT:

import pandas as pd
from pathlib import Path

csv_path = Path(__file__).with_name("EPIC_100_validation_dataset.csv")

df = pd.read_csv(csv_path, usecols=['start_timestamp', 'stop_timestamp', 'narration'])

print (df)

if __name__ == "__main__":
    test_transcript_1 = """
    [07:42:00] Agent enters kitchen.
    [07:42:05] Agent fills kettle with water.
    [07:42:10] Agent turns on kettle.
    [07:42:15] Agent retrieves mug from cupboard.
    [07:42:20] Agent places teabag in mug.
    [07:43:20] Agent pours boiling water into mug.
    [07:43:25] Agent adds milk.
    [07:44:25] Agent removes teabag.
    [07:44:30] Agent drinks tea.
    [07:44:35] Agent places mug in sink.
    """

    result_1 = get_behavior_analysis(test_transcript_1, BEHAVIOUR_CATEGORY_RUBRIC)

    print('RESULT 1', json.dumps(result_1, indent=2))   # pretty-print if it parsed to a dict

    test_transcript_2 = """
    [07:42:13] Agent walks into kitchen, flicks light switch, light doesn't come on, flicks it again.
    [07:42:20] Agent fills kettle, slightly overfills, tips a bit back out into sink.
    [07:42:34] Agent sets kettle to boil, leans against counter.
    [07:42:51] Agent opens cupboard, looks for mug, moves two mugs aside, picks the one at the back.
    [07:43:10] Agent gets distracted by phone, scrolls for about 40 seconds.
    [07:43:55] Agent looks up as kettle clicks off, realises it boiled a while ago.
    [07:44:02] Agent drops teabag in mug, pours water, splashes slightly.
    [07:44:20] Agent forgets the milk, opens fridge after already pouring, adds it. 
    [07:45:30] Agent fishes teabag out, squeezes it against the side, drops it in bin, misses, picks it up.
    [07:46:00] Agent sips, it's too hot, sets it down, waits.
    [07:48:30] Agent drinks slowly while staring out the window.
    """
    result_2 = get_behavior_analysis(test_transcript_2, BEHAVIOUR_CATEGORY_RUBRIC)

    print('RESULT 2', json.dumps(result_2, indent=2))   # pretty-print if it parsed to a dict



#print (get_behaviour_analysis (text_input))

#-------------------------------------------------------------
 #Print response
##print ('Analysis output:')
##print (response.response)
    
