from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from st_aggrid import AgGrid
#from io import StringIO
from PIL import Image
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
import io

def add_bg_from_url():
       st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/1933861474.jpg");
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
                opacity: 0.1
                color: #ffffff; 
            }}
            </style>
            """,
            unsafe_allow_html=True
        )




add_bg_from_url() 

#------------------------------------------------------------GOOGLE DRIVE CONNECTION---------------------------------------------------------------------------------#
# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

service = build("drive", "v3", credentials=creds)

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


latest_approved_ds=get_latest_ds(approvedordered[0])

folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"

def get_latest_file_id(latest_approved_ds):
     
     results = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(folder_id), fields="nextPageToken, files(id, name)").execute()
     items = results.get('files', [])

     if not items:
         st.write('No files found.')
     else:
        for item in items:
             if item['name'] == latest_approved_ds:
                 
                 return item['id']



latest_id=get_latest_file_id(latest_approved_ds)


@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape', low_memory=False)
    return current_db


@st.cache_data
def load_full():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull
def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated




#------------------------------------------------------------USERS_DB DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

users_db=deta_connection.Base("users_db")

def get_all_users():
    res = users_db.fetch()
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

#-----------------------------------------------------------SESSION STATES---------------------------------------------------------------------#

#creating session state variables for each column in dataset
def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""

def create_session_states_source(dbColumns):
    for column in dbColumns:
        if [column+" source"] not in st.session_state:
           st.session_state[column+ "source"] =""

if 'image_ids' not in st.session_state:
        st.session_state['image_ids']=[]
#------------------------------------------------------------METHODS -----------------------------------------------------------------------------------------#

def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, decided_by, date_decided, current_database_path, user_sources, user_images):
     """adding user"""
     #defining the email as the key
     return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Decided_By":decided_by, "Decision_Date":date_decided, 
     "Dataset_In_Use":current_database_path, "User_Sources": user_sources, "User_Images": user_images })





@st.cache_data
def load_references():
    dfReferences = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/Reference_List.csv', encoding= 'unicode_escape', low_memory=False)
    return dfReferences

@st.cache_data
def load_images():
    dfImages = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/image_database.csv', encoding= 'unicode_escape', low_memory=False)
    return dfImages

dfReferences = load_references()
dfImages = load_images()



#------------------------------------------------------------ADMIN SPECIES INFO ADDITION PAGE-----------------------------------------------------------------------------------------#


          
    
        

   


  
  
    


