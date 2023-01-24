import streamlit_authenticator as stauth
import streamlit as st
#import db_connection as db
import smtplib
import ssl
from email.mime.text import MIMEText # to enable html stuff with https://realpython.com/python-send-email/#sending-your-plain-text-email
from email.mime.multipart import MIMEMultipart
import pandas as pd
import numpy as np
import os
from deta import Deta
import csv
from dotenv import load_dotenv
from datetime import datetime
import json
st.set_page_config(page_icon='amphibs.jpeg')


#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

database_metadata=deta_connection.Base("database_metadata")

#------------------------------------------------------------metadata METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = database_metadata.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=sorted([database["Status"] for database in databases])
paths = [database["Dataset_In_Use"] for database in databases]
edit_type=[database["Edit_Type"] for database in databases]
changes=[database["Changes"] for database in databases]

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
            return database["Dataset_In_Use"]


latestds=get_latest_ds(approvedordered[0])

#method to select edits that are new species addition and pending
pending=[]

#gets dates for new species additions needing approval
def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

ordered=sorted(pending,reverse=True)


@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape', low_memory=False)
    return current_db


@st.cache
def load_full():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull
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


#----------------------------------------------------------------EXPLORING IN JSON FORMAT------------------------------------------------------------#

datacsv=load_full()

#converting the full csv to json 

#st.write("Results as json orient records")
#    resultsjsonorient=results.to_json(orient='records')
#    st.write(resultsjsonorient)
#    st.write("Results as json orient columns")
#    resultsjsoncols=results.to_json(orient='columns')
#    st.write(resultsjsoncols)
#    st.write("Results as json orient index")
#    resultsjsonindex=results.to_json(orient='index')
#    st.write(resultsjsonindex)
#    st.write("Getting json data ")
#    st.write(resultsjsoncols)


fulldatasetjson=datacsv.to_json(orient='columns')
alfrediInfo=datacsv.groupby("Species").get_group("alfredi")
speciesInfo=datacsv.groupby("Species").get_group("coppingeri")

st.write("Dataframe for coppingeri - 'speciesInfo=datacsv.groupby('Species').get_group('coppingeri')' ")
st.write(speciesInfo)
#st.write(datacsv.info())

speciesjsonrecs=speciesInfo.to_json(orient='records')
speciesjsoncols=speciesInfo.to_json(orient='columns')
speciesjsonindex=speciesInfo.to_json(orient='index')
speciesinfojson=speciesInfo.to_json()
speciesinfodict=speciesInfo.to_dict()

jsonfullcsv=st.checkbox("Convert csv to a json file - speciesjsoncols=speciesInfo.to_json(orient='columns')")
if jsonfullcsv:
    #st.write("no orient specified")
    #speciesjson=speciesInfo.to_json()
    #st.write(speciesjson)
    #st.write("orient index")
    #st.write(speciesjsonindex)
    #st.write("orient columns")
    st.write(speciesjsoncols)
    #st.write("orient records")
    #st.write(speciesjsonrecs)

showpythonobject=st.checkbox("Show as a python object - 'pythonobject=json.loads(speciesjsoncols)'")

pythonobject=json.loads(speciesjsoncols)

if showpythonobject:
#converting json into a python object
    st.write("as a python object")
    pythonobject=json.loads(speciesjsoncols)

    st.write(pythonobject)


def append_json_todf(df1, json):
    json_to_df=pd.read_json(json, orient="index")
    newdf=df1.append(json_to_df)

convertjsontodf=st.checkbox("Convert json to a pandas dataframe")

if convertjsontodf:
   st.write("json to df -  jsontodf= pd.read_json(speciesjsoncols)")
   #revertedback= pd.read_json(speciesjsoncols, orient="columns")
   jsontodf= pd.read_json(speciesjsoncols)
   st.write(jsontodf)
   #st.write(revertedback.dtypes)
   st.write("merged - merged=alfrediInfo.append(jsontodf)")
   merged=alfrediInfo.append(jsontodf)
   st.write(merged)

def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, 
                    user_comment, status, reason_denied, approved_by, date_approved, current_database_path):
    """adding user"""
    #defining the email as the key
    return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, 
    "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, 
    "Reason_Denied":reason_denied, "Decided_By":approved_by, "Decision_Date":date_approved, "Dataset_In_Use":current_database_path })

addtodb=st.checkbox("Add to db")

#add_to_database(str(now), newPath, get_approved(), "New Species Addition", st.session_state["Species"], 
# st.session_state["Genus"], st.session_state["username"], 
# st.session_state["comment"], "Pending", "n/a", "n/a", "n/a", get_approved())
now=datetime.now()
if addtodb:
   #add_to_database(str(now), speciesjsoncols, "currentDB", "json test 2", "json test 2", "Alfredi", "Alfredi", "col ui", "jsontest", "Pending", "n/a",
   #  "n/a", "n/a ")
   #add_to_database(str(now), fulldatasetjson, "a database", "New Species Addition", 
    #"jsonallspecies", "jsonallgenus", "admin", "full db in json", "Pending", "n/a", "n/a", "n/a", "a database")

   st.write(" comment out ")


fetchfromdb=st.checkbox("Fetch speciesjsoncols from db")

if fetchfromdb:
    "speciesjsoncols retrieved from database"
#2023-01-23 10:03:16.758975
    for database in databases:
                    if database["User_Comment"]=="speciesjsoncols":
                        fromdb=database["Changes"]
    st.write(fromdb)
    
    "changed to a dataframe - fromjsondbtodf= pd.read_json(fromdb) no orient"

    #"adding brackets"
    #withbrackets="["+fromdb+"]"
    #st.write(withbrackets)
    fromjsondbtodf= pd.read_json(fromdb)
    st.write((fromjsondbtodf))
    #st.write(speciesdf)
    "merged from db - mergedfromdb=alfrediInfo.append(fromjsondbtodf)"
    mergedfromdb=alfrediInfo.append(fromjsondbtodf)
    st.write(mergedfromdb)


speciesaddedfromui=st.checkbox("Species json from add species UI")
#speciesjsoncols blank test
if speciesaddedfromui:
    for database in databases:
                    if database["User_Comment"]=="merge sanity":
                        fromdbui=database["Changes"]
    fromjsondbuitodf= pd.read_json(fromdbui)
    st.write((fromjsondbuitodf))
    #st.write(speciesdf)
    "merged from db - mergedfromdb=alfrediInfo.append(fromjsondbtodf)"
    mergedfromdbui=alfrediInfo.append(fromjsondbuitodf)
    st.write(mergedfromdbui)
    

    
    
