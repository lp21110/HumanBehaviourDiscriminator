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
