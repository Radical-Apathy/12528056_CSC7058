from re import search
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_icon='amphibs.jpeg')


@st.cache
def load_original():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/GABiP_July.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

dfFull=load_original()

speciesdf= []
def speciesSearchTest(option2):
    col1,col2=st.columns(2)
    col1.header(option2, " Species Summary:")
    col1.image("amphibs.jpeg")
    url= url="https://amphibiansoftheworld.amnh.org/amphib/basic_search/(basic_query)/"+option2
    col1.write("AMNH web link for "+ option2+  " [AMNH Link](%s)" % url)
    url2="https://amphibiaweb.org/cgi/amphib_query?where-scientific_name="+ option2 +"&rel-scientific_name=contains&include_synonymies=Yes"
    col1.write("Amphibian web link for "+ option2+  " [Amphibia Web Link](%s)" % url2)
    col2.header("Column 2 header")
    speciesInfo = dfFull.groupby("Species").get_group(option2)
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


def referDisplay():
    tab1, tab2, tab3 = st.tabs(["Page 1", "Page 2", "Page 3"])
    with tab1:
        st.write("Testing tab page 1")
    with tab2:
        st.write("Testing tab page 2")
    with tab3:
        st.write("Testing tab page 3")


#generic method for searching
def groupby(option1, option2):
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
  st.write(groupby(singleOptions, text_input))
  referDisplay()
except:("Sorry, no results found. Try checking your category choice or spelling")

multiOptions = st.multiselect("choose a few ", options=dfFull.columns)##"Subfamily","Genus","Species"
text_inputMulti = st.text_input("Enter your queries", "relicta")
submitButton2=st.button(" Multi Search")

if submitButton2:
    st.write(dfFull[multiOptions].drop_duplicates())
    #st.write(groupby(multiOptions, text_input))


    





