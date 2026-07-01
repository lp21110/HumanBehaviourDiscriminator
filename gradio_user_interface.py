import json

import gradio as gr

from human_behaviour_discriminator.behaviour_rubric import (BEHAVIOUR_CATEGORY_RUBRIC, BEHAVIOUR_DIMENSION_SUMMARIES,)
from human_behaviour_discriminator.get_behaviour_analysis import (
    get_behaviour_analysis,)
from human_behaviour_discriminator.text_to_actionlog import text_to_action_log


DIMENSION_NAMES = list(BEHAVIOUR_CATEGORY_RUBRIC)

DIMENSION_CHOICES = [
    (
        f"{name} — {BEHAVIOUR_DIMENSION_SUMMARIES.get(name, 'Behaviour rubric category')}",
        name,
    )
    for name in DIMENSION_NAMES
]


def _selected_rubric(selected_dimensions, custom_prompt):

    """Build the rubric selected in the Gradio form.
    
    Input: 
    - selected_dimensions: the dimensions that the user selected on the interface screen 
    - custom_prompt: any user-inputted promt that was entered on the interface screen

    Output: 
    - dimensions_of_interest: a list of the dimension names selected by the user to analyse the text, including 'own prompt' for a custom prompt
    - rubric: a rubric of the dimension names and their respective prompts selected by the user to analyse the text, including the custom prompt 
    
    """

    selected_dimensions = list(dict.fromkeys(selected_dimensions or [])) #the dimensions that the user selected on the interface
    #unknown_dimensions = [name for name in selected_dimensions if name not in BEHAVIOUR_CATEGORY_RUBRIC] #these wont be an issue as you cannot choose dimensions not in the rubric
    #if unknown_dimensions:
    #    raise ValueError(
    #        f"Unknown rubric dimension(s): {', '.join(unknown_dimensions)}")

    rubric = {name: BEHAVIOUR_CATEGORY_RUBRIC[name] for name in selected_dimensions} #WHAT DOES THIS LINE DO - does this just return the name of the dimension or the whole prompt?
    dimensions_of_interest = selected_dimensions.copy()

    custom_prompt = (custom_prompt or "").strip() #remove trailing and whitspace/ uneccesary characters from custom prompt by user
    if custom_prompt: #append the 'custom_prompt to the rubric of 'dimensions_of_interest
        rubric["OWN_PROMPT"] = [custom_prompt]
        dimensions_of_interest.append("OWN_PROMPT")

    if not rubric: #if no dimension or own_prompt was entered 
        raise ValueError("Select at least one rubric dimension or enter a custom prompt.")

    return dimensions_of_interest, rubric


def _category_rows(analysis):

    """Convert category dictionaries into rows for the results table.
    
    Input:
    - analysis : the output of the get_behavioural_analysis function

    Output: 
    - Returns a structured version of the the get_behavioural_output function to be visualised on the gradio screen
    
    """
    return [

        [   category.get("category", ""), #get() gets the value of the 'category' key in the output dictionary 
            category.get("average_score_of_category", ""), # "" for average score (and so on for the keys below)
            category.get("human_or_generated_label", ""),
            category.get("score_reasoning", ""),
            category.get("score_evidence", ""), ]

        for category in analysis.get("categories", []) #for each category/ dimension that is scored (as per the user's request) 
        if isinstance(category, dict) #if the category is a dictionary 
    ]


def analyse_behaviour(behaviour_text, selected_dimensions, custom_prompt, progress=gr.Progress(),):

    """Run the complete text-to-action-log-to-analysis pipeline.
    
    Input: 
        -behaviour_text: the behaviour text inputted by the user to be analysed
        -selected_dimensions: the dimensions selected by the user to analyse the text on (use 'selected_dimensions' function)
        -custom_prompt: any prompts that were inputted by the user, not predefined 
        -progress: allows for the interface to track the development of the analysis and 


    Output:
        - progress: report the stage of analysis that is currently occuring. Refreshes after each step
        - summary:
        - action log:
        - analysis, category by category:
        - full JSON analysis reply:
    
    """

    behaviour_text = (behaviour_text or "").strip() #remove any trailing and whitspace/ uneccesary characters from custom prompt by user

    if not behaviour_text: #Return error message on screen if the user has not entered a input behavioural transcript to be analysed
        raise gr.Error("Enter behaviour text before running the analysis.") 

    try:
        dimensions_of_interest, rubric = _selected_rubric(selected_dimensions, custom_prompt) 
    except ValueError as exc: #convert error into an error pop-up 
        raise gr.Error(str(exc)) from exc #uses the original error message to explain Error raised

    progress(0.1, desc="Converting the text into an action log") #dsiplays on screen current step of converting input text to an action log 
    try:
        action_log = text_to_action_log(behaviour_text)
    except json.JSONDecodeError as exc: #debugging error message for if the transcript canonot be converted to a json action log format 
        raise gr.Error(
            "Ollama returned invalid JSON while creating the action log. "
            "Please retry the request."
        ) from exc
    
    except Exception as exc: #if there are issues other than json formatting that are preventing the input from being converted to an action log
        raise gr.Error(
            f"Could not create the action log. Check that Ollama and the configured "
            f"model are running. Details: {exc}"
        ) from exc

    progress(0.45, desc="Scoring the selected behaviour dimensions") #displays on screen current stage of scoring the dimensions - call get_behaviour_analysis
    try:
        analysis = get_behaviour_analysis(
            text_input=action_log,
            rubric=rubric,
            dimensions_of_interest=dimensions_of_interest,
        )
    except json.JSONDecodeError as exc: #error message
        raise gr.Error(
            "Ollama returned incomplete or invalid analysis JSON. Retry the request "
            "or select fewer dimensions."
        ) from exc
    except Exception as exc: #error message 
        raise gr.Error(
            f"The behaviour analysis failed. Check the Ollama server and model. "
            f"Details: {exc}"
        ) from exc

    progress(0.95, desc="Preparing results") # displays on screen the current stage of fetching and compiling results in a readable style
    percentage = analysis.get("overall_human_likeness_percentage", "Not provided")
    classification = analysis.get("classification", "Not provided")
    model_summary = analysis.get("classification_summary", "No summary was returned.")
    summary = (
        "## Analysis result\n"
        f"**Classification:** {classification}  \n"
        f"**Human-likeness:** {percentage}%  \n\n"
        f"{model_summary}"
    )

    return summary, action_log, _category_rows(analysis), analysis


def build_app():

    """Create the Gradio application without launching its web server."""

    with gr.Blocks(title="Human Behaviour Discriminator") as app:
        gr.Markdown(
            "# Human Behaviour Discriminator\n"
            "Enter an action description, choose the dimensions to assess, and run "
            "the complete Ollama-backed analysis pipeline.")

        with gr.Row():
            with gr.Column(scale=3):
                behaviour_text = gr.Textbox(
                    label="Behaviour description or transcript",
                    placeholder=(
                        "Example: [07:42:13] Agent enters the kitchen and tries the "
                        "light switch twice..."),
                    lines=14,
                    )
                custom_prompt = gr.Textbox(
                    label="Optional custom assessment prompt",
                    placeholder="Example: Does the agent show fatigue?",
                    lines=2,
                    )

            with gr.Column(scale=2):
                dimensions = gr.CheckboxGroup(
                    choices=DIMENSION_CHOICES,
                    value=DIMENSION_NAMES,
                    label="Behaviour dimensions",
                    info="All dimensions are selected by default.",
                )
                analyse_button = gr.Button("Run analysis", variant="primary")
                clear_button = gr.ClearButton(
                    value="Clear",
                    components=[behaviour_text, dimensions, custom_prompt],
                )

        summary_output = gr.Markdown("Run an analysis to see the result.")

        with gr.Tabs():
            with gr.Tab("Category results"):

                category_output = gr.Dataframe(
                    headers=[
                        "Category",
                        "Average score",
                        "Label",
                        "Reasoning",
                        "Evidence",
                    ],
                    datatype=["str", "number", "str", "str", "str"],
                    interactive=False,
                    label="Scores by category",
                )

            with gr.Tab("Action log"):
                action_log_output = gr.JSON(label="Converted action log")
            with gr.Tab("Full JSON"):
                analysis_output = gr.JSON(label="Complete analysis response")

        analyse_button.click(
            fn=analyse_behaviour,
            inputs=[behaviour_text, dimensions, custom_prompt],
            outputs=[
                summary_output,
                action_log_output,
                category_output,
                analysis_output,],
        )

    return app


demo = build_app()


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1).launch(show_error=True, share=True)