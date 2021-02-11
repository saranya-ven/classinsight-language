'''
Having trained a logistic classifier with the optimal configuration for each utterance type:
- load all the classifiers into a single object
- receive an unannotated CSV file
- perform and output the classification scores of the new CSV file
'''
import os,pickle, jsonpickle
import pandas as pd

from read_input_file import process_file, get_filenames_in_dir
from sentence_embeddings import load_embeddings_model
from get_dataset import extract_features_period,save_dataframe_as_CSV


if __name__ == "__main__":
    
    import config as cfg
    csv_folder=cfg.csv_folder+"/2020"#where the input files are
    test_folder=cfg.test_folder#where the outputs will be placed
    
    time_format="%H:%M:%S"
    testing_filenames=get_filenames_in_dir(csv_folder,".csv")
    #testing_filenames=["20200225_Sara_Pd7_8_Mixed_Andi_Tarang.csv"]
    
    pickle_filepath="master_logistic_classifier.pkl"
    with open(pickle_filepath, 'rb') as file:
        (all_classifiers,all_thresholds,embedding_per_utt_type)= pickle.load(file)
    
    #IDENTIFY THE EMBEDDING TYPES THAT ARE NECESSARY ACCORDING TO THE OPTIMAL CLASSIFIER CONFIGURATIONS
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
    
    #LOADING THE EMBEDDING MODELS IS COSTLY AND PRONE TO ERRORS, SO WE CAN LOAD THEM JUST ONCE FOR ALL THE INPUT FILES
    #Sometimes the cached models throw errors, particularly if a model is downloaded again (not sure why) and the download process fails, then the 
    #corresponding files in the cache should be located and deleted, and then run the script again to try to download again the model
    os.environ['TFHUB_CACHE_DIR']=cfg.tf_cache_folder
    embedding_models={}
    for embedding_type in necessary_embeddings:
        print ("\nLoading embedding model:"+embedding_type)
        embedding_models[embedding_type]=load_embeddings_model(embedding_type)
        print("Embedding model loaded: "+embedding_type)
       
    #PROCESS EACH INPUT FILE
    for testing_filename in testing_filenames:
        print()
        #GET JSON FILE
        json_filename=process_file(testing_filename,csv_folder,test_folder,time_format,testing=True)
        json_file=open(json_filename)
        json_str = json_file.read()
        period_object = jsonpickle.decode(json_str)
        json_filename_base=os.path.basename(json_filename)[:-5] # we only need the bare name without extension
            
        #EXTRACT FEATURES AND CREATE A DATAFRAME FOR EACH NEEDED EMBEDDING TYPE
        dataset_per_embedding={}
        for embedding_type in necessary_embeddings:
            if embedding_type=="512t":embedding_dimensionality=512
            else: embedding_dimensionality=int(embedding_type)
            
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
                
            period_utterances_features=extract_features_period(period_object,embedding_models[embedding_type],embedding_dimensionality)
            dataset_per_embedding[embedding_type]=pd.DataFrame(period_utterances_features,columns=headers)
        print("\nFeatures extracted and Dataframes created for file: "+testing_filename)
        
        
        #GET MODEL'S PREDICTIONS
        predictions={}
        for utt_type in embedding_per_utt_type:
            print ("Processing "+utt_type)
            conf_emb_type=embedding_per_utt_type[utt_type]
            print (conf_emb_type)
            
            if conf_emb_type=="no_embedding":      
                for embed in necessary_embeddings:break #this is apparently the fastest way to retrieve one element in a set without removing it
                embedding_type=embed
            elif conf_emb_type.find("_onlyemb")>-1:embedding_type=conf_emb_type[:-8]
            else:                                  embedding_type=conf_emb_type
            
            dataframe=dataset_per_embedding[embedding_type]  
            last_class_dim=dataframe.columns.get_loc("Utt_Student_ExpEvi")
            first_embedding_dim=dataframe.columns.get_loc("Embedding_0")
            
            #USE NOEMB, ONLY EMB OR EMB+FEAT
            if conf_emb_type=="no_embedding":       selected_x_dims=list(range(last_class_dim+1,first_embedding_dim))
            elif conf_emb_type.find("_onlyemb")>-1: selected_x_dims=list(range(first_embedding_dim,len(dataframe.columns)))
            else:                                   selected_x_dims=list(range(last_class_dim+1,len(dataframe.columns)))
            
            x=dataframe.iloc[:,selected_x_dims].values
           
            classifier = all_classifiers[utt_type]
            threshold=all_thresholds[utt_type]
            
            predicted_y=classifier.predict_proba(x)
            predicted_y=predicted_y[:,1]
            
            predictions[utt_type]= [True if prob>threshold else False for prob in predicted_y]
            
        
        #AFTER GETTING THE PREDICTIONS, PUT THEM INTO A DATAFRAME
        for embed in necessary_embeddings:break #this is apparently the fastest way to retrieve one element in a set without removing it
        dataframe=dataset_per_embedding[embed] #we get one dataframe (any type of embedding)
        
        for u_type in embedding_per_utt_type:
            var_index=dataframe.columns.get_loc(u_type)
            dataframe.iloc[:,var_index]=predictions[u_type]
        
        #THEN CONVERT THE DATAFRAME BACK TO CSV
        output_csv_filename=testing_filename[:-4]+"_classifier.csv"
        save_dataframe_as_CSV(dataframe,test_folder+"/"+output_csv_filename)
                
    
    
    
    
        
        
    
    
        
        
        