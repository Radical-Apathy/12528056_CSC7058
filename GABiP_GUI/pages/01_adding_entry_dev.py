from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
from dotenv import load_dotenv
st.set_page_config(page_icon='amphibs.jpeg')



#-------------------------------DATABASE CONNECTION------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

metaData=deta_connection.Base("database_versions")


st.session_state['username']
#------------------------------------METHODS--------------------------------------------#
#check for the most recent approved csv version
currentPath=""

@st.cache
def load_cleaned():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

#add user's entries to csv 
def insert_csv(date_time, file_Path, edit_type, username, status):
    """adding user"""
    #defining the email as the key
    return metaData.put({"key":date_time, "File_Path": file_Path, "Edit_Type": edit_type, "Edited_By":username, "Status":status })



















#-----------------------------------MAIN PAGE--------------------------------------------#
st.header('Add Entry page')

with st.form("my_form"):
          st.write("Inside the form")
          order =st.text_input("Order","Order - e.g. Anura", key='Order')
          family =st.text_input("Family","Family - e.g. Allophrynidae", key='Family')
          genus =st.text_input("Genus", "Genus - e.g. Allophryne", key='Genus')
          species =st.text_input("Species","Species - e.g. Relicta", key='Species')
          submitted = st.form_submit_button("Submit")
          if submitted:
            st.write(order, family, genus, species)