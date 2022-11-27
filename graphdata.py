import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats

class GraphData :
    def graph_all_dv(self, csv_name) :
        rats = pd.read_csv(csv_name)
    
        for dependent_var in rats : 
            if dependent_var == "name" or dependent_var == "auc": 
                continue

            pearsonr = scipy.stats.pearsonr(rats["auc"], rats[dependent_var])

            plt.scatter(rats["auc"], rats[dependent_var])
            plt.title(dependent_var + " per LL choice")
            plt.xlabel("AUC")
            plt.ylabel(dependent_var)
            plt.xlim(0, 1)
            plt.ylim(0)
            # line of best fit
            plt.plot(np.unique(rats["auc"]), np.poly1d(np.polyfit(rats["auc"], rats[dependent_var], 1))(np.unique(rats["auc"])))

            # plt.annotate(rats["name"], [rats["auc"], rats[dependent_var]])
            #plt.text(.5,2.2,"third")

            plt.show()
            print("r = ", round(pearsonr[0],3), "\np = ", round(pearsonr[1], 3))
            print("\n\n")
