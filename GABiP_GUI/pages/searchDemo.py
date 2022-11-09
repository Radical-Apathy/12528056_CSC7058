from re import search
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_icon='amphibs.jpeg')

@st.cache
def load_original():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/GABiP_July.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

@st.cache
def load_references():
    dfReferences = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/Reference_List.csv', encoding= 'unicode_escape', low_memory=False)
    return dfReferences

@st.cache
def load_images():
    dfImages = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/image_database.csv', encoding= 'unicode_escape', low_memory=False)
    return dfImages


dfFull=load_original()
dfReferences = load_references()
dfImages = load_images()

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

speciesdf= []
def speciesSearchTest(option2):
    col1,col2=st.columns(2)
    col1.header(option2, " Species Summary:")
    speciesInfo = dfFull.groupby("Species").get_group(option2)
    col1.markdown("[![Image not Available]("+displayImage(speciesInfo)+")]("+embeddedImage(speciesInfo)+")")
    url= url="https://amphibiansoftheworld.amnh.org/amphib/basic_search/(basic_query)/"+option2
    col1.write("AMNH web link for "+ option2+  " [AMNH Link](%s)" % url)
    url2="https://amphibiaweb.org/cgi/amphib_query?where-scientific_name="+ option2 +"&rel-scientific_name=contains&include_synonymies=Yes"
    col1.write("Amphibian web link for "+ option2+  " [Amphibia Web Link](%s)" % url2)
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
        speciesInfo.drop_duplicates()
        col2.write (speciesInfo)

#generic method for searching
def optionCheck(option1, option2):
    if option1=="Species":
        speciesSearchTest(option2)
    else:
         search = dfFull.groupby(option1).get_group(option2)
         search.drop_duplicates()
         hide_row_no="""<style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>"""
         st.markdown(hide_row_no, unsafe_allow_html=True)

         return search
    
st.title("Streamlit Search Ability Demo")

st.image("amphibs.jpeg", width=200)
singleOptions = st.selectbox("Dropdown allowing one choice, showing all columns", options=dfFull.columns)##"Subfamily","Genus","Species"
text_input = st.text_input("Enter your query", "relicta")

submitButton=st.button("Search")

try:
 if submitButton:
  st.write("Results: ")
  speciesInfo=optionCheck(singleOptions, text_input)
  st.write(speciesInfo)
except:("Sorry, no results found. Try checking your category choice or spelling")

multiOptions = st.multiselect("choose a few ", options=dfFull.columns)##"Subfamily","Genus","Species"
#text_inputMulti = st.text_input("Enter your queries", "relicta")
submitButton2=st.button(" Multi Search")

if submitButton2:
    st.write(dfFull[multiOptions].drop_duplicates())
    #st.write(groupby(multiOptions, text_input))















