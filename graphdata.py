import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import make_interp_spline
import scipy.stats

from config import Config

config = Config()

class GraphData :
    def overall_discounting_curve(self, rat_percent_ll) :
        total_percent_ll = {}
        #transform rat_percent_ll to averages
        for rat, vals in rat_percent_ll.items() :
            for block, val in vals.items() :
                #create block in totals dict, if not exists
                if block not in total_percent_ll :
                    total_percent_ll[block] = val["percent_ll"]
                else :
                    total_percent_ll[block] += val["percent_ll"]
            
        #divide each value by number rats
        avg_percent_ll = {}

        for block in total_percent_ll : 
            avg_percent = 100*total_percent_ll[block] / len(rat_percent_ll)
            avg_percent_ll[block] = round(avg_percent, 3)
        
        x = np.array([])
        y = np.array([])

        for block, val in avg_percent_ll.items() :
            x = np.append(x, block.replace("block_", ""))
            y = np.append(y, val)

        plt.plot(x, y)
        plt.title("Overall Discounting Curve")
        plt.xlabel("Delay Block")
        plt.ylabel("Percent Larger Later Choice")
        plt.ylim(0, 100)
        plt.show()


    def auc_table(self, csv_name) :
        rats = pd.read_csv(csv_name)

        #transfer names and aucs into table data format
        table_data = [["Subject", "AUC"]]
        for key, val in rats["name"].items() : 
            table_data.append([val])
            
        for key, val in rats["auc"].items() : 
            table_data[key + 1].append(val)


        #create table
        table = plt.table(cellText=table_data, loc='center', cellLoc='left', edges="open")
        table.scale(1, 1.5)

        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)

        plt.title("Area Under the Curve (AUC) by Subject")
        plt.show()

    def entries_per_block(self, entry_stats) :
        tot_entries_4s = 0
        tot_entries_8s = 0
        tot_entries_16s = 0
        tot_entries_32s = 0
        
        for rat in entry_stats :

            tot_entries_4s += entry_stats[rat]["block_4s"]["entries_per_ll"]
            tot_entries_8s += entry_stats[rat]["block_8s"]["entries_per_ll"]
            tot_entries_16s += entry_stats[rat]["block_16s"]["entries_per_ll"]
            tot_entries_32s += entry_stats[rat]["block_32s"]["entries_per_ll"]
        
        avg_entries = {}
        avg_entries["block_4s"] = round(tot_entries_4s / len(entry_stats), 2)
        avg_entries["block_8s"] = round(tot_entries_8s / len(entry_stats), 2)
        avg_entries["block_16s"] = round(tot_entries_16s / len(entry_stats), 2)
        avg_entries["block_32s"] = round(tot_entries_32s / len(entry_stats), 2)

        courses = list(avg_entries.keys())
        values = list(avg_entries.values())
        
        fig = plt.figure(figsize = (10, 5))
        
        # creating the bar plot
        plt.bar(courses, values, color ='blue',
                width = 0.4)
        
        plt.ylabel("Average Head Entries")
        plt.xlabel("Delay Block")
        plt.title("Overall Head Entries Per Block")
        plt.show()


    def first_entry_per_block(self, entry_stats) :
        tot_lat_4s = 0
        tot_lat_8s = 0
        tot_lat_16s = 0
        tot_lat_32s = 0

        for rat in entry_stats :

            tot_lat_4s += entry_stats[rat]["block_4s"]["first_entry_lat"]
            tot_lat_8s += entry_stats[rat]["block_8s"]["first_entry_lat"]
            tot_lat_16s += entry_stats[rat]["block_16s"]["first_entry_lat"]
            tot_lat_32s += entry_stats[rat]["block_32s"]["first_entry_lat"]
        
        avg_lat = {}
        avg_lat["block_4s"] = round(tot_lat_4s / len(entry_stats), 2)
        avg_lat["block_8s"] = round(tot_lat_8s / len(entry_stats), 2)
        avg_lat["block_16s"] = round(tot_lat_16s / len(entry_stats), 2)
        avg_lat["block_32s"] = round(tot_lat_32s / len(entry_stats), 2)

        courses = list(avg_lat.keys())
        values = list(avg_lat.values())
        
        fig = plt.figure(figsize = (10, 5))
        
        # creating the bar plot
        plt.bar(courses, values, color ='blue',
                width = 0.4)
        
        plt.ylabel("Average First Entry Latency")
        plt.xlabel("Delay Block")
        plt.title("Overall First Entry Latency Per Block")
        plt.show()


    def graph_dv_correlations(self, csv_name) :
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
