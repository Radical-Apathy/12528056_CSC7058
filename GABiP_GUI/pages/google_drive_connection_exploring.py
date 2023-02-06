import streamlit as st
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from gspread_pandas import Spread,Client
from datetime import datetime
import io



# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

drive_service = build("drive", "v3", credentials=creds)

# # Get a list of the user's files
# results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
# items = results.get("files", [])

# # Display the results in Streamlit
# for item in items:
#     st.write(f"{item['name']} ({item['id']})")


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
folder_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"
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
version=now.strftime("%d.%m.%Y-%H.%M.%S")

        #path_end = version
newPath=version+"pathtesting"+"-approved"+".csv"

if create_new_csv:
    # Save the DataFrame as a CSV file in Google Drive
    st.write(newPath)
    dataset.head()
    dataset.to_csv(newPath, index=False)
    file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'application/vnd.ms-excel'}
    media = MediaFileUpload(newPath, mimetype='text/csv')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    

    st.write("File saved, check google drive!")
  

filesaved_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN/dataset_clean.csv"

readtest=load_dataset(filesaved_url)
st.write("Reading saved file from google drive")
st.write(readtest)



























# # Create a Google Authentication connection object
# scope = ['https://spreadsheets.google.com/feeds',
#          'https://www.googleapis.com/auth/drive']

# credentials = service_account.Credentials.from_service_account_info(
#                 st.secrets["gcp_service_account"], scopes = scope)
# client = Client(scope=scope,creds=credentials)


# #code to create google api service instance -ref https://www.youtube.com/watch?v=cCKPjW5JwKo

# #
# import streamlit as st