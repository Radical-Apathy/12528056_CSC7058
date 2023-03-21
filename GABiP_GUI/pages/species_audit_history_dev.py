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


#@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db


#get submissions for species info addition

pending_edit_info=[]

# try:
#     current=load_latest()
# except:
     
#     st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 30px;"><strong>***   Due to high traffic, page is temporarily unavailable. Please try again in 20 minutes. Time of error    ***</strong></p>', unsafe_allow_html=True)
#     sys.exit()

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

    dates_added=[]
    information_added=[]
    date_accepted=[]
    accepted_by=[]
    submitted_by=[]
    def approval_history():

        for database in  sorted (databases, key=lambda x: x["key"], reverse=True):
                    if database["Species_Affected"] == species_dropdown and database["Genus_Affected"]==genus_dropdown and database["Status"]=="Approved" and database["Edit_Type"]=="Information Addition":
                        dates_added.append(database['key'])
                        information_added.append(database["Changes"])
                        date_accepted.append(database["Decision_Date"])
                        accepted_by.append(database["Decided_By"])
                        submitted_by.append(database["Edited_By"])

     # changes_parsed=json.loads(species_after)
        property_added=[]
        values_added=[]
        def parse_changes(information_added):
            for info in information_added:
                if info != "image only":
                    
                    info_parsed=json.loads(info)
                    #information_added_col.write(info_parsed)
                    for key, value in info_parsed.items():
                        for inner_key, inner_value in value.items():
                            property=inner_key
                            property_added.append(property)
                            new_value=inner_value
                            values_added.append(new_value)
                            
                else:
                    property_added.append("N/A")
                    values_added.append("Image Added")
            return property_added, values_added





        add_tab, additions_tab, edit_tab, deletions_tab =st.tabs(["Species Added", "Data Addition", "Data Removals", "User Images"])

        with add_tab:
            st.write("addition tab")
        
        with additions_tab:
            parse_changes(information_added)
            property_added_col, information_added_col, date_added_col, date_accepted_col, submitted_by_col, acepted_by_col = st.columns(6)

            property_added_col.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Property</strong></em></p>',unsafe_allow_html=True)
            for property in property_added:
             property_added_col.write(property)
             #property_added_col.markdown("***")

            information_added_col.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Info Added</strong></em></p>',unsafe_allow_html=True)
          

            for value in values_added:
               information_added_col.write(value)
               #property_added_col.markdown("***")

            date_added_col.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Date Added</strong></em></p>',unsafe_allow_html=True)
            for date in dates_added:
                date_added_col.write(date)
                date_added_col.markdown("***")
            date_accepted_col.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Date Accepted</strong></em></p>',unsafe_allow_html=True)
            for dates in date_accepted:
             date_accepted_col.write(dates)
            submitted_by_col.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Submitted by</strong></em></p>',unsafe_allow_html=True)
            for submit in submitted_by:

             submitted_by_col.write(submit)

            acepted_by_col.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Accepted By</strong></em></p>',unsafe_allow_html=True)
            for accept in accepted_by:
             acepted_by_col.write(accept)

            additions_tab.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Alternative view with Dataframe</strong></em></p>',unsafe_allow_html=True)

           # df_view = pd.DataFrame({"Field": property_added,"Information Added": values_added, "Submitted By": submitted_by, "Date Submitted":dates_added, "Date Approved":date_accepted, "Approved By":accepted_by})
            df_view2 = pd.DataFrame({"Submitted By": submitted_by, "Date Submitted":dates_added, "Date Approved":date_accepted, "Approved By":accepted_by})
            additions_tab.dataframe(df_view2)
            

            parse_changes(information_added)
            # def create_expanders():
            #     for date in dates_added:
            #         for property in property_added:
            #          for value in values_added:
            #           expander = st.expander(date)
            #           expander.write(f"Field changed: {property}")
            #           expander.write(f"value added: {value}")
            # def create_expanders(date, property, value):
            #     expander = st.expander(date)
            #     expander.write(f"Field changed: {property}")
            #     expander.write(f"value added: {value}")
            # for date in dates_added:
            #     for property in property_added:
            #       for value in values_added:
            #         create_expanders(date, property, value)


            def create_expanders():
                # create a dictionary to store unique combinations of date, property, and value
                expander_dict = {}
                for i in range(len(dates_added)):
                    key = (dates_added[i], property_added[i], values_added[i], submitted_by[i], accepted_by[i], date_accepted[i])
                    if key not in expander_dict:
                        expander_dict[key] = []
                    expander_dict[key].append(i)
                
                # create an expander for each unique combination of date, property, and value
                for key, indices in expander_dict.items():
                    date, prop, val, sub, acc, dateacc = key
                    expander = st.expander(f"**DATE SUBMITTED** : {date}")
                    expander.write(f"Field changed: {prop}")
                    expander.write(f"Information added: {val}")
                    expander.write(f"Submitted by: {sub}")
                    expander.write(f"Approved by: {acc}" )
                    expander.write(f"Approved on: {dateacc}")
                    
            create_expanders()

            def create_expanders_no_dups():
                # create a dictionary to store unique combinations of date and submitted by
                expander_dict = {}
                for i in range(len(dates_added)):
                    key = (dates_added[i], submitted_by[i])
                    if key not in expander_dict:
                        expander_dict[key] = []
                    expander_dict[key].append((property_added[i], values_added[i], accepted_by[i], date_accepted[i]))

                # create an expander for each unique combination of date and submitted by
                for key, values in expander_dict.items():
                    date, sub = key
                    expander = st.expander(f"**DATE SUBMITTED** : {date}")
                    expander.write(f"Submitted by: {sub}")
                    for val in values:
                        prop, value, acc, dateacc = val
                        expander.write(f"Field changed: {prop}")
                        expander.write(f"Information added: {value}")
                        expander.write(f"Approved by: {acc}")
                        expander.write(f"Approved on: {dateacc}")

            additions_tab.write("No duplicates")
            create_expanders_no_dups()
            additions_tab.write(information_added)
            additions_tab.write(property_added)
            additions_tab.write(values_added)

            


    options=st.sidebar.radio("Options", ('Show Approval History','Show Rejection History'))
    if options=="Show Approval History":
        approval_history()
                       
    
def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, decided_by, date_decided, current_database_path, user_sources, user_images):
     """adding user"""
     #defining the email as the key
     return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Decided_By":decided_by, "Decision_Date":date_decided, 
     "Dataset_In_Use":current_database_path, "User_Sources": user_sources, "User_Images": user_images })

#species_audit_history()

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
reset_to_original_db()

