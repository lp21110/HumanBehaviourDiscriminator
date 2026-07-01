from ast import Return
import json 

from .ollama_config import client, model
from .behaviour_rubric import BEHAVIOUR_CATEGORY_RUBRIC
from .identify_behaviour_dimensions import parse_behaviour_dimension_reply


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

    system_prompt = "You are a behaviour discriminator. Your role is to analyse behaviour using a provided behaviour rubric, and score how human-like the agents actions are on a scale from 0 to 10, where 0=generated-like and 10=clearly human-like."
    
    # categories will contain the average score for each category, and reasoning and evidence for the score given.
    #maintain as list, then convert into JSON format at the end of the function (along with overall human-likeness score and classification)
    categories = []
    for dimension in rubric: 
        
        #calculating the average score for each dimension with LLM, but the overall human-likeness score and classification will be calculated in the function itself.
        user_prompt = f"""Analyse the following behaviour input, using steps outlined below and the provided dimension. 

                 
            NEW Step 1: 
            - Apply and answer the prompts in the current dimension to the behavioural action log
            - Only include actions explicitly present in the input. Do not infer or invent acions such as hidden actions, intentions, locations, emotions, mistakes, missing steps
            - Do not invent or assume actions that are not recorded
            - Give each question a score between 0 to 10, where 0= strongly generated-like, 5=ambiguous, and 10= strongly human-like 
            - If the category is 'social_behaviour', only consider if there is a presence of another agent. Else provide a scoring of 5.
            - If the category is 'timing', only consider inputs which have time logs for actions. If the action log does not include times, provide a scoring of 5.
            - If a behaviour has insufficient evidence, assign a score of 5 rather than assuming it is generated-like or human-like. Provide this as the evidence for the scoring.
            - Provide what from the actions in the transcript contributed to the score given, including if category is scored with insufficient evidence 
            - Calculate the average of the prompt scores in the category

            Behaviour input: 
            {text_input}

            Behaviour dimension:
            {dimension}

            Dimension prompts: 
            {rubric[dimension]}
                
            Return valid JSON only:
            {{  "category": "{dimension}",
                "average_score_of_category": 0,
                "score_reasoning": "",
                "score_evidence": "" }}
        """

        # Send the prompt to the Ollama API
        #if using 'qwen' model, include the variable 'think' (, think = False ). Else remove 
        init_response = client.generate(model=model, system = system_prompt, prompt= user_prompt, format= "json", think=False, options={"temperature": 0}) #temperature keeps the results reproducible  
        response = init_response["response"] #only wnat the actual text response from LLM instead of entire dicionary returned after a call to the LLM API.

        parsed_response = json.loads(response) #LLM response is parsed into a dictionary format for further processing.
        parsed_response['dimensions_of_interest'] = dimensions_of_interest #add the dimensions of interest to the parsed response

        #use the average category score to classify the category as human-like or generated-like:
        if parsed_response['average_score_of_category'] >= 7: #if the average score is greater than 7, classify as human-like
            parsed_response['human_or_generated_label'] = 'human-like'
        else: #if average score is less than 7, classify as generated-like 
            parsed_response['human_or_generated_label'] = 'generated-like'

        #add the current category analysis to list of categories to calculate overall scorings and return analysis to user
        categories.append(parsed_response)


    #now find the average of the average scores and classify an overall human-likeness score for the given text
    overall_average_score = (sum(category['average_score_of_category'] for category in categories))  / (len(categories)*10)
    overall_human_likeness_percentage = (overall_average_score * 100) #calculate the overall human-likeness percentage for all the categories considered

    #calculate overall human-likeness classification based on average score
    if overall_human_likeness_percentage >= 70:
        final_overall_classification = 'human-like'
    else:
        final_overall_classification = 'generated-like'


    #call LLM for a summary for the score reasoning and evidence for the overall human-likeness score, considering the scored categories in the list 'categories'   
    user_prompt_2_summary = f"""Using the categories in the list 'categories', return a summary for the overall human-likeness score, including reasoning 
        and evidence for the score given. Only consider the scored categories in the list 'categories'. 
    
        overall human-likeness percentage:
        {overall_human_likeness_percentage}
        
        categories: 
        {json.dumps(categories, indent=2)}

        Return valid JSON only: 
        {{'summary': ""}}

    """

    init_response_2_summary = client.generate(model=model, system = system_prompt, prompt= user_prompt_2_summary, format= "json", think=False, options={"temperature": 0}) #temperature keeps the results reproducible  
    response_2_summary = init_response_2_summary["response"]

    parsed_response_2_summary = json.loads(response_2_summary) #LLM response for summary of score reasoning is parsed into dictionary format for further processing.
    final_output_summary = parsed_response_2_summary.get("summary", "" )
    #group all the results together for complete final analysis
    final_analysis = {
        "overall_human_likeness_percentage": overall_human_likeness_percentage,
        "classification": final_overall_classification,
        "classification_summary": parsed_response_2_summary, 
        "categories": categories, 
        "dimensions_of_interest": dimensions_of_interest
    }

    return final_analysis


