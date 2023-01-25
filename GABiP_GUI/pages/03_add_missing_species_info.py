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

jsondata=[]
def create_json_data():
  for column in dbColumns:
      jsondata.append({column:st.session_state[column]})
  return jsondata
#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#

headercol1, headercol2, headercol3=st.columns(3)
headercol2.subheader("Add Species Info")
#st.session_state
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

#st.write(genusdropdown)
#st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>More Options</strong></p>', unsafe_allow_html=True)
#st.markdown('Streamlit is **_really_ cool**.')
#st.markdown("This text is :red[colored red], and this is **:blue[colored]** and bold.")

col1, col2, col3 = st.columns(3)

col3.markdown("**All Genea of** "+speciesdropdown)

col3.write(genusdropdown)
col3.write(speciesGenus["Genus"].iloc[0])
col2.dataframe(results.iloc[0], width=500)
col1.write("Image Goes Here")

#st.write(speciesGenus)

#speciesSearchTest(speciesdropdown)





def get_extra_userinfo():
     for option in addinfo_options:
        
        userText=st.text_input(option, key=option)
        if userText:
         st.session_state[option] == userText
        #else :
         #   st.session_state[option]==""


def populate_additionLinfo():
        for column in dbColumns:
            additionalInfo.append(st.session_state[column])
        

def add_information():
    pass

   

addinfo_options=st.multiselect("Add Information", ['SVLMMx', 'SVLFMx', 'SVLMx', 'Longevity', 'NestingSite', 'ClutchMin',	'ClutchMax',
                             'Clutch', 'ParityMode',	'EggDiameter', 'Activity',	'Microhabitat', 'GeographicRegion',	'IUCN',	
                             'PopTrend',	'RangeSize', 'ElevationMin','ElevationMax','Elevation'])

#st.write(addinfo_options)

#df.loc[0, 'A'] = 10

if addinfo_options:
     get_extra_userinfo()



populate_additionLinfo()
#st.write(additionalInfo)

def comparedfs(df1,df2):
    diff = df1.diff(df2)
    if diff.empty:
        st.success('The DataFrames are equal.')
    else:
        st.dataframe(diff.style.applymap(lambda x: 'background-color: red' if x else ''))

def comparerows(df1,df2):
    mask = (df1['Order'] == df2['Order'])
    diff_mask = mask & (df1 != df2)

    if diff_mask.empty:
        st.success('The DataFrames are equal.')
    else:
            st.dataframe(df1[diff_mask].style.applymap(lambda x: 'background-color: red' if x else ''))
            st.dataframe(df2[diff_mask].style.applymap(lambda x: 'background-color: red' if x else ''))



#search=dfFull[multiOptions].drop_duplicates()
#def update_results(addinfo_options): #addinfo_options):
#    speciesIndex=results.index[0]
#    results_updated = results.copy()
#    columns=addinfo_options
#    results_updated.at[speciesIndex, columns] = "method testing"
#    return results_updated

def update_results(addinfo_options): #addinfo_options):
    speciesIndex=results.index[0]
    results_updated = results.copy()
    for column in addinfo_options:
        results_updated.at[speciesIndex, column] = st.session_state[column]
    return results_updated


showresults=st.checkbox("Show updates")

if showresults:
    st.write("magic happens here")
    #st.write(update_results(addinfo_options))
    #reviewdf = pd.DataFrame(userInfo, current_db.columns)
    #st.dataframe(reviewdf, width=300) 

    methodcol1, methodcol2, methodcol3=st.columns(3)
    methodcol2.dataframe(update_results(addinfo_options).iloc[0], width=300)