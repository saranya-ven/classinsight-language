'''
Main process to classify utterances in the transcripts, assuming a number of datasets have been prepared

'''
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression 
from sklearn.metrics import accuracy_score,f1_score,recall_score,precision_score,confusion_matrix,roc_curve,roc_auc_score, precision_recall_curve,auc
from sklearn.model_selection import cross_val_score, RepeatedStratifiedKFold

from metric_data_plot import plot_metric_by_data_size, plot_metric_by_data_size_vs_embedding_type
from evaluation import report_roc_auc,report_precision_recall_auc,report_precision_recall_fscore


def train_test_validation_split(xs,ys,testval_size,rm_state=0):
    xtrain, xtest, ytrain, ytest = train_test_split(xs, ys, test_size=testval_size, random_state=rm_state)
    #Divide test into validation and test
    xval=xtest[0:int(len(xtest)/2)]
    xtest=xtest[int(len(xtest)/2):]
    yval=ytest[0:int(len(ytest)/2)]
    ytest=ytest[int(len(ytest)/2):]
    
    return xtrain,xval,xtest,ytrain,yval,ytest

def report_best_performance(var_name,y_all,y_test,y_predicted): 
    print("\n",var_name)
    counter=Counter(y_all)
    print (counter)
    counter_test=Counter(y_test)
    print (counter_test)      
    print (f'\nBest Th:{best_th_val:.2f} F1-Score:{f1_score(y_test, y_predicted):.3f}')
    print("Confusion Matrix : \n", confusion_matrix(y_test,y_predicted))        
    print(f"Precision: {precision_score(y_test, y_predicted):.2f}")
    print(f"Recall   : {recall_score(y_test, y_predicted):.2f}")
    print(f"Accuracy : {accuracy_score(y_test, y_predicted):.2f}")
    
    
def get_f1_auc_plots_through_datasizes(x,y,classifier,embedding_type,test_val_size=0.10,rn_state=1,directory_path="plots/performance_vs_datasize"):
    
    xtrain,xval,xtest,ytrain,yval,ytest=train_test_validation_split(x, y, testval_size=test_val_size, rm_state=rn_state)
    
    all_f1_scores_percs=[]
    all_auc_scores_percs=[]
    
    for i in range(2,100,2):
        if i%10==0:print (i,"percent...")
        xtrain_percent=xtrain[:int(i*len(xtrain)/100.0)]
        ytrain_percent=ytrain[:int(i*len(ytrain)/100.0)]
        #Train 
        classifier.fit(xtrain_percent, ytrain_percent) 
        
        #get predictions in validation set
        y_pred_proba_val = classifier.predict_proba(xval)
        y_pred_val = classifier.predict(xval)
        #get predictions in testing set
        y_pred_proba_test=classifier.predict_proba(xtest)
        y_pred_test=classifier.predict(xtest)
        #We are only interested in the probability of the given class, not in the alternative (!given_class)
        # keep probabilities for the positive outcome only
        y_pred_proba_val = y_pred_proba_val[:, 1]
        y_pred_proba_test = y_pred_proba_test[:, 1]
        
        #these values are only on validation
        best_th_val,precrec_aucscore_val=report_precision_recall_fscore(yval, y_pred_proba_val,use_plots=False)
        
        y_test_bestpred = [True if prob>best_th_val else False for prob in y_pred_proba_test]
        best_f1_score_test=f1_score(ytest,y_test_bestpred)
    
        all_f1_scores_percs.append(best_f1_score_test)
        all_auc_scores_percs.append(precrec_aucscore_val)
        
    plot_metric_by_data_size_vs_embedding_type("F1-Score",variable_name, all_f1_scores_percs, range(2,100,2),embedding_type,directory_path)
    plot_metric_by_data_size_vs_embedding_type("AUC",variable_name, all_auc_scores_percs, range(2,100,2),embedding_type,directory_path)
  
        
if __name__ == "__main__":
    
    embedding_types=["20","50","128","250","512","512t"]
    
    all_embeddings_f1scores=[]
    all_embeddings_aucscores=[]
    
    for embedding_type in embedding_types:
        #embedding_type="512"
        
        dataset_path="transcripts/official_transcripts/4_Datasets/dataset_all_"+embedding_type+"dim.csv"
        dataset = pd.read_csv(dataset_path) 
        
        last_class_dim=dataset.columns.get_loc("Utt_Student_ExpEvi")
        first_embedding_dim=dataset.columns.get_loc("Embedding_0")
        #embedding_dimensionality=len(dataset.columns)-first_embedding_dim
        
        #just for reference, not really used
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
        
        print("\nUsing embeddings:"+embedding_type+"\n")
    
        use_embeddings=True
        if use_embeddings:x= dataset.iloc[:,last_class_dim+1:].values
        else:             x= dataset.iloc[:,last_class_dim+1:first_embedding_dim].values
        
        interest_variables=range(2,12)# the indices of the columns related to the classes we want to predict
     
        embedding_f1_scores=[]
        embedding_auc_scores=[]
        for var_index in interest_variables:
            #HERE WE CAN CHANGE THE TYPE OF CLASSIFIER
            classifier = LogisticRegression(solver="lbfgs",random_state = 0)
            
            #Divide Train/Test/Validation
            variable_name=dataset.columns[var_index]
            y = dataset.iloc[:, var_index].values   
            #if we want to plot performance vs datasize, the following 2 lines replace the rest
            #print("processing ",variable_name)
            #get_f1_auc_plots_through_datasizes(x, y, classifier,embedding_type, test_val_size=0.20, rn_state=1)
            
            xtrain,xval,xtest,ytrain,yval,ytest=train_test_validation_split(x, y, testval_size=0.20, rm_state=1)
         
            #Train 
            classifier.fit(xtrain, ytrain) 
              
            #get predictions in validation set
            y_pred_proba_val = classifier.predict_proba(xval)
            y_pred_val = classifier.predict(xval)
            #get predictions in testing set
            y_pred_proba_test=classifier.predict_proba(xtest)
            y_pred_test=classifier.predict(xtest)
            #We are only interested in the probability of the given class, not in the alternative (!given_class)
            # keep probabilities for the positive outcome only
            y_pred_proba_val = y_pred_proba_val[:, 1]
            y_pred_proba_test = y_pred_proba_test[:, 1]
              
              
            # Note : Not using ROC curve as it is applicable to balanced datasets (one v/s many classifiers are typically unbalanced)
            auc_score=report_precision_recall_auc(yval, y_pred_proba_val,variable_name,embedding_type,directory_path="plots/AUC_vs_embedding")
            
            best_th_val,precrec_aucscore_val=report_precision_recall_fscore(yval, y_pred_proba_val,variable_name,embedding_type,directory_path="plots/prec_recall_fscore_"+embedding_type+"dim")#get best th on validation
            y_test_bestpred = [True if prob>best_th_val else False for prob in y_pred_proba_test]
            best_f1_score_test=f1_score(ytest,y_test_bestpred)
      
            #report_best_performance(variable_name,y,ytest,y_test_bestpred)
            print("Prec/Rec AUC: %.3f" % precrec_aucscore_val)
          
            embedding_f1_scores.append(best_f1_score_test)
            embedding_auc_scores.append(precrec_aucscore_val)
         
        print(f"\nAverage F1-Score Across Types:{sum(embedding_f1_scores)/len(embedding_f1_scores):.3f}")
        print(f"Average Prec/Rec AUC-Score Across Types:{sum(embedding_auc_scores)/len(embedding_auc_scores):.3f}")
        all_embeddings_f1scores.append(embedding_f1_scores)
        all_embeddings_aucscores.append(embedding_auc_scores)
    print(all_embeddings_f1scores)
    print(all_embeddings_aucscores)
            
        #===========================================================================
        # utts=dataset.iloc[:,1].values
        # teacher_sp=dataset.iloc[:,12].values
        # student_naming=dataset.iloc[:,52]
        # filenames=dataset.iloc[:,0].values
        #  
        # for utt,teach,stud_nam,x_elem,y_elem,file_n in zip(utts,teacher_sp,student_naming,x,y,filenames):
        #     prediction=classifier.predict([x_elem])
        #     if prediction!=y_elem :
        #         print (utt,file_n,teach,stud_nam,y_elem,prediction)
        #     if prediction==y_elem and prediction==True :
        #         print ("\t",utt,file_n,teach,stud_nam,y_elem,prediction)
        #===============================================================================
        