'''
Author: xxx email
 
File: xxx.py
 
Description:
'''

import requests
import json

#base URL for local Ollama API 
url = "http://localhost:11434/api/chat"


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
'HUMAN_IMPERFECTIONS_PROMPTS' : ['Does the agent make any mistakes, undertake imperfect action?', #what classifies as a 'mistake'?
                               
                               
                               ],

#RECOVERY
'ERROR_RECOVERY_PROMPTS' : [''
                          ]

}

#2. Append these prompts to the initial prompt messages list under the 'system' role, to set the context for the behaviour discriminator to follow when analyzing the 
    #behavioural transcript
    ### Could later further modify by choosing which specific dimensions to analyse (instead of all of them) by selecting the relevant prompts to append to the initial prompt 
    #messages list.


#3. 


#Define the prompt for the behavior discriminator
prompt = {
    "model": "llama3", #the Ollama model to use for the behaviour discriminator (can use other models available in Ollama)
    "messages": [ #the initial messages to set the context for the behaviour discriminator. 
        #Modify the 'system' role to include specific instructions or examples for the behaviour of the discriminator to follow when analyzing the behaviour transcript.
        #Modify the 'user'role by appending the text input (the behaviour transcript) to the messages list. The text input should be a description of the agents actions 
        #and movements expected in natural language format.
        {
            "role": "system",
            "content": "You are a behavior discriminator, recognising patterns in agent behaviour and ranking them on a scale from 10 (human) to 0 (generated)."
        },      
        {
            "role": "user",
            "content": ""Analyze the following behaviour transcript, using the rubric below. 

            For each category in the rubric: 
            - answer each question and provide a score from 0 (completely generated) to 10 (human behaviour)
            - provide a reasoning of why from the transcript
            - give an overall category-average score, and whether for this category the behaviour seemed agent-like (below 6) or human-like (6 or above)
        
            Then give an overall human-likeness percentage combining all the categories 

            If the percentage is less than 60%, classify the input as generated  

            If the percentage is greater than 60%, classify the input as human 

            Output the categories, grouped into two: categories scoring agent-like and the categories scoring human-like

            Behaviour transcript: 
            {text_input}

            Return your answer as JSON in the following structure:

            {{'time'}}


             and identify the state of the simulation at each time step:""
        }
    ]
}



# function to send the prompt to the Ollama API and get the response
def get_behavior_analysis(input_log, dimensions):
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

# input prompt here: 
#Define the prompt for the behavior discriminator
    prompt = {
        "model": "llama3", #the Ollama model to use for the behaviour discriminator (can use other models available in Ollama)
        "messages": [ #the initial messages to set the context for the behaviour discriminator. 
        #Modify the 'system' role to include specific instructions or examples for the behaviour of the discriminator to follow when analyzing the behaviour transcript.
        #Modify the 'user'role by appending the text input (the behaviour transcript) to the messages list. The text input should be a description of the agents actions 
        #and movements expected in natural language format.
            {
                "role": "system",
                "content": "You are a behavior discriminator, recognising patterns in agent behaviour and ranking them on a scale from 10 (human) to 0 (generated)."
            },      
            {
                "role": "user",
                "content": ""Analyze the following behaviour transcript, using the rubric below. 

                First, convert the transcript into a behavioural action log, recognise and record each seperate action taken and the timestep at which the action occurs.

                Secondly, use the following prompts for each category in the rubric, referencing the behavioural action log: 
                - answer and provide a score between 0 (completely generated) to 10 (human behaviour) for each question in this category
                - provide a reasoning of why this score was given from the transcript
                - give an overall category score calculated by the average and whether for this category the behaviour seemed agent-like (below 6) or human-like (6 or above)
        
                Third, combine and find the average of all overall category scores for an overall human-likeness percentage. 
                If the overall percentage is less than 60%, classify the input as generated  
                If the overall percentage is greater than 60%, classify the input as human 

                Output the categories, grouped into two: categories scoring agent-like and the categories scoring human-like

                Behaviour transcript: 
                {text_input}

                Return your answer as JSON in the following structure:

                {{ 
                   'overall_human_score': 0, 
                   'summary': '',
                   'time_steps': [
                       {{
                            'time_step': '',
                            'observed_behaviour': '',
                           # 'inferred_states at action': '', #i.e. what the agent seems to be thinking - not really related to anaysing physical behaviour?
                            'human_scoring_categories': '', #list of categories that scored as a human input
                            'human_likeness_evidence': '',
                            'generated_likeness_evidence':'',
                            'generated_scoring_categories': '', #list of categories that scored as generated inputs 
                            'overall_score'
                       }}
                   ]
               }},

                    
                    'time'}}




    # Send the prompt to the Ollama API
    response = requests.post(url, json=prompt)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None