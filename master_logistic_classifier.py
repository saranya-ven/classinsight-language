'''
Having trained a logistic classifier with the optimal configuration for each utterance type:
- load all the classifiers into a single object
- receive an unannotated CSV file
- perform and output the classification scores of the new CSV file
'''
import os
import pandas as pd
import numpy as np
import pickle

from read_input_file import process_file

if __name__ == "__main__":
    
    pickle_filepath="master_classifier.pkl"
    with open(pickle_filepath, 'rb') as file:
        (all_classifiers,all_thresholds,necessary_embeddings)= pickle.load(file)
    
    csv_folder="transcripts/official_transcripts/2_CSV_Files/"
    json_folder_test="transcripts/official_transcripts/3_JSON_Files_Test/"
    csv_test_folder="transcripts/official_transcripts/5_Test_Output_CSV_Files/"
    time_format="%H:%M:%S"
    
    testing_filenames=["20190508_Bonnie_per1.csv"]
    
    json_filename=process_file(testing_filename,csv_folder,json_folder_test,time_format,testing=True)
    json_filename_base=os.path.basename(json_filename)[:-5] # we only need the bare name without extension
    
    json_file=open(json_folder_test+"/"+filename)
    json_str = json_file.read()
    period_object = jsonpickle.decode(json_str)
        
    os.environ['TFHUB_CACHE_DIR']='tf_cache'
    
    for embedding_type in necessary_embeddings:#this does not consider using no embeddings
        
        if embedding_type=="512t":embedding_dimensionality=512
        else: embedding_dimensionality=int(embedding_type)
        
        output_csv_filename=json_filename_base+"_"+embedding_type+".csv"
        outputfile_path=csv_test_folder+output_csv_filename
        
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
            
                
        embedding_model=load_embeddings_model(embedding_type)
        print("Embedding model loaded: "+embedding_type)
        #Sometimes the cached models throw errors, particularly if the download process fails, then the 
        #corresponding files should be located and deleted, and then run the script again to try to download again the model
        
        with open(outputfile_path,"w+",encoding="utf-8") as output_csv_file:
            file_writer = csv.writer(output_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(headers)
            
            for period in all_periods:
               period_utterances_features=extract_features_period(period,embedding_model)
               for utt_features in period_utterances_features:
                   try:dataset_writer.writerow(utt_features)
                   except UnicodeEncodeError as e:
                       print (e)
                       utt_features[1]=utt_features[1].encode('utf-8')
                       print (utt_features[1])
                       dataset_writer.writerow(utt_features)
               
               print ("Features extracted and added to file")
    
            print ("\n All files processed and dataset file created: "+outputfile_path)