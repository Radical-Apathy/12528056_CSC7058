from deta import Deta
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

#metaData=deta_connection.Base("database_versions")
metaData=deta_connection.Base("database_metadata")

def insert_csv(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, approved_by, date_approved, current_database_path):
    """adding user"""
    #defining the email as the key
    return metaData.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Approved_By":approved_by, "Date_Approved":date_approved, "Current Dataset":current_database_path })

#"C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv"
now=datetime.now()
#insert_csv(str(now), "n/a", "C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv", "none", "n/a", "n/a", "admin", "n/a", "Approved", "n/a", "admin",str(now), "C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv")


def get_all_paths():
    res = metaData.fetch()
    
    return res.items

databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=sorted([database["Status"] for database in databases])
path = sorted([database["Current Dataset"] for database in databases])
edit_type=[database["Edit_Type"] for database in databases]
changes=[database["Changes"] for database in databases]

approved=[]


def get_latest():
    for database in databases:
     for i in date_time:
        #for database["key"] in databases:
      if database["key"]== i and database["Status"] =="Approved":
        break
    return(database["Current Dataset"])

path=get_latest()

#method to get pending approvals for new species addition

pending=[]

#gets dates for new species additions needing approval
def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()
ordered=sorted(pending,reverse=True)

#get user info for each date in pending
latest=ordered[0]
print(latest)

def get_user_info(date):
    for database in databases:
        if database["key"]==date:
            print(database["Edited_By"])

get_user_info(latest)

def get_changes_csv(date):
    for database in databases:
        if database["key"]==date:
            print(database["Changes"])

#get_changes_csv(latest)

print("latest" + get_latest())