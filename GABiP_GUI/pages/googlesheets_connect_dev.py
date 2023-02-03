from re import search
import streamlit as st
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from gspread_pandas import Spread,Client
#from gspread_pandas import Spread, Client
from shillelagh.backends.apsw.db import connect
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_icon='amphibs.jpeg')

#set up a connection object

# Create a Google Authentication connection object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
client = Client(scope=scope,creds=credentials)
spreadsheetname = "GABiP-December"
spread = Spread(spreadsheetname,client = client)

# Check the connection
st.write(spread.url)
#url="https://docs.google.com/spreadsheets/d/1PCcg_kCxu3_ICk_wlISC9WjyRm6l1BD8i24G1SrEmG4/edit#gid=246960271"
#path="https://drive.google.com/uc?id="+url.split('/')[-2]
#forcsv = pd.read_csv(path)

#st.write(forcsv.head())

sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()

# Functions 
@st.cache()
# Get our worksheet names
def worksheet_names():
    sheet_names = []   
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)  
    return sheet_names

# Get the sheet as dataframe
def load_the_spreadsheet(spreadsheetname):
    worksheet = sh.worksheet(spreadsheetname)
    df = pd.DataFrame(worksheet.get_all_records())
    return df


sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()

# Functions 
@st.cache()
# Get our worksheet names
def worksheet_names():
    sheet_names = []   
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)  
    return sheet_names

# #folder link
# folder_link="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"
# file_name="dataset_clean.csv"
# full_link=folder_link + "/" + file_name
#gooogle_drive_link="https://drive.google.com/file/d/1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"#/dataset_clean.csv"

# #sheet link
# sheetLink="https://docs.google.com/spreadsheets/d/1PCcg_kCxu3_ICk_wlISC9WjyRm6l1BD8i24G1SrEmG4/edit#gid=246960271"

# #-----------reddit attempt------------#

# sheet_id = "https://docs.google.com/spreadsheets/d/1PCcg_kCxu3_ICk_wlISC9WjyRm6l1BD8i24G1SrEmG4/edit#gid=246960271"
# sheet_name = "dataset_clean"

# # df_test=pd.read_csv(full_link)

@st.cache
def load_dataset(url):
    dataset=pd.read_csv(google_url, encoding= 'unicode_escape')
    return dataset



file_id = "1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV"
google_url = f"https://drive.google.com/uc?id={file_id}"
#gooogle_drive_link=
file_folder_url="https://drive.google.com/file/d/1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV/view?usp=sharing"
folder_url="https://drive.google.com/drive/u/1/folders/1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"
st.write("from google drive")

from_google=pd.read_csv(google_url, encoding= 'unicode_escape')#, low_memory=False))
st.write(from_google)

dataset=load_dataset(google_url)
st.write(dataset)