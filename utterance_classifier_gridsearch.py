'''
Main process to classify utterances in the transcripts, assuming several datasets have been prepared

'''
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from collections import Counter
import pickle
import sklearn

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import accuracy_score,f1_score,recall_score,precision_score,confusion_matrix,roc_curve,roc_auc_score, precision_recall_curve,auc
from sklearn.model_selection import cross_val_score, RepeatedStratifiedKFold

from metric_data_plot import plot_metric_by_data_size, plot_metric_by_data_size_vs_embedding_type
from evaluation import report_roc_auc,plot_precision_recall_auc,report_precision_recall_fscore

from warnings import filterwarnings
filterwarnings('ignore')


def train_test_validation_split(xs,ys,testval_size,rm_state=0):
    xtrain, xtest, ytrain, ytest = train_test_split(xs, ys, test_size=testval_size, random_state=rm_state)
    #Divide test into validation and test
    xval=xtest[0:int(len(xtest)/2)]
    xtest=xtest[int(len(xtest)/2):]
    yval=ytest[0:int(len(ytest)/2)]
    ytest=ytest[int(len(ytest)/2):]
    
    return xtrain,xval,xtest,ytrain,yval,ytest

def report_best_performance(var_name,y_all,y_test,y_predicted,threshold): 
    print("\n",var_name)
    counter=Counter(y_all)
    print (counter)
    counter_test=Counter(y_test)
    print (counter_test)      
    print (f'\nBest Th:{threshold:.2f} F1-Score:{f1_score(y_test, y_predicted):.3f}')
    print("Confusion Matrix : \n", confusion_matrix(y_test,y_predicted))        
    print(f"Precision: {precision_score(y_test, y_predicted):.2f}")
    print(f"Recall   : {recall_score(y_test, y_predicted):.2f}")
    print(f"Accuracy : {accuracy_score(y_test, y_predicted):.2f}")
    
def save_model_and_configuration(model,config,file_path):    
    output_file=open(file_path,'wb')
    pickle.dump((model,config),output_file)
    output_file.close()
    
def get_f1_auc_plots_through_datasizes(x,y,classifier,category_label,embedding_type,test_val_size=0.10,rn_state=1,directory_path="plots/performance_vs_datasize"):
    
    xtrain,xval,xtest,ytrain,yval,ytest=train_test_validation_split(x, y, testval_size=test_val_size, rm_state=rn_state)
    
    all_f1_scores_percs=[]
    all_auc_scores_percs=[]
    initial_point=2
    if category_label=="Utt_Student_ExpEvi":initial_point=20
    
    for i in range(initial_point,100,2):
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
        best_th_val,precrec_aucscore_val=report_precision_recall_fscore(yval, y_pred_proba_val,category_label,embedding_type,use_plots=False)
        
        y_test_bestpred = [True if prob>best_th_val else False for prob in y_pred_proba_test]
        best_f1_score_test=f1_score(ytest,y_test_bestpred)
    
        all_f1_scores_percs.append(best_f1_score_test)
        all_auc_scores_percs.append(precrec_aucscore_val)
        
    plot_metric_by_data_size_vs_embedding_type("F1-Score",category_label,all_f1_scores_percs, range(initial_point,100,2),embedding_type,directory_path)
    plot_metric_by_data_size_vs_embedding_type("AUC",category_label,all_auc_scores_percs, range(initial_point,100,2),embedding_type,directory_path)
  
        
if __name__ == "__main__":
    
    seed_all=42
    embedding_types=["no_embedding","20","50","128","250","512","512t"]
   
    #WHETHER WE WANT TO TEST WITH ONLY EMBEDDINGS: IN GENERAL, ONLY EMBEDDINGS IS A VERY POOR CONFIGURATION, IT-S GOOD TO KNOW BUT IN PRACTICE NOT USEFUL
    test_only_embedding=False
    
    all_embeddings_f1scores=[]
    all_embeddings_aucscores=[]
    best_models_configs={}
    
    for embedding_type in embedding_types:
        
        if embedding_type=="no_embedding":dataset_path="transcripts/official_transcripts/4_Datasets/dataset_all_20dim.csv"
        else:dataset_path="transcripts/official_transcripts/4_Datasets/dataset_all_"+embedding_type+"dim.csv"
        
        dataset = pd.read_csv(dataset_path) 
        
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
        
        last_class_dim=dataset.columns.get_loc("Utt_Student_ExpEvi")
        first_embedding_dim=dataset.columns.get_loc("Embedding_0")
        
        embedding_dimensionality=len(dataset.columns)-first_embedding_dim
        for i in range(embedding_dimensionality):headers.append("Emb_"+str(i))
        
        print("\nUsing embeddings:"+embedding_type+"\n")
        
        #shuffle the data, there are some differences in performance... maybe due to differences in split in test/train
        dataset = dataset.sample(frac=1,random_state=seed_all).reset_index(drop=True)
        #FOR A GIVEN TYPE OF EMBEDDING, TEST USING NOEMB, EMB+FEAT AND/OR ONLYEMB
        x_datasets=[]
        if embedding_type=="no_embedding":
            x= dataset.iloc[:,last_class_dim+1:first_embedding_dim].values
            x_datasets.append((x,embedding_type))
        else:
            x_feat_emb=dataset.iloc[:,last_class_dim+1:].values
            x_datasets.append((x_feat_emb,embedding_type))
            if test_only_embedding:
                x_emb=dataset.iloc[:,first_embedding_dim:].values
                x_datasets.append((x_emb,embedding_type+"_onlyemb"))
        
        
        interest_variables=range(2,12)#indices of the columns related to the classes we want to predict
        for (x_dataset,label_feats) in x_datasets:
            embedding_f1_scores=[]
            embedding_auc_scores=[]
            for var_index in interest_variables:
        
                variable_name=dataset.columns[var_index]
                y = dataset.iloc[:, var_index].values   
        
                #if we want to plot performance vs datasize, the following line replaces the rest
                #get_f1_auc_plots_through_datasizes(x_dataset, y, classifier,variable_name,embedding_type, test_val_size=0.20, rn_state=seed_all)            
                
                #10-fold CrossValidation. We use this loop to obtain reliable performance scores (f1 and auc)
                rskf = RepeatedStratifiedKFold(n_splits=10, n_repeats=1,random_state=seed_all)  
                cv_f1scores=[]
                cv_aucscpres=[]
                cv_ths=[]
                for train_index, test_index in rskf.split(x_dataset, y):
                    val_index= test_index[0:int(len(test_index)/2)]
                    test_index=test_index[int(len(test_index)/2):]
                     
                    X_train,X_val,X_test = x_dataset[train_index], x_dataset[val_index],x_dataset[test_index]
                    y_train,y_val,y_test = y[train_index], y[val_index], y[test_index]
                    
                    #HERE WE CAN CHANGE THE TYPE OF CLASSIFIER
                    
                    #We are essentially doing 2 CVs, one to get the parameter for the regularizer, implemented by the LRCV function below, and the second one, to evaluate the classifier
                    #classifier = LogisticRegressionCV(cv=10,solver="lbfgs", random_state=seed_all,max_iter=300) # We use this line if we want to tune the weight of the regularizer, we get very similar results, but more slowly
                    
                    #use class_weight='balanced' to balance the classes
                    #use solver="saga" to use l1 regularization 
                    classifier = LogisticRegression(solver="lbfgs", random_state=seed_all,max_iter=300) 
                    classifier.fit(X_train,y_train)
                
                    #get probabilities in validation and testing sets
                    y_pred_proba_val = classifier.predict_proba(X_val)
                    y_pred_proba_test=classifier.predict_proba(X_test)
                    #We are only interested in the probability of the given class, not in the alternative (!given_class)
                    y_pred_proba_val = y_pred_proba_val[:, 1]
                    y_pred_proba_test= y_pred_proba_test[:,1]
                       
                    # Note : Not using ROC curve as it is applicable to balanced datasets (one v/s many classifiers are typically unbalanced)
                    
                    #Using 10fold CV, we would end up with 10 plots (1 per fold), so, probably we can avoid the plots altogether unless necessary
                    #plot_precision_recall_auc(y_val,y_pred_proba_val,variable_name,label_feats,directory_path="plots/AUC_vs_embedding") 
                    
                    #get threshold, and auc on validation
                    best_th_val,precrec_aucscore_val=report_precision_recall_fscore(y_val, y_pred_proba_val,variable_name,label_feats,directory_path="plots/prec_recall_fscore_"+label_feats,use_plots=False)#get best th on validation
                    
                    #use threshold on validation to classify on test
                    y_test_bestpred = [True if prob>best_th_val else False for prob in y_pred_proba_test]
                    best_f1_score_test=f1_score(y_test,y_test_bestpred)
                    
                    cv_f1scores.append(best_f1_score_test)
                    cv_aucscpres.append(precrec_aucscore_val)
                    cv_ths.append(best_th_val)
                    
                cv_precrec_auc=np.mean(cv_aucscpres)
                cv_f1score=np.mean(cv_f1scores)
                cv_th=np.mean(cv_ths)
                print("Prec/Rec AUC: %.3f" % cv_precrec_auc+"\tFScore: %.3f" %cv_f1score+"\t"+"\tTau: %.3f" %cv_th+"\t"+variable_name)
                
                model_config={"interest_variable":variable_name,"embed_type":label_feats,
                              "threshold":best_th_val,"random_seed":seed_all}
                if variable_name not in best_models_configs or best_models_configs[variable_name][2]<cv_f1score:
                    best_models_configs[variable_name]=(classifier,model_config,cv_f1score)
                    save_model_and_configuration(classifier, model_config, "saved_models/best_"+variable_name+".pkl")

                embedding_f1_scores.append(cv_f1score)
                embedding_auc_scores.append(cv_precrec_auc)
              
            print(f"\nAverage F1-Score Across Types:{sum(embedding_f1_scores)/len(embedding_f1_scores):.3f}")
            print(f"Average Prec/Rec AUC-Score Across Types:{sum(embedding_auc_scores)/len(embedding_auc_scores):.3f}")
            all_embeddings_f1scores.append(embedding_f1_scores)
            all_embeddings_aucscores.append(embedding_auc_scores)
    
    #these scores can be plotted using metric_data_plot.py
    print(all_embeddings_f1scores)
    print(all_embeddings_aucscores)
    plt.close("all")