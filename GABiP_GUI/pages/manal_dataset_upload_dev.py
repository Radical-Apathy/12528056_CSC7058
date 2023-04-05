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
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import io
import json
from io import StringIO


# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

service = build("drive", "v3", credentials=creds)

#------------------------------------------------------------DATABASE_METADATA DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

metaData=deta_connection.Base("database_metadata")

#------------------------------------------------------------ DATABASE_METADATA DATABASE METHODS-----------------------------------------------------------------------------------------#

def manual_dataset_upload():
 
   
 #-------------------------------------------------------------MANUAL UPLOAD METHODS----------------------------------------------------------------------------------------------#
  
  now=datetime.now()
  version=now.strftime("%d.%m.%Y-%H.%M.%S")
  folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"          
  newPath=version+"-"+st.session_state['username']+"-manual uploaded"+".csv"
  
  def create_new_updated_dataset_google():
                newDataset=dataset_uploader
                newDataset = newDataset.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                with io.BytesIO() as csv_buffer:
                    csv_string = newDataset.to_csv(index=False)
                    csv_buffer.write(csv_string.encode('utf-8'))
                    csv_buffer.seek(0)
                    for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                        # process each chunk as needed
                        pass
    
            # upload bytes to Google Drive
                file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
                media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

  def csv_converter(dataset_uploader):
       st.write("converts excel to csv")
 #-------------------------------------------------------------MANUAL UPLOAD UI---------------------------------------------------------#
  manual_upload_option=st.checkbox("Manually Upload a dataset")
  
  if manual_upload_option:
   st.warning("Uploading a dataset will over-ride the current most recent dataset...Are you sure you want to proceed?")
   dataset_uploader=st.file_uploader("Choose a CSV file", accept_multiple_files=True)

   if dataset_uploader is not None:
    try:
        # Get the first file uploader object from the list
        uploaded_file = dataset_uploader[1]
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Display the DataFrame in a Streamlit table
        st.write(df)
    except Exception as e:
        st.error(f'Error loading CSV file: {str(e)}')

   



manual_dataset_upload()
