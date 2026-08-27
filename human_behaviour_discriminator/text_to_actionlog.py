from .model_provider import get_model_provider


def text_to_action_log(text_input):

    '''
    Role: From the text input, find the state of the agent at each time-step for the behavioural analysis. 
        'Action' entails any movements, interactions with the environment and other agents. ALso records time stamps, time taken for each action and movement, task progress
    
    Whether timing is included is depedent on the input: 
        If timing is provided alongside the text input, return an action log alongside the times at which they occurred. 
        Else, create an action log without a corresponding time record. (Can later analyse with all behaviour categories in rubric other than time.
            In this case, the timing recorded will be qualitative; if there are cues towards duration of actions or relative action times
    '''
    
    prompt = f"""Convert the following text input into a structured action log, recording each individual action seperately.
        
        If text input has explicit timestamps, for each action give its step in the sequence, its timestamp and short description of the action.
        Only include actions that appear in the text, and keep as much of the text_input as possible.
        
        timestamps are the times i.e. mm:ss (minute:second) at which the action started (time_start), and at which the action ended (time_end).
        If text input does not have explicit timestamps but does have time cues or duration cues for an action, give its steps in the sequence, the action, the time/ duration cue mentioned in the text, and a short description of the action

        If text input does not have any timestamps or time cues or duration cues, give its step in the sequence and a short description of the action.
        
        Only include and analyse what is literally given in the text input, do not make up or invent times, and leave the 'time_start / time_end" response empty if not mentioned.
        Text input: {text_input}

        
        Return JSON using these keys: {{
            "action_log" : [ {{
                "step": 1,
                "time_start":"",
                "time_end":"",
                "action": ""
                }} ]
            }}""" 
    
    model_provider = get_model_provider()
    response = model_provider.generate_json(
        system_prompt=(
            "You convert behaviour descriptions into structured action logs. "
            "Return only the requested JSON object."
        ),
        user_prompt=prompt,
    )

    if "action_log" not in response or not isinstance(response["action_log"], list):
        raise ValueError("The model response did not contain an action_log list.")

    return response["action_log"]

