import numpy as np 
import matplotlib.pyplot as plt 

def plot_metric_by_data_size(metric_label, metric, n_data):
    plt.plot(n_data, metric, marker='.', label='Model Performance & Input Size')
    plt.xlabel('Number of Data Samples')
    plt.ylabel(metric_label)
    plt.legend()
    #plt.show()
    plt.savefig('./performance_data_plot.png')


if __name__ == "__main__":
    # --------Example Use----------
    a = [2,4,5,6]
    b = [8,8,8,5]
    name = "AUC"
    print("inside plot")
    plot_metric_by_data_size(name, a, b)
