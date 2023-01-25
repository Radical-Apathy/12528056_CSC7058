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
   # mergedInfo=pd.merge(speciesInfo, dfImages, on="Species")
   mergedInfo=pd.merge(speciesInfo, dfImages, on="Genus")
   mergedInfo.drop_duplicates()
   return mergedInfo["Display Image"].loc[0]

def embeddedImage(speciesInfo):
    #mergedInfo=pd.merge(speciesInfo, dfImages, on="Species")
    mergedInfo=pd.merge(speciesInfo, dfImages, on="Genus")
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
headercol2.subheader("Add Species Info Dev")
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

st.write(results["RangeSize"])

missingInfoColumns=[]
def get_missing_info_columns(results):
    pass
    #for column in dbColumns:
       # if pd.isna(results[column]):
        #    missingInfoColumns.append[results[column]]

        #if results[column]==None:
         #   st.write(results[column])
            #missingInfoColumns.append[column]
   # return missingInfoColumns


#st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>More Options</strong></p>', unsafe_allow_html=True)
#st.markdown('Streamlit is **_really_ cool**.')
#st.markdown("This text is :red[colored red], and this is **:blue[colored]** and bold.")

col1, col2, col3 = st.columns(3)

col3.markdown("**Genea of** "+speciesdropdown)
col3.write(genusdropdown)
col3.write(speciesGenus["Genus"].iloc[0])
col2.write("All data")
col2.write(results)
#col2.dataframe(results.iloc[0], width=500)
col2.write("Missing column data only")
col2.dataframe(get_missing_info_columns(results))
#col2.write(missingInfoColumns)
col1.write("Image Goes Here")
#col1.markdown("[![Image not Available]("+displayImage(results)+")]("+embeddedImage(results)+")")
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



show_missing_info=st.multiselect("Add Missing Information", ["Option1", "option2"])


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


dataframeapproach=st.checkbox("Replacing values with dataframe approach - hard coded")

if dataframeapproach:
    speciesIndex=results.index[0]
    st.write("Results before")
    st.write(results)
    st.write("After results..copying old df and using df_new.at[index_label, 'column_name'] = new_value")
    results_updated = results.copy()
    results_updated.at[speciesIndex, 'SVLMMx'] = 99
    #results.at[speciesIndex, 'Order']="Order updated"
    st.write(results_updated)
    st.write("Updating multiple at once -")
    #df_new.at[index_label, ['column_name1', 'column_name2']] = [new_value1, new_value2]
    results_multiple=results.copy()
    results_multiple.at[speciesIndex, ('Order', 'Family', 'SVLMMx')] = ["New order", "New Family", 88 ]
    st.write(results_multiple)

    diff_mask = results != results_multiple

    #st.dataframe(results.style.applymap(lambda x: 'background-color: yellow' if x else ''))
    #st.dataframe(results_multiple.style.applymap(lambda x: 'background-color: yellow' if x else ''))

    compare=st.button("Compare")
    if compare:
        #col1, col2, col3 = st.columns(3)
        #st.dataframe(speciesInfo.iloc[0])
        comparecol1,comparecol2, comparecol3=st.columns(3)
        comparecol1.write("Original Species")
        comparecol1.dataframe(results.iloc[0], width=300)
        comparecol2.write("Updated Species Info")
        comparecol2.dataframe(results_multiple.iloc[0], width=300)
        comparecol3.write("Differences highlighted?")
        #comparerows(results, results_multiple)




    
jsonarraywithsessionstate=st.checkbox("Create json array using session state and columns")

if jsonarraywithsessionstate:
    create_json_data()
    st.write(jsondata)

dfaskeyvaluedict=st.checkbox("Turn df into key value pair dictionary")

if dfaskeyvaluedict:
    st.write("dict=results.to_dict()")
    dict=results.to_dict()
    st.write(dict)
    st.write("dict.get('Species')")
    st.write(dict.get("Species"))
    st.write("Back to dataframe - dictreverted=pd.DataFrame(dict)")
    dictreverted=pd.DataFrame(dict)
    st.write(dictreverted)
    st.write("dictorient=results.to_dict(orient='index')")
    dictorient=results.to_dict(orient='index')
    st.write(dictorient)
    #dictnorec=results.to_dict('records')
    #st.write(dictnorec.get("Family"))

methodcheck=st.checkbox("Practicing value replacement using results as a dictionary - hardcoded")
if methodcheck:
    #st.write("code pending") 
    dict=results.to_dict() 
    #st.write("dict.update({'Family':'hardcoded update value'})")
    #dict.update({'non existent column':'hardcoded update family'})
    dict.update({'Order':'checking index preservation'})
    st.write(dict)
    dictreverted=pd.DataFrame(dict)
    st.write(dictreverted)

indexmethodcheck=st.checkbox("Practicing value replacement using results as a dictionary and keeping index - hardcoded")

if indexmethodcheck:
    #index = df.loc[df['A'] == 2].index[0]
    #results=current.loc[(current["Species"] == speciesdropdown) & (current['Genus'] == genusdropdown)]
    speciesIndex=results.index[0]
    st.write(speciesIndex)
    dictorient=results.to_dict(orient='index')
    #st.write(dictorient)
    dictorient[6]['Family'] = 'Fam update and preserving index for '
    #dict.update({'Genus':'hardcoded update genus'})
    st.write(dictorient)
    dictreverted=pd.DataFrame(dictorient)
    st.write(dictreverted)
    st.write("code to be written")










jsonexperiemnt=st.checkbox("Convert results to a json file")

if jsonexperiemnt:
    st.write("Results as a dataframe - results=current.loc[(current['Species'] == speciesdropdown) & (current['Genus'] == genusdropdown)]")
    st.write(results)
   # st.write("Results as json orient records")
    resultsjsonorientrecs=results.to_json(orient='records')
    #st.write(resultsjsonorient)
    st.write("Results as json orient columns - resultsjsoncols=results.to_json(orient='columns')")
    resultsjsoncols=results.to_json(orient='columns')
    st.write(resultsjsoncols)
    #st.write(resultsjsonorientrecs["Family"])

    #st.write("Results as json orient index")
    #resultsjsonindex=results.to_json(orient='index')
    #st.write(resultsjsonindex)
    #st.write("Getting json data ")
    #st.write(resultsjsoncols)

pythonobjectexperiemnt=st.checkbox("Convert results to a python object")

if pythonobjectexperiemnt:
    resultsjsoncols=results.to_json(orient='columns')
    speciespythonobject= json.loads(resultsjsoncols)
    st.write(speciespythonobject)
    st.write("replacing family via speciespythonobject[2]='family replaced' - didnt work ")
    speciespythonobject[2]="family replaced"
    st.write(speciespythonobject)




   
  
    
    


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

