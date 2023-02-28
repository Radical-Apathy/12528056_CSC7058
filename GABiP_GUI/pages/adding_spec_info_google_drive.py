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
from io import BytesIO
from PIL import Image

#---------------------------------------------------------------------------Authentication Section----------------------------------------------------------------------------#


load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)



# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive


service = build("drive", "v3", credentials=creds)

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



@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape')#, low_memory=False)
    return current_db


file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"

request = service.files().get_media(fileId=file_id)
file = request.execute()



google_url = f"https://drive.google.com/uc?id={file_id}"

folder_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN/"
st.write("from google drive, csv must be unrestricted")
folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"

#--------------------------------------------------------------------------IMAGE DATABASE-----------------------------------------------------------#



#--------------------------------------------------------------------------EXPLORING IMAGE UPLOADING---------------------------------------------------------------------#


#https://drive.google.com/file/d/1OF4VQ6bMuc-d6OG2No24FT_1xsceOkZR/view?usp=sharing

latestdb=pd.read_csv("https://drive.google.com/uc?id=1OF4VQ6bMuc-d6OG2No24FT_1xsceOkZR", encoding= 'unicode_escape')

@st.cache_data

def load_images_csv():
    dfImages = pd.read_csv('https://drive.google.com/uc?id=1AfojhCdyKPk2HKCUyfXaVpnUZwWgBxwi', encoding= 'unicode_escape')
    return dfImages

images_csv=load_images_csv()
st.write(images_csv.head())

image_folder_id = "1g_Noljhv9f9_YTKHEhPzs6xUndhufYxu"

show_all_files=st.button("Show all files in folder")

if show_all_files:

    results = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(image_folder_id), fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])


    if not items:
        st.write('No files found.')
    else:
        st.write('Files:')
        for item in items:
            st.write('{0} ({1})'.format(item['name'], item['id']))


uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    st.image(uploaded_image)

#1ponSB-fWVG_UW0MYI5o0lpS0NX6wG-Br
 #https://drive.google.com/file/d/1qppGCkBHTqB59BN2c4pSt1YPLC5MGg3v/view?usp=sharing
 #https://drive.google.com/file/d/1B5ZFSm8RhtMKOKV9fe_AMBx_zUssYkeD/view?usp=sharing
 
submit_image=st.button("Submit image")

st.image("https://drive.google.com/uc?id=1ponSB-fWVG_UW0MYI5o0lpS0NX6wG-Br")

image_id=""
if submit_image and uploaded_image:
    bytes_data = uploaded_image.getvalue()
    try:
            file_metadata = {
                'name': uploaded_image.name,
                'parents': [image_folder_id],
                'mimeType': 'image/jpeg'  # change the MIME type to match your image format
            }
           #media = googleapiclient.http.MediaIoBaseUpload(user_image, mimetype='image/jpeg')
            media = MediaIoBaseUpload(io.BytesIO(bytes_data), mimetype='text/csv', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            image_id = file.get('id')
            st.success(f'Image uploaded!')
          
    except:
            st.error("Please try again. Be sure to check your file type is in the correct format")
    
st.write(image_id)
#st.write(get)
#----------------------------------------------------------------------------------------------------------------------------------#
# def add_new_image():
#             newDataset=current.append(user_changes, ignore_index=True)
#             csv_bytes = io.StringIO()
#             newDataset.to_csv(csv_bytes, index=False)
#             csv_bytes = csv_bytes.getvalue().encode('utf-8')
    
#             # upload bytes to Google Drive
#             file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
#             media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
#             file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()


