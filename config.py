class Config :
    #manage misspelled names  "name in ledger" : "corrected name"
    #must keep ALL rat names mapped to themselves, i.e. "susan" : "susan",
    accepted_name_map = {
        "cecilia" : "cecilia",
        "susan" : "susan",
        "virginia" : "virginia",
        "virgina" : "virginia",
        "patricia" : "patricia",
        "marian" : "marian",
        "sara" : "sara",
        "sarah" : "sara",
        "fran" : "fran",
        "catherine" : "catherine"   
    }

    #Number of sessions to track after stability_start_date per rat
    stability_session_count = 5

    #Date of FIRST stable session.
    stability_start_date = {
        "marian": "11/11/22",
        "sara": "11/28/22",
        "fran": "11/08/22",
        "catherine": "11/14/22",
        "cecilia": "11/04/22",
        "susan": "11/08/22",
        "virginia": "11/04/22",
        "patricia": "11/08/22"   
    }

    #calculate AUC based on block intra-distances
    auc_distance_map = {
        "block_0s" : 1,
        "block_4s" : 2,
        "block_8s" : 3,
        "block_16s" : 4,
        "block_32s" : 5
    }

    #Ignore programs in raw data with the following names
    irrelevant_programs = [
        "amanda-L", 
        "amanda-R", 
        "cano-L 3 pellets", 
        "cano-R 3 pellets"
    ]