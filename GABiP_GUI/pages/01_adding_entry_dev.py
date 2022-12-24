from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
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
#------------------------------------------------------------METHODS-----------------------------------------------------------------------------------------#

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

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated


def create_new_csv(dataframe, path):
    new_dataframe.to_csv(path,index=False)

path=get_latest()

@st.cache
def load_latest():
    current_db = pd.read_csv(path, encoding= 'unicode_escape', low_memory=False)
    return current_db


current_db=load_latest()



#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#
st.header('Add Entry page')


st.write(current_db)

path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"




#add entry form

with st.form("my_form"):
          st.write("Inside the form")
          order =st.text_input("Order","Order - e.g. Anura", key='Order')
          family =st.text_input("Family","Family - e.g. Allophrynidae", key='Family')
          genus =st.text_input("Genus", "Genus - e.g. Allophryne", key='Genus')
          species =st.text_input("Species","Species - e.g. Relicta", key='Species')
          submitted = st.form_submit_button("Submit")
          if submitted:
            st.write(order, family, genus, species)


#new_dataframe=({"Order":[order], "Family":[family], "Genus":[genus], "Species":[species]})
new_dataframe=({"Order":[order], "Family":[family], "Genus":[genus], "Species":[species]})

new_dataframe=pd.DataFrame(new_dataframe)
st.write("values added "+ new_dataframe)
#st.write(new_dataframe)
#st.write(new_dataframe)
updatedDataframe=(add_changes(current_db, new_dataframe))
st.write(updatedDataframe)

path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"
now=str(datetime.now())
#new_path=path_prefix+now+".csv"

#st.write(new_path)
#new_dataframe.to_csv(f"C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/changes.csv", index=False)

#updatedDataframe.to_csv(new_path)

#def create_new_csv(dataframe, path):
 #   new_dataframe.to_csv(path,index=False)

#def insert_csv(date_time, file_Path, edit_type, username, status):
#    """adding user"""
    #defining the email as the key
#    return metaData.put({"key":date_time, "File_Path": file_Path, "Edit_Type": edit_type, "Edited_By":username, "Status":status })

#insert_csv(now, "C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/newDB.csv", "Addition","To Compare", "Pending Approval")