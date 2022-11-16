from re import search
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_icon='amphibs.jpeg')

#@st.cache
#def load_original():
#    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/GABiP_July.csv', encoding= 'unicode_escape', low_memory=False)
#    return dfFull

@st.cache
def load_cleaned():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull
@st.cache
def load_references():
    dfReferences = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/Reference_List.csv', encoding= 'unicode_escape', low_memory=False)
    return dfReferences

@st.cache
def load_images():
    dfImages = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/image_database.csv', encoding= 'unicode_escape', low_memory=False)
    return dfImages


#dfFull=load_original()
dfFull=load_cleaned()
dfReferences = load_references()
dfImages = load_images()


#creating session state object
"st.session_state_object:", st.session_state

#Initializing session state values
if 'drop_option' not in st.session_state:
    st.session_state['drop_option'] = "Species"
if 'text_option' not in st.session_state:
    st.session_state['text_option'] = "relicta"
if 'range_options' not in st.session_state:
    st.session_state['range_options'] = "BodySize"
if 'BodySize_slider' not in st.session_state:
    st.session_state['BodySize_slider'] = (850.0, 1500.0)
if 'slidercheck' not in st.session_state:
    st.session_state['slidercheck'] = (70.0, 980.0)
#if 'speciesInfo' not in st.session_state:
 #  st.session_state['speciesInfo']=dfFull.groupby(st.session_state['drop_option']).get_group(st.session_state['text_option'])
for item in st.session_state.items():
    st.write("item: ", item)
for values in st.session_state.values():
    st.write("session state value: ",values)

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
    maskedRangedf=pd.DataFrame([maskedRange.Species, maskedRange.Genus, maskedRange.SVLMx])
    st.write(maskedRangedf)

def multioptionCheck(options=[]):
    for option in options:
     if option=="Species" and text_inputMulti:
        speciesSearchTest(text_inputMulti)
     if option=="Species":
        #svlmxRange= st.slider('SVLMx Range searching', 0.0, 1700.0, (850.0, 1500.0))
        #rangeSVLMx(dfFull, svlmxRange)
        ranges=st.radio('Range Search: ', ['BodySize', 'Clutch Size', 'Egg Diameter'], key='range_options')
        for choice in ranges:
           if choice == 'BodySize':
                   svlmxRange= st.slider('SVLMx Range searching', 0.0, 1700.0, (100.0, 1000.0), key='BodySize_slider')
                   rangeSVLMx(dfFull, svlmxRange)
           if choice=="Clutch Size":
                    clutchSize= st.slider('Clutch Size', 0.0, 1700.0, (850.0, 1500.0), key='ClutchSize_slider')
           if choice=="Egg Diameter":
                    eggSize= st.slider('Egg Diameter', 0.0, 1700.0, (850.0, 1500.0), key='EggDiameter_slider')

     else:
         search=dfFull[multiOptions].drop_duplicates()
         search.drop_duplicates()
        

    st.write(search)


def separateGroupby():
    speciesInfo=dfFull.groupby("Species").get_group(st.session_state['text_option'])
    st.write(speciesInfo)


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
        separateGroupby()
        #speciesSearchTest(st.session_state['text_option'])
        #st.session_state['speciesInfo']=dfFull.groupby(st.session_state['drop_option']).get_group(st.session_state['text_option'])
        #speciesInfo=dfFull.groupby("Species").get_group(st.session_state['text_option'])
        #st.write(speciesInfo)
        #speciesInfo.drop_duplicates()
        
       # col2.write (separateGroupby())

st.title("Streamlit Search Ability Demo")

st.image("amphibs.jpeg", width=200)


multiOptions = st.multiselect("choose a few ", options=dfFull.columns, key='drop_option')
text_inputMulti = st.text_input("Enter your queries", "relicta", key='text_option')
submitButton2=st.button(" Multi Search")

try:
 if submitButton2:
    #text_inputMulti = st.text_input("Enter your queries")
    st.write("Results for: ")
    multioptionCheck(multiOptions)
    
except:("Sorry, search term not recognised. Try checking your category choice or spelling")
    
st.write(separateGroupby())

sliderCheck=st.slider('Slider display check', 0.0, 1700.0, (850.0, 1500.0), key='slidercheck')






















