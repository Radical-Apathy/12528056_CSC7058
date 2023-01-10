from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
from dotenv import load_dotenv
from datetime import datetime


#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

metaData=deta_connection.Base("database_metadata")

#------------------------------------------------------------METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = metaData.fetch()
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

path=get_latest()

@st.cache
def load_latest():
    current_db = pd.read_csv(path, encoding= 'unicode_escape', low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated

#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#

st.header("Addition")

st.write("Current Database")
current=load_latest()
currentstyled=current.style.set_properties(**{'background-color':'white', 'color':'black'})
st.write(current)

st.write("changes file example ")
changes=pd.read_csv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/changes.csv", encoding= 'unicode_escape', low_memory=False)
highlighted=changes.style.set_properties(**{'background-color':'yellow', 'color':'black'})
st.write(highlighted)
st.subheader("DB updated with changes")

st.write("User comments")
st.write("User source citation")

st.subheader("Current db with changes added")
updated=add_changes(current, changes)
st.write(updated)

