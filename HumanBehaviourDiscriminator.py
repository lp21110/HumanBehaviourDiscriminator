
'''
Author: xxx email
 
File: xxx.py
 
Description:
'''
import ollama 
import json
#import requests


#initialise Ollama client 
client = ollama.Client()

#define model 
#model = 'llama3.2:3b'
model = 'llama3.1:8b'
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

    'INTENTIONALITY_PROMPTS' : [
        'Does the agent exhibit goal-directed behaviour?', #Does the behaviour build towards a larger goal? 
        'Does the behaviour show a hierarchy of short and long term goals?',
        'Do the inferred goals of the actions and tasks fit the scenario context?',
        'Are the agents actions coherent across time steps and do they remain so over time?'],   

    #ADAPTABILITY PROMPTS: adaptability of the agent's behaviour. Dealing with uncertainty, ability to improv, re-plan or update plans as they happen.
    'ADAPTABILITY_PROMPTS' : [
		'Does the agent show evidence of adapting its behaviour when the environment or context changes?',
        'Does the agent suggest the use of prior experience when encountering familiar situations?',
        'Does the agent show evidence of adjusting its behaviour in response to external feedback?',
        'Does the agent revise its goals when encountering unexpected events?'
        'Does the agent show evidence of flexibility in their behaviour, such as being able to switch between different strategies or approaches to achieve their goals?',
        'Does the agent show evidence of improvisation or creativity in their actions?',                 
		'Does the agent show evidence of re-planning or updating their plans as they happen?'
     ],

    #ROUTINE AND VARIABILITY PROMPTS: 
    'ROUTINE_PROMPTS' : ['Does the agent show evidence of habitual or routinely executed actions?',   
                         'Does the agents behaviour show evidence of routine, automated actions and procedural familiarity with their tasks',                            
                        'Does the agents suggest procedural familiarity with the task?',
                        'If the agents actions are inferred as uncertain, does the agents behaviour suggest exploratory, investigative behaviour i.e. through trial and error?',
                        'Does the agent show an ability to perform routine tasks with a degree of variability, if the task is repeated can the agent complete it using different action sequences?',
                        'Do actions appear habitual or automatic rather than explicitly deliberative?'
                        'Does the agents actions contain actions that verify the progress state of the action?'
    ],

    #IMPERFECTIONS, ERRORS, VARIABILITY
    'HUMAN_IMPERFECTIONS_PROMPTS' : [  
        'Do the actions of the agent sh uncertainty, such as hesitation, action reversal or changes of course in their carrying out of the task?',
        'Does the agent show signs of forgetfulness in their action sequences?',
        'Does the agent shows signs of distraction from the current task?',
        'Are there interruptions in behaviour and action flow, such as pauses between actions or interruptions in task flow (in contrast to a smooth flow)?'
    ],

    #ERROR RECOVERY 
    'RECOVERY_PROMPTS' : ['If actions of the agent are inferred as mistakes, do the mistakes and recovery appear overly direct or artificially convenient? The more true this is, the lower the score.',
        'If the agent shows signs of mistakes, are the agents able to correct their path of action, or recover from a potential error?',
        'Does the agent show evidence of being able to detect and recognise its own mistakes?',
        'Does the behaviour show evidence of reviewing or self-checking between tasks and after mistakes?'
    ],


    #EMOTIONS
    'EMOTIONAL_ACTION_PROMPTS' : [
        'Does the agent show behaviour and actions that are not purely rational or utility-maximising?'
    ],

    #NON-OPTIMALITY 
    'PREFERENCES_AND_NON_OPTIMAL_BEHAVIOUR' : [ #deviation from a clean task flow
        'Does the agents behaviour suggest preference-driven choices over optimal actions?',
        'Does the agent behaviour display sub-optimal behaviour?', 
        'Does the agents behaviour show signs of settling for adequate rather than optimal action flows?',
        'Does the agents behaviour show small variations in action sequences that can be inferred as routine behaviour?'
    ],
    
    #TIMING
    'TIMING' : [
        'Do the time intervals between different actions or task sequences performed show realistic variation? '
        'Do action timings exhibit realistic variation  (in comparison to e.g. being evenly spaced out) i.e. the timing of the actions, time taken for each action and time between actions?',
        'Do the times taken for each action correspond with the time generally required for the actions?',
        'Are the times taken to perform tasks realistic rather than optimally efficient?'
    ],

    #MICRO-BEHAVIOUR
    'MICRO-BEHAVIOUR' : [
        'Does the agents behaviour perform any automatic, subconscious or micro-behaviours, behaviours with no outward goal? Some examples include yawning, stretching, fidgeting, sighing, flinching, startling, hiccups etc.',
    ],

    #ENVIRONMENTAL CONTEXTUAL BEHAVIOUR
    'ENVIRONMENTAL_CONTEXT_BEHAVIOUR' : [
	    'Do the actions of the human adapt to the locations of the objects they are interacting with?',
	    'Do the agents actions show an awareness of their environmental constraints, surrounding wise?', #i.e. physically, walking around obstacles, repositioning objects, adjusting grip, changing posture
	    'Do the actions of the human show that they have been influenced by their surrounding environment?'
    ],

    #PHYSIOLOGICAL_CONTEXT
    'PHYSIOLOGICAL_CONTEXT' : [
	    'Do the agents actions show an awareness of and reflect realistic constraints of the body?',
	    'Do the agents actions and behaviour seem physically plausible?'
	],
	
    #ATTENTIVENESS
    'ATTENTIVENESS' : [
        'Does the agent exhibit actions that suggests it periodically monitor or reassess its environment?',
	    'Does attention shift between multiple goals or objects?',
	    'Does the agents behaviour suggest selective attention rather than perfect awareness of the environment?',
	    'Does the agents behaviour show signs that some information is overlooked?'
	],
    
    #FORESIGHT
    'FORESIGHT' : [
	    'Does the agent show signs of bundling related actions together when possible?',
	    'Does the behaviour indicate towards an awareness of anticipating future resource needs, or evidence of planning/ foresight?',
	    'Are multiple goals being pursued simultaneously?',
	    'Are some goals temporarily postponed or left in favour of other goals?'
	],
	
    #SOCIAL BEHAVIOUR
    'SOCIAL_BEHAVIOUR': [
        'If other agents or living beings are present, does the agents behaviour adapt to their actions?',
        'If other agents are present, does the agent coordinate its actions with the others?',
        'If other agents are present, does the agent show an adequate awareness of social expectations?'
    ]
}                              

# function to send the prompt to the Ollama API and get the response
def get_behavior_analysis(text_input, rubric): # can later incorporate a dimensions input where you can choose which dimensions you wish to analyse 
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
    #define prompt
    #Define the prompt for the behavior discriminator
    #the initial messages to set the context for the behaviour discriminator. 
        #Modify the 'system' role to include specific instructions or examples for the behaviour of the discriminator to follow when analyzing the behaviour transcript.
        #Modify the 'user'role by appending the text input (the behaviour transcript) to the messages list. The text input should be a description of the agents actions 
        #and movements expected in natural language format.
    
    system_prompt = "You are a behavior discriminator, with the task of analysing behaviour in a inputted behavioural transcript using a provided behaviour rubric, and scoring how human-like the agents actions are on a scale from 0 to 10, where 0=generated-like and 10=clearly human-like."
    
    user_prompt = f"""Analyse the following behaviour transcript, using steps outlined below and the provided rubric. 

                Step 1: 
                - If text_input is not already in a behavioural action-log format, literally and precisely convert it into a behavioural action log. 
                - Record each seperate observable action taken and the timestep at which actions occur.
                - Only include actions explicitly present in the transcript
                - Do not invent, assume or ass actions that are not recorded

                Step 2: For each category in the behavioural rubric:
                -Answer each question in the category applied to the behavioural action log 
                -Give each question a score between 0 to 10, where 0= strongly generated-like, 5=ambiguous, and 10= strongly human-like 
                -If a question has insufficient evidence, assign a score of 5
                -If the category is 'social_behaviour', only consider if there is a presence of another agent. Else give a a human-likeness scoring of 5.
                -Provide clear evidence from the transcript for why the score was given, including categories scored with insufficient evidence  
                -Calculate the average of the scores in the category
                -Classify the category as 'human-like' if the category average >= 7
                -Classify the category as 'generated-like' if the category average <7

                Step 3: 
                - Calculate the overall human-likeness score for the behavioural action log by finding the average of average scores of all the categories.
                - Multiply the overall human-likeness score of the 10 for a human-likeness percentage
                - Classify the inputed text as 'human' if the overall human-likeness percentage >=70
                - Classify the inputted text as 'generated' if the overall human-likeness percentage <70

                Step 4:
                -Grouped the categories by their classification, into human-like categories and generated-like categories.

                Behaviour transcript: 
                {text_input}

                behaviour rubric: 
                {rubric}

                Return valid JSON only:
                For "categories", return an entry for each category in the behavioural rubric. Do not skip or omit any category even if no evidence is available.
                {{"overall_human_likeness_percentage": 0, 
                "classification": "",
                "summary": "",
                "behavioural_action_log" : [{{
                    "timestep": "",
                    "action": ""
                   }}],
                "human_like_categories" : ""
                "generated_like_categories": "",
                "categories": [ {{
                    "category": "",
                    "average_score": 0,
                    "human_or_generated_label": "",
                    "label_evidence_reasoning": ""
                    }} ] }}
    """

    # Send the prompt to the Ollama API
    response = client.generate(model=model, system = system_prompt, prompt= user_prompt, format= 'json', options={'temperature': 0}) #temperature keeps the results reproducible  
    return json.loads(response['response'])

#------------------------------------------------------------------------------------
#TEXT INPUT: CHANGE ANY GIVEN TEXT INPUT INTO A BEHAVIOURAL TRANSCRIPT 

def text_to_action_log (text_input):

    '''
    Timing is depedent on the input: 
        If timing is provided alongside the text input, return an action log alongside the times at which they occurred. 
        Else, create an action log without a corresponding time record. (Can later analyse with all behaviour categories in rubric other than time.
            In this case, the timing recorded will be qualitative; if there are cues towards duration of actions or relative action times
    '''
    prompt = f"""Convert the following text input into a structured action log, recording each individual action seperately.
        
        If text input has explicit timestamps, for each action give its step in the sequence, its timestamp and short description of the action.
        Only include actions that appear in the text.
    
        If text input does not have explicit timestamps but does have time cues or duration cues for an action, give its steps in the sequence, the action, the time/ duration cue mentioned in the text, and a short description of the action

        If text input does not have any timestamps or time cues or duration cues, give its step in the sequence and a short description of the action.
        
        Only include and analyse what is literally given in the text input, do not make up or invent times, and leave the 'time_stamp / time_cue" response empty.
        Text input: {text_input}

        Return JSON: {{
            "action log" : [ {{
                "step": 0,
                "time stamp / time_cue": "",
                "action": ""
                }} ]
            }}""" 

    # Send the prompt to the Ollama API
    response = client.generate(model=model, prompt= prompt, format= 'json', options={'temperature': 0}) #temperature keeps the results reproducible  
    return json.loads(response['response'])['action_log']

#------------------------------------------------------------------------------------
#VIDEO INPUT: CHANGE ANY GIVEN VIDEO INPUT INTO A BEHAVIOURAL TRANSCRIPT / ACTION LOG 
#extracts frames from video input and audio as a transcript

vision_model = "qwen2.5-VL"

video_file_path = "" #insert path to the video to be analysed here
frames_directory = "frames" 
frame_interval = 30 #1 frame every 30 frames (~1 second if 30fps) #what does fps mean!
video_transcript_file = "video_transcript.txt"

#FOR VISION MODEL QWEN2.3VL:7B 
## REFERENCE WEBSITE: https://pyimagesearch.com/2025/06/16/video-understanding-and-grounding-with-qwen-2-5/

#Import classes and functions from required libraries 
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info 

#call/ instantiate model
vision_model_qwen = Qwen2_5_VLForConditionalGeneration.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", torch_dtype="auto", device_map="auto")

#FOR THE PROCESSOR: WHY DO YOU NEED THE MIN/MAX PIXEL VALUES?
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)

#sample and visualise frames within the video 
from IPython.display import Markdown, display 
import numpy as np
from PIL import image 


#Below code is not required - only for debugging 
# import decord 
# from decord import VideoReader, cpu
# def get_video_frames (video_file_path, frame_interval = frame_interval):
#     '''
#     INPUTS:
#         video_file_path - the file path to the video input 
#         frame_interval - the number of frames between each frame 

#     OUTPUTS: a JSON of frame timestamps and a short description of the action in each time stamp
#         frames 
#         timestamps 
#     FUNCTION:
#         Extract evenly spaced frames and timestamps from a video file 
#     '''

#     vr = VideoReader (video_file_path, ctx=cpu(0))
#     total_frames = len(vr)
#     num_frames = total_frames / frame_interval 
#     indices = np.linspace(0, total_frames -1, num=num_frames, dtype=int)
#     frames = vr.get_batch(indices).asnumpy()
#     timestamps = np.array([vr.get_frame_timestamp(idx) for idx in indices])

#     return frames, timestamps 
    
#inference of the video frames function 
#WHAT DO THE INPUTS MEAN ?
def video_inference (vision_model, processor, video_path, max_new_tokens=1024, total_pixels=20480*28*28, min_pixels=16*28*28):
    
    user_prompt = f"""Localize a series of activity events in the video, output the start and end timestamp for each event, and describe each 
        event with sentences. Provide the result in json format with 'seconds' format for time depiction."""
    
    messages =[
        {"role": "system",
         "content": "Your role is to create an action log for the provided video input, stating the time-step / frame-step and the a short description of the action being taken in each frame"
         },
        #WHAT DOES EACH LINE OF THIS MEAN? 
        {"role": "user",
         "content": [
             {"type": "text", "text": user_prompt},
             {"video": video_path, "total_pixels": total_pixels, "min_pixels": min_pixels}

         ]}]
    
    #Prep for inference: 
    #process_vision_info extracts image and video inputs and frame rate information 
    image_inputs, video_inputs, video_kwargs = process_vision_info([messages], return_video_kwargs = True)
    fps_inputs = video_kwargs ['fps']

    #combine text, images and video data into tensors, transfer to GPU  
    inputs = processor( text= [user_prompt], images = image_inputs, videos = video_inputs, fps = fps_inputs, padding = True, return_tensores='pt')
    inputs = input.to('cuda')

    #UNDERSTAND WHAT THESE INDIVIDUAL LINES DO! 
    #Generate model outputs and extract new tokens beyond initial input length
    output_ids = vision_model.generate(**inputs, max_new_tokens = max_new_tokens)
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
    #decode tokens into human-readable text
    output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return output_text[0]

#calling the vision model 
## video_inference_action_log = video_inference(vision_model, processor, video_file_path, prompt)
## display(Markdown(video_inference_action_log))

#------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------
#COMBINE ABOVE TO CREATE A PIPELINE 

#get action log -> input into discriminator (include into discriminator option to make time category optional based on input)

#------------------------------------------------------------------------------------

#TESTING THE CODE:

import pandas as pd
from pathlib import Path

#csv_path = Path(__file__).with_name("EPIC_100_validation_dataset.csv")

#df = pd.read_csv(csv_path, usecols=['start_timestamp', 'stop_timestamp', 'narration'])

#print (df)

if __name__ == "__main__":
    test_transcript_1 = """
    [07:42:00] Agent enters kitchen.
    [07:42:05] Agent fills kettle with water.
    [07:42:10] Agent turns on kettle.
    [07:42:15] Agent retrieves mug from cupboard.
    [07:42:20] Agent places teabag in mug.
    [07:43:20] Agent pours boiling water into mug.
    [07:43:25] Agent adds milk.
    [07:44:25] Agent removes teabag.
    [07:44:30] Agent drinks tea.
    [07:44:35] Agent places mug in sink.
    """

    result_1 = get_behavior_analysis(test_transcript_1, BEHAVIOUR_CATEGORY_RUBRIC)

    print('RESULT 1', json.dumps(result_1, indent=2))   # pretty-print if it parsed to a dict

    test_transcript_2 = """
    [07:42:13] Agent walks into kitchen, flicks light switch, light doesn't come on, flicks it again.
    [07:42:20] Agent fills kettle, slightly overfills, tips a bit back out into sink.
    [07:42:34] Agent sets kettle to boil, leans against counter.
    [07:42:51] Agent opens cupboard, looks for mug, moves two mugs aside, picks the one at the back.
    [07:43:10] Agent gets distracted by phone, scrolls for about 40 seconds.
    [07:43:55] Agent looks up as kettle clicks off, realises it boiled a while ago.
    [07:44:02] Agent drops teabag in mug, pours water, splashes slightly.
    [07:44:20] Agent forgets the milk, opens fridge after already pouring, adds it. 
    [07:45:30] Agent fishes teabag out, squeezes it against the side, drops it in bin, misses, picks it up.
    [07:46:00] Agent sips, it's too hot, sets it down, waits.
    [07:48:30] Agent drinks slowly while staring out the window.
    """
    result_2 = get_behavior_analysis(test_transcript_2, BEHAVIOUR_CATEGORY_RUBRIC)

    print('RESULT 2', json.dumps(result_2, indent=2))   # pretty-print if it parsed to a dict



#print (get_behaviour_analysis (text_input))

#-------------------------------------------------------------

#The llama vision model code

#extract frames - for vision_model llama3.2
# def extract_video_frames (video_path, output_dir, interval=frame_interval):
#     """
#     Input: 
#     video_path : the variable defining the path to the input videp 
#     output_dir : the output file/ directory to which you want the frames to be outputted to 
#     interval : the time interval between each frame (determined by the number of frames between each recorded frame)
    
#     Output: 
    

#     Function: Open the video and reads the video by frame.
#     The frame read are frames at each defined frame_interval
#     Provides input for the vision model to then process the images/ the frames
#     """   

#     os.makedirs(output_dir, exist_ok=True)
#     cap = cv2.VideoCapture(video_path)
#     frame_count, saved = 0,0 
#     while True: 
#         ret, frame = cap.read()
#         if not ret: 
#             break 
#             if frame_count % interval == 0:
#                 frame_path = os.path.join(output_dir, f"frame_{saved:03d}.jpg")
#                 cv2.imwrite(frame_path, frame)
#                 saved += 1
#             frame_count += 1
#         cap.release()
#         print (f"'Extracted' {saved} frames to '{output_dir}')

#to meet ollama requirements: encode images (inside a JSON payload) to base64
# #WHAT IS BASE64? 
# def encode_image_to_base64(image_path):
#     with open(image_path, "rb") asw img:
#         return base64.b64encode(img.read()).decode("utf-8")

# #transcribe any audio from input video 
# def transcribe_video(video_path, output_file):
#     """
#     Function:
#     Transcribing audio from video. Using whisper.
    
#     Input:
#     video_path: The path to the video file to be analysed
#     output_file: The file to output the transcription to 

#     Output:
#     file with the transcription from the audio
#     """
#     model = whisper.load_model("small")
#     result = model.transcribe(video_path)
#     text = result["text"]
#     with open(output_file, "w", encoding = "utf-8") as f: #WHAT DO THESE VARIABLES MEANNNN
#         f.write(text)
#     print (f"transcription saved to '{output_file}'")
#     return text 

# def video_discriminator (prompt, frames_dir, transcript_file):
#     frames = sorted ([f for f in os.listdir(frames_dir) if f.endwith("jpg")])
    
#     frame_path = os.path.join(frames_dir, frames[0])
#     image_b64 = encode_image_to_base64(frame_path)

#     with open(transcript_file, "r", encoding="utf-8") as f:
#         transcript = f.read()
#     #want an output that shows 
#     input_for_model = {
#         "model": vision_model,
#         "messages": [
#             {
#             "role": "user",

#             }
#         ]
#     }