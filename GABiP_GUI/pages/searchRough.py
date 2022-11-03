
from re import search
import streamlit as st
import pandas as pd
import numpy as np

#@st.cache(allow_output_mutation=True)
#@st.cache(allow_output_mutation=True)
#def load_model(model_name):
 #   nlp=spacy.load(model_name)
  #  return (nlp)

st.set_page_config(page_icon='amphibs.jpeg')
#dfFull=pd.read_csv('C:/Users/Littl/OneDrive/Desktop/Project Research 17-10-2022/Thesis Notes/CodeExp/streamLit Guide/Experimenting/GABiP_PROTECTED.csv', encoding= 'unicode_escape', low_memory=False)
@st.cache
def load_original():
    dfFull = pd.read_excel(r'C:/Users/Littl/OneDrive/Desktop/Project Research 17-10-2022/Thesis Notes/CodeExp/streamLit Guide/Experimenting/GABiP.xlsx',sheet_name='GABiP DATA_V5')
    return dfFull

dfFull=load_original()

def groupby(option1, option2):
    search = dfFull.groupby(option1).get_group(option2)
    search.drop_duplicates()
   # st.write(search.head())
    return search

#def groupbyMulti(list={}, *args):
 #   search = dfFull.groupby(list{0}).get_group(list{1})
    #search.drop_duplicates()
  #  st.write(list[0])
#dfFull.set_index("Family", inplace=True)
arrayData=np.array(dfFull) # making it a numpy array

st.title("Search Page Prototype")
st.image("amphibs.jpeg", width=200)


#options = st.selectbox("Choose only one", ["Order","Family","Subfamily","Genus","Species"])
#st.write("you chose ", options)
#optionButton=st.button("Submit")
#family=dfFull["Family"].unique()

def groupbyCasCade(*args):
   for x in args:
    print(x)

#watch this: https://www.youtube.com/watch?v=7zeAIEPJaoQ

multiOptions2 = st.multiselect("choose a few ", options=dfFull.columns)##"Subfamily","Genus","Species"
text_input = st.text_input("Enter your query", "relicta")
submitButton=st.button("Search")
st.write("Results: ")
if  submitButton:
    st.write(groupby(multiOptions2, text_input))

st.write("External Link")
 #images? https://calphotos.berkeley.edu/cgi/img_query?where-taxon=Discoglossus+scovazzi&rel-taxon=begins+with&where-lifeform=specimen_tag&rel-lifeform=ne (grab the href here)
url="https://amphibiaweb.org/cgi/amphib_query?where-scientific_name="+text_input+"&rel-scientific_name=contains&include_synonymies=Yes"
st.write("Amphibian web link for "+text_input+  " [Amphibia Web Link](%s)" % url)

#optionButton2=st.button("Submit Multiple")
#def get_dropdown(option2):
 #   if optionButton2:
  #   return options2

#def get_input(string):
 #   if text_input:
  #   return string

#st.write("Using groupby with typed values")
#groupby("Order", "Gymnophiona")
#show_more= st.checkbox("show more")
#st.write("Using group by with selection")
#groupby(multiOptions2, text_input )
#extraOptions = dfFull.iloc[10:17].head(0)

#def show_extra(dataframe):
 #   for option in dfFull.iloc[10:17].head(0):
  #      str(option)
#def show_extra(data):
 #   for option in extraOptions:
  #      str(option)

def show_extra(data):

    for data[0] in data:
        st.write(data[0])

def show_extra2(data):
    choices = []
    for data.iloc[0] in data:
        choices.append(data.iloc[0])
    return choices

def show_extra3(data):
    choices = []
    for data in data.iloc[0:0]:
        choices.append(data)
    return choices




#dfFull["Family"].loc[0:11]
def showSpecies(array):
    for i in array:
        print(i)

def removeNan(array):
    for i in array:
        if i != 'NaN':
            print(i)




firstArray=arrayData[0]
#firstArrayNaNRemoved=np.char.replace(str(firstArray, 'nan', '')) #how to get nan removed
speciesNumpy=[arrayData[0][4], arrayData[1][4]] 
speciesSomeInfoNumpy=[arrayData[0][4],arrayData[0][5]]
speciesSomeInfoPandas=str([dfFull["Species"].iloc[0], dfFull["SVLMMn"].iloc[0]])
speciesOnlyPandas=dfFull["Species"].head(10)
SVLMMnOnlyPandas=dfFull["SVLMMn"].iloc[0]
genusOnlyPandas=dfFull["Genus"].head(10)

print(speciesSomeInfoNumpy)


#print("-------------------------")
#print(speciesSomeInfoPandas)

family= dfFull["Family"].iloc[0:705].sort_values(ascending=True) #need to show each occurance only once
species=dfFull["Species"].iloc[0:11].sort_values( ascending=True)

familyDupsRemoved=family.drop_duplicates()
option = st.selectbox(
    'Showing family alphabetically from pandas dataframe, duplications removed',
    (familyDupsRemoved))
   # (showSpecies (str(dfFull["Species"].iloc[0:11]))))

option = st.selectbox(
    'Showing all data in first row with numpy array(can maybe use this to select some common data and then tick option for displaying more/all available',
    (firstArray))

option = st.selectbox(
    'Showing species data in first 2 rows with numpy array',
    (speciesNumpy))

option = st.selectbox(
    'Showing selected data in first rows with numpy array',
    (speciesSomeInfoNumpy))

option = st.selectbox(
    'Showing some species data in first rows with pandas df...prints each letter in array form',
    (str(speciesSomeInfoPandas)))


option= st.multiselect("Multiselect, first ten genus ", (genusOnlyPandas))
'''
option = st.selectbox(
    'Showing all data in first row with numpy array and nan removed',
    (firstArrayNaNRemoved))
'''

dfGenusSpecies=dfFull.loc[dfFull["Genus"]=="Allophryne", "Species"]
#st.write(str(extraOptions))
#st.write(show_extra2(dfFull))
#specifics = st.multiselect("Choose specifics ", [show_extra2(dfFull)])
#if optionButton:
 #   st.write(dfFull[options].iloc[0:12].drop_duplicates(),dfFull["Genus"].iloc[0:12].drop_duplicates())
  #  st.write(dfFull["Genus"].iloc[0:12].drop_duplicates())



#if optionButton2:
 #   for option in options2:
  #      st.write (dfFull[options2].iloc[0:12].drop_duplicates())
    
        
#if show_more:
 #        for option in options2:
  #          st.write(dfFull[options2].iloc[12:].drop_duplicates())
        
        

st.sidebar.header("A side bar in search page")

st.header("Species Result Summary")

missingSVLMMn = dfFull["SVLMMn"].isna().sum()

st.write("missing data in SVLMMn column")
st.write (missingSVLMMn )

col1,col2=st.columns(2)
col1.header("Column 1 header")
col1.image("amphibs.jpeg")
col2.header("Column 2 header")

def speciesSummary(dfull):
    #species = groupby("Species", "ruthveni")
    #species.drop_duplicates()
    #st.write(species["SVLMMn"].drop_duplicates())
    #st.write( species["YearDiscovery"].drop_duplicates())
    #st.write("SVLMMn", species.iloc[0:5])
    return species

#col2.dataframe(speciesSummary(dfFull))

#col2.dataframe (dfFull.groupby("Species").get_group("ruthveni"))

ruthveniInfo = dfFull.groupby("Species").get_group("relicta")
speciesdf= []
col2.write("Empty data frame")
col2.write(speciesdf)
col2.write(ruthveniInfo["SVLMMn"])
col2.write(ruthveniInfo["SVLMMx"]) #IUCNStat_2015
col2.write(ruthveniInfo["BodyMass"])
col2.write(ruthveniInfo["Microhabitat"])
col2.write(ruthveniInfo["IUCNStat_2015"])
speciesdf.append(ruthveniInfo["SVLMMn"])
speciesdf.append(ruthveniInfo["SVLMMx"])
speciesdf.append(ruthveniInfo["BodyMass"])
#speciesdf.append(ruthveniInfo["Microhabitat"])
speciesdatadf=pd.DataFrame(speciesdf)
col2.dataframe(speciesdf)
col1, col2= st.columns(2)


#st.title("Using no method") 


#st.write("Using method with groupby - Genus, Alsodes")
#groupby("Genus", "Alsodes")
#famSearch=dfFull.groupby("Family").get_group("Alsodidae")

#col1.write("genus from Alsodidae family: ")

#col1.write(famSearch["Genus"].drop_duplicates())

#groupby(["Genus", "Allophryne"])
#col2.write("Species from Alsodidae family, showing first 5")
#col2.write(famSearch["Species"].iloc[0:5])
#show_more = col2.checkbox("Show more")

#if show_more:
 #   col2.write(famSearch["Species"].iloc[5:])
#st.write(genusSearch)

