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

        all_percents = {
            "ll_block_0s" : [],
            "ll_block_4s" : [],
            "ll_block_8s" : [],
            "ll_block_16s" : [],
            "ll_block_32s" : []

        }

        #transform rat_percent_ll to averages
        for rat, vals in rat_percent_ll.items() :
            for block, val in vals.items() :


                all_percents["ll_" + block].append(val["percent_ll"])
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

        
        plt.plot(x, y, color="black")
        plt.title("Overall Discounting Curve")
        plt.xlabel("Delay Block")
        plt.ylabel("Percent Larger Later Choice")
        plt.ylim(0, 100)
        plt.show()

        print(avg_percent_ll)


    def auc_table(self, csv_name) :
        rats = pd.read_csv(csv_name)

        all_auc = []

        #transfer names and aucs into table data format
        table_data = [["Subject", "AUC"]]
        for key, val in rats["name"].items() : 
            table_data.append([val])
            
        for key, val in rats["auc"].items() : 
            table_data[key + 1].append(val)
            all_auc.append(val)


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
        entries_4s = []
        entries_8s = []
        entries_16s = []
        entries_32s = []
        
        for rat in entry_stats :

            tot_entries_4s += entry_stats[rat]["block_4s"]["entries_per_ll"]
            tot_entries_8s += entry_stats[rat]["block_8s"]["entries_per_ll"]
            tot_entries_16s += entry_stats[rat]["block_16s"]["entries_per_ll"]
            tot_entries_32s += entry_stats[rat]["block_32s"]["entries_per_ll"]

            entries_4s.append(entry_stats[rat]["block_4s"]["entries_per_ll"])
            entries_8s.append(entry_stats[rat]["block_8s"]["entries_per_ll"])
            entries_16s.append(entry_stats[rat]["block_16s"]["entries_per_ll"])
            entries_32s.append(entry_stats[rat]["block_32s"]["entries_per_ll"])
        
        avg_entries = {}
        avg_entries["4s"] = round(tot_entries_4s / len(entry_stats), 2)
        avg_entries["8s"] = round(tot_entries_8s / len(entry_stats), 2)
        avg_entries["16s"] = round(tot_entries_16s / len(entry_stats), 2)
        avg_entries["32s"] = round(tot_entries_32s / len(entry_stats), 2)

        courses = list(avg_entries.keys())
        values = list(avg_entries.values())

        
        fig = plt.figure(figsize = (10, 5))

        
        # creating the bar plot
        plt.bar(courses, values, color ='black',
                width = 0.4)
        
        plt.ylabel("Average Head Entries")
        plt.xlabel("Delay Block")
        plt.title("Overall Head Entries Per Block")
        plt.show()

        print("AVG ENTRIES: ", avg_entries)
        # print("4s SD: ", np.std(entries_4s, ddof=1))
        # print("8s SD: ", np.std(entries_8s, ddof=1))
        # print("16s SD: ", np.std(entries_16s, ddof=1))
        # print("32s SD: ", np.std(entries_32s, ddof=1))

    def first_entry_per_block(self, entry_stats) :
        tot_lat_4s = 0
        tot_lat_8s = 0
        tot_lat_16s = 0
        tot_lat_32s = 0
        entries_4s = []
        entries_8s = []
        entries_16s = []
        entries_32s = []

        for rat in entry_stats :

            tot_lat_4s += entry_stats[rat]["block_4s"]["first_entry_lat"]
            tot_lat_8s += entry_stats[rat]["block_8s"]["first_entry_lat"]
            tot_lat_16s += entry_stats[rat]["block_16s"]["first_entry_lat"]
            tot_lat_32s += entry_stats[rat]["block_32s"]["first_entry_lat"]

            entries_4s.append(entry_stats[rat]["block_4s"]["first_entry_lat"])
            entries_8s.append(entry_stats[rat]["block_8s"]["first_entry_lat"])
            entries_16s.append(entry_stats[rat]["block_16s"]["first_entry_lat"])
            entries_32s.append(entry_stats[rat]["block_32s"]["first_entry_lat"])
        
        avg_lat = {}
        avg_lat["4s"] = round(tot_lat_4s / len(entry_stats), 2)
        avg_lat["8s"] = round(tot_lat_8s / len(entry_stats), 2)
        avg_lat["16s"] = round(tot_lat_16s / len(entry_stats), 2)
        avg_lat["32s"] = round(tot_lat_32s / len(entry_stats), 2)

        courses = list(avg_lat.keys())
        values = list(avg_lat.values())
        
        fig = plt.figure(figsize = (10, 5))
        
        # creating the bar plot
        plt.bar(courses, values, color ='black',
                width = 0.4)
        
        plt.ylabel("Average First Entry Latency")
        plt.xlabel("Delay Block")
        plt.title("Overall First Entry Latency Per Block")
        plt.show()

        print("AVERAGE LAT: ", avg_lat)

        # print("4s SD: ", np.std(entries_4s, ddof=1))
        # print("8s SD: ", np.std(entries_8s, ddof=1))
        # print("16s SD: ", np.std(entries_16s, ddof=1))
        # print("32s SD: ", np.std(entries_32s, ddof=1))


    def graph_dv_correlations(self, csv_name) :
        rats = pd.read_csv(csv_name)
    
        for dependent_var in rats : 
            if dependent_var == "name" or dependent_var == "auc": 
                continue

            pearsonr = scipy.stats.pearsonr(rats["auc"], rats[dependent_var])

            plt.rcParams.update({'font.size': 18})

            plt.scatter(rats["auc"], rats[dependent_var], color="black")
            plt.title(dependent_var.title().replace("S", "s") + " per LL choice")
            plt.xlabel("AUC")
            plt.ylabel(dependent_var.title().replace("S", "s"))

            plt.xlim(0, 1)
            plt.ylim(0)
            # line of best fit
            plt.plot(np.unique(rats["auc"]), np.poly1d(np.polyfit(rats["auc"], rats[dependent_var], 1))(np.unique(rats["auc"])), color="black")

            # plt.annotate(rats["name"], [rats["auc"], rats[dependent_var]])
            #plt.text(.5,2.2,"third")

            plt.show()
            print("r =", round(pearsonr[0],3), "\np =", round(pearsonr[1], 3))
            print("\n\n")
