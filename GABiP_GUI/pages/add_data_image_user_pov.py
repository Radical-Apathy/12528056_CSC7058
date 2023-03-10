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



#--------------------------------------------------------------GENERAL CHECK IMAGE METHODS----------------------------------------------------------------------------------------------#

#--------------------------------------------------------------NEW EDIT REVIEW SCREEN -------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------REMOVE SPECIES INFORMATION DISPLAY-----------------------------------------------------------------------------------------------------------------------------#
def add_species_information():
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

    missingInfoColumns = []
    def get_missing_info_columns(results):
        for column in dbColumns:
            if results[column].isna().any():
                missingInfoColumns.append(results[column].name)
        return missingInfoColumns

    user_missing_info = []
    def get_missing_userinfo():
        for option in show_missing_info:
            userText = st.text_input(option, key=option)
            if userText:
                user_missing_info.append(st.session_state[option])
        return user_missing_info

    def update_missing_results(show_missing_info):
        speciesIndex = species_results.index[0]
        results_updated = species_results.copy()
        for column in show_missing_info:
            results_updated.at[speciesIndex, column] = st.session_state[column]
        return results_updated

    now = datetime.now()
    image_folder_id = "1g_Noljhv9f9_YTKHEhPzs6xUndhufYxu"
    image_id=[]

    def upload_image():
        if 'image_ids' in st.session_state:
            image_ids = st.session_state['image_ids']
        else:
            image_ids = []

       
        uploaded_image = col1.file_uploader("Choose an image", type=["jpg", "png", "bmp", "gif", "tiff"])
        if uploaded_image is not None:
            col1.write("**Image preview - click submit if satisfied**")
            col1.image(uploaded_image)

        submit_image=col1.button("Submit image")
        if submit_image and uploaded_image:
            bytes_data = uploaded_image.getvalue()
            try:
                file_metadata = {
                    'name': uploaded_image.name,
                    'parents': [image_folder_id],
                    'mimeType': 'image/jpeg'  # change the MIME type to match your image format
                }
                media = MediaIoBaseUpload(io.BytesIO(bytes_data), mimetype='text/csv', resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                image_id = file.get('id')

                st.success(f'Image uploaded! You can choose to upload more')
                image_ids.append(image_id)
                st.session_state['image_ids'] = image_ids

                uploaded_image = None
            except:
                st.error("Please try again. Be sure to check your file type is in the correct format")

    def check_user_image(species_dropdown, genus_dropdown):
     image_found=False
     for user_image in sorted(user_images, key=lambda x: x["key"], reverse=True):
          if user_image["Species"] == species_dropdown and user_image["Genus"]==genus_dropdown:
            if user_image['Images']:
                col1.write("Image")
                col1.image(f"https://drive.google.com/uc?id={user_image['Images'][0]}")
                col1.markdown(f"Submitted by {user_image['Submitted_By']} on {user_image['key']}") 
                image_found=True  
            break
     if not image_found: 
      col1.write("No Images Available")
      upload_image()

    def link_image(results):
     merged_image_df = pd.merge(results, dfImages, left_on=['Genus', 'Species'], right_on=['Genus', 'Species'], how='inner')
     if merged_image_df.empty or merged_image_df["Display Image"].iloc[0] == "https://calphotos.berkeley.edu image not available":
         check_user_image(species_dropdown, genus_dropdown)
     elif not merged_image_df.empty and merged_image_df["Display Image"].iloc[0] != "https://calphotos.berkeley.edu image not available":
         return merged_image_df["Display Image"].iloc[0]
        
    def link_embedded_image(results):
        embedded_image_df= pd.merge(results, dfImages, left_on=['Genus', 'Species'], right_on=['Genus', 'Species'], how='inner')
        if not embedded_image_df.empty and embedded_image_df["Display Image"].iloc[0] != "https://calphotos.berkeley.edu image not available":
            return embedded_image_df["Embedded Link"].iloc[0]
        else:
            return None

    def update_user_json(original_results_json, user_df_json):
        data = json.loads(original_results_json)
        new_keys_data = json.loads(user_df_json)

        for key, value in new_keys_data["0"].items():
            if key in data:
                data[key][str(results_index)] = value
        return data
   
   #-----------------------------------------------------------------ADD SPECIES INFO MAIN PAGE-------------------------------------------------#
    headercol1, headercol2, headercol3=st.columns(3)
    headercol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 30px;"><em><strong>Add Species Information</strong></em></p>', unsafe_allow_html=True)
    







    dbColumns=current.columns
    create_session_states(dbColumns)
    all_genus=[]
    def get_genus(species_dropdown):
        all_genus=current.loc[current["Species"]==species_dropdown]
        return all_genus


    additional_info=[]

    species_alphabetical=(sorted(current["Species"].drop_duplicates(), reverse=False))

    additional_info_sources=[]

    species_dropdown=st.selectbox("Select a species to add to: ", (species_alphabetical))

    species_genus=current.loc[current["Species"]==species_dropdown]

    genus_alphabetical=(sorted(current["Genus"].drop_duplicates(), reverse=False))

    genus_dropdown=st.selectbox("Select "+species_dropdown+ " Genus", species_genus["Genus"])

    species_results=current.loc[(current["Species"] == species_dropdown) & (current['Genus'] == genus_dropdown)]

    source_fields=[]
    summary_dataframe=[]
    def create_source_fields(show_missing_info):
       for option in show_missing_info:
               user_source=st.text_input("Please enter a source for "+option, key=option+" source")
    
       for option in show_missing_info:
           if user_source and user_source!="":
               st.session_state[option+" source"]==user_source
               additional_info_sources.append(st.session_state[option+" source"])
           
       return additional_info_sources
   
    col1, col2, col3 = st.columns(3)

    col3.markdown("**All Genea of** "+species_dropdown)

    col3.dataframe(species_genus["Genus"])


    col2.write(f"{genus_dropdown} {species_dropdown} Summary")

    col2.dataframe(species_results.iloc[0], width=500)

    col1.markdown(f"[![]({link_image(species_results)})]({link_embedded_image(species_results)})")

    get_missing_info_columns(species_results)

    image_ids=st.session_state['image_ids']
    st.write(len(image_ids))
    show_missing_info=st.multiselect("Add Missing Information", missingInfoColumns)

    if show_missing_info:
        get_missing_userinfo()

    results_copy=species_results.copy()

    results_updated=update_missing_results(show_missing_info)

    # show_results=st.checkbox("Show updates")
 
    # compared=species_results.iloc[0].equals(results_updated.iloc[0])

    # if show_results and compared:
    #     st.warning("**No information has been changed. Please select at lease one option from Add Missing Information dropdown**")
    # elif show_results and len(show_missing_info) != len(user_missing_info):
    #     st.warning("**Please ensure values are added for each field selected**")
    # elif show_results and not compared: 
    #     comparecol1,comparecol2, comparecol3=st.columns(3)
    #     comparecol1.write("**Original Species**")
    #     comparecol1.dataframe(species_results.iloc[0], width=300)
    #     comparecol3.write("**Updated Species Info**")
    #     comparecol3.dataframe(results_updated.iloc[0], width=300)
    
    sourcecol1,sourcecol2,sourcecol3=st.columns(3)
    sourcecol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
    sourcecol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*Information Sources*</strong></p>', unsafe_allow_html=True)
    sourcecol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
    if len(image_ids) >0:
        image_source=st.text_input("Image(s) Source")
    create_source_fields(show_missing_info)
    

    sourcesum1, sourcesum2,sourcesum3=st.columns(3)
    source_summary=sourcesum2.checkbox("Review Addition and Submit for review")
    sources_review_dataframe = pd.DataFrame(additional_info_sources, show_missing_info)
    sources_review_json=sources_review_dataframe.to_json(orient="columns")
    #source_tab1, source_tab2=st.tabs(2)
    #st.tabs(["Species Added", "User Info", "User Source", "User Edit History"])
    preview_sucess=False

    

    if source_summary and len(image_ids)!=0:
        source_tab1, source_tab2, source_tab3=st.tabs(["Field Sources", "Image Sources", "Updated Info"])
        
        

        if not additional_info_sources:

         st.warning("Please ensure sources are provided for each information point")
        else:
            with source_tab1:
                tab1_sumcol1,tab1_sumcol2,tab1_sumcol3=st.columns(3)
                tab1_sumcol1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Field</strong></em></p>', unsafe_allow_html=True)
                tab1_sumcol3.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Source</strong></em></p>', unsafe_allow_html=True)
                sources_parsed=json.loads(sources_review_json)
                for key, value in sources_parsed.items():
                    for inner_key, inner_value in value.items():
                        tab1_sumcol1.markdown("***")
                        tab1_sumcol1.markdown("**"+inner_key+"**")
                        tab1_sumcol3.markdown("***")
                        tab1_sumcol3.markdown("*"+inner_value+"*")
            with source_tab2:
                 tab2_sumcol1,tab2_sumcol2,tab2_sumcol3=st.columns(3)
                 tab2_sumcol1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Images</strong></em></p>', unsafe_allow_html=True)
                 source_tab2.markdown('<p style="font-family:sans-serif; color:White; font-size: 15px;"><em><strong>Note: If you are not seeing all images submitted, please ensure the submit button has been clicked after each image upload</strong></em></p>', unsafe_allow_html=True)
                 for image_id in image_ids:
                     tab2_sumcol1.image(f"https://drive.google.com/uc?id={image_id}")
                 tab2_sumcol3.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Sources</strong></em></p>', unsafe_allow_html=True)
                 tab2_sumcol3.write(image_source)
            preview_sucess=True
            with source_tab3:
                tab3_sumcol1,tab3_sumcol2,tab3_sumcol3=st.columns(3)
                tab3_sumcol2.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Updated Results</strong></em></p>', unsafe_allow_html=True)
                tab3_sumcol2.dataframe(results_updated.iloc[0], width=500)

                     

    if source_summary and len(image_ids)==0:
        
        sumcol1,sumcol2,sumcol3=st.columns(3)
        if not additional_info_sources:

         st.warning("Please ensure sources are provided for each information point")
        else:
            
            sumcol1.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Field</strong></em></p>', unsafe_allow_html=True)
            sumcol3.markdown('<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Source</strong></em></p>', unsafe_allow_html=True)
            sources_parsed=json.loads(sources_review_json)
            for key, value in sources_parsed.items():
                for inner_key, inner_value in value.items():
                    sumcol1.markdown("***")
                    sumcol1.markdown("**"+inner_key+"**")
                    sumcol3.markdown("***")
                    sumcol3.markdown("*"+inner_value+"*")
        preview_sucess=True

    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*****************************************************************************************</strong></p>', unsafe_allow_html=True)

    # preview_updated_dataset=st.checkbox("**View updated dataset and submit**")

    # if preview_updated_dataset and len(show_missing_info) != len(user_missing_info):
    #         st.warning("**Please ensure values are added for each field selected**")
    # preview_success= False
        
        
    # if  preview_updated_dataset and  len(show_missing_info) != len(additional_info_sources):
    #         st.warning("**Please ensure sources are added for each field selected**")
    # preview_success=False

    # if preview_updated_dataset and len(show_missing_info) == len(additional_info_sources) and len(show_missing_info) == len(user_missing_info) :
    
    #     results_index=species_results.index[0]
    #     updated_db=current.copy()
    #     search_results_to_json=species_results.to_json(orient="columns")
    #     try:
    #         pd.DataFrame(user_missing_info, show_missing_info)
    #         user_changes=pd.DataFrame(user_missing_info, show_missing_info)
    #         user_changes_json=user_changes.to_json()    
    #         updated_json=json.dumps(update_user_json(search_results_to_json, user_changes_json))
    #         updated_row=pd.read_json(updated_json)
    #         updated_db.loc[results_index] =(updated_row.loc[results_index])
    #         st.dataframe(updated_db)
    #         preview_success=True
    #     except:
    #         st.warning("**Please ensure all fields selected from the 'Add Missing Information' dropdown are filled in AND fields have correct data e.g. numerical data for SVLMx**")
    #             #st.warning()
    #     if preview_success:
    #      user_comments = st.text_area("**Additional comments (optional)**", height=30)
       
    if preview_sucess:
        prev_col1, prev_col2, prev_col3=st.columns(3) 
        commit_addition=prev_col2.button("Submit Addition")
        

        
        if commit_addition and len(show_missing_info) == len(user_missing_info) and len(show_missing_info) == len(additional_info_sources) :
                user_changes=pd.DataFrame(user_missing_info, show_missing_info)
                user_changes_json=user_changes.to_json() 
                search_results_to_json=species_results.to_json(orient="columns") 
                add_to_database(str(now), user_changes_json, search_results_to_json, "Information Addition", species_dropdown,  genus_dropdown, st.session_state["username"], image_source, "Pending", "n/a", "n/a", "n/a", latest_approved_ds, sources_review_json, st.session_state['image_ids'] )
                if 'image_ids' in st.session_state:
                 del st.session_state['image_ids']
                
                
                st.markdown('<p style="font-family:sans-serif; color:White; font-size: 30px;"><strong>***      ADDITION SUBMITTED        ***</strong></p>', unsafe_allow_html=True)
        elif commit_addition and len(show_missing_info) != len(user_missing_info) or len(show_missing_info) != len(additional_info_sources) or len(user_missing_info)==0:
                st.warning("Please check all fields selected and sources have been provided in order to submit")


add_species_information()
    