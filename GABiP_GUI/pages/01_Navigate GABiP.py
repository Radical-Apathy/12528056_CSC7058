import streamlit_authenticator as stauth
import streamlit as st
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
#--------------------------------------------------------------------Database Connections-------------------------------------------------------------------------------------#
#------------------------------------------------------------DATABASE_METADATA DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

database_metadata=deta_connection.Base("database_metadata")


#------------------------------------------------------------IMAGES DATABASE CONNECTION-----------------------------------------------------------------------------------------#
users_images=deta_connection.Base("user_images")

def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
     return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })

def get_all_user_images():
    res = users_images.fetch()
    return res.items
user_images=get_all_user_images()
#------------------------------------------------------------ DATABASE_METADATA DATABASE METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = database_metadata.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()



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
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')
    return current_db

try:
     current=load_latest()
except HttpError as error:
     st.write(f"An HTTP error {error.resp.status} occurred: {error.content}")
except RefreshError:
        st.write("The credentials could not be refreshed.")
except Exception as error:
        st.write(f"An error occurred: {error}")

#--------------------------------------------------------------------Methods---------------------------------------------------------------------------------------------------#

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
        


def ref_generator_top(speciesInfo):
    mergedRef = pd.merge(speciesInfo, dfReferences, on='Order')
    #order references from most recent
    sortedYear =mergedRef.sort_values(by='Year', ascending=False)
    displaymergedRef = sortedYear[["Year","Reference", "Order"]]
    displaymergedRef.drop_duplicates()
    return displaymergedRef.head()

def ref_generator_all(speciesInfo):
    mergedRef = pd.merge(speciesInfo, dfReferences, on='Order')
    #order references from most recent
    sortedYear =mergedRef.sort_values(by='Year', ascending=False)
    displaymergedRef = sortedYear[["Year","Reference", "Order"]]
    return displaymergedRef.drop_duplicates()

def rangeSVLMx(dataframe, svlmxRange):
    maskRange=current["SVLMx"].between(*svlmxRange)
    maskedRange=current[maskRange]
    #maskedRange.sort_values(by='SVLMx', ascending=True)
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.SVLMx])
   # maskedRangedf.sort_values(by='SVLMx', ascending=True)
    #st.write(maskedRangedf.sort_values(by='SVLMx', ascending=True))
    st.write(maskedRangedf)


def clutchRange(dataframe,  clutchSize):
    maskRange=current["Clutch"].between(*clutchSize)
    maskedRange=current[maskRange]
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.Clutch])
    #sortedYear =mergedRef.sort_values(by='Year', ascending=False)
    st.write(maskedRangedf)

def eggDiameterRange(dataframe,  eggSize):
    maskRange=current["EggDiameter"].between(*eggSize)
    maskedRange=current[maskRange]
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.EggDiameter])
    st.write(maskedRangedf)




#--------------------------------------------------------------------Navigate Dateset Main Page---------------------------------------------------------------------------------#


def background():
        st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/248177756.jpg");
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
    



headercol1, headercol2,  headercol3=st.columns(3)

headercol2.markdown('<p style="font-family:sans-serif; color:White; font-size: 30px;"><em><strong>Search Dataset</strong></em></p>', unsafe_allow_html=True)
    
current=load_latest()


species_alphabetical=(sorted(current["Species"].drop_duplicates(), reverse=False))

additional_info_sources=[]

species_dropdown=st.selectbox("Select a species", (species_alphabetical))

species_genus=current.loc[current["Species"]==species_dropdown]

genus_dropdown=st.selectbox("Select "+species_dropdown+ " Genus", species_genus["Genus"])

species_results=current.loc[(current["Species"] == species_dropdown) & (current['Genus'] == genus_dropdown)]

    
   
   
col1, col2, col3 = st.columns(3)

col3.markdown("**All Genera of** "+species_dropdown)

col3.dataframe(species_genus["Genus"])


col2.write(f"{genus_dropdown} {species_dropdown} Summary")

col2.dataframe(species_results.iloc[0], width=500)


#formaing a dataframe that can be grouped with the references
species_dataframe=current.groupby("Species").get_group(species_dropdown)

col1.markdown(f"[![]({link_image(species_results)})]({link_embedded_image(species_results)})")
url= url="https://amphibiansoftheworld.amnh.org/amphib/basic_search/(basic_query)/"+species_dropdown
col1.write("AMNH web link for "+ species_dropdown+  " [AMNH Link](%s)" % url)
url2="https://amphibiaweb.org/cgi/amphib_query?where-scientific_name="+ species_dropdown +"&rel-scientific_name=contains&include_synonymies=Yes"
col1.write("Amphibian web link for "+ species_dropdown+  " [Amphibia Web Link](%s)" % url2)




tab1, tab2, tab3, tab4= st.tabs(["Literature References - Most Recent", "See All Literature References", "Public Contributed Data", "Search Species by Range"])

with tab1:
    references_dataframe=ref_generator_top(species_dataframe)
    if references_dataframe.empty:
         st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No documented literary references for {species_dropdown}</strong></em></p>', unsafe_allow_html=True)
    else:
         st.write(references_dataframe)
with tab2:
    all_references_dataframe=ref_generator_all(species_dataframe)
    if all_references_dataframe.empty:
         st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>No documented literary references for {species_dropdown}</strong></em></p>', unsafe_allow_html=True)
    else:
         st.write(all_references_dataframe)


with tab3:
    
    st.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>See Species Audit History</strong></em></p>', unsafe_allow_html=True)


with tab4:
    range_col1, range_col2, range_col3=st.columns(3)

    range_col2.markdown(f'<p style="font-family:sans-serif; color:White; font-size: 20px;"><em><strong>Filter Species by Ranges</strong></em></p>', unsafe_allow_html=True)
    ranges=st.radio('Range Search: ', ['BodySize', 'Clutch Size', 'Egg Diameter'], key='range_options')
        # ranges=st.radio('Range Search: ', st.session_state.radio_options, key='radio_options')
    if ranges == 'BodySize':
        svlmxRange= st.slider('SVLMx Range searching', 0.0, 1700.0, (850.0, 1700.0), key='BodySize_slider')
        rangeSVLMx(current, svlmxRange)
    if ranges=="Clutch Size":
        clutchSize= st.slider('Clutch Size', 0.0, 1700.0, (850.0, 1700.0), key='ClutchSize_slider')
        clutchRange(current, clutchSize)
    if ranges=="Egg Diameter":
        eggSize= st.slider('Egg Diameter', 0.0, 20.0, (10.0, 20.0), key='EggDiameter_slider') 
        eggDiameterRange(current, eggSize)  

        
     