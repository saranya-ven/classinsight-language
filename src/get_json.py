'''
Created on January 10, 2020
Last Modified: March 26 2020

@author: jzc1104

It takes a CSV file or directory with CSV files and converts it/them into JSON files

This file results by putting together the files "read_input_file.py" and "data_structures.py" in order to have a single file
Apart from avoiding importing the Structures in data_structures.py, the method isTimeFormat() appears in both files, so only one copy is preserved here

'''

import os,csv,copy
from datetime import datetime


time_format="%H:%M:%S"
buoyancy=False
#These seem to be stable and homogeneous, they refer to column names in the CSV files
speaker_label="Speaker"
transcript_label="Transcript"
timestamp_label="Time_Stamp"
participation_types=['Whole class discussion', 
         'Lecture', 
         'Small group + Instructor',  
         'Individual Work', 
         'Pair Work', 
         'Other']

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

header2= ['Speaker', 
     'Time_Stamp', 
     'Transcript', 
     
     'Turn-Taking Facilitation', 
     'Metacognitive Modeling Questions', 
     'Behavior Management Questions', 
     'Re-Voicing',
     'Teacher Open-Ended S/Q', 
     'Teacher Close-Ended S/Q', 
     'Teacher Explanation + Evidence',
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
     'Other',
     'Activity Description']

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

utterance_types2=['Turn-Taking Facilitation', 
         'Metacognitive Modeling Questions', 
         'Behavior Management Questions', 
         'Re-Voicing',
         'Teacher Open-Ended S/Q', 
         'Teacher Close-Ended S/Q', 
         'Teacher Explanation + Evidence',
         'Student Open-Ended S/Q', 
         'Student Close-Ended S/Q', 
         'Student Close-Ended Response', 
         'Student Open-Ended Response', 
         'Student Explanation + Evidence']


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
    def __init__(self,teacher,title,segments,time_format,original_csvfile):
        self.teacher=teacher
        self.title=title
        self.segments=segments
        self.original_csv=original_csvfile
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
    def print_me(self):
        print(self.teacher,self.title,self.original_csv)
        print(self.initial_time,self.end_time)
        for seg in self.segments:
            seg.print_me()
            
    def save_to_json(self,json_filename):
        import jsonpickle,json
        json_string=jsonpickle.encode(self)
        parsed = json.loads(json_string)
        json_string_formatted=json.dumps(parsed, indent=4, sort_keys=True)
        
        output_file=open(json_filename,"w+")
        output_file.write(json_string_formatted)
        output_file.close()
    
class Participation_Segment:
    def __init__(self,participation_type,speaking_turns=[]):
        self.participation_type=participation_type
        self.speaking_turns=speaking_turns
    
    def calculate_duration(self,time_format):
        self.initial_time=self.speaking_turns[0].initial_time
        self.end_time=self.speaking_turns[-1].end_time
        self.duration=calculate_duration_from_timestamps(self.initial_time, self.end_time, time_format)
                
    def print_me(self,prefix=""):
        print(prefix,self.participation_type,self.initial_time,self.end_time)
        for speak_turn in self.speaking_turns:
            speak_turn.print_me(prefix+"\t")
    
class Speaking_Turn:
    def __init__(self,speaker_pseudo,utterances=[]):
        self.speaker_pseudonym=speaker_pseudo
        self.utterances=utterances
        
        if "Teacher" in speaker_pseudo:
            self.speaker_type="teacher"
        elif "Student" in speaker_pseudo:
            self.speaker_type="student"
        else: self.speaker_type="other"
    
    def print_me(self,prefix=""):
        print(prefix,self.speaker_pseudonym,self.speaker_type,self.initial_time,self.end_time)
        for utt in self.utterances:
            utt.print_me(prefix+"\t")
        
        
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
                print ("invalid initial time",chunk[0].timestamp,last_valid_time,initial_time)
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
        
    def print_me(self,prefix=""):
        print (prefix,self.line_number,self.utterance,self.utterance_type)    
    

def get_filenames_in_dir(dir_path,file_extension):
    from os import listdir
    from os.path import isfile, join
    
    filenames = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    filenames = [f for f in filenames if file_extension in f]
    print(filenames)
    return filenames

def addheader_and_trimspaces(file_path_name):
    lines=[]
    
    file_basename=os.path.basename(file_path_name)
    file_path=os.path.dirname(file_path_name)
    
    use_header2=False
    
    with open(file_path_name, encoding = 'utf-8', errors="ignore") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        orig_header=next(reader)#we ignore the header in the file which is prone to typos, and use our own
    
        file_header=copy.copy(header)
        for h in orig_header:
            if h.find("oicing")>-1: 
                use_header2=True
                file_header=copy.copy(header2)
                break
        
        if not use_header2 and 'Activity Description' in orig_header: file_header.append('Activity Description')
        lines.append(file_header)
        
        for row in reader:
            row_strip=[column_content.strip() for column_content in row]
            lines.append(row_strip)

    
    aux_filename=file_path+"/mod_"+file_basename
    with open(aux_filename,"w+",encoding = 'utf-8')  as csvfile:
        writer=csv.writer(csvfile,delimiter=",")
        for row in lines:
            writer.writerow(row)
            
    return aux_filename
            
         
def verify_speaker_format(speaker_string):
    if speaker_string.endswith(":"):
        speaker_string=speaker_string[:-1]
    return speaker_string

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

def get_line_participation_type(line_dict):
    for part_type in participation_types:
        if line_dict[part_type]=="1" or line_dict[part_type]==1:
            return part_type
    return "none"
   
def get_utterance_types(line_dict,utt_types):
    return [utt_type for utt_type in utt_types if line_dict[utt_type]=="1" or line_dict[utt_type]==1]
    
    
    
def split_participation_segments(speaking_turns,use_activity_descritions=False):
    current_segment=Participation_Segment("no_segment")
    segments=[]
        
    for (turn,participation_type) in speaking_turns:
        if participation_type!=current_segment.participation_type:
            
            if current_segment.participation_type!="no_segment":segments.append(current_segment)
            current_segment=Participation_Segment(participation_type,[turn])
            if use_activity_descritions: 
                current_segment.activity_description=turn.activity_description
                del turn.activity_description
        else:
            current_segment.speaking_turns.append(turn)
            if use_activity_descritions: 
                current_segment.activity_description.extend(turn.activity_description)
                del turn.activity_description
    
    segments.append(current_segment)
    return segments

    
        
def split_speaking_turns(transcript_lines,teacher_nickname,testing=False):
    current_turn=Speaking_Turn("no_speaking_turn")
    current_participation_type="no_participation_type"
    speaking_turns=[]
    
    if buoyancy:last_valid_time="[00:00:00;00]"
    else:last_valid_time="00:00:00"
    
    line_number=0
    for line in transcript_lines:
        line_number+=1
        
        l_speaker=verify_speaker_format(line[speaker_label])
        if l_speaker==teacher_nickname: l_speaker="Teacher"
        l_transcript=line[transcript_label]
        if l_transcript=="": continue #if the transcript is empty, ignore it
        

        l_time=line[timestamp_label]
        if isTimeFormat(l_time,time_format): last_valid_time=l_time
        elif l_time!="":print ("invalid time at line:"+str(line_number)+"__"+l_time+"__")

        if testing:l_utterance_type=[]
        else:
            if 'Re-Voicing' in line:l_utterance_type=get_utterance_types(line,utterance_types2)
            else:l_utterance_type=get_utterance_types(line, utterance_types)
                
        l_participation_type=get_line_participation_type(line)
        if l_participation_type=="none":
            print (str(line_number)+" no participation type")
            l_participation_type=current_participation_type
            
        new_utterance=Utterance(line_number,l_transcript,l_utterance_type,l_time)
                        
        #IF SPEAKER CHANGES OR THE PARTICIPATION TYPE CHANGES, WE ASSUME A NEW SPEAKING TURN
        if (l_speaker!= current_turn.speaker_pseudonym and l_speaker!="") or l_participation_type!= current_participation_type:
            
            if current_turn.speaker_pseudonym!= "no_speaking_turn": #If there is already a speaking turn  
                current_turn.end_time=last_valid_time
                current_turn.do_time_calculations(time_format)
                
                speaking_turns.append((current_turn,current_participation_type))
            
            if l_speaker=="": #If the participation structure changed and the speaker is the same (signaled by empty)
                l_speaker=current_turn.speaker_pseudonym
            
            current_turn=Speaking_Turn(l_speaker,[new_utterance])
            
            
            if 'Activity Description' in line:
                #print (line['Activity Description'])
                if line['Activity Description']!="": current_turn.activity_description=[line['Activity Description']]
                else:current_turn.activity_description=[]
            current_turn.initial_time=last_valid_time
            current_participation_type=l_participation_type
        
        else:
            current_turn.utterances.append(new_utterance)
            if 'Activity Description' in line and line['Activity Description']!="":current_turn.activity_description.append(line['Activity Description'])
       
                        
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
    
    initial_interval=int(initial_seconds/interval_size)
    end_interval=int(end_seconds/interval_size)

    return range(initial_interval,end_interval+1)


def process_file(file_name,csv_folder,json_folder,time_format,testing=False):
    filename_base=os.path.basename(file_name)
    
    teacher_nick= filename_base[:-4].split("_")[1]
    period_date= filename_base[:-4].split("_")[0]
    extra_suffixes= "_".join(filename_base[:-4].split("_")[2:])
    
    if csv_folder!="":file_name_path=csv_folder+"/"+filename_base
    else:file_name_path=file_name
    
    print("Processing: "+file_name_path)
    
    #This part creates an auxiliary file: mod_+originalfilename
    aux_filename=addheader_and_trimspaces(file_name_path)
    transcript_lines=[]
    with open(aux_filename,encoding="utf-8") as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=",")
        for line in csvreader:
            transcript_lines.append(line)   
    if 'Activity Description' in line: 
        use_activity_description=True
        print("Using Activity Descriptions")
    else: use_activity_description=False 
    #Here we remove the auxiliary file
    os.remove(aux_filename) 
    
    if not buoyancy:verify_timeformat(transcript_lines)
    
    turns=split_speaking_turns(transcript_lines,teacher_nick,testing)
    print ("Turns split")
    
    class_segments=split_participation_segments(turns,use_activity_description)
    for segment in class_segments:segment.calculate_duration(time_format)
    print ("Participation Segments split")
    
    period_object=Period(teacher_nick,period_date,class_segments,time_format,filename_base) 
    #period object needs to be created before the following because the period object triggers the calculation of turn durations         
    for (turnx,_) in turns:
        turnx.interval_5min=divide_turns_by_interval(turnx, 300)
        turnx.interval_10min=divide_turns_by_interval(turnx, 600)
        turnx.calculate_utterance_durations(time_format,period_object.initial_time)
        
    json_filename=json_folder+"/"+teacher_nick+"_"+period_date
    if extra_suffixes!="":json_filename+="_"+extra_suffixes
    json_filename+=".json"
    period_object.save_to_json(json_filename)    
    print("Created json file: "+json_filename+"\n")
    return json_filename
    
    

if __name__ == "__main__":
    
    live=True
    #live=False
    
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
            print("Input directory: "+arguments.inputdir)
            csv_folder=arguments.inputdir
            filenames=get_filenames_in_dir(csv_folder,".csv")
        else: #if no input file/directory is given, use current directory
            dirname, filename = os.path.split(os.path.abspath(__file__))
            print("Current directory taken as input directory:"+dirname)
            csv_folder=dirname 
            filenames=get_filenames_in_dir(csv_folder,".csv")
        
            
        if arguments.outputdir:
            print("Ouput directory: "+arguments.outputdir)
            json_folder=arguments.outputdir
        else: 
            dirname, filename = os.path.split(os.path.abspath(__file__))
            print("Current directory taken as output directory:"+dirname)
            json_folder=dirname
        
    else:
        import config as cfg
        csv_folder=cfg.csv_folder
        json_folder=cfg.json_folder
        
        filenames=get_filenames_in_dir(csv_folder,".csv")
        #filenames=["20200121_Evan_Pd7_8_Mixed_Andi_Tarang.csv"]
                                
        if buoyancy:
            csv_folder=json_folder=cfg.data_folder
            filenames=["Buoyancy_Teacher.csv"]
            time_format="[%H:%M:%S;%f]"


        
    for filename in filenames:
        process_file(filename,csv_folder,json_folder,time_format)
        #g=input("press something to continue")
            
                
        
            