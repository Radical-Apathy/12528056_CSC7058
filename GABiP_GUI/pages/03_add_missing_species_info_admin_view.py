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

def add_bg_from_url():
       st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/1933861474.jpg");
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
                opacity: 0.1
                color: #ffffff; 
            }}
            </style>
            """,
            unsafe_allow_html=True
        )




add_bg_from_url() 

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


@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape', low_memory=False)
    return current_db


#get submissions for species info addition


pending=[]


def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="Information Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

submission_ordered=sorted(pending,reverse=True)


#------------------------------------------------------------USERS_DB DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

users_db=deta_connection.Base("users_db")

def get_all_users():
    res = users_db.fetch()
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

#-----------------------------------------------------------SESSION STATES---------------------------------------------------------------------#

#creating session state variables for each column in dataset
def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""

def create_session_states_source(dbColumns):
    for column in dbColumns:
        if [column+" source"] not in st.session_state:
           st.session_state[column+ "source"] =""

if 'image_ids' not in st.session_state:
        st.session_state['image_ids']=[]
#------------------------------------------------------------METHODS -----------------------------------------------------------------------------------------#

def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, decided_by, date_decided, current_database_path, user_sources, user_images):
     """adding user"""
     #defining the email as the key
     return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Decided_By":decided_by, "Decision_Date":date_decided, 
     "Dataset_In_Use":current_database_path, "User_Sources": user_sources, "User_Images": user_images })

#------------------------------------------------------------ADMIN SPECIES INFO ADDITION PAGE-----------------------------------------------------------------------------------------#

def new_information_review():
    current=load_latest()

    st.write("**New species Information in order of date submitted**")
    datesubmitted = st.selectbox(
        'Date submitted',
        (submission_ordered))
    
    for database in databases:
                if database["key"]==datesubmitted:
                    genus_added_to=database["Genus_Affected"]
                    species_added_to=database["Species_Affected"]
    
    #st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Information</strong></em></p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px; border: 2px solid green;background-color: green; padding: 10px;"><em><strong>Genus: {genus_added_to},      Species: {species_added_to}</strong></em></p>', unsafe_allow_html=True)
    

    def update_user_json(species_before, species_after):
        data = json.loads(species_before)
        new_keys_data = json.loads(species_after)

        for key, value in new_keys_data["0"].items():
            if key in data:
                data[key][str(species_index)] = value
        return data


    if datesubmitted:
        new_info_tab1, new_info_tab2, new_info_tab3, new_info_tab4, new_info_tab5, new_info_tab6 = st.tabs([ "Overview", "Information Breakdown", "Images Submitted", "Species Edit History","User Info", "User Comment"])
       
        #-------------------------------------------------------------information added display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    species_before=database["Dataset_Pre_Change"]
                    species_after=database["Changes"]
        
        before_jsonn=json.loads(species_before)
        species_index = list(before_jsonn['Order'].keys())[0]
        with new_info_tab1:
            tab1_col1, tab1_col2=st.columns(2)
        
        updated_species_json=json.dumps(update_user_json(species_before, species_after))
        tab1_col1.markdown("**Species Before**")
        tab1_col1.write(pd.read_json(species_before).iloc[0])
        tab1_col2.markdown("**Species After Addition**")
        tab1_col2.write(pd.read_json(updated_species_json).iloc[0])
        
        #-------------------------------------------------------------information sources display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    user_sources=database["User_Sources"]
        
        with new_info_tab2:
            tab2_col1, tab2_col2 = st.columns(2)
            tab2_col1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Information</strong></em></p>', unsafe_allow_html=True)
            tab2_col2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Source</strong></em></p>', unsafe_allow_html=True)
            sources_parsed=json.loads(user_sources)
            for key, value in sources_parsed.items():
                for inner_key, inner_value in value.items():
                    tab2_col1.markdown("***")
                    tab2_col1.markdown("**"+inner_key+"**")
                    tab2_col2.markdown("***")
                    tab2_col2.markdown("*"+inner_value+"*")
        #-------------------------------------------------------------image sources display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    user_images=database["User_Images"]
        

        image_folder_id = "1g_Noljhv9f9_YTKHEhPzs6xUndhufYxu"
        
        results = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(image_folder_id), fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            st.write('No files found.')
        else:
            for item in items:
                for value in user_images:
                  if item['id'] == value:
                    new_info_tab3.write(item['name'])
                    new_info_tab3.image(f"https://drive.google.com/uc?id={item['id']}", width=600)
            
    #-------------------------------------------------------------user info display--------------------------------------------------------------------#
    with new_info_tab5:

        for database in databases:
                if database["key"]==datesubmitted:
                    author=database["Edited_By"]
                    authorComment=database["User_Comment"]
        for user in users:
                if user["username"]==author:
                    #tab2.write(((user["firstname"],user["surname"], user["key"])))
                    first_name=user["firstname"]
                    surname = user["surname"] 
                    user_email= user["key"]
                    user_name=user['username']

    with new_info_tab5:
        tab5_col1, tab5_col2 = st.columns(2)
        tab5_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>First Name: </strong></em></p>', unsafe_allow_html=True)
        tab5_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Surname: </strong></em></p>', unsafe_allow_html=True)
        tab5_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Email: </strong></em></p>', unsafe_allow_html=True)
        tab5_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>User Name: </strong></em></p>', unsafe_allow_html=True)
        tab5_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Country: </strong></em></p>', unsafe_allow_html=True)
        tab5_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Acandemic Institute: </strong></em></p>', unsafe_allow_html=True)
        tab5_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{first_name}</em></p>', unsafe_allow_html=True)
        tab5_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{surname}</em></p>', unsafe_allow_html=True)
        tab5_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{user_email}</em></p>', unsafe_allow_html=True)
        tab5_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{user_name}</em></p>', unsafe_allow_html=True)


  
  
    
new_information_review()

