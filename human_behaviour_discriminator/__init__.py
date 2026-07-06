from .behaviour_rubric import BEHAVIOUR_CATEGORY_RUBRIC
from .requests_for_user_input import ask_for_text_input
from .requests_for_user_input import ask_for_behaviour_dimensions
from .get_behaviour_analysis import get_behaviour_analysis


def get_behavioural_analysis_interactive(rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    user_input_text_reply = ask_for_text_input()
    user_dimensions_REPLY = ask_for_behaviour_dimensions(rubric)
    analysis_output = get_behaviour_analysis(text_input=user_input_text_reply, rubric=rubric, user_dimension_reply=user_dimensions_REPLY,)
    return analysis_output 

#result_interactive_input = get_behavioural_analysis_interactive(rubric=BEHAVIOUR_CATEGORY_RUBRIC)

