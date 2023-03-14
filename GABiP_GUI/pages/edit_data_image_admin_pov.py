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


st.set_page_config(page_icon='amphibs.jpeg')

# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

service = build("drive", "v3", credentials=creds)


#------------------------------------------------------------DATABASE CONNECTIONS-----------------------------------------------------------------------------------------#

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

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated

try:
     current=load_latest()
except HttpError as error:
     st.write(f"An HTTP error {error.resp.status} occurred: {error.content}")
except RefreshError:
        st.write("The credentials could not be refreshed.")
except Exception as error:
        st.write(f"An error occurred: {error}")
        exit()
        




#current=load_latest()

pending_new_info=[]
def get_pending_new_info():
    for database in databases:
        
            if database["Edit_Type"]=="Information Addition" and database["Status"] =="Pending":
                
             pending_new_info.append(database["key"])

get_pending_new_info()

new_info_submissions=sorted(pending_new_info,reverse=True)

pending_edit_info=[]






#------------------------------------------------------------IMAGES DATABASE CONNECTION-----------------------------------------------------------------------------------------#
users_images=deta_connection.Base("user_images")

def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
     return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })

def get_all_user_images():
    res = users_images.fetch()
    return res.items

approved_user_images=get_all_user_images()


#------------------------------------------------------------MAIN INFORMATION ADDITION PAGE---------------------------------------------------------------------------------------#
def information_edit_review():
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

    #loading background image
    add_new_info_bg()
    #current=load_latest()
    
    def get_pending_edit_info():
      for database in databases:
        
             if database["Edit_Type"]=="Information Edit" and database["Status"] =="Pending":
                
              pending_edit_info.append(database["key"])

    get_pending_edit_info()

    new_edit_submissions=sorted(pending_edit_info,reverse=True)
    #current=load_latest()
    st.write("New species edits in order of date submitted")
    datesubmitted = st.selectbox(
    'Date submitted',
    (new_edit_submissions))

    
    
    for database in databases:
                if database["key"]==datesubmitted:
                    genus_added_to=database["Genus_Affected"]
                    species_added_to=database["Species_Affected"]
    
    #st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Information</strong></em></p>', unsafe_allow_html=True)
    
    

    


    if datesubmitted:
        st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px; border: 2px solid green;background-color: green; padding: 10px;"><em><strong>Genus: {genus_added_to}      Species: {species_added_to}</strong></em></p>', unsafe_allow_html=True)
        def update_user_json(species_before, species_after):
            data = json.loads(species_before)
            new_keys_data = json.loads(species_after)

            for key, value in new_keys_data["0"].items():
                if key in data:
                    data[key][str(species_index)] = value
            return data


        new_info_tab1, new_info_tab2, new_info_tab3, new_info_tab5, new_info_tab6= st.tabs([ "Overview", "Information Breakdown", "Images Submitted","User Info", "User Comment"])
        
        #-------------------------------------------------------------information added display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    species_before=database["Dataset_Pre_Change"]
                    species_after=database["Changes"]
                    user_images=database["User_Images"]
        
        if species_before=="image only edit":
             before_jsonn="image only edit"
        else:
             before_jsonn=json.loads(species_before)
             species_index = list(before_jsonn['Order'].keys())[0]
             changes_parsed=json.loads(species_after)
        
        def list_fields():
            
            for key, value in changes_parsed.items():
                for inner_key, inner_value in value.items():
                    tab1_col1.markdown(inner_key)

               
        image_count=len(user_images)
        
        with new_info_tab1:
            tab1_col1, tab1_col2=st.columns(2)
        tab1_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>Information Added</em></p>', unsafe_allow_html=True)
        if species_after=="image only edit":
             tab1_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>Image only editted</em></p>', unsafe_allow_html=True)

        else:
             list_fields()
        tab1_col2.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>Number of Images Added</em></p>', unsafe_allow_html=True)
        tab1_col2.write(f"{image_count} images have been added")
        

        
               
                
        #-------------------------------------------------------------information breakdown display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    user_sources=database["User_Sources"]

        user_approved_images=[]          
        for approved_image in  sorted (approved_user_images, key=lambda x: x["key"], reverse=True):
                    if approved_image["Species"] == species_added_to and approved_image["Genus"]==genus_added_to:
                        if approved_image['Images']:
                            user_approved_images.append(approved_image['Images'])
                            

        
        with new_info_tab2:
            tab2_col1, tab2_col2, tab2_col3, tab2_col4 = st.columns(4)
            
            tab2_col2.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Breakdown</strong></em></p>', unsafe_allow_html=True)
          
            if species_after=="image only edit":
                tab2_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Current Image for {genus_added_to} {species_added_to}</strong></em></p>', unsafe_allow_html=True)
                if len(user_approved_images)==0:
                     st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No Current Images for {genus_added_to} {species_added_to}</strong></em></p>', unsafe_allow_html=True)
                else:
                         
                    for image in range(len(user_approved_images)):
                            st.image(f"https://drive.google.com/uc?id={user_approved_images[image][0]}")
                            break
                
            else:
                    new_info_tab2.markdown("**Reminder: If there exists a current value, then an addition has been made in the past and verified. Please check with Species Audit History before deciding**")
                    sources_parsed=json.loads(user_sources)
                    changes_parsed=json.loads(species_after)
                    original_parsed=json.loads(species_before)
                    
                    species_index = list(before_jsonn['Order'].keys())[0]
                
                    
                    def get_current_values(species_after, species_before):
                     changed_fields_current_data = json.loads(species_after)
                     current_data = json.loads(species_before)

                     for key in changed_fields_current_data["0"].keys():
                            if key in current_data:
                                changed_fields_current_data["0"][key] = current_data[key][str(species_index)]
                     return json.dumps(changed_fields_current_data)
                        
                
                    

                    changed_fields_current_data=json.loads(get_current_values(species_after, species_before))
                
                
                    source_rows=[]
                    source_values=[]
                    new_values=[]
                    current_values=[]

                    for key, value in sources_parsed.items():
                        for inner_key, inner_value in value.items():
                            source_row=inner_key
                            source_rows.append(source_row)
                            source_value=inner_value
                            source_values.append(source_value)
                    
                    for key, value in changes_parsed.items():
                        for inner_key, inner_value in value.items():
                            new_value=inner_value
                            new_values.append(new_value)

                    for key, value in changed_fields_current_data.items():
                        for inner_key, inner_value in value.items():
                            current_value=inner_value
                            current_values.append(current_value)
                    
                    df = pd.DataFrame({"Information": source_rows,"Current Value": current_values, "Proposed Values": new_values, "Sources": source_values })
                    
                    
                    st.dataframe(df)
                   
                    if len(user_approved_images)==0:
                     st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No Images for {genus_added_to} {species_added_to}</strong></em></p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Current Image</strong></em></p>', unsafe_allow_html=True)
                        for image in range(len(user_approved_images)):
                         st.image(f"https://drive.google.com/uc?id={user_approved_images[image][0]}")
                         break
            

                    
        #-------------------------------------------------------------image sources display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    user_images=database["User_Images"]
        
        image_count=len(user_images)
        approved_images=[]

        image_folder_id = "1g_Noljhv9f9_YTKHEhPzs6xUndhufYxu"
        with new_info_tab3:
            tab3_col1,tab3_col2,tab3_col3=st.columns(3)
        
        if image_count <1:
            new_info_tab3.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>No Images Submitted</em></p>', unsafe_allow_html=True)

        
            
            
        else:
            
            tab3_col1,tab3_col2,tab3_col3=st.columns(3)
            results = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(image_folder_id), fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
             
            new_info_tab3.write("***")
            for item in items:
                for value in user_images:
                    if item['id'] == value:
                        #with new_info_tab3.form(item['name']):
                            new_info_tab3.image(f"https://drive.google.com/uc?id={item['id']}", width=600)
                            accept_image = new_info_tab3.checkbox(f"Accept image {item['id']}")
                            reject_image = new_info_tab3.checkbox(f"Deny image {item['id']}")
                            if accept_image and reject_image:
                                    new_info_tab3.error("Warning! Both options have been selected. Please review decision")
                            elif accept_image:
                                approved_images.append(item['id'])

                            new_info_tab3.write("***")
            
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
    
     #-------------------------------------------------------------user comment display--------------------------------------------------------------------#
        with new_info_tab6:
            new_info_tab6.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Additional Comments: </strong></em></p>', unsafe_allow_html=True)
            new_info_tab6.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{authorComment}</em></p>', unsafe_allow_html=True)
            
    
        st.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><strong>*****************************************************************************************</strong></p>', unsafe_allow_html=True)

        preview_updated_dataset=st.checkbox("**View updated dataset **")

     #-------------------------------------------------------------preview dataset and decide --------------------------------------------------------------------#
    
        now=datetime.now()
        version=now.strftime("%d.%m.%Y-%H.%M.%S")
            
        newPath=version+"-"+st.session_state['username']+"-approved"+".csv"

        def create_new_updated_dataset_google():
                newDataset=updated_db
                csv_bytes = io.StringIO()
                newDataset.to_csv(csv_bytes, index=False)
                csv_bytes = csv_bytes.getvalue().encode('utf-8')
        
                # upload bytes to Google Drive
                file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
                media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    
        def update_GABiP():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)
        def update_GABiP_image():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
         return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })
        
        def reject_new_addition():
                updates = {"Status":"Denied", "Reason_Denied":reject_new_info_reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        if preview_updated_dataset and species_before=="image only edit":
            st.write(species_added_to)
            preview_new=True
            if preview_new:
                
                # st.dataframe(updated_db)
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Image")
                reject_information=pre_col3.button("Deny Image")
                reject_new_info_reason=pre_col3.text_area("Reasons for rejection for user")
                st.write(approved_images)

                if accept_information:
                        #create_new_updated_dataset_google() #<-------- working
                        update_GABiP_image()
                        
                        add_to_image_db(datesubmitted, genus_added_to, species_added_to, user_name, str(now), st.session_state['username'], approved_images )#<------working
                        pre_col1.write("Image Added")
                if reject_information and reject_new_info_reason:
                            reject_new_addition()
                            pre_col3.write("Reason sent to user")
                elif reject_information:
                        pre_col3.warning("Please add a reason for rejection for user to review")

        elif preview_updated_dataset and approved_images:
                
                updated_db=current.copy()
                try:
                    
                    updated_json=json.dumps(update_user_json(species_before, species_after))
                    updated_row=pd.read_json(updated_json)
                    updated_db.loc[int(species_index)] =(updated_row.loc[int(species_index)])
                    preview_new=True
                except:
                 st.error("Something went wrong. Please check the user has submitted numerical data if fields are numerical")
                 preview_new=False

                st.write("aproved images length second elif") 
                st.write(len(approved_images))
                st.dataframe(updated_db)
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Addition")
                reject_information=pre_col3.button("Deny Addition")
                reject_new_info_reason=pre_col3.text_area("Reasons for rejection for user")

                if accept_information:
                        create_new_updated_dataset_google() #<-------- working
                        update_GABiP()
                        
                        add_to_image_db(datesubmitted, genus_added_to, species_added_to, user_name, str(now), st.session_state['username'], approved_images )#<------working
                        pre_col1.write("GABiP updated!")
                if reject_information and reject_new_info_reason:
                            reject_new_addition()
                            pre_col3.write("Reason sent to user")
                elif reject_information:
                        pre_col3.warning("Please add a reason for rejection for user to review")
        elif preview_updated_dataset and not approved_images:
                
                
                try:
                    updated_db=current.copy()
                    updated_json=json.dumps(update_user_json(species_before, species_after))
                    updated_row=pd.read_json(updated_json)
                    updated_db.loc[int(species_index)] =(updated_row.loc[int(species_index)])
                    preview_new=True
                except:
                 st.error("Something went wrong. Please check the user has submitted numerical data if fields are numerical")
                 preview_new=False

                st.write("aproved images length last elif") 
                st.write(len(approved_images))
                st.dataframe(updated_db)
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Addition")
                reject_information=pre_col3.button("Deny Addition")
                reject_new_info_reason=pre_col3.text_area("Reasons for rejection for user")

                if accept_information:
                        create_new_updated_dataset_google() #<-------- working
                        update_GABiP()
                        
                       # add_to_image_db(datesubmitted, genus_added_to, species_added_to, user_name, str(now), st.session_state['username'], approved_images )#<------working
                        pre_col1.write("GABiP updated!")
                if reject_information and reject_new_info_reason:
                            reject_new_addition()
                            pre_col3.write("Reason sent to user")
                elif reject_information:
                        pre_col3.warning("Please add a reason for rejection for user to review")

information_edit_review()