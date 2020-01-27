'''
Created on January 10, 2020
Last Modified: Jan 21 2020

@author: jzc1104

It takes a CSV file or directory with CSV files and converts it/them into JSON files

This file results by putting together the files "read_input_file.py" and "data_structures.py"
Apart from avoiding importing the Structures in data_structures.py, the method isTimeFormat() appears in both files, therefore only one copy is preserved here
The initial part where pip is imported and some packages are installed appears only in this file

'''
#import csv, os
from datetime import datetime

import pip

pkgs = ['csv', 'os','jsonpickle','json']
for package in pkgs:
    try:
        import package
    except ImportError, e:
        print (e)
        pip.main(['install', package])


def calculate_duration_from_timestamps(init_timestamp,end_timestamp,time_format):
    init_time=datetime.strptime(init_timestamp,time_format)
    end_time=datetime.strptime(end_timestamp,time_format)
    duration=end_time-init_time
    return duration.total_seconds()

def isTimeFormat(t_string,t_format):
    try:
        datetime.strptime(t_string,t_format)
        return True
    except ValueError:
        return False
    

class Period :
    def __init__(self,teacher,title,segments,time_format):
        self.teacher=teacher
        self.title=title
        self.segments=segments
        self.calculate_duration(time_format)
        self.calculate_turns_cumulative_durations(time_format)
        
    def calculate_duration(self,time_format):
        self.initial_time=self.segments[0].initial_time
        self.end_time=self.segments[-1].end_time
        self.duration=calculate_duration_from_timestamps(self.initial_time,self.end_time, time_format)
        
        
    def calculate_turns_cumulative_durations(self,time_format):
        for segment in self.segments:
            for turn in segment.speaking_turns:
                turn.calculate_cumulative_duration(self.initial_time,time_format)
    
class Participation_Segment:
    def __init__(self,participation_type,speaking_turns=[]):
        self.participation_type=participation_type
        self.speaking_turns=speaking_turns
    
    def calculate_duration(self,time_format):
        self.initial_time=self.speaking_turns[0].initial_time
        self.end_time=self.speaking_turns[-1].end_time
        self.duration=calculate_duration_from_timestamps(self.initial_time, self.end_time, time_format)
    
class Speaking_Turn:
    def __init__(self,speaker_pseudo,utterances=[]):
        self.speaker_pseudonym=speaker_pseudo
        self.utterances=utterances
        
        if "Teacher" in speaker_pseudo:
            self.speaker_type="teacher"
        elif "Student" in speaker_pseudo:
            self.speaker_type="student"
        else: self.speaker_type="other"
        
        
    def do_time_calculations(self,time_format):
        self.duration=calculate_duration_from_timestamps(self.initial_time,self.end_time, time_format)
        self.total_tokens=sum([utt.n_tokens for utt in self.utterances])

        if self.duration>0:
            self.tokens_per_second=self.total_tokens/self.duration
        else: self.tokens_per_second=0    
        
    def calculate_cumulative_duration(self,period_initial_time,time_format):
        self.cumulative_duration=calculate_duration_from_timestamps(period_initial_time,self.end_time, time_format)
        
    def calculate_utterance_durations(self,time_format,period_initial_time):
        #IT ASSUMES CUMULATIVE DURATION AND DURATIONS TO BE ALREADY SET
        initial_time=self.cumulative_duration-self.duration#start of speaking turn
    
        #First we segment the utterances into chunks with a known initial and end timestamp
        chunks=[]
        current_chunk=[]
        for utter in self.utterances:
            if isTimeFormat(utter.timestamp,time_format):
                if len(current_chunk)>0:chunks.append(current_chunk)
                current_chunk=[utter]
            else:current_chunk.append(utter)
        chunks.append(current_chunk)
        
        #Having the chunks, determine the initial_time
        chunks_start=[]
        last_valid_time=initial_time
        zero_time=datetime.strptime(period_initial_time,time_format)
        
        for i,chunk in enumerate(chunks):
            #print i,chunk
            if i==0:# if it's the first one
                chunk_start=initial_time
                
            elif isTimeFormat(chunk[0].timestamp,time_format):
                chunk_start_timefull=datetime.strptime(chunk[0].timestamp,time_format)-zero_time
                chunk_start=chunk_start_timefull.total_seconds()
                last_valid_time=chunk_start
                
            else:
                print "invalid initial time",chunk[0].timestamp,last_valid_time,initial_time
                chunk_start=last_valid_time
            
            chunks_start.append((chunk,chunk_start))

        #Then determine the end_time
        chunks_start_end=[]
        for i,chunk_st in enumerate(chunks_start):
            if i==len(chunks)-1: chunk_end=self.cumulative_duration #if it's the last chunk, the end is the end of the turn
            else: chunk_end=chunks_start[i+1][1] # if it's not the last one, the end is the beginning of next chunk
            
            chunks_start_end.append((chunk_st[0],chunk_st[1],chunk_end))
                      
        for (chunk,start,end) in chunks_start_end:
            total_chunk_duration=end-start
            total_chunk_tokens=sum([utt.n_tokens for utt in chunk])
            if total_chunk_duration>0:tokens_per_sec=total_chunk_tokens/total_chunk_duration
            else:tokens_per_sec=0
            
            cumulative_duration=start
            for utt in chunk:
                if tokens_per_sec>0:utt.duration=utt.n_tokens/tokens_per_sec
                else: utt.duration=0
                
                cumulative_duration+=utt.duration
                utt.cumulative_duration=cumulative_duration
                utt.tokens_per_second=tokens_per_sec
            #print len(chunk),start,end,total_chunk_duration,total_chunk_tokens,tokens_per_sec    
                
        
        
        
class Utterance:
    def __init__(self,line_number,utterance,utterance_type="none",time=""):
        self.line_number=line_number
        self.utterance=utterance
        self.utterance_type=utterance_type
        self.timestamp=time
        self.n_tokens=len(self.utterance.split())
        
        
class Speaker:
    def __init__(self,pseudonym, speaker_type,periods=[]):
        self.pseudonym=pseudonym
        self.speaker_type=speaker_type
        self.periods=periods





def save_to_json(object_instance,json_filename):
    import jsonpickle,json
    json_string=jsonpickle.encode(object_instance)
    parsed = json.loads(json_string)
    json_string_formatted=json.dumps(parsed, indent=4, sort_keys=True)
    
    output_file=open(json_filename,"w+")
    output_file.write(json_string_formatted)
    output_file.close()
    
def get_filenames_in_dir(dir_path,file_extension):
    from os import listdir
    from os.path import isfile, join
    
    filenames = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    filenames = [f for f in filenames if file_extension in f]
    print (filenames)
    return filenames

def addheader_and_trimspaces(file_path_name,header):
    lines=[]
    with open(file_path_name) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        _=next(reader)#we ignore the header in the file, and use our own
        lines.append(header)
        
        for row in reader:
            row_strip=[column_content.strip() for column_content in row]
            lines.append(row_strip)
    
    with open(file_path_name,"w+")  as csvfile:
        writer=csv.writer(csvfile,delimiter=",")
        for row in lines:
            writer.writerow(row)
            
         
def verify_speaker_format(speaker_string):
    if speaker_string.endswith(":"):
        speaker_string=speaker_string[:-1]
    return speaker_string

    
            

def get_line_participation_type(line_dict):
    for part_type in participation_types:
        if line_dict[part_type]=="1" or line_dict[part_type]==1:
            return part_type
    return "none"
   
def get_utterance_type(line_dict):
    types=[utt_type for utt_type in utterance_types if line_dict[utt_type]=="1" or line_dict[utt_type]==1]
    return types
    
    
def split_participation_segments(speaking_turns):
    current_segment=Participation_Segment("no_segment")
    segments=[]
        
    for (turn,participation_type) in speaking_turns:
        if participation_type!=current_segment.participation_type:
            
            if current_segment.participation_type!="no_segment":segments.append(current_segment)
            current_segment=Participation_Segment(participation_type,[turn])
        
        else:current_segment.speaking_turns.append(turn)
    
    segments.append(current_segment)
    return segments


def add_speaker(speaker_dict,speaker_id):
    if not speaker_dict.has_key(speaker_id):
        if speaker_id=="Teacher": speaker_type="teacher"
        else: speaker_type="student"
        
        new_speaker= Speaker(speaker_id,speaker_type)
        speaker_dict[speaker_id]=new_speaker
    return speaker_dict

def verify_timeformat(transcript_lines):
    time_format="%H:%M:%S"
    time_format2="%M:%S"
    time_format3="%M:%S:00" #don-t know why this ever happens

    for line in transcript_lines:
        l_time=line[timestamp_label]
        
        if isTimeFormat(l_time, time_format):continue # all good :)
        
        elif isTimeFormat(l_time, time_format2): #if it is the short version
            time_object=datetime.strptime(l_time,time_format2)
            l_time=time_object.strftime(time_format)

        elif isTimeFormat(l_time, time_format3): #if it's Min:Sec:00
            time_object=datetime.strptime(l_time,time_format3)
            l_time=time_object.strftime(time_format)
        
        line[timestamp_label]=l_time
    
        
def split_speaking_turns(transcript_lines):
    current_turn=Speaking_Turn("no_speaking_turn")
    current_participation_type="no_participation_type"
    speaking_turns=[]
    
    if buoyancy:last_valid_time="[00:00:00;00]"
    else:last_valid_time="00:00:00"
    
    line_number=0
    for line in transcript_lines:
        
        l_speaker=verify_speaker_format(line[speaker_label])
        l_transcript=line[transcript_label]
        if l_transcript=="": continue
        

        l_time=line[timestamp_label]
        if isTimeFormat(l_time,time_format): last_valid_time=l_time
        elif l_time!="":print ("invalid time at line:"+str(line_number)+"__"+l_time+"__")

        
        l_utterance_type=get_utterance_type(line)
        l_participation_type=get_line_participation_type(line)
        if l_participation_type=="none":
            print (str(line_number)+" no participation type")
            l_participation_type=current_participation_type
            
        
        new_utterance=Utterance(line_number,l_transcript,l_utterance_type,l_time)
        line_number+=1
        
                
        #IF SPEAKER CHANGES OR THE PARTICIPATION TYPE CHANGES, WE ASSUME A NEW SPEAKING TURN
        if (l_speaker!= current_turn.speaker_pseudonym and l_speaker!="") or l_participation_type!= current_participation_type:
            
            
            if current_turn.speaker_pseudonym!= "no_speaking_turn": #If there is already a speaking turn  
                current_turn.end_time=last_valid_time
                current_turn.do_time_calculations(time_format)
                
                speaking_turns.append((current_turn,current_participation_type))
            
            if l_speaker=="": #If the participation structure changed and the speaker is the same (signaled by empty)
                l_speaker=current_turn.speaker_pseudonym
            
            current_turn=Speaking_Turn(l_speaker,[new_utterance])
            current_turn.initial_time=last_valid_time
            current_participation_type=l_participation_type
        
        else:current_turn.utterances.append(new_utterance)
                        
    current_turn.end_time=last_valid_time
    current_turn.do_time_calculations(time_format)
    speaking_turns.append((current_turn,current_participation_type))
    
    return speaking_turns

def divide_turns_by_interval(turn,interval_size=300):
    '''
    interval is given in amount of seconds
    returns a list with the labels of the intervals to which the turn belongs
    '''    
    initial_seconds=int(turn.cumulative_duration-turn.duration)
    end_seconds=int(turn.cumulative_duration)
    
    initial_interval=initial_seconds/interval_size
    end_interval=end_seconds/interval_size

    return range(initial_interval,end_interval+1)
        


if __name__ == "__main__":
    
    live=True
    live=False
    buoyancy=False
    time_format="%H:%M:%S"
    
    if live:
        
        import argparse
        parser = argparse.ArgumentParser()
        
        parser.add_argument("-i","--inputdir", help="directory that contains all input CSV files. If not specified and not -f, then the current directory (where the script is located) is considered as input directory.")
        parser.add_argument("-o","--outputdir", help="directory where all JSON files will be placed. If not specified, the current directory is considered the output directory")
        parser.add_argument("-f","--file", help="input file. If specified, the script will only process a single file")
        
        arguments= parser.parse_args()
        
        if arguments.file: #if single file is to be processed
            filenames=[arguments.file]
            csv_folder=""
        elif arguments.inputdir:# if input directory is given
            print ("Input directory: "+arguments.inputdir)
            csv_folder=arguments.inputdir
            filenames=get_filenames_in_dir(csv_folder,".csv")
        else: #if no input file/directory is given, use current directory
            dirname, filename = os.path.split(os.path.abspath(__file__))
            print ("Current directory taken as input directory:"+dirname)
            csv_folder=dirname 
            filenames=get_filenames_in_dir(csv_folder,".csv")
        
            
        if arguments.outputdir:
            print ("Ouput directory: "+arguments.outputdir)
            json_folder=arguments.outputdir
        else: 
            dirname, filename = os.path.split(os.path.abspath(__file__))
            print ("Current directory taken as output directory:"+dirname)
            json_folder=dirname
        
    else:
        csv_folder="transcripts/official_transcripts/2_CSV_Files/2020"
        json_folder="transcripts/official_transcripts/3_JSON_Files/2020"
        filenames=get_filenames_in_dir(csv_folder,".csv")
        
        #=======================================================================
        # csv_folder="transcripts/official_transcripts/2_CSV_Files/"
        # json_folder="transcripts/official_transcripts/3_JSON_Files/"
        # filenames=get_filenames_in_dir(csv_folder,".csv")
        #=======================================================================
        #filenames=["0205_Bill.csv","0205_Jeff.csv","0212_Caren.csv","0212_Evan.csv","0805_Tom.csv","190212_Sara_Per_2.csv","20190517_Stephanie_Per_3.csv"]
        #filenames=["190429_Michelle_Per_5.csv","190501_Bonnie_Per_5.csv","190520_Sheila_Per_8.csv","20190502_Kim_Per6.csv","20190515_Bill_Per3.csv"]
        #filenames=["20190508_Bonnie_per1.csv"]

   
    if buoyancy:
        csv_folder="transcripts/"
        json_folder="transcripts/"
        filenames=["Buoyancy_Teacher.csv"]
        time_format="[%H:%M:%S;%f]"


    
    header= ['Speaker', 
         'Time_Stamp', 
         'Transcript', 
         
         'Turn-Taking Facilitation', 
         'Metacognitive Modeling Questions', 
         'Behavior Management Questions', 
         'Teacher Open-Ended S/Q', 
         'Teacher Close-Ended S/Q', 
         'Student Open-Ended S/Q', 
         'Student Close-Ended S/Q', 
         'Student Close-Ended Response', 
         'Student Open-Ended Response', 
         'Student Explanation + Evidence', 
        
         'Whole class discussion', 
         'Lecture', 
         'Small group + Instructor', 
         'Individual Work', 
         'Pair Work', 
         'Other']

    utterance_types=['Turn-Taking Facilitation', 
             'Metacognitive Modeling Questions', 
             'Behavior Management Questions', 
             'Teacher Open-Ended S/Q', 
             'Teacher Close-Ended S/Q', 
             
             'Student Open-Ended S/Q', 
             'Student Close-Ended S/Q', 
             'Student Close-Ended Response', 
             'Student Open-Ended Response', 
             'Student Explanation + Evidence' ]
    
    participation_types=['Whole class discussion', 
             'Lecture', 
             'Small group + Instructor',  
             'Individual Work', 
             'Pair Work', 
             'Other']
    
    speaker_label="Speaker"
    transcript_label="Transcript"
    timestamp_label="Time_Stamp"
    
    
    
    def process_file(file_name,header):
        print ("Processing: "+file_name)
        
        filename_base=os.path.basename(file_name)
        
        teacher_nick= filename_base[:-4].split("_")[1]
        period_date= filename_base[:-4].split("_")[0]
        extra_suffixes= "_".join(filename_base[:-4].split("_")[2:])
        
        if csv_folder!="":file_name_path=csv_folder+"//"+filename_base
        else:file_name_path=file_name
        
        print(file_name_path)
        
        addheader_and_trimspaces(file_name_path,header)
    
        transcript_lines=[]
        with open(file_name_path) as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=",")
            for line in csvreader:
                transcript_lines.append(line)    
        
        if not buoyancy:verify_timeformat(transcript_lines)
        
        turns=split_speaking_turns(transcript_lines)
        print ("Turns split")
        #=======================================================================
        # for (turn,part_type) in turns[:100]:
        #     print turn.speaker_pseudonym
        #     print turn.initial_time
        #     print turn.end_time
        #     print turn.duration
        #     print turn.total_tokens
        #     print turn.tokens_per_second
        #     for utterance in turn.utterances:
        #         print "\t",utterance.line_number,utterance.utterance_type,utterance.utterance
        #=======================================================================
        
        class_segments=split_participation_segments(turns)
        for segment in class_segments:segment.calculate_duration(time_format)
        print ("Participation Segments split")
        
        period_object=Period(teacher_nick,period_date,class_segments,time_format)
         
        for (turnx,_) in turns:
            turnx.interval_5min=divide_turns_by_interval(turnx, 300)
            turnx.interval_10min=divide_turns_by_interval(turnx, 600)
            turnx.calculate_utterance_durations(time_format,period_object.initial_time)
            
        json_filename=json_folder+"/"+teacher_nick+"_"+period_date
        if extra_suffixes!="":json_filename+="_"+extra_suffixes
        json_filename+=".json"
        
        save_to_json(period_object,json_filename)    
        print ("Created json file: "+json_filename+"\n")
        
        
    for filename in filenames:
        process_file(filename,header)
            