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
import sys



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
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db


#get submissions for species info addition

pending_edit_info=[]

try:
     current=load_latest()
except:
     
     st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 30px;"><strong>***   Due to high traffic, page is temporarily unavailable. Please try again in 20 minutes. Time of error    ***</strong></p>', unsafe_allow_html=True)
     sys.exit()

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



#--------------------------------------------------------------GENERAL CHECK IMAGE METHODS----------------------------------------------------------------------------------------------#

#--------------------------------------------------------------NEW EDIT REVIEW SCREEN -------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def species_audit_history():
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr30l_orig.jpg");
                background-attachment: fixed;
                background-size: cover;
                background-position: 60.00% 64.97% ;
                opacity: 0.1
                color: #ffffff; 
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    add_bg_from_url()
  
    #creating dicitonaries from meta database


    

   #-----------------------------------------------------------------ADD SPECIES INFO MAIN PAGE-------------------------------------------------#
    headercol1, headercol2, headercol3=st.columns(3)
    headercol2.markdown('<p style="font-family:sans-serif; color:White; font-size: 30px;"><em><strong>Species Audit History</strong></em></p>', unsafe_allow_html=True)
    
    dbColumns=current.columns
    create_session_states(dbColumns)
    all_genus=[]
    def get_genus(species_dropdown):
        all_genus=current.loc[current["Species"]==species_dropdown]
        return all_genus


    additional_info=[]

    species_alphabetical=(sorted(current["Species"].drop_duplicates(), reverse=False))

    additional_info_sources=[]

    species_dropdown=st.selectbox("Select a species history to view: ", (species_alphabetical))

    species_genus=current.loc[current["Species"]==species_dropdown]

    genus_alphabetical=(sorted(current["Genus"].drop_duplicates(), reverse=False))

    genus_dropdown=st.selectbox("Select "+species_dropdown+ " Genus", species_genus["Genus"])

    species_results=current.loc[(current["Species"] == species_dropdown) & (current['Genus'] == genus_dropdown)]

    species_index=species_results.index[0]
    #now=datetime.now()
    #st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Current Data for{genus_dropdown} {species_dropdown} as of {str(now)}</strong></em></p>', unsafe_allow_html=True)
    
    def approval_history():
        
        species_addition_tab, additions_tab, edit_tab, deletions_tab,  images_added_tab, images_removed_tab =st.tabs(["Species Added", "Data Addition", "Data Edits","Data Removals", "Images Added", "Images Removed"])

        with species_addition_tab:
            st.write("addition tab")
        
        with additions_tab:
            dates_added=[]
            information_added=[]
            date_accepted=[]
            accepted_by=[]
            submitted_by=[]
            
            sources_added=[]
            
                
            

            for database in  sorted (databases, key=lambda x: x["key"], reverse=True):
                        if database["Species_Affected"] == species_dropdown and database["Genus_Affected"]==genus_dropdown and database["Status"]=="Approved" and database["Edit_Type"]=="Information Addition":
                            dates_added.append(database['key'])
                            information_added.append(database["Changes"])
                            sources_added.append(database["User_Sources"])
                            date_accepted.append(database["Decision_Date"])
                            accepted_by.append(database["Decided_By"])
                            submitted_by.append(database["Edited_By"])

            if len(dates_added)==0:
                st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No recorded additions for {genus_dropdown} {species_dropdown}</strong></em></p>', unsafe_allow_html=True)
                
            else:                    
                def display_addition_expanders(info, sources, dates, submitted_by, accepted_by, date_accepted):
                    for i, item in enumerate(info):
                        if item != "image only":
                                # Remove extra quotes around JSON string
                            json_str = item.replace('"{"', '{"').replace('"}"', '}"')
                            data = json.loads(json_str)
                            sources_json_str = sources[i].replace('"{"', '{"').replace('"}"', '}"')
                            sources_data = json.loads(sources_json_str)
                            with st.expander(f"**DATE SUBMITTED**: {dates[i]}"):
                                rows = []
                                for key, value in data["0"].items():
                                     sources_value = sources_data["0"].get(key, "")
                                     rows.append([key, value, sources_value])
                                df = pd.DataFrame(rows, columns=['Properties Added', 'Values Added', 'Sources'])
                                st.write(df)
                                st.write(f"**Submitted by**: {submitted_by[i]} ")
                                st.write(f"**Approved by**: {accepted_by[i]} ")
                                st.write(f"**Date Approved**: {date_accepted[i]} ")           

                

            
                display_addition_expanders(information_added, sources_added, dates_added, submitted_by, accepted_by, date_accepted)

        with edit_tab:
            information_edited=[]
            dates_edited=[]
            edit_sources_added=[]
            date_edit_accepted=[]
            edit_accepted_by=[]
            edit_submitted_by=[]
            original_values=[]

            for database in  sorted (databases, key=lambda x: x["key"], reverse=True):
                        if database["Species_Affected"] == species_dropdown and database["Genus_Affected"]==genus_dropdown and database["Status"]=="Approved" and database["Edit_Type"]=="Information Edit":
                            dates_edited.append(database['key'])
                            information_edited.append(database["Changes"])
                            original_values.append(database['Dataset_Pre_Change'])
                            edit_sources_added.append(database["User_Sources"])
                            date_edit_accepted.append(database["Decision_Date"])
                            edit_accepted_by.append(database["Decided_By"])
                            edit_submitted_by.append(database["Edited_By"])
            
            if len(dates_edited) == 0:
                st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No recorded edits for {genus_dropdown} {species_dropdown}</strong></em></p>', unsafe_allow_html=True)
            else:
                                                    

                def display_edit_expanders(info, sources, original_values, dates, submitted_by, accepted_by, date_accepted):
                    for i, item in enumerate(info):
                        if item != "image only":
                            # Remove extra quotes around JSON string
                            json_str = item.replace('"{"', '{"').replace('"}"', '}"')
                            data = json.loads(json_str)
                            sources_json_str = sources[i].replace('"{"', '{"').replace('"}"', '}"')
                            sources_data = json.loads(sources_json_str)
                            original_values_json_str=original_values[i].replace('"{"', '{"').replace('"}"', '}"')
                            original_data=json.loads(original_values_json_str)

                            
                            with st.expander(f"**DATE SUBMITTED**: {dates[i]}"):
                                rows = []
                                for key, value in data["0"].items():
                                    sources_value = sources_data["0"].get(key, "")
                                    original_value=original_data.get(key,"").get(str(species_index),"")
                                    #original_value = original_data.get(key, {}).get(species_index, "")
                                    rows.append([key, value,  original_value, sources_value,])
                                df = pd.DataFrame(rows, columns=['Properties Added', 'Values Added', 'Original Values','Sources', ])
                                st.write(df)
                                st.write(f"**Submitted by**: {submitted_by[i]} ")
                                st.write(f"**Approved by**: {accepted_by[i]} ")
                                st.write(f"**Date Approved**: {date_accepted[i]} ")

            

            

                display_edit_expanders(information_edited, edit_sources_added, original_values, dates_edited, edit_submitted_by, edit_accepted_by, date_edit_accepted)

        with deletions_tab:  
            
            dates_removed=[]
            information_removed=[]
            original_values=[]
            removal_reason=[]
            date_removal_accepted=[]
            removal_accepted_by=[]
            removal_submitted_by=[]

            for database in  sorted (databases, key=lambda x: x["key"], reverse=True):
                        if database["Species_Affected"] == species_dropdown and database["Genus_Affected"]==genus_dropdown and database["Status"]=="Approved" and database["Edit_Type"]=="Information Removal":
                            dates_removed.append(database['key'])
                            information_removed.append(database["Changes"])
                            original_values.append(database['Dataset_Pre_Change'])
                            removal_reason.append(database["User_Sources"])
                            date_removal_accepted.append(database["Decision_Date"])
                            removal_accepted_by.append(database["Decided_By"])
                            removal_submitted_by.append(database["Edited_By"])

            if len(dates_removed)==0:
                st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No recorded data removals for {genus_dropdown} {species_dropdown}</strong></em></p>', unsafe_allow_html=True)
            else:

                

                def display_removal_expanders(info, sources, original_values, dates, submitted_by, accepted_by, date_accepted):
                    for i, item in enumerate(info):
                        if item != "image only delete":
                            # Remove extra quotes around JSON string
                            json_str = item.replace('"{"', '{"').replace('"}"', '}"')
                            data = json.loads(json_str)
                            sources_json_str = sources[i].replace('"{"', '{"').replace('"}"', '}"')
                            sources_data = json.loads(sources_json_str)
                            original_values_json_str=original_values[i].replace('"{"', '{"').replace('"}"', '}"')
                            original_data=json.loads(original_values_json_str)

                            
                            with st.expander(f"**DATE SUBMITTED**: {dates[i]}"):
                                rows = []
                                for key, value in data["0"].items():
                                    sources_value = sources_data["0"].get(key, "")
                                    original_value=original_data.get(key,"").get(str(species_index),"")
                                    #original_value = original_data.get(key, {}).get(species_index, "")
                                    rows.append([key, original_value, sources_value,])
                                df = pd.DataFrame(rows, columns=['Properties Removed', 'Value Removed','Removal Reason', ])
                                st.write(df)
                                st.write(f"**Submitted by**: {submitted_by[i]} ")
                                st.write(f"**Approved by**: {accepted_by[i]} ")
                                st.write(f"**Date Approved**: {date_accepted[i]} ")

                display_removal_expanders(information_removed, removal_reason, original_values, dates_removed, removal_submitted_by, date_removal_accepted, date_removal_accepted)

        with images_added_tab:
            
            date_added=[]
            date_accepted=[]
            submitted_by=[]
            approved_by=[]
            images=[]
            

            for user_image in  sorted (user_images, key=lambda x: x["key"], reverse=True):
                            if user_image["Species"] == species_dropdown and user_image["Genus"]==genus_dropdown:
                                date_added.append(user_image['key'])
                                date_accepted.append(user_image['Decision_Date'])
                                submitted_by.append(user_image['Submitted_By'])
                                approved_by.append(user_image['Decided_By'])
                                images.append(user_image['Images'])
            if len(date_added)==0:
                 st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No user submitted images for {genus_dropdown} {species_dropdown}</strong></em></p>', unsafe_allow_html=True)
            else:

                def display_image_expanders(date_added, date_accepted, submitted_by, approved_by, images):
                 for i in range(len(date_added)):
                    with st.expander(f"**DATE SUBMITTED**: {date_added[i]}"):
                        if len(images)!=0:
                          for array in images:
                              for val in array:
                                  st.image(f"https://drive.google.com/uc?id={val}")

                        st.write(f"**Submitted by**: {submitted_by[i]} ")
                        st.write(f"**Approved by**: {approved_by[i]} ")
                        st.write(f"**Date Approved**: {date_accepted[i]} ")
                                        

            display_image_expanders(date_added, date_accepted, submitted_by, approved_by, images)






            
            


    options=st.sidebar.radio("Options", ('Show Approval History','Show Rejection History'))
    if options=="Show Approval History":
        approval_history()
                       
    

species_audit_history()

def reset_to_original_db():

    now=datetime.now()
    add_blank_slate=st.checkbox("Add original data set")
    if add_blank_slate:
        add_to_database(str(now), "n/a", "n/a", "Original", "n/a", "n/a", "n/a", "n/a", "Approved", "n/a", "n/a", str(now), "dataset_clean", "n/a", "n/a"  )
        st.write("current db reset to original dataset")

    # st.write(approvedordered[0])
    latest_id="196Gn-ABF1jjjMWgdKA4SK8aOM8xiZbL3"
    st.write(latest_id)
    clean=pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape', low_memory=False)
    st.dataframe(clean)
#reset_to_original_db()

