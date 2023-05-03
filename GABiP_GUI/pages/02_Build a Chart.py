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

#getting the most recent approved csv file
#def get_latest():
 #   for database in databases:
  #   for i in date_time:
        
 #     if database["key"]== i and database["Status"] =="Approved":
 #       break
 #   return(database["Current Dataset"])

#path=get_latest()

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

@st.cache
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated




current=load_latest()

st.title("Interactive Chart")

st.write("Choose a chart type")

chartOptions=st.selectbox("Choose a chart type",('Scatter Chart', 'Bar Chart', 'Line Chart', 'Pie Chart'))

x_axis=st.selectbox("Select X value", options=current.columns)
y_axis=st.selectbox("Select Y value", options=current.columns)
z_axis=st.selectbox("Select Z Value", options=current.columns)
def dynamicChart(dataframe):
    if chartOptions == ('Scatter Chart'):
       # x_axis=st.selectbox("Select Xx value", options=dfFull.columns)
        #y_axis=st.selectbox("Select Yy value", options=dfFull.columns)
        plot=px.scatter(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)
    elif chartOptions==('Bar Chart'):
         plot=px.bar(dataframe, x=x_axis, y=y_axis)
         st.plotly_chart(plot)
    elif chartOptions==('Line Chart'):
        plot=px.line(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)
    elif chartOptions==('Pie Chart'):
        plot=px.pie(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)

    
   
(dynamicChart(current))







