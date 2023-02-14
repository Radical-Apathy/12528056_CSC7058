from re import search
import streamlit as st
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from deta import Deta
import csv
from dotenv import load_dotenv


# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

#authenticate and build api drive
service = build("drive", "v3", credentials=creds)
#------------------------------------------------------------META DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

metaData=deta_connection.Base("database_metadata")



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


@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape')#, low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated

#gets dates for new species additions needing approval
pending=[]


def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

ordered=sorted(pending,reverse=True)

st.set_page_config(page_icon='amphibs.jpeg')



@st.cache
def load_cleaned():
    dfFull = pd.read_csv('https://drive.google.com/uc?id=1TJs2ykby1yxJvLcnGXdTduoLrtl7csMV', encoding= 'unicode_escape')
    return dfFull
@st.cache
def load_references():
    dfReferences = pd.read_csv('https://drive.google.com/uc?id=1h1UKe6xOy5C_maVOyGtbLCr4g0aH1Eek', encoding= 'unicode_escape')
    return dfReferences

@st.cache
def load_images():
    dfImages = pd.read_csv('https://drive.google.com/uc?id=1AfojhCdyKPk2HKCUyfXaVpnUZwWgBxwi', encoding= 'unicode_escape')
    return dfImages


#dfFull=load_original()
dfFull=load_latest()
dfReferences = load_references()
dfImages = load_images()


#creating session state object
#"st.session_state_object:", st.session_state

#Initializing session state values
if 'drop_option' not in st.session_state:
    st.session_state['drop_option'] = "Order"
if 'text_option' not in st.session_state:
    st.session_state['text_option'] = ""
if 'range_options' not in st.session_state:
    st.session_state['range_options'] = "BodySize"
#if 'radio_options' not in st.session_state:
 #   st.session_state['radio_options'] = "BodySize"
#else:
 #   st.session_state.radio_options = ['BodySize', 'Clutch Size', 'Egg Diameter'] 
if 'BodySize_slider' not in st.session_state:
    st.session_state['BodySize_slider'] = (850.0, 1500.0)
if 'ClutchSize_slider' not in st.session_state:
    st.session_state['ClutchSize_slider'] = (850.0, 1500.0)
if 'EggDiameter_slider' not in st.session_state:
    st.session_state['EggDiameter_slider'] = (850.0, 1500.0)
if 'boolean' not in st.session_state:
    st.session_state.boolean = False



def refGeneratorTop(speciesInfo):
    mergedRef = pd.merge(speciesInfo, dfReferences, on='Order')
    #order references from most recent
    sortedYear =mergedRef.sort_values(by='Year', ascending=False)
    displaymergedRef = sortedYear[["Year","Reference", "Order"]]
    displaymergedRef.drop_duplicates()
    return displaymergedRef.head()

def refGeneratorAll(speciesInfo):
    mergedRef = pd.merge(speciesInfo, dfReferences, on='Order')
    #order references from most recent
    sortedYear =mergedRef.sort_values(by='Year', ascending=False)
    displaymergedRef = sortedYear[["Year","Reference", "Order"]]
    return displaymergedRef.drop_duplicates()

def displayImage(speciesInfo):
    mergedInfo=pd.merge(speciesInfo, dfImages, on="Species")
    mergedInfo.drop_duplicates()
    return mergedInfo["Display Image"].loc[0]

def embeddedImage(speciesInfo):
    mergedInfo=pd.merge(speciesInfo, dfImages, on="Species")
    mergedInfo.drop_duplicates()
    return mergedInfo["Embedded Link"].loc[0]

def rangeSVLMx(dataframe, svlmxRange):
    maskRange=dfFull["SVLMx"].between(*svlmxRange)
    maskedRange=dfFull[maskRange]
    #maskedRange.sort_values(by='SVLMx', ascending=True)
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.SVLMx])
   # maskedRangedf.sort_values(by='SVLMx', ascending=True)
    #st.write(maskedRangedf.sort_values(by='SVLMx', ascending=True))
    st.write(maskedRangedf)


def clutchRange(dataframe,  clutchSize):
    maskRange=dfFull["Clutch"].between(*clutchSize)
    maskedRange=dfFull[maskRange]
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.Clutch])
    #sortedYear =mergedRef.sort_values(by='Year', ascending=False)
    st.write(maskedRangedf)

def eggDiameterRange(dataframe,  eggSize):
    maskRange=dfFull["EggDiameter"].between(*eggSize)
    maskedRange=dfFull[maskRange]
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.EggDiameter])
    st.write(maskedRangedf)


def multioptionCheck(options=[]):
    ranges = ""
    for option in options:
     if option=="Species":
           ranges=st.radio('Range Search: ', ['BodySize', 'Clutch Size', 'Egg Diameter'], key='range_options')
       # ranges=st.radio('Range Search: ', st.session_state.radio_options, key='radio_options')
           if ranges == 'BodySize':
            svlmxRange= st.slider('SVLMx Range searching', 0.0, 1700.0, (850.0, 1700.0), key='BodySize_slider')
            rangeSVLMx(dfFull, svlmxRange)
           if ranges=="Clutch Size":
              clutchSize= st.slider('Clutch Size', 0.0, 1700.0, (850.0, 1700.0), key='ClutchSize_slider')
              clutchRange(dfFull, clutchSize)
           if ranges=="Egg Diameter":
            eggSize= st.slider('Egg Diameter', 0.0, 20.0, (10.0, 20.0), key='EggDiameter_slider') 
            eggDiameterRange(dfFull, eggSize)  
     if option=="Order" and text_inputMulti:
        orderSearch()
     if option=="Species" and text_inputMulti:
        speciesSearchTest(text_inputMulti)
     if option=="Family" and text_inputMulti:
        familySearch()
     if option=="Genus" and text_inputMulti:
        genusSearch()
   
                             

    else:
         search=dfFull[multiOptions].drop_duplicates()
         #searchText=search.groupby(st.session_state.drop_option).get_group(st.session_state.text_option)
         search.drop_duplicates()
        

    st.write(search)


speciesdf= []
def speciesSearchTest(option2): # formally option2
    col1,col2=st.columns(2)
    col1.header(st.session_state['text_option'], " Species Summary:")
    #speciesInfo = dfFull.groupby("Species").get_group(st.session_state['text_option']) # only definition of the three speciesInfo that works
    speciesInfo=dfFull.groupby("Species").get_group(st.session_state['text_option'])
    #speciesInfo = st.session_state['drop_option']
    #st.session_state.speciesInfo = speciesInfo
    col1.markdown("[![Image not Available]("+displayImage(speciesInfo)+")]("+embeddedImage(speciesInfo)+")")
    url= url="https://amphibiansoftheworld.amnh.org/amphib/basic_search/(basic_query)/"+option2
    col1.write("AMNH web link for "+ st.session_state['text_option']+  " [AMNH Link](%s)" % url)
    url2="https://amphibiaweb.org/cgi/amphib_query?where-scientific_name="+ st.session_state['text_option'] +"&rel-scientific_name=contains&include_synonymies=Yes"
    col1.write("Amphibian web link for "+ st.session_state['text_option']+  " [Amphibia Web Link](%s)" % url2)
    col2.header("Species Summary")
    
    tab1, tab2= st.tabs(["Literature References - Most Recent", "See All References"])
    with tab1:
       st.write(refGeneratorTop(speciesInfo)) 
    with tab2:
        st.write(refGeneratorAll(speciesInfo))
    speciesdf.append(speciesInfo["Genus"])
    speciesdf.append(speciesInfo["GeographicRegion"])
    speciesdf.append(speciesInfo["SVLMMx"])
    speciesdf.append(speciesInfo["RangeSize"])
    speciesdf.append(speciesInfo["ElevationMin"])
    speciesdf.append(speciesInfo["ElevationMax"])
    speciesdf.append(speciesInfo["IUCN"])
    speciesdatadf=pd.DataFrame(speciesdf)
    hide_row_no="""<style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>"""
    st.markdown(hide_row_no, unsafe_allow_html=True)
    col2.write(speciesdatadf)
    showMore = col2.checkbox("Show All")
    

    if showMore:
        #separateGroupby()
        #speciesSearchTest(st.session_state['text_option'])
        #st.session_state['speciesInfo']=dfFull.groupby(st.session_state['drop_option']).get_group(st.session_state['text_option'])
        #speciesInfo=dfFull.groupby("Species").get_group(st.session_state['text_option'])
        col2.write(dfFull.groupby(st.session_state['drop_option']).get_group(st.session_state['text_option']))
        #speciesInfo.drop_duplicates()
        
        #col2.write (separateGroupby())

familydf=[]
def familySearch():
     familyInfo=dfFull.groupby("Family").get_group(st.session_state['text_option'])
     for option in multiOptions:
        familydf.append(familyInfo[option])
     

     familydatadf=pd.DataFrame(familydf)
     st.write(familydatadf)

orderdf=[]
def orderSearch():
     orderInfo=dfFull.groupby("Order").get_group(st.session_state['text_option'])
     for option in multiOptions:
        orderdf.append(orderInfo[option])
     

     orderdatadf=pd.DataFrame(orderdf)
     st.write(orderdatadf)

genusdf=[]
def genusSearch():
     genusInfo=dfFull.groupby("Genus").get_group(st.session_state['text_option'])
     for option in multiOptions:
        genusdf.append(genusInfo[option])
     

     genusdatadf=pd.DataFrame(genusdf)
     st.write(genusdatadf)

st.title("Streamlit Search Ability Demo")
#st.session_state
st.image("amphibs.jpeg", width=200)


multiOptions = st.multiselect("choose a few ", options=dfFull.columns, key='drop_option')
#st.write(multiOptions)
text_inputMulti = st.text_input("Enter your text search for " +multiOptions[0], multiOptions[0], key='text_option')
submitButton2=st.button("Multi Search")
#if st.session_state.get('button') != False:


try:
 if submitButton2 or st.session_state.boolean:
    st.session_state.boolean =True
    #text_inputMulti = st.text_input("Enter your queries")
    #st.session_state.boolean=True
    st.write("Results for: ")
    multioptionCheck(multiOptions)
    
except:("Sorry, search term not recognised. Try checking your category choice or spelling")

#if st.session_state.boolean == True:
 #    st.write("Results for: ")
  #   multioptionCheck(multiOptions)
    






      
        
        
















