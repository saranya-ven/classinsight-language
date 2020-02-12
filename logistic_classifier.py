import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression 
from sklearn.metrics import accuracy_score,f1_score,recall_score,precision_score,confusion_matrix

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

#===============================================================================
# for i,elem in enumerate(headers):
#     print(i, elem)
#===============================================================================

#x = dataset.iloc[:, 12:71].values
x= dataset.iloc[:,12:71+embedding_dimensionality].values

for var_index in range(2,12):
    y = dataset.iloc[:, var_index].values 
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size = 0.10, random_state = 0)
    
    classifier = LogisticRegression(random_state = 0) 
    classifier.fit(xtrain, ytrain) 

    y_pred = classifier.predict(xtest) 
        
    print("Utt Type: ",headers[var_index])
    print("Confusion Matrix : \n", confusion_matrix(ytest, y_pred)) 
    print("Accuracy : ", accuracy_score(ytest, y_pred))
    print("Precision: ", precision_score(ytest, y_pred))
    print("Recall   : ", recall_score(ytest, y_pred))
    print("F1       : ", f1_score(ytest, y_pred))
    print()
    
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
    plt.show()


#===============================================================================
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
        
        



