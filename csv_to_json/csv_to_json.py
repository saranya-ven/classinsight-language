import argparse
import csv
import pandas as pd
import itertools
from collections import Counter 
from itertools import tee, count
import json
import pprint
from datetime import datetime
import glob
import os
import numpy as np
from pathlib import Path

def convert_to_json(csv_path_list, json_folder_path):
    """Function that takes a list of .csv file(s) and a path to a destination folder as input, 
    converts the .csv file contents into .json format and stores it in the destination folder
    to be used for visualization.   
    """ 
    for file in csv_path_list:

        print("Processing file ", file)

        with open(file, "r") as f:
            reader = csv.reader(f)
            i = next(reader)
            rest = list(reader)

            meta_idx = list(filter(None, i))[1:] # First line of .csv contains metadata headers
            meta_vals = list(filter(None, rest[0])) # Second line of .csv contains metadata values
            title_line = rest[1] # Third line contains data headers
            fields = rest[2:] # Fourth line marks the beginning of data values
        
        # Metadata is stored in a separate dictionary and data is stored in a dataframe that are combined later
        meta_dict = dict(zip(meta_idx, meta_vals))
        meta_dict["teacher"] = meta_dict.pop('Instructor')
        
        def uniquify(seq, suffs = count(1)):
            """Make all the items unique by adding a suffix (1, 2, etc).

            `seq` is mutable sequence of strings.
            `suffs` is an optional alternative suffix iterable.
            """
            not_unique = [k for k,v in Counter(seq).items() if v>1] # so we have: ['name', 'zip']
            # suffix generator dict - e.g., {'name': <my_gen>, 'zip': <my_gen>}
            suff_gens = dict(zip(not_unique, tee(suffs, len(not_unique))))  
            for idx,s in enumerate(seq):
                try:
                    suffix = str(next(suff_gens[s]))
                except KeyError:
                    # s was unique
                    continue
                else:
                    seq[idx] += suffix

        uniquify(title_line) # To make all column names unique 
        
        # Storing data in a dataframe to be combined with metadata dictionary later
        df = pd.DataFrame(fields,columns=title_line)     
        df = df.rename(columns=str.lower)
        
        def reformat_time(time):
            """Takes a time value and converts it into standard("%H:%M:%S") format"""
            target_time_format = "%H:%M:%S" # Format to be converted into
            other_time_formats = ["%M:%S", "%M:%S:00"] # Adding different time formats present in the dataset
            
            try:
                if datetime.strptime(time, target_time_format):
                    return time
            except:
                for i in range(len(other_time_formats)):
                    try:
                        if datetime.strptime(time, other_time_formats[i]):
                            time_object=datetime.strptime(time, other_time_formats[i])
                            time = time_object.strftime(target_time_format)
                    except:
                        continue
            return time
                               
        df['time stamp'] = list(map(reformat_time, df['time stamp'].values))
            
        df['speaker'] = df['speaker'].replace(':','', regex=True) # Removing ":" trailing speaker names
        
        durations = list()
        for first, second in zip(df['time stamp'], df['time stamp'].values[1:]):
            time_format="%H:%M:%S"
            try:
                init_time=datetime.strptime(first, time_format)
                end_time=datetime.strptime(second, time_format)
                duration=end_time-init_time
                durations.append(duration.total_seconds())
            except:
                durations.append(0.0) # If either start or end time stamps are missing
        durations.append(0.0) # The last data entry's duration is unknown as class end time isn't available
        df['duration'] = durations
        
        df.rename(columns={"time stamp":"initial_time", "speaker":"speaker_pseudonym" \
                        }, errors='raise', inplace=True) # Renaming feilds as needed for visualization
        init_times = list(df["initial_time"].values[1:])
        init_times.append("")
        df["end_time"] = init_times
        codes_list = []
        codes1 = df["cluster codes (r, e, i, b, p, c)1"].values
        codes2 = df["cluster codes (r, e, i, b, p, c)2"].values
        for i in range(len(codes1)):
            if codes2[i]:
                codes_list.append([codes1[i], codes2[i]]) # Combine codes (if more than 1) into list for visualization
            else: codes_list.append([codes1[i]])
        
        # Pushing "utterance" and "utterance_type" into a nested dictionary within "utterances"
        df["utterance_type"] = codes_list
        dict_utterance_info = {}
        dict_utterance_info['utterance'] = df['utterance']
        dict_utterance_info['code'] = df['utterance_type']
        df = df.groupby(['speaker_pseudonym','initial_time','duration','end_time'], as_index=False) \
                        .apply(lambda x: x[["utterance","utterance_type"]].to_dict('r')).reset_index() 
        df.rename(columns={0:"utterances"}, inplace=True) 
        
        # Converting dataframe to json
        j = df.to_json(orient='records', indent=2)
        parsed = json.loads(j)
        
        # Restructuring metadata dictionary for plotting
        meta_dict = dict((k.lower(), v) for k,v in meta_dict.items())
        meta_dict['segments'] = {}
        meta_dict['title'] = meta_dict["pre-interview"].split('_')[0]
        
        # Combining dataframe i.e. data ("parsed") with metadata dictionary
        meta_dict['segments']['speaking_turns'] = parsed
        
        meta_dict['duration'] = sum(durations[:-1])
        meta_dict['end_time'] = df['end_time'].values[-1]
        meta_dict['initial_time'] = '0:00:00'
        
        # Create .json filename based on .csv finename
        json_filename = json_folder_path + '/' +Path(file).stem + '.json'
        
        # Write .json to filename
        with open(json_filename, 'w') as outfile:
            outfile.write(json.dumps(meta_dict, indent=4, sort_keys=False)) 

if __name__ == "__main__":
    

    parser = argparse.ArgumentParser()
        
    parser.add_argument("-i","--inputdir", help="directory that contains all input CSV files. \
                       If not specified, the current directory is considered the output directory")
    parser.add_argument("-o","--outputdir", help="directory where all JSON files will be placed. \
                        If not specified, the current directory is considered the output directory")

    arguments= parser.parse_args()


    if arguments.inputdir:# If input directory is provided
        csv_folder=arguments.inputdir
    else: # If no input file/directory is provided, use current directory
        dirname, filename = os.path.split(os.path.abspath(__file__))
        csv_folder=dirname 
    filenames=glob.glob(csv_folder+"/*.csv")
    print("filenames", filenames)
   
    if arguments.outputdir:
        json_folder=arguments.outputdir
    else: 
        dirname, filename = os.path.split(os.path.abspath(__file__))
        json_folder=dirname
        
    convert_to_json(filenames,json_folder)

# Input and output folder locations cana lso be hardcoded like so:
#     csv_folder="transcripts/official_transcripts/2_CSV_Files/2020"
#     json_folder="transcripts/official_transcripts/3_JSON_Files/2020"
#     filenames=glob.glob(csv_folder+"/*.csv")