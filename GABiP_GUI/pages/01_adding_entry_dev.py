import streamlit as st
import pandas as pd
import numpy as np
import os
from deta import Deta
import csv
from dotenv import load_dotenv
from datetime import datetime
st.set_page_config(page_icon='amphibs.jpeg')

#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

database_metadata=deta_connection.Base("database_metadata")


#------------------------------------------------------------ METADATABASE METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = database_metadata.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=[database["Status"] for database in databases]
path = [database["Current Dataset"] for database in databases]

#getting the most recent approved csv file
def get_latest():
    for database in databases:
     for i in date_time:
        
      if database["key"]== i and database["Status"] =="Approved":
        break
    return(database["Current Dataset"])

#add user's entries to csv 
def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, approved_by, date_approved, current_database_path):
    """adding user"""
    #defining the email as the key
    return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Approved_By":approved_by, "Date_Approved":date_approved, "Current Dataset":current_database_path })


path=get_latest()

@st.cache
def load_latest():
    current_db = pd.read_csv(path, encoding= 'unicode_escape', low_memory=False)
    return current_db


current_db=load_latest()

#------------------------------------------------------------SESSION STATE INITIATION-----------------------------------------------------------------------------------------#

if 'comment' not in st.session_state:
    st.session_state['comment']=""

#creating session state variables for each column in dataset
def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""
         
#st.session_state["username"]

#------------------------------------------------------------METHODS----------------------------------------------------------------------------------------------------------#

#enforcing mandatory fields
def blank_validation(states=['order','family','genus','species']):
    for i in states:
     if i=="":
        st.warning("Order, Family, Genus, Species fields can not be left blank. Please recheck mandatory field section")

#displays text fields for optional information
def display_extra_fields():
    for option in more_options:
        userText=st.text_input(option, key=option)
        st.session_state[option] == userText

#sets session state values for optional extra fields
def get_extra_userinfo():
    for option in more_options:
        
        userText=st.text_input(option, key=option)
        if userText:
         st.session_state[option] == userText
        elif not userText :
            st.session_state[option]==""

#stores user info in an array      
def populate_userinfo():
    for column in dbColumns:
        userInfo.append(st.session_state[column])

#checking that both the genus and species submitted don't exist on current csv    
def check_current_db(genus, species):
    if genus.lower() in current_db["Genus"].str.lower().values and species.lower() in current_db["Species"].str.lower().values:
        st.warning(f"Data already exists for " +genus+ " " +species+ " Check full dataset option and consider making and edit to current dataset instead of an addition") 

#contructs a dataframe for user to see summary of their addition
def construct_review_dataframe(userinfo, columns=current_db.columns):
    completed = pd.DataFrame(userInfo, current_db.columns)
    st.write(completed) 

#creates a csv file with users addition
def create_csv(columnrow, inforow):
    with open(newPath,  'w', encoding= 'UTF8', newline='') as f:
        writer=csv.writer(f)
        writer.writerow(columnrow)
        writer.writerow(inforow)

#------------------------------------------------------------MAIN PAGE--------------------------------------------------------------------------------------------------------#
st.header('Add Entry page')

st.write(current_db)
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


#--------------------------------------------------------------------------------------------MANAGING ADDITIONAL FIELDS -------------------------------------------------------#
st.markdown('***')
st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>More Options</strong></p>', unsafe_allow_html=True)
more_options=st.multiselect("Add more Information", ['SVLMMx', 'SVLFMx', 'SVLMx', 'Longevity', 'NestingSite', 'ClutchMin',	'ClutchMax',
                             'Clutch', 'ParityMode',	'EggDiameter', 'Activity',	'Microhabitat', 'GeographicRegion',	'IUCN',	
                             'PopTrend',	'RangeSize', 'ElevationMin','ElevationMax','Elevation'])


if more_options:
    get_extra_userinfo()


   
review_information=st.button("Review Information")
       

if review_information:
    
    populate_userinfo()
    blank_validation([st.session_state['Order'], st.session_state['Family'], st.session_state['Genus'], st.session_state['Species']])
    check_current_db(st.session_state['Genus'], st.session_state['Species']) 
    userdf=construct_review_dataframe(userInfo, columns=current_db.columns)
    

user_message=st.text_area("Please leave a comment citing the source for this addition", key='comment')
    

commit_changes=st.button("Submit for review")

now=datetime.now()
timeStamp=now.strftime("%d.%m.%Y-%H.%M.%S")
path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/pending changes/Additions/"
path_end = timeStamp
newPath=path_prefix+path_end+"-"+st.session_state['username']+".csv"

        
if commit_changes and user_message:
    populate_userinfo()
    columnrow=current_db.columns
    inforow=userInfo
    create_csv(columnrow, inforow)
    #add_to_database(str(now), newPath, get_latest(), "Addition", st.session_state["Species"], st.session_state["Genus"], st.session_state["username"], st.session_state["comment"], "Pending", "n/a", "n/a", "n/a", get_latest())
    st.markdown("Changes submitted")    

elif commit_changes and user_message=="":
    st.error("Please add a source")
  



 

