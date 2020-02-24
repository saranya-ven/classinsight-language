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
    
def get_bar_plots_grouped_embeddingtype(metric_label,all_data,group_labels,embedding_types):
    width = 0.12  # the width of the bars
    
    ind = np.arange(len(group_labels))  # the x locations for the groups
    indices_all=[ind]
    
    for sublist in np.arange(len(all_data)-1):
        new_indices=np.array([x + width for x in indices_all[sublist]])
        indices_all.append(new_indices)
            
    fig, ax = plt.subplots(figsize=(20,10))
    rects_all=[]
    for data_list,label_type,indices in zip(all_data,embedding_types,indices_all):
        rects_all.append(ax.bar(indices - width/2,data_list, width, label=label_type))
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(metric_label)
    ax.set_title('Scores by UtteranceType and Embedding')
    
    ax.set_xticks([r + width*2 for r in range(len(ind))])
    ax.set_xticklabels(utt_types)
    ax.legend()

    
    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.
    
        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """
    
        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0, 'right': 1, 'left': -1}
    
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{:.2f}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(offset[xpos]*3, 3),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        ha=ha[xpos], va='bottom')
    
    for rect in rects_all:autolabel(rect,"center")
    fig.tight_layout()
    plt.savefig(metric_label+".png")    

if __name__ == "__main__":
    # --------Example Use----------
    #===========================================================================
    # a = [2,4,5,6]
    # b = [8,8,8,5]
    # c = [4,6,9,9]
    # name = "AUC"
    # class_label="Open Questions"
    # plot_metric_by_data_size(name, a, b,class_label)
    # 
    # plot_metric_by_data_size_vs_embedding_type(name, class_label, b, a, "emb1")
    # plot_metric_by_data_size_vs_embedding_type(name, class_label, c, a, "emb2")
    #===========================================================================
    all_f1=[[0.6027397260273972, 0.4444444444444445, 0.4475524475524475, 0.6096654275092938, 0.54, 0.5405405405405405, 0.7142857142857144, 0.46774193548387094, 0.49593495934959353, 0.4444444444444444], [0.7042253521126761, 0.46808510638297873, 0.40740740740740744, 0.6171875, 0.5106382978723405, 0.5, 0.7304347826086957, 0.46956521739130436, 0.5494505494505495, 0.4705882352941177], [0.6956521739130435, 0.48148148148148157, 0.48437499999999994, 0.6276150627615062, 0.5615384615384615, 0.4166666666666667, 0.7326732673267328, 0.5037037037037037, 0.5394736842105263, 0.4615384615384615], [0.6774193548387096, 0.4705882352941177, 0.42372881355932196, 0.6209677419354839, 0.5198776758409785, 0.5142857142857142, 0.6722689075630252, 0.432, 0.5111111111111111, 0.5], [0.6896551724137931, 0.4313725490196078, 0.47482014388489213, 0.6337448559670782, 0.5806451612903225, 0.5, 0.7115384615384615, 0.48951048951048953, 0.5813953488372093, 0.4347826086956522], [0.6885245901639345, 0.5357142857142857, 0.5255474452554745, 0.6693548387096774, 0.5827814569536424, 0.42105263157894735, 0.7130434782608696, 0.5, 0.553191489361702, 0.39999999999999997]]
    all_auc=[[0.4958271788171767, 0.3018409595039662, 0.2931444113274104, 0.7235584556103586, 0.5384159070481306, 0.2707098552156372, 0.7135219236080479, 0.45059637881819953, 0.4054238852896813, 0.42021484620037886], [0.6702419698855899, 0.3533262589447408, 0.3308994271021133, 0.7252649150418514, 0.5651607506238187, 0.2300187768050982, 0.6613760471232726, 0.47964011185716915, 0.4141031753593629, 0.4330708267989306], [0.6263697351359839, 0.36275423706252274, 0.40518346995776744, 0.7682552115126083, 0.5695991005540758, 0.273971417396041, 0.6693515819563758, 0.471521119562856, 0.44472453969176917, 0.4304480427583498], [0.6212613282665076, 0.32178294396750096, 0.3010093768452388, 0.718607690281798, 0.5684014202983243, 0.23418830001741614, 0.7166910496059546, 0.4677192320454605, 0.4351561328081617, 0.5784853532645979], [0.6875862606994763, 0.3295755759459211, 0.35991798108080986, 0.7771311130263912, 0.5927914726593079, 0.2553629224052405, 0.755013843091279, 0.4974258852210202, 0.5094354080523303, 0.5108451258725132], [0.6055577363187261, 0.40569644623927764, 0.43314843101910555, 0.8053042712475941, 0.6151170605277501, 0.27813643928092835, 0.7395887691627253, 0.48892595828905555, 0.5674972107881929, 0.5483164121819583]]
    all_f1=np.array(all_f1)
    all_auc=np.array(all_auc)
    
    utt_types=["Utt_Turn_Taking",#2
                 "Metacognitive_Modelling",#3
                 "Utt_Behavior",#4
                 "Utt_Teacher_OpenQ",#5
                 "Utt_Teacher_CloseQ",#6
                 "Utt_Student_OpenQ",#7
                 "Utt_Student_CloseQ",#8
                 "Utt_Student_CloseR",#9
                 "Utt_Student_OpenR",#10
                 "Utt_Student_ExpEvi"]    
    embedding_types=["20","50","128","250","512","512t"]
       

    get_bar_plots_grouped_embeddingtype("FScores",all_f1, utt_types, embedding_types)
    get_bar_plots_grouped_embeddingtype("AUC",all_auc, utt_types, embedding_types)