import numpy as np 
import matplotlib.pyplot as plt 

def plot_metric_by_data_size(metric_label, metric_values, n_data,class_label, directory_path="plots/performance_vs_datasize"):
    plt.figure(metric_label)
    plt.plot(n_data, metric_values, marker='.', label=class_label)
    plt.title("Performance Vs Training Data Size")
    plt.xlabel('Percentage of Data Samples')
    plt.ylabel(metric_label)
    plt.legend()
    #plt.show()
    plt.savefig(directory_path+'/percent_data_'+metric_label+'_plot.png')

def plot_metric_by_data_size_vs_embedding_type(metric_label,category_label, metric_values, n_data ,embedding_type, directory_path="plots/performance_vs_datasize"):
    '''
    Plots a given metric vs datasize, and each time it is called, a new line is added corresponding to a new type embedding
    This method exploits the fact that using plt.figure() we can add stuff to the same figure as long as the name is the same
    '''
    
    plt.figure(metric_label+category_label,figsize=(20,10))
    plt.plot(n_data, metric_values, marker='.', label=embedding_type)
    plt.xlabel('Percentage of Data Samples')
    plt.ylabel(metric_label)
    plt.title(category_label)
    plt.legend()
    #plt.show()
    plt.savefig(directory_path+'/percent_data_'+metric_label+"_"+category_label+'_plot.png')

if __name__ == "__main__":
    # --------Example Use----------
    a = [2,4,5,6]
    b = [8,8,8,5]
    c = [4,6,9,9]
    name = "AUC"
    class_label="Open Questions"
    plot_metric_by_data_size(name, a, b,class_label)
    
    plot_metric_by_data_size_vs_embedding_type(name, class_label, b, a, "emb1")
    plot_metric_by_data_size_vs_embedding_type(name, class_label, c, a, "emb2")
    
    