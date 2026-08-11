#To chunk input texts that are larger than 9000 characters, and action logs larger than 12000 characters so that they can be analysed by the model and don't exceed the model context.
##for input texts, 9000 characters is chosen as a smaller limit to ensure that the model has enough context to create an accurate action log from the input text.
##for action logs, 12000 characters is chosen as a larger limit so that the model has enough context to analyse each action log cluster accurately

from __future__ import annotations #stores type hints (the data type of a variable) as strings until something explicitely asks for the real data type.
## 'type annotation': indicates what type of value/s a variable is expected to hold, or what type of value/s a function is expected to return without python actually enforcing it
## essentially defines the expected data type of a variable or function return value, but does not enforce it at runtime.

import json
from collections import defaultdict #creates a default dictionary that returns a default value when a key is not present (creates a new key-value pair with the default value (e.g. an empty list) when a non-existent key is accessed)
from typing import Any

from .get_behaviour_analysis import get_behaviour_analysis
from .text_to_actionlog import text_to_action_log


# Chunked so that the prompt, JSON action-log output, and model response all fit in the context window.
DEFAULT_TRANSCRIPT_CHUNK_CHARS = 9_000
DEFAULT_ACTION_LOG_CHUNK_CHARS = 12_000


def split_transcript(text: str, max_chars: int = DEFAULT_TRANSCRIPT_CHUNK_CHARS) -> list[str]:
    """
    Role: If a transcript is larger than the defined maximum character limit, split into smaller chunks.
    Split at line or sentence boundaries so that as much of the transcript context is retained.
    
    Input:
    text: transcript to analyse, string data type
    max_chars: maximum number of characters in each chunk, integer data type

    Output:
    list of transcript chunks, each chunk is a string data type
    """

    #return text as is if smaller than the maximum character limit
    if len(text) <= max_chars:
        return [text]

    # Newline-separated logs are ideal.  Sentence boundaries are a useful fallback
    # for a transcript pasted from a single Notepad line.
    units = text.splitlines(keepends=True) #splits the input text transcript string into list of lines. Splits at linebreaks, and keeps where the linebreaks are in the original string.
    if len(units) <= 1: #if the input text transcript does not have any linebreaks, split at the end of each sentence.
        units = text.replace(". ", ".\n").replace("! ", "!\n").replace("? ", "?\n").splitlines(keepends=True) #add linebreak after common sentence-ending punctuation

    chunks: list[str] = [] #empty list to store the chunks of the input text transcript
    current = "" 
    for unit in units: #for each line in 'units'
        #append the next line in 'units' to the current line until the maximum character limit is reached. This creates one 'chunk' of the input text.
        while len(unit) > max_chars: #if the current line is larger than the maximum character limit, split it into smaller chunks
            if current: 
                # if the current line is not empty, append it to the list of chunks and reset the current line to empty
                chunks.append(current)
                current = ""

            chunks.append(unit[:max_chars]) #append the first 'max_chars' characters of the current line to the list of chunks
            unit = unit[max_chars:] #reset the current line to remove the first 'max_chars' characters that were just appended as a chunk. Keep characters not yet appended
        #once the current line is smaller than the max_char limit
        if current and len(current) + len(unit) > max_chars: #if the current line is not empty and appending the next line would exceed the maximum character limit
            chunks.append(current) #append the current line to the list of chunks
            current = unit #reset the current line to the next line
        else: #if appending the next line would not exceed the maximum character limit, append the next line to the current line
            current += unit 
    if current: #if the current line is not empty (for the final line), append it to the list of chunks
        chunks.append(current)

    return chunks


def split_action_log(action_log: list[dict[str, Any]], max_chars: int = DEFAULT_ACTION_LOG_CHUNK_CHARS) -> list[list[dict[str, Any]]]:
    """
    Role: Splits the action log into smaller chunks if it exceeds maximum character limit so that the model can analyse each chunk.

    Input:
    action_log - a list of dictionaries containing information about each action step. Output from 'text_to_action_log' function. Information includes the step number, time stamp/cue and the action.
    max_chars - the maximum number of characters allowed in each chunk. Default is 12000. Integer data type.

    Output:
    A list of lists, each a chunk of the action log. Each chunk is a list of dictionaries containing information about each action step
    """ 
    
    chunks: list[list[dict[str, Any]]] = [] #a list of the chunks of the action log. Each 'chunk' is multiple actions from the original action log
    current: list[dict[str, Any]] = [] #the current chunk of the action log that is being built.
    current_size = 2 # counts for the comma and space added when the next action is appended to the current chunk
    for action in action_log: #for each action (each dictionary) in the action log list
        action_size = len(json.dumps(action, ensure_ascii=False)) + 2 #convert action dictionary into json string and get its length in characters. 2 added for the comma and space added when the action is appended to the current chunk.
        if current and current_size + action_size > max_chars: #if there is an action in the current chunk and the total number of characters in the current chunk plus the next action is larger than themaximum character limit
            chunks.append(current) #append the current chunk to the list of chunks 
            current, current_size = [], 2  #reset the current chunk to empty and the current size to 2 
        current.append(action) #append the action to the current chunk
        current_size += action_size #add the size of the action added to the curent chunk to the current chunk size
    if current: #if there is an action in the current chunk
        chunks.append(current) #append the current chunk to the list of chunks 
    return chunks


def analyse_large_behaviour_text(behaviour_text: str, rubric: dict[str, list[str]], dimensions_of_interest: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Role: Analyse any input text that is larger than the maximum character limit. 
    
    Input:
    behaviour_text - the text to be analysed (the output of the text_to_action_log function). String data type.
    rubric - the behaviour rubric used for text analysis. Dict data type  
    dimensions_of_interest - the behavioural dimensions that you want to analyse the text for. List of strings data type.

    Output:

    Method:
    Scores are weighted by the number of observed actions in each scoring chunk (the higher the number of actions in a chunk the higher weightage the chunk has).
    The action logs have a `source_chunk` field, allowing the UI and
    later code to trace evidence back to the relevant part of the transcript.
    """

    complete_action_log: list[dict[str, Any]] = [] #list to store the complete action log for the entire input text.                                                                
    for source_chunk, transcript_chunk in enumerate(split_transcript(behaviour_text), start=1): #source_chunk: Index of chunks created from the input text. transcript_chunk: the chunk of the input text being analysed
        actions = text_to_action_log(transcript_chunk) #convert the current chunk of the input text into an action log 
        for action in actions:
            if not isinstance(action, dict): #if the action is not a dictionary raise an error
                raise ValueError("The model returned an action log containing a non-object action.")
            action = dict(action) #convert the action to a dictionary
            action["source_chunk"] = source_chunk #index of the chunk of the input text that the action was extracted from.
            action["global_step"] = len(complete_action_log) + 1 #the step number of the action in the complete action log
            complete_action_log.append(action) #append the action to the complete action log 

    if not complete_action_log: #if the complete action log is empty raise an Error
        raise ValueError("No actions could be extracted from the supplied transcript.")

    results_by_category: dict[str, list[tuple[dict[str, Any], int]]] = defaultdict(list) #defines expected format of 'results_by_category'. dictionary storing the results of the analysis, categorised by the behavioural dimension.
    for log_chunk in split_action_log(complete_action_log): #split the inputted complete action log into smaller chunks. Then for each chunk of the action log
        chunk_analysis = get_behaviour_analysis(text_input=log_chunk, rubric=rubric, dimensions_of_interest=dimensions_of_interest, include_summary=False) #run behavioural analysis for each smaller chunk
        weight = len(log_chunk) #assign a weightage to the chunk based on its length (the number of actions grouped in the chunk)
        for category in chunk_analysis["categories"]: #for each category that the chunk was analysed for (the categories are predetermined by the user when the analysis is called)
            results_by_category[category["category"]].append((category, weight)) #append the analysis to the results_by_category dictionary, under the key of the category name. Outputs a list of tuples, each tuple containing the analysis for that category and the weightage of the chunk.

    categories: list[dict[str, Any]] = [] #set an empty list to store the final analysis of each category after the complete action log has been analysed
    for dimension in dimensions_of_interest: #for each dimension that was analysed
        category_results = results_by_category[dimension] #access the analysis results for the current dimension for all the chunks of the action log
        total_weight = sum(weight for _, weight in category_results) #weight determined by the number of actions in each chunk. total weight sums all the weights in the category (sums weights of all the chunks)
        average = sum(item["average_score_of_category"] * weight for item, weight in category_results) / total_weight #sums the (average scoring * weightage) value of each category, then divides by the total sum of weights 
        evidence = "\n\n".join(
            f"Chunk {index + 1}: {item.get('score_evidence', '')}"
            for index, (item, _) in enumerate(category_results)
            if item.get("score_evidence")
        )
        categories.append({ #to the empty list previously defined, append the overall category scores for the whole input, from combining analysis outputs of all the individual chunks
            "category": dimension, 
            "average_score_of_category": round(average, 2), #round the score to 2 decimal points
            "human_or_generated_label": "human-like" if average >= 7 else "generated-like", #output 'human-like' if the score is above 7, adn 'generated-like' if the score is below.
            "score_evidence": evidence,
        })

    overall = round(sum(item["average_score_of_category"] for item in categories) / len(categories) * 10, 2) #the overall human-likeness score, combining the scores from all the categories analysed.
    analysis = { #the final analysis output, combining output from all the individual chunks
        "overall_human_likeness_percentage": overall, 
        "classification": "human-like" if overall >= 70 else "generated-like", 
        "classification_summary": "Scores were calculated from independently analysed action-log chunks and weighted by the number of actions in each chunk.",
        "categories": categories,
        "dimensions_of_interest": dimensions_of_interest,
        "processing": {"mode": "chunked", "transcript_chunks": len(split_transcript(behaviour_text))}, #can access whether it was analysed as a whole text or in chunks
    }
    return complete_action_log, analysis
