import streamlit as st
import pandas as pd
import numpy as np
import google.auth
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from datetime import datetime
from googleapiclient.http import MediaIoBaseUpload
import io
from deta import Deta
import csv
from dotenv import load_dotenv
import os

#---------------------------------------------------------------------------Authentication Section----------------------------------------------------------------------------#


load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)



# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

drive_service = build("drive", "v3", credentials=creds)

#get all folders and file in drive

#------------------------------------------------------------META DATABASE CONNECTION-----------------------------------------------------------------------------------------#
metaData=deta_connection.Base("database_metadata")

#fetching info from the database
def get_all_paths():
    res = metaData.fetch()
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


latestds=get_latest_ds(approvedordered[0])


@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape')#, low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated

#gets dates for new species additions needing approval
pending=[]


def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

ordered=sorted(pending,reverse=True)



service = build("drive", "v3", credentials=creds)

file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"

request = service.files().get_media(fileId=file_id)
file = request.execute()



file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"
google_url = f"https://drive.google.com/uc?id={file_id}"

folder_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN/"
st.write("from google drive, csv must be unrestricted")
folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"


#--------------------------------------------------------------------------refactoring get latest---------------------------------------------------------------------#
st.write("Showing dataset by csv id")

file_folder_url="https://drive.google.com/file/d/1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV/14.02.2023-09.59.39-admin-approved.csv"

google_prefix=f"https://drive.google.com/uc?id={file_id}"

latest_id="1JwpLPGeYf4yckMuVO22snAXxoptpMtp2"

#https://drive.google.com/file/d/1OF4VQ6bMuc-d6OG2No24FT_1xsceOkZR/view?usp=sharing

latestdb=pd.read_csv("https://drive.google.com/uc?id=1OF4VQ6bMuc-d6OG2No24FT_1xsceOkZR", encoding= 'unicode_escape')

#st.write(latestdb)

show_all_files=st.button("Show all files in folder")

if show_all_files:

    results = drive_service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(folder_id), fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])


    if not items:
        st.write('No files found.')
    else:
        st.write('Files:')
        for item in items:
            st.write('{0} ({1})'.format(item['name'], item['id']))


#14.02.2023-09.59.39-admin-approved.csv (1JwpLPGeYf4yckMuVO22snAXxoptpMtp2)
st.write("latest db approved name")

latest_approved_db=get_latest_ds(approvedordered[0])

#st.write(latestdb)

def get_latest_file_id(latest_approved_db):
     
     results = drive_service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(folder_id), fields="nextPageToken, files(id, name)").execute()
     items = results.get('files', [])

     if not items:
         st.write('No files found.')
     else:
        for item in items:
             if item['name'] == latest_approved_db:
                 
                 return item['id']

latest_id=get_latest_file_id(latest_approved_db)

st.write(latest_id)

#original dataset path https://drive.google.com/uc?id=1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV
st.write(pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape'))






