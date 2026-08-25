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
            - If the category is 'SOCIAL', only consider it when another agent is present. Otherwise, there is insufficient evidence.
            - If the category is 'TIMING', only consider it when the action log contains action times. Otherwise, there is insufficient evidence.
            - If there is insufficient evidence for the current category, set "average_score_of_category" to "N/A". Do not assign a numeric score.
            - When returning "N/A", explain why evidence is insufficient in both "score_reasoning" and "score_evidence".
            - When evidence is sufficient, calculate the average of the prompt scores in the category.

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

        parsed_response["category"] = dimension
        returned_score = parsed_response.get("average_score_of_category")
        if isinstance(returned_score, str) and returned_score.strip().upper() == "N/A":
            parsed_response["average_score_of_category"] = "N/A"
            parsed_response["human_or_generated_label"] = "N/A"
        else:
            try:
                average_score = float(returned_score)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"The model returned an invalid average score for {dimension}."
                ) from exc

            if not 0 <= average_score <= 10:
                raise ValueError(
                    f"The model score for {dimension} must be between 0 and 10."
                )

            parsed_response["average_score_of_category"] = average_score
            parsed_response["human_or_generated_label"] = (
                "human-like" if average_score >= 7 else "generated-like"
            )

        #add the current category analysis to list of categories to calculate overall scorings and return analysis to user
        categories.append(parsed_response)


    scored_categories = [
        category
        for category in categories
        if isinstance(category["average_score_of_category"], (int, float))
    ]
    if scored_categories:
        overall_average_score = sum(
            category["average_score_of_category"] for category in scored_categories
        ) / len(scored_categories)
        overall_human_likeness_percentage = round(overall_average_score * 10, 2)
        final_overall_classification = (
            "human-like" if overall_human_likeness_percentage >= 70 else "generated-like"
        )
    else:
        overall_human_likeness_percentage = "N/A"
        final_overall_classification = "N/A"


    if not include_summary:
        return {
            "categories": categories,
            "dimensions_of_interest": dimensions_of_interest,
        }

    if not scored_categories:
        final_output_summary = (
            "No overall human-likeness score was calculated because all selected "
            "categories had insufficient evidence."
        )
    else:
        # Call the model for an overall summary using only categories with numeric scores.
        user_prompt_2_summary = f"""Using the categories in the list 'categories', return a summary for the overall human-likeness score, including reasoning 
        and evidence for the score given. Only consider the scored categories in the list 'categories'. 
    
        overall human-likeness percentage:
        {overall_human_likeness_percentage}
        
        categories: 
        {json.dumps(scored_categories, indent=2)}

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


