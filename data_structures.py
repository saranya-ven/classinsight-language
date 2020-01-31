'''
Created on Sep 24, 2019

Contains the datastructures necessary to contain the information

@author: jzc1104
'''
from datetime import datetime


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
    '''
    Container for a single lesson. Each lesson is divided into participation SEGMENTS, where each segment can be e.g. Lecture, or Whole-class discussion
    '''
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
    '''
    Each segment in which a lesson is divided according to diverse pedagogical goals. Composed by speaking turns
    '''
    
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
    '''
    Within the same participation segment, a turn refers to all the utterances produced consecutively by the same speaker
    '''
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
    
        
