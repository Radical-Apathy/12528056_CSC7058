from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
from dotenv import load_dotenv
from datetime import datetime


#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

metaData=deta_connection.Base("database_metadata")

#------------------------------------------------------------metadata METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = metaData.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=sorted([database["Status"] for database in databases])
paths = [database["Current Dataset"] for database in databases]

#getting the most recent approved csv file
#def get_latest():
 #   for database in databases:
  #   for i in date_time:
        
 #     if database["key"]== i and database["Status"] =="Approved":
 #       break
 #   return(database["Current Dataset"])

#path=get_latest()

approved=[]
def get_approved():
    for database in databases:
        
            #if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Approved":
                if database["Status"] =="Approved":
                
                 approved.append(database["key"])

get_approved()

approvedordered=sorted(approved,reverse=True)


def get_latest_ds(key):
    for database in databases:
        if database["key"] ==key:
            return database["Current Dataset"]


latestds=get_latest_ds(approvedordered[0])


@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape', low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated


#------------------------------------------------------------USERS_DB DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

users_db=deta_connection.Base("users_db")

def get_all_users():
    res = users_db.fetch()
    #print(res.items) #using return here gives an address
    return res.items

#converts each individual values for users to a their own list using list comprehension
users=get_all_users()
email=[user["key"] for user in users]
username=[user["username"] for user in users]
firstname=[user["firstname"] for user in users]
surname = [user["surname"] for user in users]
hashed_passwords=[user ["password"] for user in users]
isApproved=[user["approved"]for user in users]
isAdmin=[user["admin"] for user in users]

#-----------------------------------------------------------SESSION STATES-----------------------------------------#
#if "subdate" not in st.session_state:
#   st.session_state["subdate"] ==""

#st.session_state
#------------------------------------------------------------METHODS -----------------------------------------------------------------------------------------#


#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#

st.header("Amin New Species Addition dev")

st.write("Current Database")
current=load_latest()
currentstyled=current.style.set_properties(**{'background-color':'white', 'color':'black'})
st.write(current)



#database metadata items
date_time= sorted([database["key"] for database in databases], reverse=True)
status=[database["Status"] for database in databases]
path = [database["Current Dataset"] for database in databases]
edit_type=[database["Edit_Type"] for database in databases]
changes=[database["Changes"] for database in databases]


#method to select edits that are new species addition and pending
pending=[]

#gets dates for new species additions needing approval
def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

ordered=sorted(pending,reverse=True)

st.write("Using selectbox to show pending new species edits in chronological order")


datesubmitted = st.selectbox(
    'Date submitted',
    (ordered))


st.write("Tabs to show user info related to edit selected")
#get_changes_csv(ordered[0])

if datesubmitted:

    tab1, tab2, tab3, tab4 = st.tabs(["Species Added", "User Info", "User Source", "User Edit History"])

    #tab1 methods
    for database in databases:
            if database["key"]==datesubmitted:
                path=database["Changes"]
    user_changes = pd.read_csv(path, encoding= 'unicode_escape', low_memory=False)
    tab1.write(user_changes)

    tab1.write("Displaying vertically")
    tab1.dataframe(user_changes.iloc[0], width=300)


    #tab2 methods
    for database in databases:
            if database["key"]==datesubmitted:
                author=database["Edited_By"]
                authorComment=database["User_Comment"]
    for user in users:
            if user["username"]==author:
                #tab2.write(((user["firstname"],user["surname"], user["key"])))
                authorName=user["firstname"]
                authorSurname = user["surname"] 
                authorEmail= user["key"]
                
    tab2.write("Author firstname: "+" "+authorName)
    tab2.write("Author surname: "+authorSurname)
    tab2.write("Author email: "+authorEmail)

    tab3.write("User comments: "+ " "+ authorComment)

    tab4.subheader("User edit history")
    tab4.write("This is tab 4")


    preview=st.checkbox("Preview new addition to current dataset")




    def preview_addition(df1,df2):
        #result = df1.append(df2, ignore_index=True).append(df3, ignore_index=True)
        
        proposed=df1.append(df2, ignore_index=True)
        last_row=proposed.iloc[-1]
        st.dataframe(proposed.style.applymap(lambda _: 'background-color: yellow', subset=pd.IndexSlice[last_row.name, :]))



    now=datetime.now()
    version=now.strftime("%d.%m.%Y-%H.%M.%S")
    path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"
    #path_end = version
    newPath=path_prefix+version+"-"+st.session_state['username']+"-approved"+".csv"

    #def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, 
    # species_affected, genus_affected, username, user_comment, status, reason_denied, approved_by, date_approved, current_database_path):
    #   """adding user"""
        #defining the email as the key
    #  return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, 
    # "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Approved_By":approved_by, "Date_Approved":date_approved, "Current Dataset":current_database_path })

    def create_new_dataset():
        newDataset=current.append(user_changes, ignore_index=True)
        newDataset.to_csv(newPath, index=False)
    
    #updates the status, 
    def update_GABiP():
        updates = {"Status":"Approved", "Reason_Denied":"n/a", "Approved_By":st.session_state['username'], "Date_Approved":str(now), "Current Dataset":newPath, "Dataset_Pre_Changes":latestds }
        metaData.update(updates, datesubmitted)

    if preview:
        newDataset=preview_addition(current, user_changes)
        col1,col2=st.columns(2)

        accept=col1.button("Approve Addition")
        reject=col2.button("Deny Addition")

                
        if accept:
            create_new_dataset()
            update_GABiP()
            st.write("GABiP updated!")
            
        if reject:
            reason=col2.text_area("Reasons for declining")
            confirmReject=col2.button("Confirm")
            if confirmReject:
                col2.write("Submission has been rejected")


