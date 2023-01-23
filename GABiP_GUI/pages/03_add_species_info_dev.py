from re import search
import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
import os
from dotenv import load_dotenv
from datetime import datetime
from st_aggrid import AgGrid



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


@st.cache
def load_full():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull
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

#creating session state variables for each column in dataset
def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""

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
       

    #if showMore:
    allInfo=current.groupby("Species").get_group(speciesChoice)
    #infoSummary=allInfo.iloc[0]
    col2.dataframe(allInfo.iloc[0], width=500)

        
    
def show_knowledge_gaps():
    st.write("knowledge gaps")
#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#

st.header("Add Species Info Dev")
current=load_full()
dbColumns=current.columns
create_session_states(dbColumns)
#st.dataframe(df.style.highlight_null(null_color='red'))
#showgaps=st.checkbox("Show knowledge gaps")
#if showgaps:
#    st.write("Current Database")
#    st.dataframe(current.style.highlight_null(null_color='yellow'))
    #AgGrid(current, grid_options={'editable': True})

allgenus=[]
def get_genus(speciesdropdown):
    allgenus=current.loc[current["Species"]==speciesdropdown]
    return allgenus


#user_changes.iloc[0], width=300

additionalInfo=[]

speciesdropdown=st.selectbox("Select a species to add to: ", (current['Species']))

speciesGenus=current.loc[current["Species"]==speciesdropdown]

genusdropdown=st.selectbox("Select "+speciesdropdown+ " Genus", speciesGenus["Genus"])

results=current.loc[(current["Species"] == speciesdropdown) & (current['Genus'] == genusdropdown)]

st.dataframe(results.iloc[0], width=300)


st.write(speciesGenus)

#speciesSearchTest(speciesdropdown)



def replace_value(species, colname, value):
     speciesInfo=current.groupby("Species").get_group(species)
     #df.at[0, 'A'] = value
     speciesInfo.at[0, colname]=value
     st.dataframe(speciesInfo.iloc[0])
     st.write(speciesInfo["Species"] + " has been updated")

def get_extra_userinfo():
     for option in addinfo_options:
        
        userText=st.text_input(option, key=option)
        if userText:
         st.session_state[option] == userText
        #elif not userText :
         #   st.session_state[option]==""

def populate_additionLinfo():
        for column in dbColumns:
            additionalInfo.append(st.session_state[column])

def add_information():
    pass

   

addinfo_options=st.multiselect("Add Information", ['SVLMMx', 'SVLFMx', 'SVLMx', 'Longevity', 'NestingSite', 'ClutchMin',	'ClutchMax',
                             'Clutch', 'ParityMode',	'EggDiameter', 'Activity',	'Microhabitat', 'GeographicRegion',	'IUCN',	
                             'PopTrend',	'RangeSize', 'ElevationMin','ElevationMax','Elevation'])


#df.loc[0, 'A'] = 10

if addinfo_options:
     get_extra_userinfo()

st.write(additionalInfo)
 
methodcheck=st.checkbox("Practicing value replacement")
if methodcheck:
      
    #st.write(str(results.index.values))
    #df = pd.DataFrame(data, columns=columns, index=False)
    st.write(results.index.values.astype(int))
    #df = pd.DataFrame(data, columns=columns, index=False)
    st.write(results)
    results.at[5262,'NestingSite']="my nesting site"
    st.write(results)

jsonexperiemnt=st.checkbox("Convert results to a json file")

if jsonexperiemnt:
    st.write("Results as a dataframe")
    st.write(results)
    st.write("Results as json orient records")
    resultsjsonorient=results.to_json(orient='records')
    st.write(resultsjsonorient)
    st.write("Results as json orient columns")
    resultsjsoncols=results.to_json(orient='columns')
    st.write(resultsjsoncols)
    st.write("Results as json orient index")
    resultsjsonindex=results.to_json(orient='index')
    st.write(resultsjsonindex)
    st.write("Getting json data ")
    st.write(resultsjsoncols)
   
  
    
    


#speciestext=st.text_input("Manual Species Search: ", "relicta") 
#speciesSearchTest(speciestext)           


#genus count dev

#st.write("counting  occurances using .sum()")

#reps=(current["Species"] == "wittei").sum()

#st.write(reps)

#valueCounts=current["Species"].value_counts()

#st.write("Value counts")
#st.write(valueCounts)

#def get_genea_count(speciesname):
#    if ((current["Species"] == speciesname).sum()) >1:
#        st.write("More than one occurance of this")
    #for speciesname in current["Species"]:
     #   st.write(current["Genus"])


#get_genea_count(speciesdropdown)

#st.write("Printing row nums where species name is")
#st.write(current.loc[current["Species"]==speciesdropdown])

#st.write("Printing all genus")

