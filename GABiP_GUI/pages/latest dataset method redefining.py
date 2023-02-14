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



# #@st.cache
# def load_dataset(url):
#     dataset=pd.read_csv(google_url, encoding= 'unicode_escape')
#     return dataset



#authenticate and build api drive
service = build("drive", "v3", credentials=creds)

file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"

request = service.files().get_media(fileId=file_id)
file = request.execute()



file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"
google_url = f"https://drive.google.com/uc?id={file_id}"

folder_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN/"
st.write("from google drive, csv must be unrestricted")
folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"
#dataset=load_dataset(google_url)


# create_new_csv=st.button("Create a new csv")
# now=datetime.now()
# version=now.strftime("%d-%m-%Y-%H-%M-%S")
# newPath=version+"pathtesting"+".csv"
# if create_new_csv:
#     # write CSV content to bytes
#     csv_bytes = io.StringIO()
#     dataset.to_csv(csv_bytes, index=False)
#     csv_bytes = csv_bytes.getvalue().encode('utf-8')
    
#     # upload bytes to Google Drive
#     file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
#     media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     st.write("File saved, check google drive!")

#folder_and_name="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN/06-02-2023-13.53.58-admin-approved.csv"
#from_google=load_dataset(folder_and_name)
#st.write(from_google)

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






#-----------------------------------------------------------------saving a new file to google drive folder----------------------------------------------------------------------#


#--------------------------------------------working-------------------------------------------------------------#
# dataset.head()
# dataset.to_csv('datasethead.csv', index=False)
# file_metadata = {'name': 'datasethead.csv', 'parents': [folder_id], 'mimeType': 'application/vnd.ms-excel'}
# media = MediaFileUpload('datasethead.csv', mimetype='text/csv')
# file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#----------------------------------------------------------------------------------------------------------------#


#-----------------------------------------------------------working but saves it locally first---------------------#
# if create_new_csv:
#     dataset.to_csv(newPath, index=False)
#     file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'application/vnd.ms-excel'}
#     media = MediaFileUpload(newPath, mimetype='text/csv')
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     st.write("File saved, check google drive!")
  #................................................................................................................#
 #ref https://towardsdatascience.com/how-to-manage-files-in-google-drive-with-python-d26471d91ecd


# import pandas as pd
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive

# # Authenticate and create PyDrive client
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth() # follow the authentication steps in the browser
# drive = GoogleDrive(gauth)



# # Convert DataFrame to CSV file in memory
# csv_file = dataset.to_csv(index=False)

# # Upload CSV file to Google Drive
# file = drive.CreateFile({'title': newPath})
# file.Upload() # Upload file to Google Drive
# file.SetContentString(csv_file) # Set the content of the file to the CSV data
# file.Upload() # Update the file with the CSV data


#st.write("Uploading without using pydrive")

# directtogoogledrive=st.button("Create directly to drive")

# if directtogoogledrive:
# # Convert DataFrame to CSV file in memory
#  csv_file = dataset.to_csv(index=False)
 
#  try:
#     # Upload CSV file to Google Drive
#      file_metadata = {'name': newPath, 'parents': [folder_id]}
#      media = googleapiclient.http.MediaIoBaseUpload(io.StringIO(csv_file), mimetype='text/csv')
#      file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#      st.write(f'File ID: {file.get("id")}')
#  except HttpError as error:
#      st.write(f'An error occurred: {error}')














# # Create a Google Authentication connection object
# scope = ['https://spreadsheets.google.com/feeds',
#          'https://www.googleapis.com/auth/drive']

# credentials = service_account.Credentials.from_service_account_info(
#                 st.secrets["gcp_service_account"], scopes = scope)
# client = Client(scope=scope,creds=credentials)


# #code to create google api service instance -ref https://www.youtube.com/watch?v=cCKPjW5JwKo

# #
# import streamlit as st