"""
Created by jzc1104 on Jan 21 2020

Takes a directory with JSON files created with the red_input_file script, and creates a dataset in order to do classification

"""
from read_input_file import get_filenames_in_dir
import jsonpickle, csv
from nltk.tokenize import word_tokenize

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"
embed = hub.Module(module_url)


""" This function takes as input a list of sentences/one sentence at a time and returns a 512 length embedding from
    Google's Universal Sentence Encoder pretrained module.

    Input parameter: Un-processed string sentences in a list/one at a time.
    For example inputs can be one of the following 2 types:
    Type 1: List of string type sentences ->  sentences_ = ["I am a sentence for which I would like to get its embedding.",
                        "Universal Sentence Encoder embeddings also support short paragraphs. ",
                        "There is no hard limit on how long the paragraph is. Roughly, the longer ",
                        "the more 'diluted' the embedding will be."]
    Type 2: one string sentence at a time -> sentences_ = "This is a single sentence input."

    Returns : Numpy array of dimension (n,512) where n is the number of sentences in input, and 512 is the embedding dimension
"""
def get_sentence_embedding(sentences):
    if not isinstance(sentences,(list,)):
        sentences = [sentences]
    tf.logging.set_verbosity(tf.logging.ERROR)
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        sentence_embedding = session.run(embed(sentences))
        return np.array(sentence_embedding)

sentences_ = ["I am a sentence for which I would like to get its embedding.",
            "Universal Sentence Encoder embeddings also support short paragraphs. ",
            "There is no hard limit on how long the paragraph is. Roughly, the longer ",
            "the more 'diluted' the embedding will be." ]

# Can also try this as input -> Uncomment next line
#sentences_ = "I am a sentence for which I would like to get its embedding."

# function call
#embeddings = get_sentence_embedding(sentences_)



def get_utterance_features(utterance_string,speaker_type,previous_speaker_type,particip_structure,utterance_types,original_csvname):
    

    
    
    speaker_types=["teacher","student","other"]
    previous_speaker_types=["teacher","student","other","no_previous_speaker"]
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
    
    
    utterance_features=[original_csvname]
    
    
    for sp_type in speaker_types:
        if sp_type == speaker_type:utterance_features.append(True)
        else: utterance_features.append(False)
         
    for sp_type in previous_speaker_types:
        if sp_type == previous_speaker_type:utterance_features.append(True)
        else: utterance_features.append(False)
        
    for part_structure in participation_structures:
        if part_structure== particip_structure:utterance_features.append(True)
        else: utterance_features.append(False)
        
    for utt_type in utterance_types_general:
        if utt_type in utterance_types: utterance_features.append(True)
        else: utterance_features.append(False)
        
    #FEATURES RELATED TO THE STRING
    if len(utterance_string.split())>1: single_word=False
    else: single_word=True
    utterance_features.append(single_word)

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
    
    
    json_folder="transcripts/official_transcripts/3_JSON_Files/"
    
    json_files=get_filenames_in_dir(json_folder,".json")
    #json_files=["Bonnie_20190508_per1.json"]
    json_files=['Teacher_Buoyancy.json']
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
    headers=["Original_CSV_File","Speaker_teacher","Speaker_student","Speaker_other","Previous_speaker_teacher","Previous_speaker_student","Previous_speaker_other","Previous_speaker_none",
             "Part_Discussion","Part_Lecture","Part_Small_Group","Part_Individual","Part_Pairs","Part_Other",
             "Utt_Turn_Taking","Utt_Behavior","Utt_Teacher_OpenQ","Utt_Teacher_CloseQ","Utt_Student_OpenQ","Utt_Student_CloseQ","Utt_Student_CloseR","Utt_Student_OpenR","Utt_Student_ExpEvi",
             "Single_Word",
             "what","What","why","Why","how","How","Is","do","Do","does","Does","can","Can","could","Could","where","Where","when","When",
             "QuestionMark","Student","Quotation","explain","Explain","right","no","No","yes","Yes","yeah","Yeah","because","Because",
             "Go_ahead","go_ahead","right_questionmark", "Right_period","How_many","How_much",
             "Embedding"
             ]
  
    with open("dataset_buoyancy.csv","w+") as output_csv_file:
        dataset_writer = csv.writer(output_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        dataset_writer.writerow(headers)
        
        for period in all_periods:
            print
            print period.original_csv
            utterances_period=[]
            
            first_speaker=True
            for segment in period.segments:
                #print "\t",segment.participation_type
                
                for turn in segment.speaking_turns:
                    if first_speaker:
                        previous_speaker_type="no_previous_speaker"
                        first_speaker=False
                    #print "\t","\t",turn.speaker_pseudonym, turn.speaker_type,previous_speaker_type#, turn.initial_time, turn.end_time, turn.cumulative_duration, turn.duration, "seconds"    
                    for utterance in turn.utterances:
                        #print "\t","\t","\t",utterance.utterance
                
                        new_utt=[utterance.utterance, turn.speaker_type, previous_speaker_type, segment.participation_type, utterance.utterance_type,period.original_csv]
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
            utterance_embeddings_period=get_sentence_embedding(only_utts_period)
             
            for utt_complete,utt_embedding in zip(utterances_period,utterance_embeddings_period):
                 
                print utt_complete[0]
                utt_features=get_utterance_features(utt_complete[0],utt_complete[1],utt_complete[2],utt_complete[3],utt_complete[4],utt_complete[5])
                utt_features.append(utt_embedding)
                dataset_writer.writerow(utt_features)
                
                
                print utt_features
    
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
         
        

        
        
         
                    
