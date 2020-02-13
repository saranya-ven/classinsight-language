import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression 
from sklearn.metrics import accuracy_score,f1_score,recall_score,precision_score,confusion_matrix,roc_curve,roc_auc_score

from metric_data_plot import plot_metric_by_data_size 

from collections import Counter
from numpy import mean
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
        

if __name__ == "__main__":
    
    dataset_path="transcripts/official_transcripts/4_Datasets/dataset_all_50dim.csv"
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
    
    embedding_dimensionality=512
    for i in range(embedding_dimensionality):
        headers.append("Embedding_"+str(i))
    # for i,elem in enumerate(headers):
    #     print(i, elem)
    
    
    #x = dataset.iloc[:, 12:71].values
    x= dataset.iloc[:,12:71+embedding_dimensionality].values
    
    for var_index in range(2,12):
        print()
        print("Utt Type: ",headers[var_index])
        y = dataset.iloc[:, var_index].values 
        
        counter=Counter(y)
        print (counter)

        xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size = 0.10, random_state = 1)

        xval=xtest[0:int(len(xtest)/2)]
        xtest=xtest[int(len(xtest)/2):]
        
        yval=ytest[0:int(len(ytest)/2)]
        ytest=ytest[int(len(ytest)/2):]
        
        counter_test=Counter(ytest)
        print (counter_test)
        
        classifier = LogisticRegression(solver="lbfgs",random_state = 0)
         
        # generate a no skill prediction (majority class)
        noskill_probs = [False for _ in range(len(ytest))]
        
        classifier.fit(xtrain, ytrain) 
        
        y_pred_proba_val = classifier.predict_proba(xval)
        y_pred_val = classifier.predict(xval)
        
        y_pred_proba_test=classifier.predict_proba(xtest)
        y_pred_test=classifier.predict(xtest)
        
        
        y_pred_proba_val = y_pred_proba_val[:, 1]
        y_pred_proba_test = y_pred_proba_test[:, 1]
        
        # keep probabilities for the positive outcome only
        thresh_values= np.arange(0.1,0.8,0.05)
        print (f'def val: {f1_score(yval, y_pred_val):.2f}')
        print (f'def test:{f1_score(ytest, y_pred_test):.2f}')
        
        #other functions https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter
        scoring_function=f1_score
        
        scores_val_th=[]
        for th in thresh_values:
            Y_val_pred = [True if prob>th else False for prob in y_pred_proba_val]
            scores_val_th.append(scoring_function(yval, Y_val_pred))
            #print (th,":",scoring_function(yval, Y_val_pred))
            
            #Y_test_pred = [True if prob>th else False for prob in y_pred_proba_test]         
            #print (th,":",scoring_function(ytest, Y_test_pred))
            
        best_score_index=np.argmax(scores_val_th)
        best_th=thresh_values[best_score_index]
        
        Y_test_pred = [True if prob>best_th else False for prob in y_pred_proba_test]         
        print (f'Th:{best_th:.2f} Score:{scoring_function(ytest, Y_test_pred):.3f}')
        
        
        
        # calculate scores
        ns_auc = roc_auc_score(yval, noskill_probs)
        lr_auc = roc_auc_score(yval, y_pred_proba_val)
        # summarize scores
        #print('No Skill: ROC AUC=%.3f' % (ns_auc))
        #print('Logistic: ROC AUC=%.3f' % (lr_auc))
        # calculate roc curves
        
        
        #=======================================================================
        # ns_fpr, ns_tpr, _ = roc_curve(ytest, noskill_probs)
        # lr_fpr, lr_tpr, thresholds = roc_curve(ytest, y_pred_proba)
        # 
        # #for fpr, tpr, th in zip(lr_fpr,lr_tpr,thresholds):
        # #    print (fpr,tpr,th)
        # 
        # # plot the roc curve for the model
        # plt.plot(ns_fpr, ns_tpr, linestyle='--', label='No Skill')
        # plt.plot(lr_fpr, lr_tpr, marker='.', label='Logistic')
        # # axis labels
        # plt.xlabel('False Positive Rate')
        # plt.ylabel('True Positive Rate')
        # # show the legend
        # plt.legend()
        # # show the plot
        # plt.show()
        # 
        #=======================================================================
        #exit()
        
        
        #=======================================================================
        #  # define evaluation procedure
        # cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=0)
        # 
        # # evaluate model
        # scores = cross_val_score(classifier, x, y, scoring='roc_auc', cv=cv, n_jobs=1)#n_jobs=-1 means use all processors... and crashes
        # 
        # # summarize performance
        # print('Mean ROC AUC: %.3f' % mean(scores))
        #=======================================================================
    
    #===============================================================================
    # Code for plotting Precision-Recall curve and AUC score 
    # Note : Not using ROC curve as it is applicable to balanced datasets 
    #        (one v/s many classifiers are typically unbalanced)

    classifier_precision, classifier_recall, thresholds = precision_recall_curve(ytest, y_pred) #over multiple thresholds
    auc_score = auc(classifier_recall, classifier_precision)
   
    print("AUC for Logistic Regression: auc=%.3f" % auc_score)

    # plot the precision-recall curve
    no_skill_line = len(ytest[ytest==1]) / len(ytest) #bare-minimum threshold for performance
    plt.plot([0, 1], [no_skill_line, no_skill_line], linestyle='--', label='Random Guess')
    plt.plot(classifier_recall, classifier_precision, marker='.', label='Logistic Regression')
    # axis labels
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    # show the legend
    plt.legend()
    # show the plot
    #plt.show()
    plt.savefig('./prec_recall_plot.png')

#===============================================================================
# Code for plotting the value of a performance metric v/d data size (number of samples/documents)

metric_name = "Recall" # {str} Could be Recall/Precision/AUC score/F score and so on
metric_values = [1,2,3,4,5] # {List} Pass list of values for metric at different data sizes
data_n = [4,5,6,7,8] # {List} Pass list of corresponding number of documents

plot_metric_by_data_size(metric_name, metric_values, data_n)



         
            
    #===========================================================================
    #     print("Utt Type: ",headers[var_index])
    #     print("Confusion Matrix : \n", confusion_matrix(ytest, y_pred)) 
    #     print("Accuracy : ", accuracy_score(ytest, y_pred))
    #     print("Precision: ", precision_score(ytest, y_pred))
    #     print("Recall   : ", recall_score(ytest, y_pred))
    #     print("F1       : ", f1_score(ytest, y_pred))
    #     print()
    # 
    # #===============================================================================
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
    #     
    #     
    #     if prediction==y_elem and prediction==True :
    #         print ("\t",utt,file_n,teach,stud_nam,y_elem,prediction)
    #===============================================================================
        
        



