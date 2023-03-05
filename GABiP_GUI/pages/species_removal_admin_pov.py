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

def add_new_info_bg():
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




add_new_info_bg()

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


#@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape', low_memory=False)
    return current_db


#get submissions for species info addition

pending_edit_info=[]


current=load_latest()

def get_pending_edit_info():
    for database in databases:
        
            if database["Edit_Type"]=="Information Edit" and database["Status"] =="Pending":
                
             pending_edit_info.append(database["key"])

get_pending_edit_info()

new_edit_submissions=sorted(pending_edit_info,reverse=True)


#------------------------------------------------------------USERS_DB DATABASE CONNECTION-----------------------------------------------------------------------------------------#

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

#------------------------------------------------------------IMAGES DATABASE CONNECTION-----------------------------------------------------------------------------------------#
users_images=deta_connection.Base("user_images")

def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
     return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })

def get_all_user_images():
    res = users_images.fetch()
    return res.items
user_images=get_all_user_images()
#-----------------------------------------------------------SESSION STATES--------------------------------------------------------------------------------------------------------#

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

#------------------------------------------------------------SPECIES SEARCH-----------------------------------------------------------------------------------------#

@st.cache_data
def load_references():
    dfReferences = pd.read_csv('https://drive.google.com/uc?id=1h1UKe6xOy5C_maVOyGtbLCr4g0aH1Eek', encoding= 'unicode_escape')
    return dfReferences

@st.cache_data
def load_images():
    dfImages = pd.read_csv('https://drive.google.com/uc?id=1AfojhCdyKPk2HKCUyfXaVpnUZwWgBxwi', encoding= 'unicode_escape')
    return dfImages

dfReferences = load_references()
dfImages = load_images()




  #---------------------------------------------------------------NEW EDIT REVIEW SCREEN -------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------REMOVE SPECIES DISPLAY-----------------------------------------------------------------------------------------------------------------------------#
def remove_species_admin():
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr4_orig.jpg");
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


    now = datetime.now()
    pending_removal_info=[]
    def get_pending_removal_info():
        for database in databases:
            
                if database["Edit_Type"]=="Removal" and database["Status"] =="Pending":
                    
                  pending_removal_info.append(database["key"])

    get_pending_removal_info()

    removal_info_submissions=sorted(pending_removal_info,reverse=True)

    st.write("New species removal request in order of date submitted")

    datesubmitted = st.selectbox(
    'Date submitted',
    (removal_info_submissions))

    for database in databases:
        if database["key"]==datesubmitted:
            species=database["Species_Affected"]
            genus=database["Genus_Affected"]
        if database["Status"]=="Approved":
            decision_date=database["Decision_Date"]
            approved_by=database["Decided_By"]


    def check_species_existence_admin_end(species, genus):
          if genus.lower() not in current["Genus"].str.lower().values and species.lower() not in current["Species"].str.lower().values:
            return True

    
    #def approve_user(username, updates):
    #return users_db.update(updates, username)
    #approve_user(user["key"], updates={"approved": "True"})

    def update_repeat_request(key, updates):
        return database_metadata.update(updates, key)
    check_species_existence_admin_end(species, genus)
   
    if datesubmitted and  check_species_existence_admin_end(species, genus):
        st.write(f"{genus} {species} has already been removed. It was removed on {decision_date} by {approved_by} For more information, see Species Audit History")
        update_db_status=st.button("Remove from dropdown")
        if update_db_status:
                update_repeat_request(datesubmitted, updates={"Status": "Duplicate Removal Reuqest"})
                st.write("Request marked as duplicate and will no longer appear on dropdown")

    

    if datesubmitted and not check_species_existence_admin_end(species, genus):

        tab1, tab2, tab3= st.tabs(["Species to be Removed", "User Info", "User Comment"])

        #tab1 methods
        for database in databases:
                if database["key"]==datesubmitted:
                    newAdd=database["Changes"]
        
        user_changes= pd.read_json(newAdd)
        

        tab1.write("Species Info")
        tab1.dataframe(user_changes.iloc[0], width=300)
        


        #tab2 ------------user info
        with tab2:

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

        with tab2:
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

        with tab3:
            tab3.write(authorComment)


        
            

        now=datetime.now()
        version=now.strftime("%d.%m.%Y-%H.%M.%S")
        
        newPath=version+"-"+st.session_state['username']+"-approved"+".csv"

        def create_new_addition_dataset():
            proposed_removal=current.copy()
            proposed_removal.drop(user_changes.index[0], inplace=True)
            
            csv_bytes = io.StringIO()
            proposed_removal.to_csv(csv_bytes, index=False)
            csv_bytes = csv_bytes.getvalue().encode('utf-8')
    
            # upload bytes to Google Drive
            file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
            media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        
        #updates the status, 
        def update_GABiP():
            updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath, "Dataset_Pre_Change":latest_approved_ds }
            database_metadata.update(updates, datesubmitted)
        
        def reject_new_addition():
            updates = {"Status":"Denied", "Reason_Denied":reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds, "Dataset_Pre_Change":latest_approved_ds }
            database_metadata.update(updates, datesubmitted)

        preview=st.checkbox("Preview new updated dataset")
        #st.write(approvedordered)
        if preview:
            try:
                proposed_removal=current.copy()
                proposed_removal.drop(user_changes.index[0], inplace=True)
                st.dataframe(proposed_removal)
                
                col1,col2=st.columns(2)

                accept=col1.button("Approve Addition")
                reject=col2.button("Deny Addition")

                        
                if accept:
                    create_new_addition_dataset()
                    update_GABiP()
                    st.write("GABiP updated!")


            
                reason=col2.text_area("Reasons for declining", key='reason') 

                

                if reject and reason:           
                    reject_new_addition()
                    col2.write("Addition rejected")
                elif reject:
                    col2.warning("Please add a reason for rejection")
            except:
             st.write("User entered non numerical data in number fields. Unable to append new addition to current dataset")

        


remove_species_admin()

def latest_id_improval():
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

    #adding modified time to try and increase accuracy
    def get_latest_file_id(latest_approved_ds):
        
       query = "mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}' and name='{1}'".format(folder_id, latest_approved_ds)
       results = service.files().list(q=query, fields="nextPageToken, files(id, name, modifiedTime)", orderBy="modifiedTime desc").execute()
       items = results.get('files', [])

       if not items:
            st.write('No files found.')
       else:
            for item in items:
                if item['name'] == latest_approved_ds:
                    
                    return item['id']



    latest_id=get_latest_file_id(latest_approved_ds)

    st.write(latest_id)
    #@st.cache_data
    def load_latest():
        current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape', low_memory=False)
        return current_db


    #get submissions for species info addition

    pending_edit_info=[]


    current=load_latest()
    #st.write(approved)
    st.write(current)


#latest_id_improval()
#remove_species_admin()