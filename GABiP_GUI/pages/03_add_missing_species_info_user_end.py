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
#from PIL import Image
import base64

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


latestds=get_latest_ds(approvedordered[0])

#method to select edits that are new species addition and pending
pending=[]

#gets dates for new species additions needing approval
def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

ordered=sorted(pending,reverse=True)


@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape', low_memory=False)
    return current_db


@st.cache
def load_full():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull
def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated


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

#------------------------------------------------------------METHODS -----------------------------------------------------------------------------------------#

@st.cache
def load_references():
    dfReferences = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/Reference_List.csv', encoding= 'unicode_escape', low_memory=False)
    return dfReferences

@st.cache
def load_images():
    dfImages = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/image_database.csv', encoding= 'unicode_escape', low_memory=False)
    return dfImages

dfReferences = load_references()
dfImages = load_images()


missingInfoColumns=[]
def get_missing_info_columns(results):
    for column in dbColumns:
        if results[column].isna().any():
         missingInfoColumns.append(results[column].name)
    return missingInfoColumns


usermissinginfo=[]
def get_missing_userinfo():
     for option in show_missing_info:
        userText=st.text_input(option, key=option)
        if userText:
         usermissinginfo.append(st.session_state[option])
     return usermissinginfo


def populate_missing_info():
        for column in dbColumns:
            additionalInfo.append(st.session_state[column])

def update_missing_results(show_missing_info): 
    speciesIndex=results.index[0]
    results_updated = results.copy()
    for column in show_missing_info:
        results_updated.at[speciesIndex, column] = st.session_state[column]
    return results_updated

now=datetime.now()

def upload_image():
    col1.markdown("**No images available**")
    uploaded_file = col1.file_uploader("Choose an image", type=["jpg", "png", "bmp", "gif", "tiff"])

def link_image(results):
    merged_image_df = pd.merge(results, dfImages, left_on=['Genus', 'Species'], right_on=['Genus', 'Species'], how='inner')
    if  merged_image_df["Display Image"].iloc[0] == "https://calphotos.berkeley.edu image not available":
        upload_image()
    else:
        col1.write("Image from amphibiaweb.org")
        return merged_image_df["Display Image"].iloc[0]
      

def link_embedded_image(results):
    embedded_image_df= pd.merge(results, dfImages, left_on=['Genus', 'Species'], right_on=['Genus', 'Species'], how='inner')
    if  embedded_image_df["Display Image"].iloc[0] != "https://calphotos.berkeley.edu image not available":
        return embedded_image_df["Embedded Link"].iloc[0]


#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#
#C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/gabip images/dataset_thumbnail.jpeg
#st.image("amphibs.jpeg", width=200)
#"C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/gabip images/black_and_green_frog.jpg"
headercol1, headercol2, headercol3=st.columns(3)
headercol1.image("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/gabip images/black_and_green_frog.jpg", width=200)

headercol2.subheader("Add Species Info Dev")
current=load_full()
dbColumns=current.columns
create_session_states(dbColumns)

allgenus=[]
def get_genus(speciesdropdown):
    allgenus=current.loc[current["Species"]==speciesdropdown]
    return allgenus


additionalInfo=[]

missingInfoSources=[]

speciesdropdown=st.selectbox("Select a species to add to: ", (current['Species']))

speciesGenus=current.loc[current["Species"]==speciesdropdown]

genusdropdown=st.selectbox("Select "+speciesdropdown+ " Genus", speciesGenus["Genus"])

results=current.loc[(current["Species"] == speciesdropdown) & (current['Genus'] == genusdropdown)]


sourcefields=[]
summarydf=[]

def create_source_fields(show_missing_info):
       for option in show_missing_info:
               usersource=st.text_input("Please enter a source for "+option, key=option+" source")

       for option in show_missing_info:
           if usersource and usersource!="":
               st.session_state[option+" source"]==usersource
               missingInfoSources.append(st.session_state[option+" source"])
           
       return missingInfoSources
   
col1, col2, col3 = st.columns(3)

col3.markdown("**All Genea of** "+speciesdropdown)

col3.dataframe(speciesGenus["Genus"])


col2.write(f"{genusdropdown} {speciesdropdown} Summary")

col2.dataframe(results.iloc[0], width=500)

col1.markdown(f"[![]({link_image(results)})]({link_embedded_image(results)})")

get_missing_info_columns(results)
show_missing_info=st.multiselect("Add Missing Information", missingInfoColumns)

if show_missing_info:
     get_missing_userinfo()

resultscopy=results.copy()

resultschanged=update_missing_results(show_missing_info)


showresults=st.checkbox("Show updates")
 


if showresults:
    methodcol1, methodcol2, methodcol3=st.columns(3)
    methodcol2.dataframe(update_missing_results(show_missing_info).iloc[0], width=300)
    diff_mask = results != resultschanged

    compare=st.button("Compare")
    if compare:
       
        comparecol1,comparecol2, comparecol3=st.columns(3)
        comparecol1.write("Original Species")
        comparecol1.dataframe(results.iloc[0], width=300)
        comparecol2.write("Updated Species Info")
        comparecol2.dataframe(resultschanged.iloc[0], width=300)
        comparecol3.write("Differences highlighted?")     

sourcecol1,sourcecol2,sourcecol3=st.columns(3)
sourcecol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
sourcecol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*Information Sources*</strong></p>', unsafe_allow_html=True)
sourcecol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
create_source_fields(show_missing_info)

sourcesum1, sourcesum2,sourcesum3=st.columns(3)
checkSummary=sourcesum2.button("View summary sources")

if checkSummary:
        sumcol1,sumcol2,sumcol3=st.columns(3)
        if not missingInfoSources:

         st.warning("Please ensure sources are provided for each information point")
        else:
            sourcesreviewdf = pd.DataFrame(missingInfoSources, show_missing_info)
            sumcol2.dataframe(sourcesreviewdf)

st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*****************************************************************************************</strong></p>', unsafe_allow_html=True)


previewwholedb=st.checkbox("Preview updated dataset")

if previewwholedb:
     resultschangedjson=resultschanged.to_json(orient='columns')
     st.write(resultschangedjson)
    
     newresults=pd.read_json(resultschangedjson)
     #st.write(newresults)
     st.write("updating whole dataset")
     speciesIndex=results.index[0]
    
     copied=current.copy()
   
     try:
        copied.loc[speciesIndex] =(newresults.loc[speciesIndex])
        st.write(copied) 
     except:
        st.warning("Please check that values entered are in correct format e.g. numerical for values such as SVLMMx")
    

subcol1,subcol2,subcol3 = st.columns(3)
submit_extra_info=subcol2.button("Submit")



jsondata=[]
def create_json_data():
  for column in missingInfoColumns:
      jsondata.append({column:st.session_state[column]})
  return jsondata

# st.write(usermissinginfo)
# def check_for_blanks(jsondata):
#      for value in {jsondata:value}:
#          if value =="":
# #              st.warning("Please ensure all fields selected have a value")

# def check_for_blanks(missingInfoColumns):
#       for column in missingInfoColumns:
#           if st.session_state[column] and st.session_state[column] =="":
#               st.warning("Please ensure all fields selected have a value")

create_json_data()
st.write(usermissinginfo)
if submit_extra_info:
   # check_for_blanks(missingInfoColumns)
    st.write("check user doesnt accidentally have blanks")
    


