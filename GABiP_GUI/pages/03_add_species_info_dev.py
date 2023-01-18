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

#------------------------------------------------------------metadata METHODS-----------------------------------------------------------------------------------------#

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

#getting the most recent approved csv file
#def get_latest():
 #   for database in databases:
  #   for i in date_time:
        
 #     if database["key"]== i and database["Status"] =="Approved":
 #       break
 #   return(database["Current Dataset"])

#path=get_latest()

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

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated


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

#-----------------------------------------------------------SESSION STATES-----------------------------------------#
#if "reason" not in st.session_state:
#   st.session_state['reason'] ==""

#st.session_state
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

def displayImage(speciesInfo):
    mergedInfo=pd.merge(speciesInfo, dfImages, on="Species")
    mergedInfo.drop_duplicates()
    return mergedInfo["Display Image"].loc[0]

def embeddedImage(speciesInfo):
    mergedInfo=pd.merge(speciesInfo, dfImages, on="Species")
    mergedInfo.drop_duplicates()
    return mergedInfo["Embedded Link"].loc[0]


speciesdf= []
def speciesSearchTest(speciesChoice): # formally option2
    col1,col2=st.columns(2)
    col1.header(speciesChoice, " Species Summary:")
    #speciesInfo = dfFull.groupby("Species").get_group(st.session_state['text_option']) # only definition of the three speciesInfo that works
    speciesInfo=current.groupby("Species").get_group(speciesChoice)
    #speciesInfo = st.session_state['drop_option']
    #st.session_state.speciesInfo = speciesInfo
    col1.markdown("[![Image not Available]("+displayImage(speciesInfo)+")]("+embeddedImage(speciesInfo)+")")
    url= url="https://amphibiansoftheworld.amnh.org/amphib/basic_search/(basic_query)/"+speciesChoice
    col1.write("AMNH web link for "+ speciesChoice+  " [AMNH Link](%s)" % url)
    url2="https://amphibiaweb.org/cgi/amphib_query?where-scientific_name="+ speciesChoice +"&rel-scientific_name=contains&include_synonymies=Yes"
    col1.write("Amphibian web link for "+ speciesChoice+  " [Amphibia Web Link](%s)" % url2)
    col2.header("Species Summary")
    
   # tab1, tab2= st.tabs(["Literature References - Most Recent", "See All References"])
   # with tab1:
   #    st.write(refGeneratorTop(speciesInfo)) 
   # with tab2:
   #     st.write(refGeneratorAll(speciesInfo))
    #speciesdf.append(speciesInfo["Genus"])
    #speciesdf.append(speciesInfo["GeographicRegion"])
    #speciesdf.append(speciesInfo["SVLMMx"])
    #speciesdf.append(speciesInfo["RangeSize"])
    #speciesdf.append(speciesInfo["ElevationMin"])
    #speciesdf.append(speciesInfo["ElevationMax"])
    #speciesdf.append(speciesInfo["IUCN"])
    #speciesdatadf=pd.DataFrame(speciesdf)
    #hide_row_no="""<style>
   #         thead tr th:first-child {display:none}
    #        tbody th {display:none}
     #       </style>"""
    #st.markdown(hide_row_no, unsafe_allow_html=True)
    #col2.write(speciesdatadf)
    #showMore = col2.checkbox("Show All")
    

    #if showMore:
    allInfo=current.groupby("Species").get_group(speciesChoice)
    infoSummary=allInfo.iloc[0]
    col2.dataframe(allInfo.iloc[0], width=500)
    #pd.DataFrame(infoSummary)
    #col2.write(infoSummary.style.highlight_null(null_color='green'), width=500)
      
    
def show_knowledge_gaps():
    st.write("knowledge gaps")
#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#

st.header("Add New Species Info Dev")
current=load_latest()
#st.dataframe(df.style.highlight_null(null_color='red'))
showgaps=st.checkbox("Show knowledge gaps")
if showgaps:
    st.write("Current Database")
    st.dataframe(current.style.highlight_null(null_color='yellow'))



speciesdropdown=st.selectbox("Select a species to add to: ", (current['Species']))

speciesSearchTest(speciesdropdown)

speciestext=st.text_input("Manual Species Search: ", "relicta") 
speciesSearchTest(speciestext)           


