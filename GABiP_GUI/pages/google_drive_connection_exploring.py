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



# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

drive_service = build("drive", "v3", credentials=creds)

#get all folders and file in drive



@st.cache
def load_dataset(url):
    dataset=pd.read_csv(google_url, encoding= 'unicode_escape')
    return dataset



#authenticate and build api drive
service = build("drive", "v3", credentials=creds)

file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"

request = service.files().get_media(fileId=file_id)
file = request.execute()



file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"
google_url = f"https://drive.google.com/uc?id={file_id}"
file_folder_url="https://drive.google.com/file/d/1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV/view?usp=sharing"
folder_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN/"
st.write("from google drive, csv must be unrestricted")
folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"
dataset=load_dataset(google_url)



#-----------------------------------------------------------------saving a new file to google drive folder----------------------------------------------------------------------#
create_new_csv=st.button("Create a new csv")

#--------------------------------------------working-------------------------------------------------------------#
# dataset.head()
# dataset.to_csv('datasethead.csv', index=False)
# file_metadata = {'name': 'datasethead.csv', 'parents': [folder_id], 'mimeType': 'application/vnd.ms-excel'}
# media = MediaFileUpload('datasethead.csv', mimetype='text/csv')
# file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#----------------------------------------------------------------------------------------------------------------#
now=datetime.now()
version=now.strftime("%d-%m-%Y-%H-%M-%S")
newPath=version+"pathtesting"+"-approved"+".csv"

#-----------------------------------------------------------working but saves it locally first---------------------#
# if create_new_csv:
#     dataset.to_csv(newPath, index=False)
#     file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'application/vnd.ms-excel'}
#     media = MediaFileUpload(newPath, mimetype='text/csv')
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     st.write("File saved, check google drive!")
  #................................................................................................................#
if create_new_csv:
    # write CSV content to bytes
    csv_bytes = io.StringIO()
    dataset.to_csv(csv_bytes, index=False)
    csv_bytes = csv_bytes.getvalue().encode('utf-8')
    
    # upload bytes to Google Drive
    file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
    media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    st.write("File saved, check google drive!")






st.write("Using pydrive to upload csv") #ref https://towardsdatascience.com/how-to-manage-files-in-google-drive-with-python-d26471d91ecd


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


st.write("Uploading without using pydrive")

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