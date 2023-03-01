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
import json
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
import io
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
st.set_page_config(page_icon='amphibs.jpeg')

#-----------------------------------------------------------GOOGLE DRIVE CONNECTIONS-----------------------------------------------------------------------------#
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
#-------------------------------------------------------------USERS_DB METHODS--------------------------------------------------------------------------------------------#


#------------------------------------------------------------DATABASE_METADATA DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

database_metadata=deta_connection.Base("database_metadata")

#------------------------------------------------------------ DATABASE_METADATA DATABASE METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = database_metadata.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=[database["Status"] for database in databases]
path = [database["Dataset_In_Use"] for database in databases]

#getting the most recent approved csv file
#def get_latest():
#    for database in databases:
#     for i in date_time:
        
#      if database["key"]== i and database["Status"] =="Approved":
#        break
#    return(database["Current Dataset"])


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

#add user's entries to csv 
def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, decided_by, date_decided, current_database_path, user_sources, user_images):
     """adding user"""
     #defining the email as the key
     return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Decided_By":decided_by, "Decision_Date":date_decided, 
     "Dataset_In_Use":current_database_path, "User_Sources": user_sources, "User_Images": user_images })




#@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')
    return current_db


current_db=load_latest()

#------------------------------------------------------------IMAGES DATABASE CONNECTION-----------------------------------------------------------------------------------------#
users_images=deta_connection.Base("user_images")

def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
     return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })

def get_all_user_images():
    res = users_images.fetch()
    return res.items
user_images=get_all_user_images()
#-------------------------------------------------------------CONNECTING TO IMAGES AND REFERENCES CSVS FROM GOOGLE DRIVE---------------------------------------------------------#
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


#------------------------------------------------------------SESSION STATE INITIATION--------------------------------------------------------------------------------------------#

if 'comment' not in st.session_state:
    st.session_state['comment']=""


def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""
        

if 'image_ids' not in st.session_state:
        st.session_state['image_ids']=[]

#-------------------------------------------------------------------------LOGIN DISPLAY PAGE METHODS-----------------------------------------------------------------------------#
#def welcome_screen():
 #   welcol1,welcol2,welcol3=st.columns(3)
  #  welcol2.image("amphibs.jpeg", width=200)
    


#--------------------------------------------------------------------------SHOW DATABASE PAGE------------------------------------------------------------------------------------#

def show_db():

    def load_db_bg():
        st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/248177756.jpg");
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

    load_db_bg()

    db_col1,db_col2=st.columns(2)
    try:
        st.dataframe(current_db, width=600)
    except HttpError as error:
     st.write(f"An HTTP error {error.resp.status} occurred: {error.content}")
    except RefreshError:
        st.write("The credentials could not be refreshed.")
    except Exception as error:
        st.write(f"An error occurred: {error}")

#--------------------------------------------------------------------------ADD ENTRY PAGE------------------------------------------------------------------------------------#

def add_entry_page():
    #-----------------Methods for adding an entry---------------------------#
#enforcing mandatory fields
    def blank_validation(states=['order','family','genus','species']):
        for i in states:
         if i=="":
            st.warning("Order, Family, Genus, Species fields can not be left blank. Please recheck mandatory field section")


    def get_extra_userinfo():
     for option in more_options:
        
        userText=st.text_input(option, key=option)
        if userText:
         st.session_state[option] == userText
        elif not userText =="" :
            st.session_state[option]==None


    #stores user info in an array      
    def populate_userinfo():
       for column in dbColumns:
           if st.session_state[column]=="":
             st.session_state[column]=None

           userInfo.append(st.session_state[column])

    #checking that both the genus and species submitted don't exist on current csv    
    def check_current_db(genus, species):
        if genus.lower() in current_db["Genus"].str.lower().values and species.lower() in current_db["Species"].str.lower().values:
            st.warning(f"Data already exists for " +genus+ " " +species+ " Check full dataset option and consider making and edit to current dataset instead of an addition") 

    

    #creates a csv file with users addition
    def create_csv(columnrow, inforow):
        with open(newPath,  'w', encoding= 'UTF8', newline='') as f:
            writer=csv.writer(f)
            writer.writerow(columnrow)
            writer.writerow(inforow)


    

 #st.write(current_db)
    path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"
    dbColumns=current_db.columns

 #creating session state variables for csv columns
    create_session_states(dbColumns)


    userInfo=[]

    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 30px;"><strong>***      * Mandatory Fields *        ***</strong></p>', unsafe_allow_html=True)
    order =st.text_input("Order","Order - e.g. Anura", key='Order') 

    family =st.text_input("Family","Family - e.g. Allophrynidae", key='Family')

    genus =st.text_input("Genus", "Genus - e.g. Allophryne", key='Genus')

    species =st.text_input("Species","Species - e.g. Relicta", key='Species')

    
 #----------------------------------------------------------------MANAGING ADDITIONAL FIELDS -------------------------------------------------------#
    st.markdown('***')
    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>More Options</strong></p>', unsafe_allow_html=True)
    more_options=st.multiselect("Add more Information", ['SVLMMx', 'SVLFMx', 'SVLMx', 'Longevity', 'NestingSite', 'ClutchMin',	'ClutchMax',
                             'Clutch', 'ParityMode',	'EggDiameter', 'Activity',	'Microhabitat', 'GeographicRegion',	'IUCN',	
                             'PopTrend',	'RangeSize', 'ElevationMin','ElevationMax','Elevation'])


    if more_options:
     get_extra_userinfo()


   
    review_information=st.button("Review Information")
    #altering populate userinfo method to create json array
      
    
    if review_information:
    
     populate_userinfo()
     blank_validation([st.session_state['Order'], st.session_state['Family'], st.session_state['Genus'], st.session_state['Species']])
     check_current_db(st.session_state['Genus'], st.session_state['Species']) 
     reviewdf = pd.DataFrame(userInfo, current_db.columns)
     st.dataframe(reviewdf, width=300) 

     #temp code for development
     #populate_userinfo()
     #data = {0: userInfo}
     #dftojsondict = pd.DataFrame.from_dict(data,orient='index',columns=current_db.columns)
     #dftojson=dftojsondict.to_json(orient="columns")
     #st.write(dftojson)
     
     
    
    #st.session_state

    user_message=st.text_area("Please leave a comment citing the source for this addition", key='comment')
    

    commit_changes=st.button("Submit for review")

    now=datetime.now()
    timeStamp=now.strftime("%d.%m.%Y-%H.%M.%S")
    path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/pending changes/Additions/"
    path_end = timeStamp
    newPath=path_prefix+path_end+"-"+st.session_state['username']+".csv"



    
    
    if commit_changes and user_message=="":  
     st.error("Please add a source")
    if commit_changes and genus.lower() in current_db["Genus"].str.lower().values and species.lower() in current_db["Species"].str.lower().values:
     st.error("Information already exists for "+ st.session_state['Genus'] + " "+st.session_state['Species'] +" check Full Database and make an addition via an edit") 
    elif commit_changes and user_message:
     populate_userinfo()
     data = {0: userInfo}
     dftojsondict = pd.DataFrame.from_dict(data,orient='index',columns=current_db.columns)
     dftojson=dftojsondict.to_json(orient="columns")
     
     add_to_database(str(now), dftojson, get_approved(), "New Species Addition", st.session_state["Species"], st.session_state["Genus"], st.session_state["username"], st.session_state["comment"], "Pending", "n/a", "n/a", "n/a", get_approved(), "n/a", "n/a")
     st.markdown('<p style="font-family:sans-serif; color:Red; font-size: 30px;"><strong>***      ADDITION SUBMITTED        ***</strong></p>', unsafe_allow_html=True)
       

    
    
    

#--------------------------------------------------------------------------ADD SPECIES INFORMATION PAGE------------------------------------------------------------------------------------#
#----------------------------------------------METHODS SPECIFIC TO ADD NEW SPECIES INFORMATION---------------------------------------------#
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
            col1.write("**Image preview**")
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
    current=load_latest()
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
    show_missing_info=st.multiselect("Add Missing Information", missingInfoColumns)

    if show_missing_info:
        get_missing_userinfo()

    results_copy=species_results.copy()

    results_updated=update_missing_results(show_missing_info)

    show_results=st.checkbox("Show updates")
 
    compared=species_results.iloc[0].equals(results_updated.iloc[0])

    if show_results and compared:
        st.warning("**No information has been changed. Please select at lease one option from Add Missing Information dropdown**")
    elif show_results and len(show_missing_info) != len(user_missing_info):
        st.warning("**Please ensure values are added for each field selected**")
    elif show_results and not compared: 
        comparecol1,comparecol2, comparecol3=st.columns(3)
        comparecol1.write("**Original Species**")
        comparecol1.dataframe(species_results.iloc[0], width=300)
        comparecol3.write("**Updated Species Info**")
        comparecol3.dataframe(results_updated.iloc[0], width=300)
    
    sourcecol1,sourcecol2,sourcecol3=st.columns(3)
    sourcecol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
    sourcecol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*Information Sources*</strong></p>', unsafe_allow_html=True)
    sourcecol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
    create_source_fields(show_missing_info)

    sourcesum1, sourcesum2,sourcesum3=st.columns(3)
    source_summary=sourcesum2.button("Review Sources Summary")
    sources_review_dataframe = pd.DataFrame(additional_info_sources, show_missing_info)
    sources_review_json=sources_review_dataframe.to_json(orient="columns")
    if source_summary:
    
        sumcol1,sumcol2,sumcol3=st.columns(3)
        if not additional_info_sources:

         st.warning("Please ensure sources are provided for each information point")
        else:
            
            sumcol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Field</strong></em></p>', unsafe_allow_html=True)
            sumcol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Source</strong></em></p>', unsafe_allow_html=True)
            sources_parsed=json.loads(sources_review_json)
            for key, value in sources_parsed.items():
                for inner_key, inner_value in value.items():
                    sumcol1.markdown("***")
                    sumcol1.markdown("**"+inner_key+"**")
                    sumcol3.markdown("***")
                    sumcol3.markdown("*"+inner_value+"*")
                    

    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*****************************************************************************************</strong></p>', unsafe_allow_html=True)

    preview_updated_dataset=st.checkbox("**View updated dataset and submit**")

    if preview_updated_dataset and len(show_missing_info) != len(user_missing_info):
            st.warning("**Please ensure values are added for each field selected**")
    preview_success= False
        
        
    if  preview_updated_dataset and  len(show_missing_info) != len(additional_info_sources):
            st.warning("**Please ensure sources are added for each field selected**")
    preview_success=False

    if preview_updated_dataset and len(show_missing_info) == len(additional_info_sources) and len(show_missing_info) == len(user_missing_info) :
    
        results_index=species_results.index[0]
        updated_db=current.copy()
        search_results_to_json=species_results.to_json(orient="columns")
        try:
            pd.DataFrame(user_missing_info, show_missing_info)
            user_changes=pd.DataFrame(user_missing_info, show_missing_info)
            user_changes_json=user_changes.to_json()    
            updated_json=json.dumps(update_user_json(search_results_to_json, user_changes_json))
            updated_row=pd.read_json(updated_json)
            updated_db.loc[results_index] =(updated_row.loc[results_index])
            st.dataframe(updated_db)
            preview_success=True
        except:
            st.warning("**Please ensure all fields selected from the 'Add Missing Information' dropdown are filled in AND fields have correct data e.g. numerical data for SVLMx**")
                #st.warning()
        if preview_success:
         user_comments = st.text_area("**Additional comments (optional)**", height=30)
        
        
        commit_addition=st.button("Submit Addition")
        

        if user_comments=="":
            user_comments="n/a"
        
        if commit_addition and len(show_missing_info) == len(user_missing_info) and len(show_missing_info) == len(additional_info_sources) :
            add_to_database(str(now), user_changes_json, search_results_to_json, "Information Addition", species_dropdown,  genus_dropdown, st.session_state["username"], user_comments, "Pending", "n/a", "n/a", "n/a", latest_approved_ds, sources_review_json, st.session_state['image_ids'] )
            if 'image_ids' in st.session_state:
             del st.session_state['image_ids']
            st.markdown('<p style="font-family:sans-serif; color:Red; font-size: 30px;"><strong>***      ADDITION SUBMITTED        ***</strong></p>', unsafe_allow_html=True)
        elif commit_addition and len(show_missing_info) != len(user_missing_info) or len(show_missing_info) != len(additional_info_sources):
            st.markdown("Please check all fields selected and sources have been provided in order to submit")





#--------------------------------------------------------------------------EDIT SPECIES INFORMATION PAGE------------------------------------------------------------------------------------#
def edit_species_information():
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/248177756.jpg");
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
 #url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr52l_orig.jpg"
    add_bg_from_url()
    
    image_folder_id = "1g_Noljhv9f9_YTKHEhPzs6xUndhufYxu"
    image_id=[]
    #current image linking methods
    def upload_image():
            if 'image_ids' in st.session_state:
                image_ids = st.session_state['image_ids']
            else:
                image_ids = []

            #col1.markdown("**No images available**")
            uploaded_image = col1.file_uploader("Choose an image", type=["jpg", "png", "bmp", "gif", "tiff"])
            if uploaded_image is not None:
                col1.write("**Image preview**")
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





    existing_info_columns = []
    def get_missing_info_columns(results):
        for column in dbColumns:
            if  not results[column].isna().any():
                existing_info_columns.append(results[column].name)
        return existing_info_columns

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
            col1.write("**Image preview**")
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
   
   #-----------------------------------------------------------------EDIT SPECIES INFO MAIN PAGE-------------------------------------------------#
    headercol1, headercol2, headercol3=st.columns(3)
    headercol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 30px;"><em><strong>Edit Species Information</strong></em></p>', unsafe_allow_html=True)
    current=load_latest()
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
    show_missing_info=st.multiselect("Edit Current Information", existing_info_columns)

    if show_missing_info:
        get_missing_userinfo()

    results_copy=species_results.copy()

    results_updated=update_missing_results(show_missing_info)

    show_results=st.checkbox("Show updates")
 
    compared=species_results.iloc[0].equals(results_updated.iloc[0])

    if show_results and compared:
        st.warning("**No information has been changed. Please select at lease one option from Add Missing Information dropdown**")
    elif show_results and len(show_missing_info) != len(user_missing_info):
        st.warning("**Please ensure values are added for each field selected**")
    elif show_results and not compared: 
        comparecol1,comparecol2, comparecol3=st.columns(3)
        comparecol1.write("**Original Species**")
        comparecol1.dataframe(species_results.iloc[0], width=300)
        comparecol3.write("**Updated Species Info**")
        comparecol3.dataframe(results_updated.iloc[0], width=300)
    
    sourcecol1,sourcecol2,sourcecol3=st.columns(3)
    sourcecol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
    sourcecol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*Information Sources*</strong></p>', unsafe_allow_html=True)
    sourcecol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
    create_source_fields(show_missing_info)

    sourcesum1, sourcesum2,sourcesum3=st.columns(3)
    source_summary=sourcesum2.button("Review Sources Summary")
    sources_review_dataframe = pd.DataFrame(additional_info_sources, show_missing_info)
    sources_review_json=sources_review_dataframe.to_json(orient="columns")
    if source_summary:
    
        sumcol1,sumcol2,sumcol3=st.columns(3)
        if not additional_info_sources:

         st.warning("Please ensure sources are provided for each information point")
        else:
            
            sumcol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Field</strong></em></p>', unsafe_allow_html=True)
            sumcol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><em><strong>Source</strong></em></p>', unsafe_allow_html=True)
            sources_parsed=json.loads(sources_review_json)
            for key, value in sources_parsed.items():
                for inner_key, inner_value in value.items():
                    sumcol1.markdown("***")
                    sumcol1.markdown("**"+inner_key+"**")
                    sumcol3.markdown("***")
                    sumcol3.markdown("*"+inner_value+"*")
                    

    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*****************************************************************************************</strong></p>', unsafe_allow_html=True)

    preview_updated_dataset=st.checkbox("**View updated dataset and submit**")

    if preview_updated_dataset and len(show_missing_info) != len(user_missing_info):
            st.warning("**Please ensure values are added for each field selected**")
    preview_success= False
        
        
    if  preview_updated_dataset and  len(show_missing_info) != len(additional_info_sources):
            st.warning("**Please ensure sources are added for each field selected**")
    preview_success=False

    if preview_updated_dataset and len(show_missing_info) == len(additional_info_sources) and len(show_missing_info) == len(user_missing_info) :
    
        results_index=species_results.index[0]
        updated_db=current.copy()
        search_results_to_json=species_results.to_json(orient="columns")
        try:
            pd.DataFrame(user_missing_info, show_missing_info)
            user_changes=pd.DataFrame(user_missing_info, show_missing_info)
            user_changes_json=user_changes.to_json()    
            updated_json=json.dumps(update_user_json(search_results_to_json, user_changes_json))
            updated_row=pd.read_json(updated_json)
            updated_db.loc[results_index] =(updated_row.loc[results_index])
            st.dataframe(updated_db)
            preview_success=True
        except:
            st.warning("**Please ensure all fields selected from the 'Add Missing Information' dropdown are filled in AND fields have correct data e.g. numerical data for SVLMx**")
                #st.warning()
        if preview_success:
         user_comments = st.text_area("**Additional comments (optional)**", height=30)
        
        
        commit_addition=st.button("Submit Addition")
        

        if user_comments=="":
            user_comments="n/a"
        
        if commit_addition and len(show_missing_info) == len(user_missing_info) and len(show_missing_info) == len(additional_info_sources) :
            add_to_database(str(now), user_changes_json, search_results_to_json, "Information Edit", species_dropdown,  genus_dropdown, st.session_state["username"], user_comments, "Pending", "n/a", "n/a", "n/a", latest_approved_ds, sources_review_json, st.session_state['image_ids'] )
            if 'image_ids' in st.session_state:
             del st.session_state['image_ids']
            st.markdown('<p style="font-family:sans-serif; color:Red; font-size: 30px;"><strong>***      ADDITION SUBMITTED        ***</strong></p>', unsafe_allow_html=True)
        elif commit_addition and len(show_missing_info) != len(user_missing_info) or len(show_missing_info) != len(additional_info_sources):
            st.markdown("Please check all fields selected and sources have been provided in order to submit")


#--------------------------------------------------------------------------GABiP EDIT OPTIONS------------------------------------------------------------------------------------#
def show_options():
    options=st.sidebar.radio("Options", ('Show Full Database','New Species Entry', 'Add Species Information','Edit Species Information' , 'Remove a Species', 'Remove Species Data'), key='current_option')     
    
    if options == "Show Full Database":
        show_db()
    if options == "New Species Entry":
        add_entry_page()
    if options == 'Add Species Information':
        add_species_information()
    if options == 'Edit Species Information':
        edit_species_information()












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
#https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/248177756.jpg
authenticator = stauth.Authenticate(email, username, hashed_passwords, "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


if authentication_status == False:
     st.error("Username/password is not recognised")
     st.write("Forgotten username/password? Enter your email below and we'll send a reminder")

     sendReminder = st.checkbox("Send Password Reminder")
     if sendReminder:
         email=st.text_input("Email address")
         sendbutton=st.button("Send reminder")
         if sendbutton and email:
             sendEmail(email)
             st.success("Email sent...please check your inbox for a password reset link")
         elif sendbutton:
             st.warning("Please enter an email address")
elif authentication_status == None:
     st.warning("Please enter username and password")
else:
     for user in users:
         if user["username"] == st.session_state['username'] and user["admin"] == "True":
             st.write("Welcome, you're an admin.")
             show_options()         
         elif user["username"] == st.session_state['username'] and user["admin"] == "False":
             if user["approved"] == "True":
                 st.write(f"Welcome {user['firstname']}, you're a trusted member.")
                 show_options()
             else:
                 st.write(f"Welcome {user['firstname']}, your access request is pending approval. We'll send you an e-mail alert to inform you of the status.")
  
authenticator.logout("Logout", "sidebar")





