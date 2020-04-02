'''
Having trained a model and saved it as pickle file, we load them and analyze its output
'''

from logistic_regression.utterance_classifier_gridsearch import train_test_validation_split,report_best_performance
from evaluation import report_precision_recall_fscore

import pandas as pd
import pickle

def show_false_negatives(x,y,classifier): 
    l=0  
    print("FALSE NEGATIVES")
    for x_elem,y_gold in zip(x,y):
        prediction=classifier.predict([x_elem[2:]])
        
        if prediction!=y_gold and y_gold==True:
            print (x_elem[1],
                   "\n\t"+x_elem[0],
                   "\n\tTeacher:     ",x_elem[2],
                   "\n\tStudentNamed:",x_elem[40],
                   "\n\tStudentNext: ",x_elem[8],
                   "\n\tExpected:    ",y_gold,
                   "\n\tPredicted:   ",prediction[0])
            l+=1
    print(l)

def show_false_positives(x,y,classifier): 
    l=0  
    print("FALSE POSITIVES")
    for x_elem,y_gold in zip(x,y):
        prediction=classifier.predict([x_elem[2:]])
        
        if prediction!=y_gold and y_gold==False:
            print (x_elem[1],
                   "\n\t"+x_elem[0],
                   "\n\tTeacher:     ",x_elem[2],
                   "\n\tStudentNamed:",x_elem[40],
                   "\n\tStudentNext: ",x_elem[8],
                   "\n\tExpected:    ",y_gold,
                   "\n\tPredicted:   ",prediction[0])
            l+=1
    print(l)

def show_true_positives(x,y,classifier): 
    l=0  
    print("TRUE POSITIVES")
    for x_elem,y_gold in zip(x,y):
        prediction=classifier.predict([x_elem[2:]])
        
        if prediction==y_gold and y_gold==True:
            print (x_elem[1],
                   "\n\t"+x_elem[0],
                   "\n\tTeacher:     ",x_elem[2],
                   "\n\tStudentNamed:",x_elem[40],
                   "\n\tStudentNext: ",x_elem[8],
                   "\n\tExpected:    ",y_gold,
                   "\n\tPredicted:   ",prediction[0])
            l+=1
    print(l)


def show_true_negatives(x,y,classifier): 
    l=0 
    print("TRUE NEGATIVES") 
    for x_elem,y_gold in zip(x,y):
        prediction=classifier.predict([x_elem[2:]])
        
        if prediction==y_gold and y_gold==False:
            print (x_elem[1],
                   "\n\t"+x_elem[0],
                   "\n\tTeacher:     ",x_elem[2],
                   "\n\tStudentNamed:",x_elem[40],
                   "\n\tStudentNext: ",x_elem[8],
                   "\n\tExpected:    ",y_gold,
                   "\n\tPredicted:   ",prediction[0])
            l+=1
    print(l)


if __name__ == "__main__":
    
    pickle_filepath="../saved_models/best_Utt_Student_OpenQ.pkl"
    with open(pickle_filepath, 'rb') as file:
        (classifier,model_config)= pickle.load(file)
        
    seed_all=model_config["random_seed"]
    label_feats=model_config["embed_type"]
    variable_name=model_config["interest_variable"]
    
    if label_feats.find("_onlyemb")>-1:embedding_type=label_feats[:-8]
    else:embedding_type=label_feats

    print("\nInterest Variable: "+variable_name)
    print("Embedding Type:"+embedding_type+"\n")
    
    if embedding_type=="no_embedding":dataset_path="../Data/4_Datasets/dataset_all_20dim.csv"
    else:dataset_path="../Data/4_Datasets/dataset_all_"+embedding_type+"dim.csv"
    
    dataset = pd.read_csv(dataset_path) 
    
    headers=["Original_CSV_File","Utterance_String",
    
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
    
    last_class_dim=dataset.columns.get_loc("Utt_Student_ExpEvi")
    first_embedding_dim=dataset.columns.get_loc("Embedding_0")
    
    embedding_dimensionality=len(dataset.columns)-first_embedding_dim
    for i in range(embedding_dimensionality):headers.append("Emb_"+str(i))
    
    #shuffle the data, there are some differences in performance... maybe due to differences in split in test/train
    dataset = dataset.sample(frac=1,random_state=seed_all).reset_index(drop=True)
    
    #HERE WE WANT TO KEEP TRACK OF THE ORIGINAL UTTERANCES AND THEIR SOURCE FILES, THAT-S WHY WE KEEP THE FIRST 2 DIMENSIONS
    x_dims=[0,1]
    #USE NOEMB, ONLY EMB OR EMB+FEAT
    if label_feats=="no_embedding":       selected_x_dims=list(range(last_class_dim+1,first_embedding_dim))
    elif label_feats.find("_onlyemb")>-1: selected_x_dims=list(range(first_embedding_dim,len(headers)))
    else:                                 selected_x_dims=list(range(last_class_dim+1,len(headers)))
    x_dims.extend(selected_x_dims)
    
    x=dataset.iloc[:,x_dims].values
    var_index=dataset.columns.get_loc(variable_name)
    y = dataset.iloc[:, var_index].values   
    #Divide Train/Test/Validation
    xtrain,xval,xtest,ytrain,yval,ytest=train_test_validation_split(x, y, testval_size=0.20, rm_state=seed_all)

    #===============================================================
    #TO SEE THE WEIGHTS
    # thetaLasso=classifier.coef_
    # print("The regularized theta using lasso regression:\n")
    # i_s=range(12,len(headers[12:])+12)
    # 
    # for i,coef,hea in zip(i_s,thetaLasso[0],headers[12:]):
    #     print(i,f"{coef:.2f}",hea)
    #===============================================================
    
    #get predictions in validation set
    y_pred_proba_val = classifier.predict_proba(xval[:,2:])
    y_pred_val = classifier.predict(xval[:,2:])
    #get predictions in testing set
    y_pred_proba_test=classifier.predict_proba(xtest[:,2:])
    y_pred_test=classifier.predict(xtest[:,2:])
    #We are only interested in the probability of the given class, not in the alternative (!given_class)
    # keep probabilities for the positive outcome only
    y_pred_proba_val = y_pred_proba_val[:, 1]
    y_pred_proba_test = y_pred_proba_test[:, 1]
     
    best_th_val,precrec_aucscore_val=report_precision_recall_fscore(yval, y_pred_proba_val,variable_name,label_feats,use_plots=False)#,directory_path="plots/prec_recall_fscore_"+label_feats)#get best th on validation
    y_test_bestpred = [True if prob>best_th_val else False for prob in y_pred_proba_test]  
    
    report_best_performance(variable_name,y,ytest,y_test_bestpred,best_th_val)
    print("Prec/Rec AUC: %.3f" % precrec_aucscore_val)
    print()
    

    show_false_negatives(xtest, ytest, classifier)
    #show_false_positives(xtest, ytest, classifier)
    #show_true_negatives(xtest, ytest, classifier)
    #show_true_positives(xtest, ytest, classifier)
    
      

       
        