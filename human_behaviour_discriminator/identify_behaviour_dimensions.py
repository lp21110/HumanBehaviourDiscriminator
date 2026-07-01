import re 
 
from .behaviour_rubric import BEHAVIOUR_CATEGORY_RUBRIC


def _split_dimension_names(text):
    '''
    Splits comma/newline/semicolon separated dimension names while preserving exact dimension names that contain underscores or hyphens.
    '''
    separators = [',', '\n', ';']
    dimension_names = [text]

    for separator in separators:
        next_names = []
        for name in dimension_names:
            next_names.extend(name.split(separator))
        dimension_names = next_names

    return [name.strip() for name in dimension_names if name.strip()]


def parse_behaviour_dimension_reply(user_reply, rubric=BEHAVIOUR_CATEGORY_RUBRIC):
    '''
    Parses the user's requested behavioural dimensions.

    Valid replies:
        - ALL_PROMPTS
        - PROVIDED_PROMPTS: DIMENSION_NAME, OTHER_DIMENSION_NAME
        - DIMENSION_NAME, OTHER_DIMENSION_NAME
        - OWN_PROMPT: custom question
        - PROVIDED_PROMPT: DIMENSION_NAME; OWN_PROMPT: custom question

    Returns:
        dimensions_of_interest: list of exact rubric dimension names, plus
            'OWN_PROMPT' if the user supplied a custom prompt.
        selected_rubric: rubric dictionary containing only selected dimensions.

    Raises:
        ValueError: if any provided dimension is not exactly in the rubric, or
            if OWN_PROMPT is present but has no prompt text.
    '''
    if not user_reply or not user_reply.strip():
        raise ValueError("No behavioural dimensions were provided.")

    reply = user_reply.strip()
    reply_upper = reply.upper()
    own_prompt_text = None

    if 'OWN_PROMPT:' in reply_upper:
        own_prompt_index = reply_upper.index('OWN_PROMPT:')
        own_prompt_text = reply[own_prompt_index + len('OWN_PROMPT:'):].strip()
        reply = reply[:own_prompt_index].strip()
        reply_upper = reply.upper()

        if not own_prompt_text:
            raise ValueError("OWN_PROMPT was included, but no custom prompt was provided after 'OWN_PROMPT:'.")

    include_all_prompts = 'ALL_PROMPTS' in reply_upper
    provided_text = reply

    if reply_upper.startswith('PROVIDED_PROMPT:'):
        provided_text = reply[len('PROVIDED_PROMPT:'):].strip()
    elif reply_upper == 'PROVIDED_PROMPT':
        provided_text = ''
    elif reply_upper.startswith('PROVIDED_PROMPT'):
        provided_text = reply[len('PROVIDED_PROMPT'):].strip(' :\n\t')

    provided_text_for_validation = re.sub('ALL_PROMPTS', '', provided_text, flags=re.IGNORECASE)
    dimension_names = _split_dimension_names(provided_text_for_validation)
    ignored_markers = {'PROVIDED_PROMPT', 'ALL_PROMPTS'}
    requested_dimensions = [name for name in dimension_names if name.upper() not in ignored_markers]

    invalid_dimensions = [name for name in requested_dimensions if name not in rubric]
    if invalid_dimensions:
        available_dimensions = ', '.join(rubric.keys())
        raise ValueError(
            "Invalid behavioural dimension(s): "
            f"{', '.join(invalid_dimensions)}. "
            "Please use exact dimension names from the rubric. "
            f"Available dimensions are: {available_dimensions}"
        )

    if include_all_prompts:
        dimensions_of_interest = list(rubric.keys())
    else:
        dimensions_of_interest = requested_dimensions

    selected_rubric = {dimension: rubric[dimension] for dimension in dimensions_of_interest}

    if own_prompt_text:
        dimensions_of_interest.append('OWN_PROMPT')
        selected_rubric['OWN_PROMPT'] = [own_prompt_text]

    if not selected_rubric:
        raise ValueError("No valid behavioural dimensions or own prompt were provided.")

    return dimensions_of_interest, selected_rubric
