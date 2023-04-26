import os
import re
import glob
from itertools import groupby

from config import Config

config = Config()

class ExtractData :
    raw_data_path = "./raw-data"
    
    def serialize_raw(self, path) :

        all_trials_str = ""
        for infile in glob.glob(os.path.join(path, '*')):
            review_file = open(infile,'r').read()
            
            #add new file str and remove "File:" line from file headers
            all_trials_str = all_trials_str + review_file.split("\n",2)[2]
            
        all_trials = all_trials_str.split("\n\n\n")

        #compile trial data into json
        serialized_dd_trials, ignored_trials, err = self.serialize_trials(all_trials)
        
        if err :
            print(err)
        else :
            print("Data extracted from raw files")
            return serialized_dd_trials
        
        
    def serialize_trials(self, all_trials) :
    
        serialized_trials = []
        
        ignored_trials = {
            "amanda" : 0,
            "cano" : 0,
            "unnamed" : 0
        }
        
        for trial_str in all_trials :
            trial = {
                "rat_name" : "not found",
                "date" : "not found",
                "program" : "not found",
                "start_time": "not found",
                "end_time": "not found",
                "total_ll" : -1,
                "total_ss" : -1,
                "block_0s" : {
                    "ll" : -1,
                    "ss" : -1,
                    "entries" : []
                },
                "block_4s" : {
                    "ll" : -1,
                    "ss" : -1,
                    "entries" : []
                },
                "block_8s" : {
                    "ll" : -1,
                    "ss" : -1,
                    "entries" : []
                },
                "block_16s" : {
                    "ll" : -1,
                    "ss" : -1,
                    "entries" : []
                },
                "block_32s" : {
                    "ll" : -1,
                    "ss" : -1,
                    "entries" : []
                }
                
            }
            
            try :
                #split text to extract values
                rat_name = trial_str.split("Subject: ")[1].split("\n")[0]
                date = trial_str.split("Start Date: ")[1].split("\n")[0]
                start_time = trial_str.split("Start Time: ")[1].split("\n")[0]
                end_time = trial_str.split("End Time: ")[1].split("\n")[0]
                program = trial_str.split("MSN: ")[1].split("\n")[0]

                trial["rat_name"] = rat_name.lower()
                trial["date"] = date
                trial["program"] = program
                trial["start_time"] = start_time
                trial["end_time"] = end_time
                
            except :
                return False, False, "error extracting name, date, or program name for: \n" + trial_str
            
            #remove phase 1 and 2 data
            if program in config.irrelevant_programs :
                ignored_trials[program.split("-")[0]] += 1
                continue
                
            #remove trials missing subject name
            if rat_name == "0" :
                ignored_trials["unnamed"] += 1
                continue
            
            try :
                #process ll array
                ll_blocks_str = trial_str.split("B:\n")[1].split("C:\n")[0].replace("\n", "")
                #remove med-pc indicies "0: , 5: , 10: "
                ll_blocks = self.remove_indicies(ll_blocks_str)

                trial["total_ll"] = int(float(ll_blocks[0])) / 3
                trial["block_0s"]["ll"] = int(float(ll_blocks[1])) / 3
                trial["block_4s"]["ll"] = int(float(ll_blocks[2])) / 3
                trial["block_8s"]["ll"] = int(float(ll_blocks[3])) / 3
                trial["block_16s"]["ll"] = int(float(ll_blocks[4])) / 3
                trial["block_32s"]["ll"] = int(float(ll_blocks[5])) / 3


                #process ss array
                ss_blocks_str = trial_str.split("D:\n")[1].split("I:\n")[0].replace("\n", "")
                #remove med-pc indicies "0: , 5: , 10: "
                ss_blocks = self.remove_indicies(ss_blocks_str)

                trial["total_ss"] = float(ss_blocks[0])
                trial["block_0s"]["ss"] = float(ss_blocks[1])
                trial["block_4s"]["ss"] = float(ss_blocks[2])
                trial["block_8s"]["ss"] = float(ss_blocks[3])
                trial["block_16s"]["ss"] = float(ss_blocks[4])
                trial["block_32s"]["ss"] = float(ss_blocks[5])
            
            except :
                return False, False, "error extracting LL or SS values in 'B' or 'D' var for: \n" + trial_str
             
            #process head entries
            all_entries = trial_str.split("V:\n")[1]
            all_trial_entries = self.remove_indicies(all_entries)
            
            #remove edge case trials where interface was not on when trial started
            if self.all_equal(all_trial_entries) :
                continue
                    
            try :
                entries_json = self.extract_entries(all_trial_entries)
                for key in entries_json :
                    trial[key]["entries"] = entries_json[key]["entries"]
                
            except :
               return False, False, "error extracting entries in 'V' var for: \n" + trial_str
            
            serialized_trials.append(trial)
            #print(json.dumps(trial, sort_keys=False, indent=4))
            
            
        return serialized_trials, ignored_trials, False
    
    
    def extract_entries(self, all_trial_entries) :
        
        all_entries = {
            "block_4s" : {
                "entries" : []
            },
            "block_8s" : {
                "entries" : []
            },
            "block_16s" : {
                "entries" : []
            },
            "block_32s" : {
                "entries" : []
            }
        }
        
        block_indicators = [-32, -16, -8, -4]
        curr_entries = []
        prev_entry = -32
        
        for i, entry in enumerate(reversed(all_trial_entries)) :
            floated_entry = float(entry)
            
            if floated_entry in block_indicators : 
                entry_block = "block_" + str(-1*prev_entry).split(".")[0] + "s"
                
                #add all found positive entries into dict
                all_entries[entry_block]["entries"] = [curr_entries] + all_entries[entry_block]["entries"]
                
                #refresh entries for next trial with entries
                curr_entries = []
                prev_entry = floated_entry
                
            elif floated_entry > 0 :
                curr_entries = [floated_entry] + curr_entries
                
                
        #add last (chronologically first) entry set into dict
        all_entries[entry_block]["entries"] = [curr_entries] + all_entries[entry_block]["entries"]
        
        return all_entries
    
    
    def remove_indicies(self, string) :
        no_indicies = re.sub('([0-9]+):', '', string)
        not_empty = [x for x in no_indicies.split("     ") if x]
        trimmed = []
        for item in not_empty :
            trimmed.append(item.replace(" ", "").replace("\n", ""))
    
        return trimmed
    
    def all_equal(self, iterable):
        g = groupby(iterable)
        return next(g, True) and not next(g, False)