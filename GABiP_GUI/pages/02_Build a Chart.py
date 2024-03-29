import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly_express as px
import cufflinks as cf
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from deta import Deta
import csv
from dotenv import load_dotenv


# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

#authenticate and build api drive
service = build("drive", "v3", credentials=creds)


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
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated


def background():
        st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/frog2_orig.jpg");
                        background-attachment: fixed;
                        background-size: cover;
                        background-position: 80% center;
                        opacity: 0.1
                        color: #ffffff; 
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

background()

current=load_latest()

st.title("Interactive Chart")


chartOptions=st.selectbox("Choose a chart type",('Scatter Chart', 'Bar Chart', 'Line Chart'))

x_axis=st.selectbox("Select X value", options=current.columns)
y_axis=st.selectbox("Select Y value", options=current.columns)

def dynamicChart(dataframe):
    if chartOptions == ('Scatter Chart'):
       
        plot=px.scatter(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)
    elif chartOptions==('Bar Chart'):
         plot=px.bar(dataframe, x=x_axis, y=y_axis)
         st.plotly_chart(plot)
    elif chartOptions==('Line Chart'):
        plot=px.line(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)
    
    
   
(dynamicChart(current))







