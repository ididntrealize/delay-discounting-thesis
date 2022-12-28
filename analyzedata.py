import json
import csv
from datetime import date, datetime
import time

from config import Config

config = Config()

class AnalyzeData :
    
    def block_choices_template(self) : 
        return {
            "ss" : {
                "session_count": 0,
                "total": 0,
                "block_0s": { 
                    "total": 0
                },
                "block_4s": { 
                    "total": 0
                },
                "block_8s": { 
                    "total": 0
                },
                "block_16s": { 
                    "total": 0
                },
                "block_32s": { 
                    "total": 0
                }
            },
            "ll" : {
                "session_count": 0,
                "total": 0,
                "block_0s": {
                    "total": 0,
                    "total_entries" : 0,
                    "total_entry_lat" : 0,
                    "first_entry_lat" : 0,
                    "last_entry_lat" : 0
                },
                "block_4s": {
                    "total": 0,
                    "total_entries" : 0,
                    "total_entry_lat" : 0,
                    "first_entry_lat" : 0,
                    "last_entry_lat" : 0
                },
                "block_8s": {
                    "total": 0,
                    "total_entries" : 0,
                    "total_entry_lat" : 0,
                    "first_entry_lat" : 0,
                    "last_entry_lat" : 0
                },
                "block_16s": {
                    "total": 0,
                    "total_entries" : 0,
                    "total_entry_lat" : 0,
                    "first_entry_lat" : 0,
                    "last_entry_lat" : 0
                },
                "block_32s": {
                    "total": 0,
                    "total_entries" : 0,
                    "total_entry_lat" : 0,
                    "first_entry_lat" : 0,
                    "last_entry_lat" : 0
                }
            }
        }
    
    
    def choices_per_block(self, obj) :
        
        block_choices = {}
        
        for session in obj :
            #don't analyze if name not in whitelist
            unaccepted_names = self.check_name_consistency(obj, config.accepted_name_map)
            if session["rat_name"] in unaccepted_names :
                continue
            

            #add new rat obj if doesn't exist
            safe_rat_name = config.accepted_name_map[session["rat_name"]]
            
            if safe_rat_name not in block_choices :
                block_choices[safe_rat_name] = self.block_choices_template()

            #don't analyze if before first_stability_date
            first_stable_date = config.stability_start_date[safe_rat_name]
            
            #reformat year from /22 to /2022
            if first_stable_date != -1 :
                first_stable_date_str = first_stable_date[:-2]
                first_stable_date_str += "20" + first_stable_date[-2:]

            #reformat year from /22 to /2022
            session_date = session["date"][:-2]
            session_date += "20" + session["date"][-2:]


            # print("\n", session_date)
            # print(session["start_time"])
            
            if first_stable_date != -1 :
                session_timestamp = time.strptime(session_date, "%m/%d/%Y")
                first_stable_timestamp = time.strptime(first_stable_date_str, "%m/%d/%Y")

                if session_timestamp < first_stable_timestamp :
                    continue

                #don't analyze if limit of stable sessions has been reached
                analyzed_session_count = block_choices[safe_rat_name]["ss"]["session_count"]
                if analyzed_session_count >= config.stability_session_count :                    
                    continue

                # Check for sessions that didn't run long enough
                format = '%H:%M:%S'
                time_elap = datetime.strptime(session["end_time"], format) - datetime.strptime(session["start_time"], format)
                
                if time_elap.total_seconds() < 50 * 60 :
                    print("session being analyzed ran less than 50 minutes: ", time_elap)
                    print("session Date: ", session_date)
            
            #increment sessions counters
            block_choices[safe_rat_name]["ss"]["session_count"] += 1
            block_choices[safe_rat_name]["ll"]["session_count"] += 1
            block_choices[safe_rat_name]["ss"]["total"] += session["total_ss"]
            block_choices[safe_rat_name]["ll"]["total"] += session["total_ll"]
            
            #calculate running total per block
            block_choices[safe_rat_name]["ss"]["block_0s"]["total"] += session["block_0s"]["ss"]
            block_choices[safe_rat_name]["ll"]["block_0s"]["total"] += session["block_0s"]["ll"]
            block_choices[safe_rat_name]["ss"]["block_4s"]["total"] += session["block_4s"]["ss"]
            block_choices[safe_rat_name]["ll"]["block_4s"]["total"] += session["block_4s"]["ll"]
            block_choices[safe_rat_name]["ss"]["block_8s"]["total"] += session["block_8s"]["ss"]
            block_choices[safe_rat_name]["ll"]["block_8s"]["total"] += session["block_8s"]["ll"]
            block_choices[safe_rat_name]["ss"]["block_16s"]["total"] += session["block_16s"]["ss"]
            block_choices[safe_rat_name]["ll"]["block_16s"]["total"] += session["block_16s"]["ll"]
            block_choices[safe_rat_name]["ss"]["block_32s"]["total"] += session["block_32s"]["ss"]
            block_choices[safe_rat_name]["ll"]["block_32s"]["total"] += session["block_32s"]["ll"]
            
            
            #integrate head entries
            for block in ['4', '8', '16', '32'] :
                
                total_entries = 0
                total_entry_lat = 0
                first_entry_lat = 0
                last_entry_lat = 0
                    
                #count each entry in each trial
                for trial in session["block_" + block + "s"]["entries"] :
                    total_entries += len(trial)

                    for i, entry in enumerate(trial) : 
                        # account for case where timer didn't stop soon enough
                        total_entry_lat += entry % 90
                        
                        if i == 0 :
                            # account for case where timer didn't stop soon enough
                            first_entry_lat += entry % 90
                            
                        if i == len(trial) - 1 :
                            # account for case where timer didn't stop soon enough
                            last_entry_lat += entry % 90
                
                block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["total_entries"] += total_entries
                block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["total_entry_lat"] += total_entry_lat
                block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["first_entry_lat"] += first_entry_lat
                block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["last_entry_lat"] += last_entry_lat
                
                # curr_block = block_choices[safe_rat_name]["ll"]["block_" + block + "s"]
                # block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["total_entries"] = round(curr_block["total_entries"], 2)
                # block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["total_entry_lat"] = round(curr_block["total_entry_lat"], 2)
                # block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["first_entry_lat"] = round(curr_block["first_entry_lat"], 2)
                # block_choices[safe_rat_name]["ll"]["block_" + block + "s"]["last_entry_lat"] = round(curr_block["last_entry_lat"], 2)
            
        return block_choices
    
    
    def percent_ll(self, block_choices) :
        rat_percent_ll = {}
    
        for rat in block_choices :
            # ll_percentage_total = block_choices[rat]["ll"]["total"] / (block_choices[rat]["ll"]["total"] + block_choices[rat]["ss"]["total"])

            ll_percentage = {}

            for block in [0, 4, 8, 16, 32] :
                ll_total = block_choices[rat]["ll"]["block_" + str(block) + "s"]["total"]
                ss_total = block_choices[rat]["ss"]["block_" + str(block) + "s"]["total"]

                ll_percentage["block_" + str(block) + "s"] = {}
                ll_percentage["block_" + str(block) + "s"]["percent_ll"] = round(ll_total / (ll_total + ss_total), 2)

            rat_percent_ll[rat] = ll_percentage

        return rat_percent_ll
    
    
    def calc_entry_stats(self, block_choices) :
        entry_stat_means = {}
    
        for rat in block_choices :
            entry_stat_means[rat] = {}

            for block in [4, 8, 16, 32] :
                safe_block = str(block)
                entry_stat_means[rat]["block_" + safe_block + "s"] = {}

                curr_block = block_choices[rat]["ll"]["block_" + safe_block + "s"]

                entries_per_ll = curr_block["total_entries"] / curr_block["total"]
                entry_stat_means[rat]["block_" + safe_block + "s"]["entries_per_ll"] = round(entries_per_ll, 3)

                first_entry_lat = curr_block["first_entry_lat"] / curr_block["total"]
                entry_stat_means[rat]["block_" + safe_block + "s"]["first_entry_lat"] = round(first_entry_lat, 3)

                if curr_block["total_entries"] != 0 :
                    avg_entry_lat = curr_block["total_entry_lat"] / curr_block["total_entries"]
                    entry_stat_means[rat]["block_" + safe_block + "s"]["avg_entry_lat"] = round(avg_entry_lat, 3)
                else :
                    entry_stat_means[rat]["block_" + safe_block + "s"]["avg_entry_lat"] = 0

        return entry_stat_means
    
    
    def calc_auc(self, rat_percent_ll) : 
        
        rat_auc = {}

        for rat, percentages in rat_percent_ll.items():

            auc_vals = []
            for block in percentages :
                auc_vals.append({
                    "distance": config.auc_distance_map[block], 
                    "percent": rat_percent_ll[rat][block]["percent_ll"],
                    "auc": 0
                })

            for i, block in enumerate(auc_vals) :
                if i + 1 == len(auc_vals) :
                    break

                #AUC equation (n1 + n2) / 2* (d2 - d1)
                auc = (auc_vals[i + 1]["percent"] + auc_vals[i]["percent"]) / 2*(auc_vals[i + 1]["distance"] - auc_vals[i]["distance"])
                
                auc_vals[i]["auc"] = auc

            total_auc = 0

            for block in auc_vals :
                total_auc += block["auc"]

            final_auc = total_auc / (len(auc_vals) - 1)
            rat_auc[rat] = round(final_auc, 2)
                
        return rat_auc
    
     
    def check_name_consistency(self, obj, accepted_names) : 
        unaccepted_names = []
        for trial in obj :
            if trial["rat_name"] not in accepted_names :
                unaccepted_names.append(trial["rat_name"])
        
        return unaccepted_names
 
   
    def create_csv(self, aucs, entry_stats, block_choices) :
        today = date.today()

        with open('rats-' + today.strftime("%m-%d-%Y") + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            headers = [
                "name", 
                "auc", 
                "head entries in 4s block", 
                "head entries in 8s block", 
                "head entries in 16s block", 
                "head entries in 32s block", 
                "first entry (s) in 4s block", 
                "first entry (s) in 8s block", 
                "first entry (s) in 16s block", 
                "first entry (s) in 32s block" 
                # "mean entry latency 4s", 
                # "mean entry latency 8s", 
                # "mean entry latency 16s", 
                # "mean entry latency 32s"
                # "mean ll 0s",
                # "mean ll 4s",
                # "mean ll 8s",
                # "mean ll 16s",
                # "mean ll 32s",
                # "mean ss 0s",
                # "mean ss 4s",
                # "mean ss 8s",
                # "mean ss 16s",
                # "mean ss 32s"
                 ]
                 
            writer.writerow(headers)
            
            for rat in entry_stats :
                name = rat
                auc = aucs[rat]

                avg_entries_4s = entry_stats[rat]["block_4s"]["entries_per_ll"]
                avg_entries_8s = entry_stats[rat]["block_8s"]["entries_per_ll"]
                avg_entries_16s = entry_stats[rat]["block_16s"]["entries_per_ll"]
                avg_entries_32s = entry_stats[rat]["block_32s"]["entries_per_ll"]

                avg_first_entries_4s = entry_stats[rat]["block_4s"]["first_entry_lat"]
                avg_first_entries_8s = entry_stats[rat]["block_8s"]["first_entry_lat"]
                avg_first_entries_16s = entry_stats[rat]["block_16s"]["first_entry_lat"]
                avg_first_entries_32s = entry_stats[rat]["block_32s"]["first_entry_lat"]

                # avg_entries_lat_4s = entry_stats[rat]["block_4s"]["avg_entry_lat"]
                # avg_entries_lat_8s = entry_stats[rat]["block_8s"]["avg_entry_lat"]
                # avg_entries_lat_16s = entry_stats[rat]["block_16s"]["avg_entry_lat"]
                # avg_entries_lat_32s = entry_stats[rat]["block_32s"]["avg_entry_lat"]

                writer.writerow([
                    name, 
                    auc, 
                    avg_entries_4s, 
                    avg_entries_8s, 
                    avg_entries_16s, 
                    avg_entries_32s,
                    avg_first_entries_4s,
                    avg_first_entries_8s,
                    avg_first_entries_16s,
                    avg_first_entries_32s
                    # avg_entries_lat_4s,
                    # avg_entries_lat_8s,
                    # avg_entries_lat_16s,
                    # avg_entries_lat_32s
                    ])
            

            print("\ncreated csv")
            return 'rats-' + today.strftime("%m-%d-%Y") + '.csv'
            
            
            