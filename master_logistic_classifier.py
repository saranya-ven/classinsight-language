'''
Having trained a logistic classifier with the optimal configuration for each utterance type:
- load all the classifiers into a single object
- receive an unannotated CSV file
- perform and output the classification scores of the new CSV file
'''
import os,csv
import pandas as pd
import numpy as np
import pickle,jsonpickle

from read_input_file import process_file
from sentence_embeddings import load_embeddings_model
from get_dataset import extract_features_period

if __name__ == "__main__":
    
    pickle_filepath="master_logistic_classifier.pkl"
    with open(pickle_filepath, 'rb') as file:
        (all_classifiers,all_thresholds,embedding_per_utt_type)= pickle.load(file)
    
    csv_folder="transcripts/official_transcripts/2_CSV_Files/"
    testing_filename="20190508_Bonnie_per1.csv"
    test_folder="transcripts/official_transcripts/5_Test/"#where the outputs will be placed
    time_format="%H:%M:%S"
    
    json_filename=process_file(testing_filename,csv_folder,test_folder,time_format,testing=True)
    json_file=open(json_filename)
    json_str = json_file.read()
    period_object = jsonpickle.decode(json_str)
    json_filename_base=os.path.basename(json_filename)[:-5] # we only need the bare name without extension
         
    os.environ['TFHUB_CACHE_DIR']='tf_cache'
    
    #conf_emb_type is a string with the embedding type plus information of whether it is only the embedding (_onlyemb) or embedding plus features (no suffix)
    necessary_embeddings=set()    
    needed_noembed=False
    for utte_type in embedding_per_utt_type:
        conf_emb_type=embedding_per_utt_type[utte_type]
        if conf_emb_type=="no_embedding":
            needed_noembed=True
            continue    
        if conf_emb_type.find("_onlyemb")>-1:embedding_type=conf_emb_type[:-8]
        else:embedding_type=conf_emb_type
        necessary_embeddings.add(embedding_type)
    
    #if there is nothing in needed_embeddings and we want the option without the embeddings, use the 20dimensional (this case would most likely never occur)
    if len(necessary_embeddings)==0 and needed_noembed: necessary_embeddings.add("20")
    
    #EXTRACT FEATURES AND CREATE A DATAFRAME FOR EACH NEEDED EMBEDDING TYPE
    dataset_per_embedding={}
    for embedding_type in necessary_embeddings:
        if embedding_type=="512t":embedding_dimensionality=512
        else: embedding_dimensionality=int(embedding_type)
        
        output_csv_filename=json_filename_base+"_"+embedding_type+".csv"
        outputfile_path=test_folder+"/"+output_csv_filename
        
        headers=["Original_CSV_File","Utterance_String","Speaker","Time_Stamp",
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
        for i in range(embedding_dimensionality):headers.append("Embedding_"+str(i))
            
        embedding_model=load_embeddings_model(embedding_type)
        print("\nEmbedding model loaded: "+embedding_type)
        #Sometimes the cached models throw errors, particularly if the download process fails, then the 
        #corresponding files should be located and deleted, and then run the script again to try to download again the model
        period_utterances_features=extract_features_period(period_object,embedding_model,embedding_dimensionality)
        dataset_per_embedding[embedding_type]=pd.DataFrame(period_utterances_features,columns=headers)
    print("\nFeatures extracted and Dataframes created for file: "+testing_filename)
    
    
    predictions={}
    for utt_type in embedding_per_utt_type:
        print ("Processing "+utt_type)
        conf_emb_type=embedding_per_utt_type[utt_type]
        print (conf_emb_type)
        
        if conf_emb_type=="no_embedding":
            embeding_type=necessary_embeddings.pop()
        elif conf_emb_type.find("_onlyemb")>-1:
            embedding_type=conf_emb_type[:-8]
        else: embedding_type=conf_emb_type
        
        dataframe=dataset_per_embedding[embedding_type]
        
        last_class_dim=dataframe.columns.get_loc("Utt_Student_ExpEvi")
        first_embedding_dim=dataframe.columns.get_loc("Embedding_0")
        
        #USE NOEMB, ONLY EMB OR EMB+FEAT
        if conf_emb_type=="no_embedding":       selected_x_dims=list(range(last_class_dim+1,first_embedding_dim))
        elif conf_emb_type.find("_onlyemb")>-1: selected_x_dims=list(range(first_embedding_dim,len(dataset.columns)))
        else:                                   selected_x_dims=list(range(last_class_dim+1,len(dataframe.columns)))
        
        x=dataframe.iloc[:,selected_x_dims].values
       
        classifier = all_classifiers[utt_type]
        threshold=all_thresholds[utt_type]
        
        predicted_y=classifier.predict_proba(x)
        predicted_y=predicted_y[:,1]
        predicted_y= [True if prob>threshold else False for prob in predicted_y]
        
        predictions[utt_type]=predicted_y
    
    #AFTER GETTING THE PREDICTIONS, PUT THEM INTO A DATAFRAME THAT ONLY CONTAINS THE FEATURES AND NO EMBEDDINGS
    dataframe=dataset_per_embedding[necessary_embeddings.pop()] #we get one dataframe (any type of embedding), then we strip off the embedding
    last_class_dim=dataframe.columns.get_loc("Utt_Student_ExpEvi")
    first_embedding_dim=dataframe.columns.get_loc("Embedding_0")
    
    dataframe_noemb=dataframe.iloc[:,:first_embedding_dim]
    for u_type in embedding_per_utt_type:
        var_index=dataframe_noemb.columns.get_loc(u_type)
        dataframe_noemb.iloc[:,var_index]=predictions[u_type]
        
    #AFTER GETTING THE DATAFRAME, PUT IT BACK INTO CSV FORMAT
    csv_participation_types=['Whole class discussion', 
         'Lecture', 
         'Small group + Instructor',  
         'Individual Work', 
         'Pair Work', 
         'Other']

    csv_header= ['Speaker', 
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
    
    df_utt_types=["Utt_Turn_Taking","Metacognitive_Modelling","Utt_Behavior","Utt_Teacher_OpenQ","Utt_Teacher_CloseQ","Utt_Student_OpenQ","Utt_Student_CloseQ","Utt_Student_CloseR","Utt_Student_OpenR","Utt_Student_ExpEvi"]
    df_part_types=["Part_Discussion","Part_Lecture","Part_Small_Group","Part_Individual","Part_Pairs","Part_Other"]
    
    output_csv_filename=testing_filename[:-4]+"_classifier.csv"

    with open(test_folder+"/"+output_csv_filename,"w+",encoding = 'utf-8')  as output_csvfile:
        writer=csv.writer(output_csvfile,delimiter=",")
        writer.writerow(csv_header)
        
        speaker_index=dataframe_noemb.columns.get_loc("Speaker")
        speakers=dataframe_noemb.iloc[:,speaker_index].values
        
        timestamp_index=dataframe_noemb.columns.get_loc("Time_Stamp")
        timestamps=dataframe_noemb.iloc[:,timestamp_index].values
        
        utterance_index=dataframe_noemb.columns.get_loc("Utterance_String")
        utterances=dataframe_noemb.iloc[:,utterance_index].values
        
        predictions=[]
        for utt_type in df_utt_types:
            u_type_index=dataframe_noemb.columns.get_loc(utt_type)
            values=dataframe_noemb.iloc[:,u_type_index].values
            values=["1" if x else " " for x in values]
            predictions.append(values)
        
        participation_types=[]
        for part_type in df_part_types:
            p_type_index=dataframe_noemb.columns.get_loc(part_type)
            values=dataframe_noemb.iloc[:,p_type_index].values
            values=["1" if x else " " for x in values]
            participation_types.append(values)
        
        for i, speaker in enumerate(speakers):
            row=[speaker,timestamps[i],utterances[i]]
            for u_type in predictions:
                row.append(u_type[i])
            for p_type in participation_types:
                row.append(p_type[i])
            
            writer.writerow(row)
        
                
    
    
    
    
        
        
    
    
        
        
        