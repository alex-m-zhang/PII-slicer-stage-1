from pydub import AudioSegment
import os
import json
import time

#if "ffmpeg" can't be found or "avprobe" can't be found, make sure to install ffmpeg and add the bin folder to the path.

#input data: the folder names of input and output folders
input_folder_name = "input_audio"
output_folder_name = "output_audio"

input_audio_names = os.listdir(input_folder_name)

#load one second of silence
silence = AudioSegment.from_file("silence_m4a.m4a")[:1000]

#sort the files into transcripts and actual audio files
transcripts = []
audio_files = []
for file in input_audio_names:
    if file.endswith(".json"):
        transcripts.append(file)
    else:
        audio_files.append(file)

for transcript in transcripts:
    print("Processing " + transcript[:-5]) #take the whole transcript name except ".json"
    for file in audio_files:
        #assume the audio file has the same name as the transcript.
        file_name = file.split(".")
        file_name = ".".join(file_name[:-1])
        #file_name is now the name of the audio file without the .xxx at the end.

        if file_name == transcript[:-5]:
            #create the audio list (and time how long it takes to import the audio file)
            start_timer = time.time()
            audio_list = AudioSegment.from_file(input_folder_name + "/" + file)
            end_timer = time.time()
            print(str(round(end_timer - start_timer, 2)) + " seconds to import. ")

            #keep track of the original file name for saving purposes later..
            original_file_name = file
            #extension type is useful to calculate but not needed for now
            extension = file.split(".")
            extension = extension[-1]
            break
    else:
        #no audio file found, don't want to do any processing
        print("Corresponding audio file not found! ")
        continue

    #load the json file
    with open(input_folder_name + "/" + transcript) as transcript_file:
        transcript_data = json.load(transcript_file)

    #print out the pre-processed audio's length for sanity check
    print("Preprocessing length: " + str(len(audio_list)) + "ms. ")
    
    start_timer = time.time()
    PII_count = 0
    for segment_type in transcript_data["value"]["segments"]:
        if segment_type["primaryType"] == "PII":
            PII_count += 1

            #AudioSegment works in ms, so convert times to ms. They're given in seconds.
            start_time = segment_type["start"] * 1000
            end_time = segment_type["end"] * 1000
            length = end_time - start_time

            #simple list slicing cuts the audio file into what we want
            #part1 is the audio file up until the start-cutting point.
            part1 = audio_list[:start_time]
            #part2 is the audio file from the end-cutting point to the end.
            part2 = audio_list[end_time:]

            #calculate how many full seconds of silence is needed
            full_silences = int(length / 1000)
            #calculate how many parts of a full silence is needed to finish
            silence_index = length % 1000

            #build the audio file
            audio_list = part1
            audio_list += silence * full_silences
            audio_list += silence[:silence_index]
            audio_list += part2

    print(str(PII_count) + " PIIs found and removed. ")
    end_timer = time.time()
    #this prints how long it took to process all the PII
    print(str(round(end_timer - start_timer, 2)) + " seconds to remove PII. ")
    
    #print the length after processing (should be exact same as length before processing
    print("Postprocessing length: " + str(len(audio_list)) + "ms. ")
    start_timer = time.time()
    #export the audio. The file format doesn't need to be specified.
    audio_list.export(output_folder_name + "/" + original_file_name)
    end_timer = time.time()
    print(str(round(end_timer - start_timer, 2)) + " seconds to export. ")

    print("\n")