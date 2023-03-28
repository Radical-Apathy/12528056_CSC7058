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
import base64




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


def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, decided_by, date_decided, current_database_path, user_sources, user_images):
     """adding user"""
     #defining the email as the key
     return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Decided_By":decided_by, "Decision_Date":date_decided, 
     "Dataset_In_Use":current_database_path, "User_Sources": user_sources, "User_Images": user_images })

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

#https://drive.google.com/file/d/1q9u_1KSwdVq5R8ZGLjNG3dQKHZbBdzQU/view?usp=sharing

@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db


def load_latest_not_cached():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db

# try:
#      current=load_latest()
# except:
     
#      st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 30px;"><strong>***   Due to high traffic, page is temporarily unavailable. Please try again in 20 minutes. Time of error    ***</strong></p>', unsafe_allow_html=True)

# clutch_added_id="https://drive.google.com/file/d/1oASckevqEcCpxBoUva8EUdjPI3TIsinL/view?usp=sharing"
# hard_code_load=pd.read_csv(f"https://drive.google.com/uc?id=1q9u_1KSwdVq5R8ZGLjNG3dQKHZbBdzQU", encoding= 'unicode_escape')

# #st.write(hard_code_load)

#------------------------------------------------------------------------Trying to load to a github repository-------------------------------------------------------------------#

#hard_code_load.copy()
#https://github.com/Radical-Apathy/gabip_datasets

#https://drive.google.com/file/d/14Tld5pj6-UAQBl6zb-yT-Vrm2JgfDMWM/view?usp=sharing

# large_file=pd.read_csv(f"https://drive.google.com/uc?id=14Tld5pj6-UAQBl6zb-yT-Vrm2JgfDMWM", encoding= 'unicode_escape')

# large_file = large_file.apply(lambda x: x.str.strip() if x.dtype == "object" else x)



#https://drive.google.com/file/d/196Gn-ABF1jjjMWgdKA4SK8aOM8xiZbL3/view?usp=sharing
original_file=pd.read_csv(f"https://drive.google.com/uc?id=1s0sEqX_WANw_8Wo6UfxEzKxgO0Q194Ap", encoding= 'unicode_escape')
st.write(original_file.iloc[6912])
#http://localhost:8501/species_audit_history_dev


now=datetime.now()

#https://drive.google.com/file/d/1at5lruJiADW8hUNiLmioUHV2ntWGbPXo/view?usp=sharing

# add_as_blob=st.checkbox("Add as blob")

# bytesIO = io.BytesIO()
# current.to_csv(bytesIO, index=False)
# byte_array = bytesIO.getvalue()

#row = current.iloc[1652]
#st.write(row)
#st.write(row.dtypes)

# if add_as_blob:
#      st.write("before insert")
#      base64_bytes = base64.b64encode(byte_array)
#      base64_string = base64_bytes.decode('utf-8')
#      add_to_database(str(now), base64_string, "dataset pre change", "edit type", "species affected", "genus affected", "edited by", "user comment", "status", "reason denied", "decided by", "decision date", "current path", "user sources", "user images")
#      st.write("blob added")