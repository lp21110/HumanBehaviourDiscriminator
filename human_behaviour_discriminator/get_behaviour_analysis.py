import json 

from .behaviour_rubric import BEHAVIOUR_CATEGORY_RUBRIC
from .identify_behaviour_dimensions import parse_behaviour_dimension_reply
from .model_provider import get_model_provider


def get_behaviour_analysis(text_input, rubric=BEHAVIOUR_CATEGORY_RUBRIC, user_dimension_reply=None, dimensions_of_interest=None, include_summary=True):
    ''' 
    Input: 
        dimensions: The behavioural dimensions the user wishes to analyse. 
            Possible dimensions include Adaptability, Human Imperfections, Recovery, Preferences and Non-Optimality, Micro-Behaviour, Environmental Context, Physiological 
            context, Attentiveness, Foresight and Social.
        text_input: An action log of the agent's actions and movements. Expected in natural language format
        rubric: The behaviour rubric to use for the analysis, containing prompts for each dimension.
        user_dimension_reply: The user reply to the prompt asking which dimensions to analyse. This can be a list of dimensions, or a custom prompt provided by the user.
        dimensions_of_interest: A list of dimensions to analyse. If None, all dimensions in the rubric will be analysed.
        include_summary: Whether to include a summary of the overall human-likeness score and reasoning for the score. If False, only the category scores will be returned.

    Output:
        Dictionary containing all the details of the final behavioural analysis for the input transcript.
        These include: overall_human_likeness_percentage score, the final classification of human or generated, summary of the classification reasonings, and the rubric categories considered
    '''
    
    if user_dimension_reply is not None:
        dimensions_of_interest, rubric = parse_behaviour_dimension_reply(user_dimension_reply, rubric)
    elif dimensions_of_interest is None:
        dimensions_of_interest = list(rubric.keys())

    if not rubric:
        raise ValueError("At least one behaviour dimension is required.")

    model_provider = get_model_provider()


    #Define the prompt for the behavior discriminator
    #the initial messages to set the context for the behaviour discriminator. 
        #Modify the 'system' role to include specific instructions or examples for the behaviour of the discriminator to follow when analyzing the behaviour transcript.
        #Modify the 'user'role by appending the text input (the behaviour transcript) to the messages list. The text input should be a description of the agents actions 
        #and movements expected in natural language format.

    system_prompt = "You are a behaviour discriminator. Your role is to analyse behaviour using a provided behaviour rubric, and score how human-like the agents actions are on a scale from 0 to 10, where 0=generated-like and 10=clearly human-like."
    
    # categories will contain the average score for each category, and reasoning and evidence for the score given.
    #maintain as list, then convert into JSON format at the end of the function (along with overall human-likeness score and classification)
    categories = []
    for dimension, dimension_prompts in rubric.items():
        
        #calculating the average score for each dimension with LLM, but the overall human-likeness score and classification will be calculated in the function itself.
        user_prompt = f"""Analyse the following behaviour input, using steps outlined below and the provided dimension. 

                 
            NEW Step 1: 
            - Apply and answer the prompts in the current dimension to the behavioural action log
            - Only include actions explicitly present in the input. Do not infer or invent acions such as hidden actions, intentions, locations, emotions, mistakes, missing steps
            - Do not invent or assume actions that are not recorded
            - Give each question a score between 0 to 10, where 0= strongly generated-like, 5=ambiguous, and 10= strongly human-like 
            - If the category is 'SOCIAL', only consider if there is a presence of another agent. Else provide a scoring of 5.
            - If the category is 'TIMING', only consider inputs which have time logs for actions. If the action log does not include times, provide a scoring of 5.
            - If a behaviour has insufficient evidence, assign a score of 5 rather than assuming it is generated-like or human-like. Provide this as the evidence for the scoring.
            - Provide what from the actions in the transcript contributed to the score given, including if category is scored with insufficient evidence 
            - Calculate the average of the prompt scores in the category

            Behaviour input: 
            {text_input}

            Behaviour dimension:
            {dimension}

            Dimension prompts: 
            {dimension_prompts}
                
            Return valid JSON only:
            {{  "category": "{dimension}",
                "average_score_of_category": 0,
                "score_reasoning": "",
                "score_evidence": "" }}
        """

        parsed_response = model_provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        try:
            average_score = float(parsed_response["average_score_of_category"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"The model returned an invalid average score for {dimension}."
            ) from exc

        if not 0 <= average_score <= 10:
            raise ValueError(
                f"The model score for {dimension} must be between 0 and 10."
            )

        parsed_response["category"] = dimension
        parsed_response["average_score_of_category"] = average_score

        #use the average category score to classify the category as human-like or generated-like:
        if average_score >= 7: #if the average score is greater than 7, classify as human-like
            parsed_response['human_or_generated_label'] = 'human-like'
        else: #if average score is less than 7, classify as generated-like 
            parsed_response['human_or_generated_label'] = 'generated-like'

        #add the current category analysis to list of categories to calculate overall scorings and return analysis to user
        categories.append(parsed_response)


    #now find the average of the average scores and classify an overall human-likeness score for the given text
    overall_average_score = sum(
        category["average_score_of_category"] for category in categories
    ) / len(categories)
    overall_human_likeness_percentage = round(overall_average_score * 10, 2)

    #calculate overall human-likeness classification based on average score
    if overall_human_likeness_percentage >= 70:
        final_overall_classification = 'human-like'
    else:
        final_overall_classification = 'generated-like'


    if not include_summary:
        return {
            "categories": categories,
            "dimensions_of_interest": dimensions_of_interest,
        }

    #call LLM for a summary for the score reasoning and evidence for the overall human-likeness score, considering the scored categories in the list 'categories'   
    user_prompt_2_summary = f"""Using the categories in the list 'categories', return a summary for the overall human-likeness score, including reasoning 
        and evidence for the score given. Only consider the scored categories in the list 'categories'. 
    
        overall human-likeness percentage:
        {overall_human_likeness_percentage}
        
        categories: 
        {json.dumps(categories, indent=2)}

        Return valid JSON only: 
        {{"summary": ""}}

    """

    parsed_response_2_summary = model_provider.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt_2_summary,
    )
    final_output_summary = parsed_response_2_summary.get("summary", "")
    #group all the results together for complete final analysis
    final_analysis = {
        "overall_human_likeness_percentage": overall_human_likeness_percentage,
        "classification": final_overall_classification,
        "classification_summary": final_output_summary,
        "categories": categories, 
        "dimensions_of_interest": dimensions_of_interest
    }

    return final_analysis


