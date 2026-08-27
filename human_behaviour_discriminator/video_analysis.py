from .model_provider import Gemini

#from transformers import Qwen3VLForConditionalGeneration, AutoProcessor
#from qwen_vl_utils import process_vision_info
#import os
#import base64
#import mimetypes
#from openai import OpenAI
#from pathlib import Path



def video_to_action_log(video_input_type, video_input):
    """
    Role: Create an action log for the inputted video - this will create an action log 
    The semantic sequence/ logical realism of the overall action sequence displayed in the video will be analysed
    """

    video_analysis_system_prompt = """Carefully watch the given video and identify each distinct action or movement made by the human/character.

      Return only one valid JSON object in this format:
      {
      "action_log": [
        {
          "action_step": 1,
          "start_time": 0,
          "end_time": 1,
          "action": "detailed description of the observed action"
        }
     ]
    }

    Use mm:ss (minutes:seconds) for recording the start_time and end_time of each action. Only include actions literally visible in the video; do not invent events or timings. Be precise and do not omit observed events."""

    vllm_model_provider = Gemini()

    response = vllm_model_provider.generate_json(video_input_type, video_input, video_analysis_system_prompt)

    return response




#def video_movement_analysis(): #CAN INTRODUCE ANALYSIS FROM 4D HUMANS HERE 
    #"""
    #realism of the body movements using maybe MediaPipe or 4DHumans (this would cover whether the actual body movements seem human or generated).
    #"""




























#combine into a class for openrouter

# """
# model_id = "qwen/qwen3.7-flash" 

# #video inference function (using openrouter)

# def determine_video_source (video_source):
#     """
#     #Build the video_url content for 
#     #  - a public http(s) URL  
#     #  - a local file path 
#     """
#     #if public url 
#     if video_source.startswith("http://") or video_source.startswith("https://"):
#         return {"type": "video_url", "video_url": {"url": video_source}}

#     #if file upload - for openrouter to analyse local files
#     path = Path(video_source)
#     if not path.exists():
#         raise FileNotFoundError(f"No such video file: {video_source}")

#     #guess the type of file (i.e. .mp4, .mov etc)
#     mime_type, _ = mimetypes.guess_type(path.name)
#     if mime_type is None:
#         mime_type = "video/mp4"  
 
#     with open(path, "rb") as f:
#         b64_data = base64.b64encode(f.read()).decode("utf-8")
 
#     data_url = f"data:{mime_type};base64,{b64_data}" 

#     return {"type": "video_url", "video_url": {"url": data_url}}


# def inference_with_openrouter_openai(video_source, prompt=default_video_analysis_prompt, model_id=model_id,):

#     video = determine_video_source(video_source)

#     client = OpenAI(api_key="", base_url="https://openrouter.ai/api/v1",)

        
#     messages = [
#         {   "role": "user",
#             "content": [
#                 video,
#                 {"type": "text", "text": prompt},
#             ]
#         }
#     ]

#     completion = client.chat.completions.create(
#         model = model_id,
#         messages = messages,
#         max_tokens = 2048,
#     )
#     return completion.choices[0].message.content








# if __name__ == "__main__":

#     #test local video 
#     test_video = "C:/Users/jyoti/OneDrive/Uni of Bristol/Internship/Questionairre/questionnaire3D/Human/humanvid1.mp4"
#     raw = inference_with_openrouter_openai(test_video)
#     print("Raw model output:\n", raw)

# ?


# --- FOR LOCAL HOSTING---

##default: Load the model on the available device(s) - needs CUDA to be locally run so is not used 
#processor = AutoProcessor.from_pretrained(model_path)

#model, output_loading_info = Qwen3VLForConditionalGeneration.from_pretrained(model_path, torch_dtype="auto", device_map="auto", output_loading_info=True)


# def inference(video, prompt, max_new_tokens=2048, total_pixels=20480 * 32 * 32, min_pixels=64 * 32 * 32, max_frames= 2048, sample_fps = 2):
#     """
#     link: https://colab.research.google.com/github/QwenLM/Qwen3-VL/blob/main/cookbooks/video_understanding.ipynb#scrollTo=2ef59a8c

#     Perform multimodal inference on input video and text prompt to generate model response.

#     Args:
#         video (str or list/tuple): Video input, supports two formats:
#             - str: Path or URL to a video file. The function will automatically read and sample frames.
#             - list/tuple: Pre-sampled list of video frames (PIL.Image or url). 
#               In this case, `sample_fps` indicates the frame rate at which these frames were sampled from the original video.
#         prompt (str): User text prompt to guide the model's generation.
#         max_new_tokens (int, optional): Maximum number of tokens to generate. Default is 2048.
#         total_pixels (int, optional): Maximum total pixels for video frame resizing (upper bound). Default is 20480*32*32.
#         min_pixels (int, optional): Minimum total pixels for video frame resizing (lower bound). Default is 16*32*32.
#         sample_fps (int, optional): ONLY effective when `video` is a list/tuple of frames!
#             Specifies the original sampling frame rate (FPS) from which the frame list was extracted.
#             Used for temporal alignment or normalization in the model. Default is 2.

#     Returns:
#         str: Generated text response from the model.

#     Notes:
#         - When `video` is a string (path/URL), `sample_fps` is ignored and will be overridden by the video reader backend.
#         - When `video` is a frame list, `sample_fps` informs the model of the original sampling rate to help understand temporal density.
#     """

#     messages = [
#         {"role": "user", "content": [
#                 {"video": video,
#                 "total_pixels": total_pixels, #resolution 
#                 "min_pixels": min_pixels, #resolution 
#                 "max_frames": max_frames, #can adjust fro longer/shorter videos as required
#                 'sample_fps':sample_fps}, #frame rate, normal is 2
#                 {"type": "text", "text": prompt},
#             ]
#         },
#     ]
#     text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) #builds template for the action log text
#     image_inputs, video_inputs, video_kwargs = process_vision_info([messages], return_video_kwargs=True, 
#                                                                    image_patch_size= 16,
#                                                                    return_video_metadata=True)
#     if video_inputs is not None:
#         video_inputs, video_metadatas = zip(*video_inputs)
#         video_inputs, video_metadatas = list(video_inputs), list(video_metadatas)
#     else:
#         video_metadatas = None
#     inputs = processor(text=[text], images=image_inputs, videos=video_inputs, video_metadata=video_metadatas, **video_kwargs, do_resize=False, return_tensors="pt")
#     inputs = inputs.to('cuda')

#     output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
#     generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
#     output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
#     return output_text[0]

# ### 1. Local Inference — Using Video URL
# result = inference(
#     video="path/to/your/video.mp4",  # CAN ALSO BE A URL 
#     prompt="Describe this video. Explain in detail the action and movement of the person/ character in the video. Output an action log with timestamped actions in JSON format: [{\"action\": ..., \"start_s\": ..., \"end_s\": ...}]",
#     sample_fps=4,  # increase for finer-grained action detection
# )
# print(result)
