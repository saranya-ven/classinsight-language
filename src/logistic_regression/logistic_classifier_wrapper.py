'''
Having done a grid search to find the optimal configuration for each utterance type:
  1. load the best performing configuration
  2. train a classifier for each utterance type with the best configuration and with the whole dataset (no training/test split)
  3. wrap up all the classifiers into one object and dump them into a pickle file

'''

from sklearn.linear_model import LogisticRegression
import pandas as pd
import pickle
import config as cfg

if __name__ == "__main__":

    utt_types=[ "Utt_Turn_Taking",#2
                "Metacognitive_Modelling",#3
                "Utt_Behavior",#4
                "Utt_Teacher_OpenQ",#5
                "Utt_Teacher_CloseQ",#6
                "Utt_Student_OpenQ",#7
                "Utt_Student_CloseQ",#8
                "Utt_Student_CloseR",#9
                "Utt_Student_OpenR",#10
                "Utt_Student_ExpEvi"
                ]
    
    #Just for reference:
    headers=["Original_CSV_File","Utterance_String","Speaker","Time_Stamp",
    
            "Utt_Turn_Taking",#2
            "Metacognitive_Modelling",#3
            "Utt_Behavior",#4
            "Utt_Teacher_OpenQ",#5
            "Utt_Teacher_CloseQ",#6
            "Utt_Student_OpenQ",#7
            "Utt_Student_CloseQ",#8
            "Utt_Student_CloseR",#9
            "Utt_Student_OpenR",#10
            "Utt_Student_ExpEvi",#11
            
            "Speaker_teacher","Speaker_student","Speaker_other","Previous_speaker_teacher","Previous_speaker_student","Previous_speaker_other","Previous_speaker_none",
            "Next_speaker_teacher","Next_speaker_student","Next_speaker_other","Next_speaker_none",
            "first_utterance_in_turn","last_utterance_in_turn",
            "Part_Discussion","Part_Lecture","Part_Small_Group","Part_Individual","Part_Pairs","Part_Other",
            "Single_Word",
            "what","What","why","Why","how","How","Is","do","Do","does","Does","can","Can","could","Could","where","Where","when","When",
            "QuestionMark","Student","Quotation","explain","Explain","right","no","No","yes","Yes","yeah","Yeah","because","Because",
            "Go_ahead","go_ahead","right_questionmark", "Right_period","How_many","How_much"
            ]
    
    all_classifiers={}
    all_thresholds={}
    embedding_per_utt_type={}
    
    output_filename="master_logistic_classifier.pkl"
    
    saved_models_path=cfg.saved_models
    datasets_path=cfg.datasets_folder
    
    for utt_type in utt_types:
        pickle_filepath=saved_models_path+"best_"+utt_type+ ".pkl"
        with open(pickle_filepath, 'rb') as file:
            (classifier,model_config)= pickle.load(file) #so far we are not using the classifier, as we retrain a classifier with the whole dataset
            
        seed_all=model_config["random_seed"]
        label_feats=model_config["embed_type"]
        embedding_per_utt_type[utt_type]=label_feats
        variable_name=model_config["interest_variable"]
        thresh=model_config["threshold"]
        
        
        if label_feats.find("_onlyemb")>-1:embedding_type=label_feats[:-8]
        else:embedding_type=label_feats
        
        print("Training: "+variable_name)
        print("Embedding Type:"+embedding_type+"\n")
        
        
        if embedding_type=="no_embedding":dataset_path=datasets_path+"dataset_all_20dim.csv"
        else:dataset_path=datasets_path+"dataset_all_"+embedding_type+"dim.csv"
        
        dataset = pd.read_csv(dataset_path) 
       
        last_class_dim=dataset.columns.get_loc("Utt_Student_ExpEvi")
        first_embedding_dim=dataset.columns.get_loc("Embedding_0")
        
        #shuffle the data, there are some differences in performance... maybe due to differences in split in test/train
        dataset = dataset.sample(frac=1,random_state=seed_all).reset_index(drop=True)
        
        #USE NOEMB, ONLY EMB OR EMB+FEAT
        if label_feats=="no_embedding":       selected_x_dims=list(range(last_class_dim+1,first_embedding_dim))
        elif label_feats.find("_onlyemb")>-1: selected_x_dims=list(range(first_embedding_dim,len(dataset.columns)))
        else:                                 selected_x_dims=list(range(last_class_dim+1,len(dataset.columns)))
        
        x=dataset.iloc[:,selected_x_dims].values
        var_index=dataset.columns.get_loc(variable_name)
        y = dataset.iloc[:, var_index].values   
       
        classifier = LogisticRegression(solver="lbfgs", random_state=seed_all,max_iter=300)
        #We train on the whole dataset
        classifier.fit(x,y) 
        
        all_classifiers[variable_name]=classifier
        all_thresholds[variable_name]=thresh
        
    output_file=open(output_filename,'wb')
    pickle.dump((all_classifiers,all_thresholds,embedding_per_utt_type),output_file)
    output_file.close()
    print("File created: "+output_filename)
        
        
        