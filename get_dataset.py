"""
Created by jzc1104 on Jan 21 2020

Takes a directory with JSON files created with the red_input_file script, and creates a dataset for classification

"""
import jsonpickle, csv

from read_input_file import get_filenames_in_dir
from sentence_embeddings import get_sentence_embeddings
from nltk.tokenize import word_tokenize


def get_utterance_features(utt_complete):
    
    utterance_string=utt_complete[0]
    speaker_type=utt_complete[1]
    previous_speaker_type=utt_complete[2]
    next_speaker_type=utt_complete[3]
    particip_structure=utt_complete[4]
    utterance_types= utt_complete[5]
    first_utt_in_turn=utt_complete[6]
    last_utt_in_turn=utt_complete[7]
    original_csvname=utt_complete[8]
    

    speaker_types=["teacher","student","other"]
    previous_speaker_types=["teacher","student","other","no_previous_speaker"]
    next_speaker_types=["teacher","student","other","no_next_speaker"]
    participation_structures=['Whole class discussion', 'Lecture', 'Small group + Instructor',  'Individual Work', 'Pair Work', 'Other']
    utterance_types_general=['Turn-Taking Facilitation', 
             'Metacognitive Modeling Questions', 
             'Behavior Management Questions', 
             'Teacher Open-Ended S/Q', 
             'Teacher Close-Ended S/Q', 
             
             'Student Open-Ended S/Q', 
             'Student Close-Ended S/Q', 
             'Student Close-Ended Response', 
             'Student Open-Ended Response', 
             'Student Explanation + Evidence' ]
    
    
    question_words=["what","What","why","Why","how","How","Is","do","Do","does","Does","can","Can","could","Could","where","Where","when","When"]
    key_words=["?","Student","\"","explain","Explain","right","no","No","yes","Yes","yeah","Yeah","because","Because"]
    key_phrases=["Go ahead","go ahead","right?", "Right.","How many","How much"]
    
    
    utterance_features=[original_csvname,utterance_string]
    
    #THESE ARE THE CLASSES WE ARE LOOKING FOR
    for utt_type in utterance_types_general:
        if utt_type in utterance_types: utterance_features.append(True)
        else: utterance_features.append(False)

    #FEATURES TO PREDICT THE CLASSES
    for sp_type in speaker_types:
        if sp_type == speaker_type:utterance_features.append(True)
        else: utterance_features.append(False)
         
    for sp_type in previous_speaker_types:
        if sp_type == previous_speaker_type:utterance_features.append(True)
        else: utterance_features.append(False)
        
    for sp_type in next_speaker_types:
        if sp_type == next_speaker_type:utterance_features.append(True)
        else: utterance_features.append(False)
        
    utterance_features.append(first_utt_in_turn)
    utterance_features.append(last_utt_in_turn)
    
    for part_structure in participation_structures:
        if part_structure== particip_structure:utterance_features.append(True)
        else: utterance_features.append(False)
        

        
    #FEATURES RELATED TO THE STRING
    if len(utterance_string.split())>1: single_word=False
    else: single_word=True
    utterance_features.append(single_word)

    if type(utterance_string)!=str:
        print (utterance_string)
        print (type(utterance_string))
    
        print ("encoding error")
        utterance_string=utterance_string.decode("utf-8",errors='ignore')
        
    utterance_tokenized=word_tokenize(utterance_string)
    for word in question_words:
        if word in utterance_tokenized:utterance_features.append(True)
        else: utterance_features.append(False)
    for word in key_words:
        if word in utterance_tokenized:utterance_features.append(True)
        else: utterance_features.append(False)
    
    for phrase in key_phrases:
        if phrase in utterance_string: utterance_features.append(True)
        else: utterance_features.append(False)
        
    return utterance_features


if __name__ == "__main__":
    
    embedding_model="50"
    embedding_dimensionality=50
    
    output_csv_filename="dataset_all_"+embedding_model+"dim.csv"
    
    json_folder="transcripts/official_transcripts/3_JSON_Files/"
    datasets_folder="transcripts/official_transcripts/4_Datasets/"
    
    json_files=get_filenames_in_dir(json_folder,".json")
    #json_files=["Bonnie_20190508_per1.json"]
    #json_files=['Teacher_Buoyancy.json']\
    #json_files=['Michelle_20190507_per2.json']
    #json_files= ['Evan_20190515_Per3.json', 'Michelle_20190507_per2.json', 'Michelle_190429_Per_5.json', 'Bonnie_20190508_per3.json', 'Bill_20190515_Per3.json']
    #json_files= ['Jeff_0205.json', 'Evan_0212.json', 'Michelle_20190521_Per2.json', 'Kim_20190502_Per6.json', 'Henry_20190423_Per2.json'] 
                #===============================================================
                # 'Jeff_0205.json', 'Evan_0212.json', 'Michelle_20190521_Per2.json', 'Kim_20190502_Per6.json', 'Henry_20190423_Per2.json', 
                # 'Caren_0212.json', 'Sara_20190423_Per1.json', 'Stephanie_20190517_Per_3.json', 'Michelle_20190521_Per3.json', 'Henry_20190516_per5.json', 
                # 'Bill_0205.json', 'Michelle_20190429_per6.json', 'Tom_0805.json', 'Sheila_190520_Per_8.json', 'Sheila_20190520_Per6.json', 
                # 'Teacher_Buoyancy.json', 'Henry_20190510_Per2.json', 'Tom_20190508_Per3.json', 'Bonnie_190501_Per_5.json', 'Michelle_20190507_per1.json', 
                # 'Sara_190212_Per_2.json', 'Kim_20190423_Per6.json', 'Bonnie_20190508_per1.json']
                #===============================================================
    

    all_periods=[]
    for filename in json_files:
        json_file=open(json_folder+"/"+filename)
        json_str = json_file.read()
        period_object = jsonpickle.decode(json_str)
        all_periods.append(period_object)
        
        
    utterances=[]
    headers=["Original_CSV_File","Utterance_String",
             "Utt_Turn_Taking","Metacognitive_Modelling","Utt_Behavior","Utt_Teacher_OpenQ","Utt_Teacher_CloseQ","Utt_Student_OpenQ","Utt_Student_CloseQ","Utt_Student_CloseR","Utt_Student_OpenR","Utt_Student_ExpEvi",
             "Speaker_teacher","Speaker_student","Speaker_other","Previous_speaker_teacher","Previous_speaker_student","Previous_speaker_other","Previous_speaker_none",
             "Next_speaker_teacher","Next_speaker_student","Next_speaker_other","Next_speaker_none",
             "first_utterance_in_turn","last_utterance_in_turn",
             "Part_Discussion","Part_Lecture","Part_Small_Group","Part_Individual","Part_Pairs","Part_Other",
             "Single_Word",
             "what","What","why","Why","how","How","Is","do","Do","does","Does","can","Can","could","Could","where","Where","when","When",
             "QuestionMark","Student","Quotation","explain","Explain","right","no","No","yes","Yes","yeah","Yeah","because","Because",
             "Go_ahead","go_ahead","right_questionmark", "Right_period","How_many","How_much"
             ]
    

    for i in range(embedding_dimensionality):
        headers.append("Embedding_"+str(i))
  
<<<<<<< HEAD
    with open(datasets_folder+output_csv_filename,"w+",encoding="utf-8") as output_csv_file:
=======
    with open(datasets_folder+output_csv_filename,"w+") as output_csv_file:
>>>>>>> branch 'master' of https://github.com/iesus/classinsight-language.git
        dataset_writer = csv.writer(output_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        dataset_writer.writerow(headers)
        
        for period in all_periods:
            print
            print (period.original_csv)
            utterances_period=[]
            
            first_speaker=True
            for s,segment in enumerate(period.segments):
                #print "\t",s,segment.participation_type
                
                for t,turn in enumerate(segment.speaking_turns):
                    
                    if t ==len(segment.speaking_turns)-1: #If it's the last speaking turn in the segment
                    
                        if s==len(period.segments)-1: next_speaker_type="no_next_speaker" #if it's the last segment
                        else: next_speaker_type=period.segments[s+1].speaking_turns[0].speaker_type #if there is another segment
                    else: 
                        next_speaker_type=segment.speaking_turns[t+1].speaker_type #if there is another turn, find out the type of the next speaker
                        
                    
                    if first_speaker:
                        previous_speaker_type="no_previous_speaker"
                        first_speaker=False
                    #print "\t","\t",turn.speaker_pseudonym, turn.speaker_type,previous_speaker_type,next_speaker_type#, turn.initial_time, turn.end_time, turn.cumulative_duration, turn.duration, "seconds"    
                    for u,utterance in enumerate(turn.utterances):
                        
                        first_utterance_in_Turn=False
                        if u==0: first_utterance_in_Turn=True
                        
                        last_utterance_in_Turn=False
                        if u == len(turn.utterances)-1:
                            last_utterance_in_Turn=True
                        
                        #print "\t","\t","\t",utterance.utterance,first_utterance_in_Turn,last_utterance_in_Turn
                        
                        new_utt=[utterance.utterance, turn.speaker_type, previous_speaker_type,next_speaker_type, segment.participation_type, utterance.utterance_type,first_utterance_in_Turn,last_utterance_in_Turn,period.original_csv]
                        utterances.append(new_utt)
                        utterances_period.append(new_utt)
                    previous_speaker_type=turn.speaker_type
            
            
            #=======================================================================
            # sp_type='Teacher Open-Ended S/Q'
            # only_specific_type=[utt[0] for utt in utterances_period if sp_type in utt[5]]
            # 
            # 
            # for utt in only_specific_type:
            #     print utt
            #     print get_utterance_features(utt)
            #=======================================================================
            
                    
            only_utts_period=[utt[0] for utt in utterances_period]
            utterance_embeddings_period=get_sentence_embeddings(only_utts_period,embedding_model)
             
            for utt_complete,utt_embedding in zip(utterances_period,utterance_embeddings_period):
                 
                #print period.original_csv,utt_complete[0]
                
                utt_features=get_utterance_features(utt_complete)
                for i in range(embedding_dimensionality):
                    utt_features.append(utt_embedding[i])
                
                try:
                    dataset_writer.writerow(utt_features)
                except UnicodeEncodeError as e:
                    print (e)
                    utt_features[1]=utt_features[1].encode('utf-8')
                    print (utt_features[1])
                    dataset_writer.writerow(utt_features)
                
                
                #print utt_features
    
#===============================================================================
#          
#     utterance_types=['Turn-Taking Facilitation', 
#              'Metacognitive Modeling Questions', 
#              'Behavior Management Questions', 
#              'Teacher Open-Ended S/Q', 
#              'Teacher Close-Ended S/Q', 
#                
#              'Student Open-Ended S/Q', 
#              'Student Close-Ended S/Q', 
#              'Student Close-Ended Response', 
#              'Student Open-Ended Response', 
#              'Student Explanation + Evidence' ]
#           
#           
# 
#     print len(utterances)
#     for utt_type in utterance_types:
#         only_specific_type=[utt[0] for utt in utterances if utt_type in utt[4]]
#         #print only_specific_type
#         print len(only_specific_type),utt_type
#===============================================================================
        #=======================================================================
        # for utt in only_specific_type:
        #     print utt
        #=======================================================================
         
        

        
        
         
                    
