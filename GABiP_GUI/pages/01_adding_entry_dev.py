from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
import csv
from dotenv import load_dotenv
from datetime import datetime
st.set_page_config(page_icon='amphibs.jpeg')

#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

metaData=deta_connection.Base("database_versions")


#st.session_state['username']
#------------------------------------------------------------ DATABASE METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = metaData.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=[database["Status"] for database in databases]
path = [database["File_Path"] for database in databases]

#getting the most recent approved csv file
def get_latest():
    for database in databases:
     for i in date_time:
        
      if database["key"]== i and database["Status"] =="Approved":
        break
    return(database["File_Path"])

#add user's entries to csv 
def insert_csv(date_time, file_Path, edit_type, username, status):
    """adding user"""
    return metaData.put({"key":date_time, "File_Path": file_Path, "Edit_Type": edit_type, "Edited_By":username, "Status":status })

#append user's edit to current csv

#def add_changes(dataframe, dataframe2):
#    updated=dataframe.append(dataframe2, ignore_index = True)
#    return updated

path=get_latest()

@st.cache
def load_latest():
    current_db = pd.read_csv(path, encoding= 'unicode_escape', low_memory=False)
    return current_db


current_db=load_latest()






#------------------------------------------------------------SESSION STATE INITIATION-----------------------------------------------------------------------------------------#

#st.session_state

def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""
         

#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#
st.header('Add Entry page')

st.write(current_db)
path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"
dbColumns=current_db.columns

#creating session state variables for csv columns
create_session_states(dbColumns)

def blank_validation(states=['order','family','genus','species']):
    for i in states:
     if i=="":
        st.warning("Order, Family, Genus, Species fields can not be left blank. Please recheck mandatory field section")

userInfo=[]
#without a form
st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 30px;"><strong>***       Mandatory Fields         ***</strong></p>', unsafe_allow_html=True)
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



def display_extra_fields():
    for option in more_options:
        userText=st.text_input(option, key=option)
        st.session_state[option] == userText
    

def get_extra_userinfo():
    for option in more_options:
        
        userText=st.text_input(option, key=option)
        if userText:
         st.session_state[option] == userText
        elif not userText :
            st.session_state[option]==""
      


if more_options:
    get_extra_userinfo()

#st.write(current_db.columns)
def populate_userinfo():
    for column in dbColumns:
        userInfo.append(st.session_state[column])
   


def construct_complete_dataframe(userinfo, dbcolumns):
    completed = pd.DataFrame(userInfo, dbColumns)
    st.write(completed) 

def construct_complete_dataframe_columns(userinfo, columns=current_db.columns):
    completed = pd.DataFrame(userInfo, current_db.columns)
    st.write(completed) 



def submit_changes():
    populate_userinfo()
    new_dataframe=pd.DataFrame(userInfo, columns=dbColumns)
    
review_information=st.button("Review Information")

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated
    
#checking that both the genus and species submitted don't exist on current csv    
def check_current_db(genus, species):
    if genus.lower() in current_db["Genus"].str.lower().values and species.lower() in current_db["Species"].str.lower().values:
        st.warning(f"Data already exists for " +genus+ " " +species+ " Check full dataset option and consider making and edit to current dataset instead of an addition") 
   
    

if review_information:
    
    populate_userinfo()
    blank_validation([st.session_state['Order'], st.session_state['Family'], st.session_state['Genus'], st.session_state['Species']])
    check_current_db(st.session_state['Genus'], st.session_state['Species']) 
    userdf=construct_complete_dataframe_columns(userInfo, columns=current_db.columns)
    
 
    

commit_changes=st.button("Submit for review")




now=datetime.now()
#
timeStamp=now.strftime("%d.%m.%Y-%H.%M.%S")
st.write(now)
newPath=""
def create_csv(columnrow, inforow):
    path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/pending changes/"
    path_end = timeStamp
    newPath=path_prefix+path_end+"-"+st.session_state['username']+".csv"
 
    with open(newPath,  'w', encoding= 'UTF8', newline='') as f:
        writer=csv.writer(f)
        writer.writerow(columnrow)
        writer.writerow(inforow)
    return newPath
        

if commit_changes:
    populate_userinfo()
    columnrow=current_db.columns
    inforow=userInfo
    
    create_csv(columnrow, inforow)
    
    st.write("Changes submitted")
  



 

