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
#latest_id="1s0sEqX_WANw_8Wo6UfxEzKxgO0Q194Ap"



@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated

def load_latest_not_cached():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db

try:
     current=load_latest()
except HttpError as error:
     st.write(f"An HTTP error {error.resp.status} occurred: {error.content}")
except RefreshError:
        st.write("The credentials could not be refreshed.")
except Exception as error:
        st.write(f"An error occurred: {error}")

#-------------------------------------------------------------METHODS FOR CHECKING LATEST GABiP FOR SPECIES EDIT REVIEWS--------------------------------------------------------#

def check_current_db(genus, species):
        current=load_latest_not_cached()
        if genus.lower() in current["Genus"].str.lower().values and species.lower() in current["Species"].str.lower().values:
            st.error(f"Data already exists for " +genus+ " " +species+ ". This means it has been added since this request. Check the Species Audit History for details. It is recommended that this addition is rejected") 

def check_current_db_edits(genus, species):
        current=load_latest_not_cached()
        if genus.lower() not in current["Genus"].str.lower().values and species.lower() not in current["Species"].str.lower().values:
            st.error(f"Data no longer exists for " +genus+ " " +species+ ". This means it has been removed since this request. Check the Species Audit History for details. It is recommended that this change request is rejected") 




#------------------------------------------------------------IMAGES DATABASE CONNECTION-----------------------------------------------------------------------------------------#
users_images=deta_connection.Base("user_images")

def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
     return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })

def get_all_user_images():
    res = users_images.fetch()
    return res.items

approved_user_images=get_all_user_images()
#-------------------------------------------------------------ADMIN USERS_DB METHODS--------------------------------------------------------------------------------------------#

def get_current_user(email):
    print (users_db.get(email))

def update_user(username, updates):
    return users_db.update(updates, username)

def manual_dataset_upload():
 
   
 #-------------------------------------------------------------MANUAL UPLOAD METHODS----------------------------------------------------------------------------------------------#
  
  now=datetime.now()
  version=now.strftime("%d.%m.%Y-%H.%M.%S")
  folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"          
  newPath=version+"-"+st.session_state['username']+"-manual uploaded"+".csv"
  date_now=str(now)
  def create_new_updated_dataset_google():
                newDataset=new_dataset
                newDataset = newDataset.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                with io.BytesIO() as csv_buffer:
                    csv_string = newDataset.to_csv(index=False)
                    csv_buffer.write(csv_string.encode('utf-8'))
                    csv_buffer.seek(0)
                    for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                        # process each chunk as needed
                        pass
    
            # upload bytes to Google Drive
                file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
                media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

  def add_new_dataset():
           
            metaData.put({"key":str(now), "Changes":"Manual upload", "Dataset_In_Use":newPath, "Dataset_Pre_Change":"n/a","Decided_By": st.session_state['username'], "Decision_Date":str(now),"Edit_Type": "Manual upload","Edited_By":st.session_state['username'], "Genus_Affected":"n/a","Reason_Denied": "n/a","Species_Affected": "n/a", "Status":"Approved", "User_Comment":"n/a","User_Images":"n/a","User_Sources":"n/a"} )
 #-------------------------------------------------------------MANUAL UPLOAD UI---------------------------------------------------------#
  manual_upload_option=st.checkbox("Manually Upload a dataset")
  
  if manual_upload_option:
   st.warning("Uploading a dataset will over-ride the current most recent dataset...Are you sure you want to proceed?")
   dataset_uploader=st.file_uploader("Choose a CSV file", type="csv")

   if dataset_uploader is not None:
    try:
        # Get the first file uploader object from the list
        #uploaded_file = dataset_uploader[0]
        
        # Read the CSV file into a DataFrame
        new_dataset = pd.read_csv(dataset_uploader)
       
        # Display the DataFrame in a Streamlit table
        st.write(new_dataset)
        upload_dataset=st.button("Upload")
    except Exception as e:
        st.error(f'Error loading CSV file: {str(e)}')
    if upload_dataset:
         create_new_updated_dataset_google()
         add_new_dataset()
         st.write("Dataset uploaded!")

   

#gets and displays users pending approval
def display_pending_users():
    st.markdown("***")
    for user in users:
     if user["approved"]=="False":
       with st.form(user["username"]):
        st.markdown(f"""<p style="font-family:sans-serif; color:white; font-size: 20px;"><strong>***********{user["username"]}'s Request**********</strong></p>""" , unsafe_allow_html=True)
        st.text(f"Username : " +user["username"])
        st.text(f"Firstname : " +user["firstname"])
        st.text(f"Surname : " +user["surname"])
        st.text(f"Email : " +user["key"])
        checkbox1 = st.checkbox(f"Allow " + user["firstname"] + " access")
        checkbox2 = st.checkbox(f"Deny " +user["firstname"] +" access")
        confirmForm = st.form_submit_button(f"Submit Decision for  : " + user["username"])
        if checkbox1 and checkbox2 and confirmForm:
            st.error("Warning! Both options have been selected. Please review decision")
        elif checkbox1 and confirmForm:
            update_user(user["key"], updates={"approved": "True"})
            st.success(f"Accepted! "+user["username"]+ " can now access the GABiP. You can revoke access at any time using the View Approved user's option")
        elif checkbox2 and confirmForm:
            update_user(user["key"], updates={"approved": "Denied"})
            st.warning(f"Access request denied for " +user["username"] )
      
        st.markdown("""<p style="font-family:sans-serif; color:white; font-size: 20px;"><strong>**************************************************************************************</strong></p>""", unsafe_allow_html=True )
        st.write("***")

def display_approved_users():
    st.markdown("***")
    for user in users:
     if user["approved"]=="True" and user["admin"]=="False":
       with st.form(user["username"]):
        st.markdown(f"""<p style="font-family:sans-serif; color:white; font-size: 20px;"><strong>***********{user["username"]}**********</strong></p>""" , unsafe_allow_html=True)
        st.text(f"Username : " +user["username"])
        st.text(f"Firstname : " +user["firstname"])
        st.text(f"Surname : " +user["surname"])
        st.text(f"Email : " +user["key"])
        checkbox1 = st.checkbox(f"Promote  " + user["firstname"] + " to Admin level")
        checkbox2 = st.checkbox(f"Revoke " +user["firstname"] +" access")
        confirmForm = st.form_submit_button(f"Submit Decision for  : " + user["username"])
        if checkbox1 and checkbox2 and confirmForm:
            st.error("Warning! Both options have been selected. Please review decision")
        elif checkbox1 and confirmForm:
            update_user(user["key"], updates={"admin": "True"})
            st.success(f"Accepted! "+user["username"]+ " is now an Admin")
        elif checkbox2 and confirmForm:
            update_user(user["key"], updates={"approved": "Revoked"})
            st.warning(f"Access privileges for " +user["username"]+" revoked" )
      
        st.markdown("""<p style="font-family:sans-serif; color:white; font-size: 20px;"><strong>**************************************************************************************</strong></p>""", unsafe_allow_html=True )
        st.write("***")
     



#-----------------------------------------------------------------------SCREEN DISPLAY METHODS-----------------------------------------------------------------------------------------------------------------------------#  
     #---------------------------------------------------------------NEW ADDITION REVIEW SCREEN -------------------------------------------------------------------------------------------------#
def new_species_review():
    #current=load_latest()
        #gets dates for new species additions needing approval
    pending_new_rows=[]


    def get_pending_row_additions():
        for database in databases:
            
                if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                    
                 pending_new_rows.append(database["key"])

    get_pending_row_additions()

    new_additions_submissions=sorted(pending_new_rows,reverse=True)


    st.write("New species additions in order of date submitted")
    datesubmitted = st.selectbox(
    'Date submitted',
    (new_additions_submissions))

   
    if datesubmitted:
        for database in databases:
         if database["key"]==datesubmitted:
                    genus=database["Genus_Affected"]
                    species = database["Species_Affected"]          
                
        check_current_db(genus, species)

        tab1, tab2, tab3= st.tabs(["Species Added", "User Info", "User Source"])

        #tab1 methods
        for database in databases:
                if database["key"]==datesubmitted:
                    newAdd=database["Changes"]
                    genus=database["Genus_Affected"]
                    species = database["Species_Affected"]
                    
        
        user_changes= pd.read_json(newAdd)
        tab1.write(user_changes)

        tab1.write("Displaying vertically")
        tab1.dataframe(user_changes.iloc[0], width=300)


        #tab2 methods
        for database in databases:
                if database["key"]==datesubmitted:
                    author=database["Edited_By"]
                    authorComment=database["User_Comment"]
        for user in users:
                if user["username"]==author:
                    authorName=user["firstname"]
                    authorSurname = user["surname"] 
                    authorEmail= user["key"]
                    authorusername= user["username"]

        with tab2:
         tab2_col1, tab2_col2 = st.columns(2)
         tab2_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>First Name: </strong></em></p>', unsafe_allow_html=True)
         tab2_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Surname: </strong></em></p>', unsafe_allow_html=True)
         tab2_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Email: </strong></em></p>', unsafe_allow_html=True)
         tab2_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>User Name: </strong></em></p>', unsafe_allow_html=True)
         tab2_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Country: </strong></em></p>', unsafe_allow_html=True)
         tab2_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Acandemic Institute: </strong></em></p>', unsafe_allow_html=True)
         tab2_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{authorName}</em></p>', unsafe_allow_html=True)
         tab2_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{authorSurname}</em></p>', unsafe_allow_html=True)
         tab2_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{authorEmail}</em></p>', unsafe_allow_html=True)
         tab2_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{username}</em></p>', unsafe_allow_html=True)          
        

        tab3.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{authorComment}</em></p>', unsafe_allow_html=True) 

        


        preview=st.checkbox("Preview new addition to current dataset")




        def preview_addition(df1,df2):
            
            
            proposed = pd.concat([df1, df2], ignore_index=True)
            st.write(proposed)
            

        now=datetime.now()
        version=now.strftime("%d.%m.%Y-%H.%M.%S")
        
        newPath=version+"-"+st.session_state['username']+"-approved"+".csv"

        
        def create_new_addition_dataset():

            newDataset = pd.concat([current, user_changes], ignore_index=True)
            newDataset = newDataset.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            with io.BytesIO() as csv_buffer:
                csv_string = newDataset.to_csv(index=False)
                csv_buffer.write(csv_string.encode('utf-8'))
                csv_buffer.seek(0)
                for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                    # process each chunk as needed
                    pass
    
            # upload bytes to Google Drive
            file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
            media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        
        #updates the status, 
        def update_GABiP():
            updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], 
                       "Decision_Date":str(now), "Dataset_In_Use":newPath, "Dataset_Pre_Change":latest_approved_ds }
            metaData.update(updates, datesubmitted)
        
        def reject_new_addition():
            updates = {"Status":"Denied", "Reason_Denied":reason, "Decided_By":st.session_state['username'], 
                       "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds, "Dataset_Pre_Change":latest_approved_ds }
            metaData.update(updates, datesubmitted)



        if preview:
            try:
                current=load_latest_not_cached()
                newDataset=preview_addition(current, user_changes)
                
                col1,col2=st.columns(2)

                accept=col1.button("Approve Addition")
                reject=col2.button("Deny Addition")

                        
                if accept:
                    try:
                        create_new_addition_dataset()
                        update_GABiP()
                        st.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>GABiP Updated!</strong></em></p>', unsafe_allow_html=True)
                    except:
                         st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 30px;"><strong>***   Due to high traffic, page is temporarily unavailable. Please try again in 20 minutes. Time of error    ***</strong></p>', unsafe_allow_html=True)


            
                reason=col2.text_area("Reasons for declining", key='reason') 

                

                if reject and reason:           
                    reject_new_addition()
                    col2.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Addition Rejected</strong></em></p>', unsafe_allow_html=True)
                elif reject:
                    col2.warning("Please add a reason for rejection")
            except:
             st.write("User entered non numerical data in number fields. Unable to append new addition to current dataset")
                

#-----------------------------------------------------------------------NEW INFORMATION ADDITION DISPLAY-----------------------------------------------------------------------------------------------------------------------------#
def information_addition_review():
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
    
    
    pending_new_info=[]
    def get_pending_new_info():
        for database in databases:
            
                if database["Edit_Type"]=="Information Addition" and database["Status"] =="Pending":
                    
                 pending_new_info.append(database["key"])

    get_pending_new_info()

    new_info_submissions=sorted(pending_new_info,reverse=True)



    st.write("**Information Addition in order of date submitted**")
    datesubmitted = st.selectbox(
        'Date submitted',
        (new_info_submissions))
    
    for database in databases:
                if database["key"]==datesubmitted:
                    genus_added_to=database["Genus_Affected"]
                    species_added_to=database["Species_Affected"]      
        


    if datesubmitted:
        for database in databases:
         if database["key"]==datesubmitted:
                    genus=database["Genus_Affected"]
                    species = database["Species_Affected"]          
                
        check_current_db_edits(genus, species)


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
        
        if species_before=="image only":
             before_jsonn="image only"
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
        if species_after=="image only":
             tab1_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>Image only submitted</em></p>', unsafe_allow_html=True)

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
          
            if species_after=="image only":
              
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
                    
                    df = pd.DataFrame({"Information": source_rows,"Previous Value": current_values, "Proposed Values": new_values, "Sources": source_values })
                    
                    
                    st.write(df)
                   
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
                newDataset = newDataset.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                with io.BytesIO() as csv_buffer:
                    csv_string = newDataset.to_csv(index=False)
                    csv_buffer.write(csv_string.encode('utf-8'))
                    csv_buffer.seek(0)
                    for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                        # process each chunk as needed
                        pass
    
            # upload bytes to Google Drive
                file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
                media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()


    
        def update_GABiP():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath}#, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)
        def update_GABiP_image():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
         return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })
        
        def reject_new_addition():
                updates = {"Status":"Denied", "Reason_Denied":reject_new_info_reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        if preview_updated_dataset and species_before=="image only":
            
            preview_new=True
            if preview_new:
                
                # st.write(updated_db)
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Image")
                reject_information=pre_col3.button("Deny Image")
                reject_new_info_reason=pre_col3.text_area("Reasons for rejection for user")
                

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
                current=load_latest_not_cached()
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
                st.write(updated_db)
                
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
                    current=load_latest_not_cached()
                    updated_db=current.copy()
                    updated_json=json.dumps(update_user_json(species_before, species_after))
                    updated_row=pd.read_json(updated_json)
                    updated_db.loc[int(species_index)] =(updated_row.loc[int(species_index)])
                    preview_new=True
                except:
                 st.error("Something went wrong. Please check the user has submitted numerical data if fields are numerical")
                 preview_new=False

                
                st.write(updated_db)
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
#-----------------------------------------------------------------------NEW INFORMATION EDIT DISPLAY-----------------------------------------------------------------------------------------------------------------------------#
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
    pending_edit_info=[]
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
                    #new_info_tab2.markdown("**Reminder: If there exists a current value, then an addition has been made in the past and verified. Please check with Species Audit History before deciding**")
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
                    
                    df = pd.DataFrame({"Information": source_rows,"Previous Value": current_values, "Proposed Values": new_values, "Sources": source_values })
                    
                    
                    st.write(df)
                   
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
                newDataset = newDataset.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                with io.BytesIO() as csv_buffer:
                    csv_string = newDataset.to_csv(index=False)
                    csv_buffer.write(csv_string.encode('utf-8'))
                    csv_buffer.seek(0)
                    for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                        # process each chunk as needed
                        pass
    
            # upload bytes to Google Drive
                file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
                media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    
        def update_GABiP():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath}#, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)
        def update_GABiP_image():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now)}#, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
         return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })
        
        def reject_new_addition():
                updates = {"Status":"Denied", "Reason_Denied":reject_new_info_reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds}#, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        if preview_updated_dataset and species_before=="image only edit":
            
            preview_new=True
            if preview_new:
                
                # st.write(updated_db)
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
                current=load_latest_not_cached()
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
                st.write(updated_db)
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
                    current=load_latest_not_cached()
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
                st.write(updated_db)
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

#------------------------------------------------------------------------------------------------INFORMATION REMOVAL PAGE-------------------------------------------------------------#
#------------------------------------------------------------------------------------------------SPECIES REMOVAL PAGE-------------------------------------------------------------#
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

    current=load_latest_not_cached()
    def check_species_existence_admin_end(species, genus):
          if genus.lower() not in current["Genus"].str.lower().values and species.lower() not in current["Species"].str.lower().values:
            return True

    
    
    def update_repeat_request(key, updates):
        return metaData.update(updates, key)
    
    if len(removal_info_submissions) >0:
         
        check_species_existence_admin_end(species, genus)
   
    if datesubmitted and  check_species_existence_admin_end(species, genus):
        st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>{genus} {species} has already been removed. It was removed on {decision_date} by {approved_by} For more information, see Species Audit History </strong></em></p>', unsafe_allow_html=True)
        update_db_status=st.button("Remove from dropdown")
        if update_db_status:
                update_repeat_request(datesubmitted, updates={"Status": "Duplicate Removal Reuqest"})
                st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Request marked as duplicate and will no longer appear on dropdown </strong></em></p>', unsafe_allow_html=True)
                

    

    if datesubmitted and not check_species_existence_admin_end(species, genus):

        tab1, tab2, tab3= st.tabs(["Species to be Removed", "User Info", "Reason for Removal Request"])

        with tab1:
            tab1_col1,tab1_col2=st.columns(2)
            #tab1 methods
            for database in databases:
                    if database["key"]==datesubmitted:
                        newAdd=database["Changes"]
            
            user_changes= pd.read_json(newAdd)
            

            tab1_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Species Info </strong></em></p>', unsafe_allow_html=True)
            tab1_col1.dataframe(user_changes.iloc[0], width=300)
        


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
            tab3.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>{authorComment}</em></p>', unsafe_allow_html=True)


        
            

        now=datetime.now()
        version=now.strftime("%d.%m.%Y-%H.%M.%S")
        
        newPath=version+"-"+st.session_state['username']+"-approved"+".csv"

        def create_new_addition_dataset():
            proposed_removal=current.copy()
            proposed_removal.drop(user_changes.index[0], inplace=True)

            
            proposed_removal = proposed_removal.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            with io.BytesIO() as csv_buffer:
                    csv_string = proposed_removal.to_csv(index=False)
                    csv_buffer.write(csv_string.encode('utf-8'))
                    csv_buffer.seek(0)
                    for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                        # process each chunk as needed
                        pass
    
            # upload bytes to Google Drive
            file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
            media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            

        
        #updates the status, 
        def update_GABiP():
            updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath}#, "Dataset_Pre_Change":latest_approved_ds }
            metaData.update(updates, datesubmitted)
        
        def reject_new_addition():
            updates = {"Status":"Denied", "Reason_Denied":reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds}#, "Dataset_Pre_Change":latest_approved_ds }
            metaData.update(updates, datesubmitted)

        current=load_latest_not_cached()
        preview=st.checkbox("Preview new updated dataset")
        #st.write(approvedordered)
        if preview:
            try:
                #current=load_latest_not_cached()
                proposed_removal=current.copy()
                proposed_removal.drop(user_changes.index[0], inplace=True)
                st.write(proposed_removal)
                
                col1,col2=st.columns(2)

                accept=col1.button("Approve Removal")
                reject=col2.button("Reject Removal")

                        
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






#----------------------------------------------------------------------------------------------DATA REMOVAL PAGE----------------------------------------------------------------------#
def data_removal_review():
    def add_new_info_bg():
       st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr52l_orig.jpg");
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
    
    pending_info_removal=[]


    def get_pending_info_removal():
        for database in databases:
            
                if database["Edit_Type"]=="Information Removal" and database["Status"] =="Pending":
                    
                 pending_info_removal.append(database["key"])

    get_pending_info_removal()

    new_info_removal_submissions=sorted(pending_info_removal,reverse=True)
    #current=load_latest()
    st.write("Data removal requests in order of date submitted")
    datesubmitted = st.selectbox(
    'Date submitted',
    (new_info_removal_submissions))

    
    
    for database in databases:
                if database["key"]==datesubmitted:
                    genus_added_to=database["Genus_Affected"]
                    species_added_to=database["Species_Affected"]
    
      
    

    if datesubmitted:
        for database in databases:
         if database["key"]==datesubmitted:
                    genus=database["Genus_Affected"]
                    species = database["Species_Affected"]          
                
        check_current_db_edits(genus, species)
        st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px; border: 2px solid green;background-color: green; padding: 10px;"><em><strong>Genus: {genus_added_to}      Species: {species_added_to}</strong></em></p>', unsafe_allow_html=True)
        def update_user_json(species_before, species_after):
            data = json.loads(species_before)
            new_keys_data = json.loads(species_after)

            for key, value in new_keys_data["0"].items():
                if key in data:
                    data[key][str(species_index)] = value
            return data


        new_info_tab1, new_info_tab2, new_info_tab3, new_info_tab5, new_info_tab6= st.tabs([ "Overview", "Information Breakdown", "Image for Removal","User Info", "User Comment"])
        
        #-------------------------------------------------------------information added display--------------------------------------------------------------------#
        for database in databases:
                if database["key"]==datesubmitted:
                    species_before=database["Dataset_Pre_Change"]
                    species_after=database["Changes"]
                    image_key=database["User_Images"]
        
        if species_before=="image only delete":
             before_jsonn="image only delete"
        else:
             before_jsonn=json.loads(species_before)
             species_index = list(before_jsonn['Order'].keys())[0]
             changes_parsed=json.loads(species_after)
        
        def list_fields():
            
            for key, value in changes_parsed.items():
                for inner_key, inner_value in value.items():
                    tab1_col1.markdown(inner_key)

               
        image_count=len(image_key)
        
        with new_info_tab1:
            tab1_col1, tab1_col2, tab1_col3=st.columns(3)
        tab1_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>Information to Remove</em></p>', unsafe_allow_html=True)
        if species_after=="image only delete":
             tab1_col1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>image removal request only</em></p>', unsafe_allow_html=True)

        else:
             list_fields()
        
        if image_count!=0 and not species_after=="image only delete":
         tab1_col2.write("Request for image removal")
        

        
               
                
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
          
            if species_after=="image only delete":
                st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Current Image for {genus_added_to} {species_added_to}</strong></em></p>', unsafe_allow_html=True)
                if len(user_approved_images)==0:
                     st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No Current Images for {genus_added_to} {species_added_to}</strong></em></p>', unsafe_allow_html=True)
                else:
                         
                    for image in range(len(user_approved_images)):
                            st.image(f"https://drive.google.com/uc?id={user_approved_images[image][0]}")
                            break
                
            else:
                    
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
                    
                    df = pd.DataFrame({"Information": source_rows,"Previous Value": current_values, "Proposed Values": new_values, "Removal Reason": source_values })
                    
                    
                    st.write(df)
                   
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
                    image_key=database["User_Images"]
        
        image_count=len(image_key)
        approved_images=[]

        user_approved_images=[]

        def get_all_species_images():          
            for approved_image in  sorted (approved_user_images, key=lambda x: x["key"], reverse=True):
                    if approved_image["Species"] == species_added_to and approved_image["Genus"]==genus_added_to:
                       
                     user_approved_images.append(approved_image['Images'])
            return user_approved_images
        

       
        
        def check_all_species_images(image_key):              
            found = False
            for array in user_approved_images:
                for value in array:
                    if value == image_key:
                        
                        found = True
                        
                        return True
                
            

             


        image_folder_id = "1g_Noljhv9f9_YTKHEhPzs6xUndhufYxu"
        with new_info_tab3:
            tab3_col1,tab3_col2,tab3_col3=st.columns(3)
        
            if image_count <1:
                new_info_tab3.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em>No Image Removal Request</em></p>', unsafe_allow_html=True)

            else:
                
                tab3_col1,tab3_col2,tab3_col3=st.columns(3)
                tab3_col1.image(f"https://drive.google.com/uc?id={image_key[1]}")
                
                
                get_all_species_images()
                
                
                check_all_species_images(image_key[1])
                
                if not check_all_species_images(image_key[1]):
                     tab3_col1.write("This image no longers exists")
                

            
                
            
            
      
            
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
                newDataset = newDataset.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                with io.BytesIO() as csv_buffer:
                    csv_string = newDataset.to_csv(index=False)
                    csv_buffer.write(csv_string.encode('utf-8'))
                    csv_buffer.seek(0)
                    for chunk in pd.read_csv(csv_buffer, chunksize=1000):
                        # process each chunk as needed
                        pass
    
            # upload bytes to Google Drive
                file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
                media = MediaIoBaseUpload(io.BytesIO(csv_string.encode('utf-8')), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
               

    
        def update_GABiP():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath}#, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)
        def update_GABiP_image():
                updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
         return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })
        
        def reject_new_addition():
                updates = {"Status":"Denied", "Reason_Denied":reject_new_info_reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds}#, "Dataset_Pre_Change":latest_approved_ds }
                metaData.update(updates, datesubmitted)

        

        new_array=[]
        def update_image_array(db_key, image_value):
                
                for approved_images in approved_user_images:
                    
                    if approved_images['key']==db_key and len(approved_images['Images'])!=1:
                        new_image_array=approved_images['Images']
                        approved_images['Images'].remove(image_value)
                        updates={'Images':new_image_array}
                        users_images.update(updates, db_key)
                    if approved_images['key']==db_key and len(approved_images['Images'])==1:
                        users_images.delete(db_key)   
                    



        def update_repeat_request(key, updates):
         return metaData.update(updates, key)           

        if preview_updated_dataset and species_before=="image only delete" and check_all_species_images(image_key[1]):
            st.write(species_added_to)
            preview_new=True
            if preview_new:
                
                
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Image Removal")
                reject_information=pre_col3.button("Deny Image Removal")
                reject_new_info_reason=pre_col3.text_area("Reasons for rejection for user")
                

                if accept_information:
                        #create_new_updated_dataset_google() #<-------- working
                        update_GABiP_image()
                        
                        update_image_array(image_key[0], image_key[1])

                        pre_col1.write("Image Removed")
                if reject_information and reject_new_info_reason:
                            reject_new_addition()
                            pre_col3.write("Reason sent to user")
                            
                elif reject_information:
                        pre_col3.warning("Please add a reason for rejection for user to review")       
        else:
            if preview_updated_dataset and species_before=="image only delete" and not check_all_species_images(image_key[1]):
                st.write(species_added_to)
                preview_new=True
                if preview_new:
                    
                    # st.write(updated_db)
                    pre_col1, pre_col2, pre_col3=st.columns(3)
                    mark_as_duplicate=pre_col2.button("Mark as duplicate")
                    

                    if mark_as_duplicate:
                            update_repeat_request(datesubmitted, updates={"Status": "Duplicate Removal Reuqest", "Decided_By":st.session_state['username'], "Decision_Date":str(now)})
                            st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Request marked as duplicate and will no longer appear on dropdown </strong></em></p>', unsafe_allow_html=True)
                        
                        

        if preview_updated_dataset and species_before!="image only delete" and len(image_key)!=0:
                current=load_latest_not_cached()
                updated_db=current.copy()
                try:
                    
                    updated_json=json.dumps(update_user_json(species_before, species_after))
                    updated_row=pd.read_json(updated_json)
                    updated_db.loc[int(species_index)] =(updated_row.loc[int(species_index)])
                    preview_new=True
                except:
                 st.error("Something went wrong. Please check the user has submitted numerical data if fields are numerical")
                 preview_new=False

                
                st.write(updated_db)
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Addition")
                reject_information=pre_col3.button("Deny Addition")
                reject_new_info_reason=pre_col3.text_area("Reason for rejection for user")

                if accept_information and check_all_species_images(image_key[1]):
                        create_new_updated_dataset_google() #<-------- working
                        update_GABiP()
                        
                        update_image_array(image_key[0], image_key[1])
                        pre_col1.write("GABiP updated!")

                
                if accept_information and not check_all_species_images(image_key[1]):
                     create_new_updated_dataset_google() #<-------- working
                     update_GABiP()
                     pre_col1.write("GABiP updated. Image Reqested for removal removed already removed")

                if reject_information and reject_new_info_reason:
                            reject_new_addition()
                            pre_col3.write("Reason sent to user")
                            
                elif reject_information:
                        pre_col3.warning("Please add a reason for rejection for user to review")
        
        if preview_updated_dataset and species_before!="image only delete" and len(image_key)==0:
                
                
                try:
                    current=load_latest_not_cached()
                    updated_db=current.copy()
                    updated_json=json.dumps(update_user_json(species_before, species_after))
                    updated_row=pd.read_json(updated_json)
                    updated_db.loc[int(species_index)] =(updated_row.loc[int(species_index)])
                    preview_new=True
                except:
                 st.error("Something went wrong. Please check the user has submitted numerical data if fields are numerical")
                 preview_new=False

                st.write(updated_db)
                pre_col1, pre_col2, pre_col3=st.columns(3)
                accept_information=pre_col1.button("Approve Addition")
                reject_information=pre_col3.button("Deny Addition")
                reject_new_info_reason=pre_col3.text_area("Reasons for rejection for user")

                if accept_information:
                        create_new_updated_dataset_google() #<-------- working
                        update_GABiP()
                        
                      
                        pre_col1.write("GABiP updated!")
                if reject_information and reject_new_info_reason:
                            reject_new_addition()
                            pre_col3.write("Reason sent to user")
                elif reject_information:
                        pre_col3.warning("Please add a reason for rejection for user to review")

#------------------------------------------------------------------------------------------------WELCOME SCREEN BACKGROUND------------------------------------------------------------#

def welcome_screen():
    def load_welcome_bg():
        st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr31l_orig.jpg.jpg");
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
    load_welcome_bg()
    
#-----------------------------------------------------------------------------------EDIT REQUEST OPTIONS SCREEN-------------------------------------------------------------------------------------------------------#
def admin_edit_options():
    options=st.sidebar.radio("Options", ('Show Current Database','New Species Entry', 'New Species Data', 'Species Edit Requests', 'Data Removal Requests', "Species Removal Requests" ), key='admin_current_option')
    if options == "Show Current Database":
        st.write("Current Database")
        try:
            current=load_latest_not_cached()
            st.write(current)
        except:
         st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 30px;"><strong>***   Due to high traffic, page is temporarily unavailable. Please try again in 20 minutes. Time of error    ***</strong></p>', unsafe_allow_html=True)
       
        

    if options == "New Species Entry":
        new_species_review()
    if options== "New Species Data":
        information_addition_review()
    if options== "Species Edit Requests":
         information_edit_review()
    if options == "Data Removal Requests":
         data_removal_review()
    if options == "Species Removal Requests":
         remove_species_admin()




#---------------------------------------------------------------------------------MAIN WELCOME SCREEN--------------------------------------------------------------------------------------------------------#
def admin_welcome_screen():
    
    st.subheader("Welcome to the Admin Area.")

    adminOptions= st.selectbox(" Admin Options", ['Manually upload a new Database','View Access Requests', 'View Existing Users','See Edit Requests'  ])
    if adminOptions=="Click here to see Admin options":
        welcome_screen()
    if adminOptions=="Manually upload a new Database":
         manual_dataset_upload()
    if adminOptions=="View Access Requests":
         display_pending_users()
    if adminOptions=="View Existing Users":
         display_approved_users()
    if adminOptions == "See Edit Requests":
        admin_edit_options()


    

#-------------------------------------------------------------------------SEND EMAIL METHOD---------------------------------------------------------------------------#
def sendEmail(email_receiver):
  email_sender='amphib.app@gmail.com'
  email_password = 'mfqk hxrk qtpp qqdp'
  message = MIMEMultipart("alternative")
  message["Subject"] = "Password Reset Request"
  message["From"] = email_sender
  message["To"] = email_sender

 #plain text and html versions of message for comparison
  text = """
  Hi AmphibiFan it's text,
  Please click on the link below to reset your password:
  https://radical-apathy-deployment-practice-forgotten-password-lu3mqh.streamlit.app/

  Requested password in error? No worries, continue logging in using your previous password.

  """
  html = """
  <html>
    <body>
      <p>Hi AmphibiFan it's from streamlit,<br>
        Please click on the link below to reset your password:<br>
        <a href="https://radical-apathy-deployment-practice-forgotten-password-lu3mqh.streamlit.app/">Reset Password</a> 
        
        Requested password in error? No worries, continue logging in using your previous password.
      </p>
    </body>
  </html>
  """

  # Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)
  message.attach(part2)
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context= context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, message.as_string())

#-----------------------------------------------------------------------HOME PAGE-----------------------------------------------------------------------------------------------------------------------------#  

def load_login_bg():
        st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr31l_orig.jpg");
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

load_login_bg()



authenticator = stauth.Authenticate(email, username, hashed_passwords,
    "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


if authentication_status == False:
     st.warning("**Username/password is not recognised**")
     
elif authentication_status == None:
     st.warning("Please enter username and password")
else:
     for user in users:
         if user["username"] == st.session_state['username'] and user["admin"] == "True":
             st.write("Welcome, you're an admin.")
             admin_welcome_screen()         
         elif user["username"] == st.session_state['username'] and user["admin"] == "False":
             if user["approved"] == "True" and user["admin"] == "False":
                 st.write(f"**Welcome {user['firstname']}, you're a trusted member. However, this section is for Admin users only**")
                 
             else:
                 st.write(f"Welcome {user['firstname']}, your access request is pending approval. We'll send you an e-mail alert to inform you of the status.")
  
authenticator.logout("Logout", "sidebar")

       




          
        




#------------------------------------------------------------PASSWORD REMINDER SECTION-----------------------------------------------------------------------------------------#

# st.write("Forgotten username/password? Enter your email below and we'll send a reminder")

# sendReminder = st.checkbox("Send Password Reminder")
# if sendReminder:
#     email=st.text_input("Email address")
#     sendbutton=st.button("Send reminder")
#     if sendbutton and email:
#         sendEmail(email)
#         st.success("Email sent...please check your inbox for a password reset link")
#     elif sendbutton:
#         st.warning("Please enter an email address")