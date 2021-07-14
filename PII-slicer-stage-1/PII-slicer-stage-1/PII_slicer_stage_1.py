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

transcripts = []
audio_files = []
for file in input_audio_names:
    if file.endswith(".json"):
        transcripts.append(file)
    else:
        audio_files.append(file)

for transcript in transcripts:
    print("Processing " + transcript[:-5])
    for file in audio_files:
        if file.startswith(transcript[:-5]):
            start_timer = time.time()
            audio_list = AudioSegment.from_file(input_folder_name + "/" + file)
            end_timer = time.time()
            print(str(round(end_timer - start_timer, 2)) + " seconds to import. ")
            original_file_name = file
            extension = file.split(".")
            extension = extension[-1]
            break
    else:
        print("Corresponding audio file not found! ")
        continue
    with open(input_folder_name + "/" + transcript) as transcript_file:
        transcript_data = json.load(transcript_file)
    print("Preprocessing length: " + str(len(audio_list)) + "ms. ")
    
    start_timer = time.time()
    PII_count = 0
    for segment_type in transcript_data["value"]["segments"]:
        if segment_type["primaryType"] == "PII":
            PII_count += 1
            start_time = segment_type["start"] * 1000
            end_time = segment_type["end"] * 1000
            length = end_time - start_time

            part1 = audio_list[:start_time]
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
    print(str(round(end_timer - start_timer, 2)) + " seconds to remove PII. ")
    
    #export the audio file
    print("Postprocessing length: " + str(len(audio_list)) + "ms. ")
    start_timer = time.time()
    audio_list.export(output_folder_name + "/" + original_file_name)
    end_timer = time.time()
    print(str(round(end_timer - start_timer, 2)) + " seconds to export. ")

    print("\n")