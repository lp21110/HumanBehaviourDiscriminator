
from .behaviour_rubric import BEHAVIOUR_CATEGORY_RUBRIC
from .behaviour_rubric import BEHAVIOUR_DIMENSION_SUMMARIES
from .text_to_actionlog import text_to_action_log


def get_behaviour_dimension_options(rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Returns (to display to user) the behavioural dimensions available in the rubric with a short explanation of what each dimension analyses.
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


def ask_for_behaviour_dimensions(rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Interactive helper that asks the user which rubric dimensions to analyse.
    '''
    display_behaviour_dimension_options(rubric)
    user_reply = input('\nEnter your selected dimensions or prompt option: ')
    return user_reply
    #return parse_behaviour_dimension_reply(user_reply, rubric)


def ask_for_text_input():
    '''
    Interactive helper that asks the user which text to analyse.
    Returns the action log to be inputted into the behavioural analysis function
    '''
    user_reply = input('\nEnter your text input to be analysed (enter as one line): ')
    action_log = text_to_action_log(user_reply)
    return action_log


