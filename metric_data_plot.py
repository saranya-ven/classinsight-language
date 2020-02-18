import numpy as np 
import matplotlib.pyplot as plt 

def plot_metric_by_data_size(metric_label, metric_values, n_data):
    plt.figure(metric_label)
    plt.plot(n_data, metric_values, marker='.', label='Model Performance & Input Size')
    plt.xlabel('Percentage of Data Samples')
    plt.ylabel(metric_label)
    plt.legend()
    #plt.show()
    plt.savefig('./plots/performance_vs_datasize/performance_percentages_data'+metric_label+'_plot.png')


if __name__ == "__main__":
    # --------Example Use----------
    a = [2,4,5,6]
    b = [8,8,8,5]
    name = "AUC"
    plot_metric_by_data_size(name, a, b)
