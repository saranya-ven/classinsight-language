import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve,roc_auc_score, precision_recall_curve,auc,precision_recall_fscore_support, f1_score


def report_roc_auc(y_test,y_pred_proba,label_figure="",directory_path="plots"):
    '''
    Receives a set of labels and a set of probabilities over those labels predicted by a classifier
    and calculates ROC_AUC
    '''
    # generate a no skill prediction (majority class)
    noskill_probs = [False for _ in range(len(y_test))]
    # calculate scores
    noskill_auc = roc_auc_score(y_test, noskill_probs)
    classifier_auc = roc_auc_score(y_test, y_pred_proba)
    # summarize scores
    print('Majority: ROC AUC=%.3f' % (noskill_auc))
    print('Model   : ROC AUC=%.3f' % (classifier_auc))

    # calculate roc curves
    noskill_fpr, noskill_tpr, _ = roc_curve(y_test, noskill_probs)
    model_fpr, model_tpr, thresholds = roc_curve(y_test, y_pred_proba)
 
    # plot the roc curve for the model
    plt.figure("ROC_AUC_"+label_figure)
    plt.plot(noskill_fpr, noskill_tpr, linestyle='--', label='Majority')
    plt.plot(model_fpr, model_tpr, marker='.', label='Model')
    # axis labels
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend()
    
    plot_filename=directory_path+'/roc_auc_'+label_figure+'.png'
    plt.savefig(plot_filename)
    
def report_precision_recall_auc(y_test,y_pred_proba,category_label,embedding_type,directory_path="plots",plot_no_skill=False):
    '''
    Code for plotting Precision-Recall curve and AUC score
    We prefer these metrics because the dataset is highly imbalanced
    Used to test classifiers across thresholds
    '''
    classifier_precision, classifier_recall, thresholds = precision_recall_curve(y_test, y_pred_proba) #over multiple thresholds
    
    auc_score = auc(classifier_recall, classifier_precision)           
    #print("AUC: %.3f" % auc_score)

    # plot the precision-recall curve   
    plt.figure("AUC_"+category_label,figsize=(20,10))

    plt.plot(classifier_recall, classifier_precision, marker='.', label=embedding_type)
    
    if plot_no_skill:
        #no_skill_line = len(y_test[y_test==True]) / len(y_test) #bare-minimum threshold for performance
        no_skill_line = len([True for val in y_test if val==True]) / len(y_test) #bare-minimum threshold for performance
        plt.plot([0, 1], [no_skill_line, no_skill_line], linestyle='--', label='Random Guess')
        
    # axis labels
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title("AUC  "+category_label)
    plt.legend()
    
    plot_filename=directory_path+'/auc_prec_recall_'+category_label+'.png'
    plt.savefig(plot_filename)
    return auc_score
    
    
def report_precision_recall_fscore(y_test,y_pred_proba,category_label,embedding_type,use_plots=True,directory_path="plots"):
    '''
    Code for plotting Precision, Recall and FScore VS Thresholds
    Used to select appropriate thresholds
    Returns the threshold with highest fscore, that fscore, and the auc_score
    '''
    classifier_precision, classifier_recall, thresholds = precision_recall_curve(y_test, y_pred_proba) #over multiple thresholds
    thresholds=np.append(thresholds,1.0)
    
    fscores_th=[]
    for th in thresholds:
        y_pred = [True if prob>th else False for prob in y_pred_proba]
        fscore=f1_score(y_test, y_pred)
        fscores_th.append(fscore)
        
    best_score_index=np.argmax(fscores_th)
    best_th=thresholds[best_score_index]
     
    auc_score = auc(classifier_recall, classifier_precision)           
    
    if use_plots:
        # PLOT the precision,recall,fscore VS thresholds   
        plt.figure("PrecRecFScore_"+category_label+embedding_type,figsize=(20,10))
        plt.plot(thresholds,classifier_precision, marker='.', label='Precision')
        plt.plot(thresholds, classifier_recall, marker='.', label='Recall')
        plt.plot(thresholds, fscores_th, marker='.', label='FScore')
    
        # axis labels
        plt.xlabel('Threshold')
        plt.ylabel('Score')
        plt.title(category_label)
        plt.legend()
        
        plot_filename=directory_path+'/prec_recall_fscore_'+category_label+'.png'
        plt.savefig(plot_filename)
    
    return best_th,auc_score



if __name__=="__main__":
    y_gold=[True,True,False,False,False,False]
    y_pred=[0.5,0.8,0.1,0.01,0.5,0.2]
    
    #report_precision_recall_auc(y_gold, y_pred)
    #report_roc_auc(y_gold, y_pred)
    report_precision_recall_fscore(y_gold, y_pred)
    
    
    #=======================================================================
    # SOMETHING ABOUT CROSS VALIDATION
    # cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=0)
    # scores = cross_val_score(classifier, x, y, scoring='roc_auc', cv=cv, n_jobs=1)#n_jobs=-1 means use all processors... and crashes
    # print('Mean ROC AUC: %.3f' % np.mean(scores))
    #=======================================================================

    