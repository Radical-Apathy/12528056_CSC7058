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
#from io import StringIO
#from PIL import Image
import base64



#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

database_metadata=deta_connection.Base("database_metadata")
#metaData=deta_connection.Base("database_metadata")

#------------------------------------------------------------metadata METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = database_metadata.fetch()
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

def create_session_states_source(dbColumns):
    for column in dbColumns:
        if [column+" source"] not in st.session_state:
           st.session_state[column+ "source"] =""


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
      
       
    
def show_knowledge_gaps():
    st.write("knowledge gaps")

jsondata=[]
def create_json_data():
  for column in dbColumns:
      jsondata.append({column:st.session_state[column]})
  return jsondata

missingInfoColumns=[]
def get_missing_info_columns(results):
    for column in dbColumns:
        if results[column].isna().any():
         missingInfoColumns.append(results[column].name)
    return missingInfoColumns


usermissingino=[]
def get_missing_userinfo():
     for option in show_missing_info:
        
        userText=st.text_input(option, key=option)
        if userText:
         #st.session_state[option] == userText
         usermissingino.append(st.session_state[option])
         #st.write("You've entered ", userText)
        #else :
         #   st.session_state[option]==""
     return usermissingino


def populate_missing_info():
        for column in dbColumns:
            additionalInfo.append(st.session_state[column])

def update_missing_results(show_missing_info): #addinfo_options):
    speciesIndex=results.index[0]
    results_updated = results.copy()
    for column in show_missing_info:
        results_updated.at[speciesIndex, column] = st.session_state[column]
    return results_updated

now=datetime.now()

# def image_upload():
#     uploaded_file = col1.file_uploader("Add an Image")
#     #col1.write("Add an image?")


def link_image(results):
    merged_image_df = pd.merge(results, dfImages, left_on=['Genus', 'Species'], right_on=['Genus', 'Species'], how='inner')
    #return merged_image_df["Display Image"].iloc[0]
    if  merged_image_df["Display Image"].iloc[0] == "https://calphotos.berkeley.edu image not available":
        col1.write("No images available.")
        #image_upload()
    else:
        col1.write("Image from amphibiaweb.org")
        return merged_image_df["Display Image"].iloc[0]
        



def link_embedded_image(results):
    embedded_image_df= pd.merge(results, dfImages, left_on=['Genus', 'Species'], right_on=['Genus', 'Species'], how='inner')
    if  embedded_image_df["Display Image"].iloc[0] != "https://calphotos.berkeley.edu image not available":
        return embedded_image_df["Embedded Link"].iloc[0]
#------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------#
#C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/gabip images/dataset_thumbnail.jpeg
#st.image("amphibs.jpeg", width=200)
#"C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/gabip images/black_and_green_frog.jpg"
headercol1, headercol2, headercol3=st.columns(3)
headercol1.image("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/gabip images/black_and_green_frog.jpg", width=200)

headercol2.subheader("Add Species Info Dev")
st.markdown("**This markdown text will be bold**")
#st.session_state
current=load_full()
dbColumns=current.columns
create_session_states(dbColumns)

allgenus=[]
def get_genus(speciesdropdown):
    allgenus=current.loc[current["Species"]==speciesdropdown]
    return allgenus


additionalInfo=[]

missingInfoSources=[]

speciesdropdown=st.selectbox("Select a species to add to: ", (current['Species']))

speciesGenus=current.loc[current["Species"]==speciesdropdown]

genusdropdown=st.selectbox("Select "+speciesdropdown+ " Genus", speciesGenus["Genus"])

results=current.loc[(current["Species"] == speciesdropdown) & (current['Genus'] == genusdropdown)]

sourcefields=[]
summarydf=[]
#st.session_state
def create_source_fields(show_missing_info):
       for option in show_missing_info:
           #if st.session_state[option] !="":
               usersource=st.text_input("Please enter a source for "+option, key=option+" source")

       for option in show_missing_info:
           if usersource and usersource!="":
               st.session_state[option+" source"]==usersource
               #missingInfoSources.append({option:st.session_state[option+" source"]})
               missingInfoSources.append(st.session_state[option+" source"])
           
       return missingInfoSources
   
col1, col2, col3 = st.columns(3)

col3.markdown("**All Genea of** "+speciesdropdown)

col3.write(genusdropdown)

col3.write(speciesGenus["Genus"].iloc[0])


#col1.dataframe(results.style.apply(highlight_null, subset=df.columns[df.iloc[0].isnull()]).render())
col2.write("Missing data highlighted")
col2.write(results.iloc[0])
#row = results.iloc[0]

col1.markdown(f"[![]({link_image(results)})]({link_embedded_image(results)})")

#embedd in method to say https://amphibiaweb.org/
#col1.write("Image Source: ")

get_missing_info_columns(results)
show_missing_info=st.multiselect("Add Missing Information", missingInfoColumns)

 






if show_missing_info:
     get_missing_userinfo()
     


populate_missing_info()

resultscopy=results.copy()

resultschanged=update_missing_results(show_missing_info)


showresults=st.checkbox("Show updates")
 


if showresults:
    st.write("magic happens here")
    methodcol1, methodcol2, methodcol3=st.columns(3)
    methodcol2.dataframe(update_missing_results(show_missing_info).iloc[0], width=300)
    diff_mask = results != resultschanged

    compare=st.button("Compare")
    if compare:
       
        comparecol1,comparecol2, comparecol3=st.columns(3)
        comparecol1.write("Original Species")
        comparecol1.dataframe(results.iloc[0], width=300)
        comparecol2.write("Updated Species Info")
        comparecol2.dataframe(resultschanged.iloc[0], width=300)
        comparecol3.write("Differences highlighted?")     

sourcecol1,sourcecol2,sourcecol3=st.columns(3)
sourcecol1.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
sourcecol2.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>*Information Sources*</strong></p>', unsafe_allow_html=True)
sourcecol3.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>**************************</strong></p>', unsafe_allow_html=True)
create_source_fields(show_missing_info)
#st.write(missingInfoSources)
#st.session_state

checkSummary=st.button("View summary sources")




if checkSummary:
        sumcol1,sumcol2,sumcol3=st.columns(3)
        if not missingInfoSources:

         st.warning("Please ensure sources are provided for each information point")
        else:
            sourcesreviewdf = pd.DataFrame(missingInfoSources, show_missing_info)
            sumcol2.dataframe(sourcesreviewdf)
# sourcesreviewdf = pd.DataFrame(missingInfoSources, show_missing_info)
# st.write("Dataframe to json")            
# jsonsources=sourcesreviewdf.to_json()
# st.write(jsonsources)
# st.write("back to dataframe") 
# st.dataframe(pd.read_json(jsonsources))
# st.write("dataset updated -hardcoded")
# speciesIndex=results.index[0]

#st.write(missingInfoColumns)


#C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/31.01.2023-17.38.12-admin-approved.csv
# dfImages = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/image_database.csv', encoding= 'unicode_escape', low_memory=False)
datacheckdf=pd.read_csv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/31.01.2023-17.48.42-admin-approved.csv", encoding= 'unicode_escape', low_memory=False)
#st.write("I've written in the 42s")
#st.write(datacheckdf.tail().to_dict())
#st.write("I've added floats")

datacheckfloat=pd.read_csv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/31.01.2023-18.09.34-admin-approved.csv", encoding= 'unicode_escape', low_memory=False)
#st.write(datacheckfloat.tail().to_dict())
#st.write(current.head().to_dict())
overwrittingsinglecells=st.checkbox("Replacing cells in stead of whole row using pandas and python dic - Admin side UI Processing")


# def updatespecies(pythondictionary):
#     for column in show_missing_info:
#         for value in usermissingino:
#             pythondictionary[column][speciesIndex] = value
#     return pythondictionary

# def iteration_check_combo():
#      for column in show_missing_info:
#         for value in usermissingino:
#             st.write(column, value)
# def iteration_check_idividual():
#     for column in show_missing_info:
#         st.write(column)
#     for value in usermissingino:
#         st.write(value)
# def iteration_check_combo_fix():
#      for column in show_missing_info:
#         for value in usermissingino:
#          st.write(column, value)


def update_species(userdict, originaldict):
    
    added_values=list(userdict.values())[0]
    for key, value in added_values.items():
      if key in originaldict:
        originaldict[key][speciesIndex] = value #float('NaN' if value == 'NaN' else value)
    return originaldict



if overwrittingsinglecells:
     currentcopy=current.copy()
     speciesIndex=results.index[0]
     #sourcesreviewdf = pd.DataFrame(missingInfoSources, show_missing_info)
     
     st.write("Original results df as python dict")
     originaldict=results.to_dict()
     #st.write(originaldict)
     st.write("Original results back to df")
     #st.dataframe(pd.DataFrame.from_dict(originaldict))
     st.write("User changes in dataframe, formed by userchanges=pd.DataFrame(usermissingino, show_missing_info) ")
     userchanges=pd.DataFrame(usermissingino, show_missing_info)
     #st.write(userchanges)
     st.write("User changes dataframe to a python dict")
     userdict=userchanges.to_dict()
     st.write(userdict)
     
     st.write("trying to replace user dic values in original row values -")
     st.write(update_species(userdict, originaldict))
     originaldictupdatedtodf = pd.DataFrame.from_dict(originaldict)
     st.write("orginal row updated in dict form")
     st.write(originaldictupdatedtodf.to_dict())
     st.write("Updated results back to dataframe")
     st.write(originaldictupdatedtodf)
     st.write("Showing datatypes")
    
     st.write("Updated results to json - does it respect numerical values?-Nope")
     st.write(originaldictupdatedtodf.to_json(orient="columns"))
     st.write("Original results updated in dataset with json")
     copied=current.copy()
   
     try:
        currentcopy.loc[speciesIndex] =(originaldictupdatedtodf.loc[speciesIndex])
        st.write(currentcopy) 
     except:
        st.warning("Please check that values entered are in correct format e.g. numerical for values such as SVLMMx")
    
     

     

        
jsondata=[]
def create_json_data():
  for column in missingInfoColumns:
      jsondata.append({column:st.session_state[column]})
  return jsondata  



json_data = '{"Order":{"3":"Anura"},"Family":{"3":"Alsodidae"}}'
new_keys = '{"0":{"Order":"55","Family":"aus nesting"}}'

def update_user_json(originalresultsjson, userchangedfjson):
    data = json.loads(originalresultsjson)
    new_keys_data = json.loads(userchangedfjson)

    for key, value in new_keys_data[0].items():
        if key in data:
            data[key][str(results_index)] = value
    return data
    # json_data_final = json.dumps(data)
    # st.write(json_data_final)


print(json_data)
overwrittingsinglecellsjson=st.checkbox("Updating individual cells using json")

if overwrittingsinglecellsjson:
    results_index=results.index[0]
    st.write(results_index)
    newdb=current.copy()
    originalresultsjson=results.to_json(orient="columns")#)orient="columns")
    st.write("Species before user change json, orient columns")
    st.write(originalresultsjson)
    
    st.write("User changes in dataframe, formed by userchanges=pd.DataFrame(usermissingino, show_missing_info) ")
    userchanges=pd.DataFrame(usermissingino, show_missing_info)
    st.write(userchanges)
    st.write("User df changes to json")
    userchangedfjson=userchanges.to_json()
    st.write(userchangedfjson)
    showresults=st.checkbox("Show updated")


    if showresults:
        st.write("updating results json with user df json")
        updated_json=json.dumps(update_user_json(originalresultsjson, userchangedfjson))
        
        updateddfrow=pd.read_json(updated_json)
        st.write("Updating entire database")
       
        newdb.loc[results_index] =(updateddfrow.loc[results_index])
        st.write(newdb)
        st.write("Converting newdb at species updated location back to json to check intuition with datatypes")
        st.write(newdb.loc[results_index].to_json(orient="columns")) 
       
        
        

    
    


    # # Load the first json into a dictionary
    # data = {"Order":{"3":"Anura"},"Family":{"3":"Alsodidae"},"Genus":{"3":"Alsodes"},"Species":{"3":"australis"},"SVLMMx":{"3":None},"SVLFMx":{"3":None},"SVLMx":{"3":63.0},"Longevity":{"3":None},"NestingSite":{"3":None},"ClutchMin":{"3":None},"ClutchMax":{"3":None},"Clutch":{"3":None},"ParityMode":{"3":"Larval"},"EggDiameter":{"3":None},"Activity":{"3":None},"Microhabitat":{"3":"Semi-aquatic"},"GeographicRegion":{"3":"South America"},"IUCN":{"3":"DD"},"PopTrend":{"3":None},"RangeSize":{"3":7833.26157373},"ElevationMin":{"3":250.0},"ElevationMax":{"3":250.0},"Elevation":{"3":250.0}}
    # #originalresultsjson
    # # Load the second json into a dictionary
    # update = {"0":{"ClutchMin":"55","NestingSite":"aus nesting"}}
    # #userchangedfjson

    # # Update the values of ClutchMin and NestingSite in the first json
    # data["ClutchMin"][str(speciesIndex)] = update["0"]["ClutchMin"]
    # data["NestingSite"][str(speciesIndex)] = update["0"]["NestingSite"]
    
    # #originalresultsjson["ClutchMin"]["3"] = userchangedfjson["0"]["ClutchMin"]
   
    # # Convert the updated dictionary to a json string
    # updated_json = json.dumps(data)
    # st.write(updated_json)

    # # Print the updated json
    # st.write(updated_json)
    # st.write("new row after updating individual cells")
    # st.write(pd.read_json(updated_json))



    





def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, 
                     user_comment, status, reason_denied, approved_by, date_approved, current_database_path):
     """adding user"""
     #defining the email as the key
     return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, 
     "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, 
     "Reason_Denied":reason_denied, "Decided_By":approved_by, "Decision_Date":date_approved, "Dataset_In_Use":current_database_path })




jsonexperiemnt=st.checkbox("Convert results to a json file")

if jsonexperiemnt:
     st.write("Results as json orient columns - resultsjsoncols=results.to_json(orient='columns')")
     resultschangedjson=resultschanged.to_json(orient='columns')
     st.write(resultschangedjson)

     addtodb=st.button("Add to metadatabase")
     
     if addtodb:
        #add_to_database(str(now), resultschangedjson, "current db", "Filling Information Gaps", speciesdropdown, genusdropdown, "admin", "ruthveni Pristimantis loves info ", "Pending", "n/a", "n/a", "n/a", "current db" )
        st.write("Added to the meta database - COMMENTED OUT")
    
     retrievefromdb=st.button("Retrieve and convert back to dataframe")

     if retrievefromdb:
        st.write("Here's the new dataframe back")
        for database in databases:
                    if database["User_Comment"]=="ruthveni Pristimantis loves info ":
                        gapsfromdb=database["Changes"]
        st.write(gapsfromdb)
        fromjsondbtodf= pd.read_json(gapsfromdb)
        st.write((fromjsondbtodf.iloc[0]))



# updatewholedbbyrow=st.checkbox("Trying row replacement with json file")   
# if updatewholedbbyrow:
#     resultschangedjson=resultschanged.to_json(orient='columns')
#     st.write(resultschangedjson)
#     #st.write(pd.Series(resultschangedjson))
#     newresults=pd.read_json(resultschangedjson)
#     st.write(newresults)
#     st.write("updating whole dataset")
#     speciesIndex=results.index[0]
#     #df.loc[row_index] = new_row

#     copied=current.copy()
#     #if not copied.loc[speciesIndex].empty:
#     #updated=copied.loc[speciesIndex] ==pd.read_json(resultschangedjson, orient='columns')
#     try:
#         copied.loc[speciesIndex] =(newresults.loc[speciesIndex])
#         st.write(copied) 
#     except:
#         st.warning("Please check that values entered are in correct format e.g. numerical for values such as SVLMMx")
    

    



   

# st.write("Exploring image uploading")

# image_test=deta_connection.Base("image_testing")

# def insert_image(date, image_bytes):
#     """adding user"""
#     #defining the email as the key
#     return image_test.put({"key":date, "user_image": image_bytes, 
#      })




# uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "bmp", "gif", "tiff"])


# if uploaded_file is not None:
#     #read as bytes
#     file_bytes = uploaded_file.read()
#     #encode in base64
#     file_to_base64=base64.b64encode(file_bytes).decode()
#     #create json object for database storage
#     #json_image = {"image": file_to_base64}
#     st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
#     #st.write(json_image)
# else:
#     st.write("No file uploaded")
   



# dbimagetest=st.button("Save image to images_database")

# if dbimagetest:
#     #insert_image(str(now), "creating db" )

#     st.success("Image saved to the database! - COMMENTED OUT")








# if uploaded_file is not None:
#     # Convert the bytes data to a PIL Image
#     img = Image.open(uploaded_file)
#     # Save the image as JPEG
#     img.save("image.jpeg", "JPEG")


#uploaded_file = st.file_uploader("Add an Image")

# if uploaded_file is not None:
#     # To read file as bytes:
#     bytes_data = uploaded_file.getvalue()
#     st.header("image in bytes :")
#     st.write(bytes_data)

#     # To convert to a string based IO:
#     #stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
#     #st.write("String IO")
#     #st.write(stringio)

#     # To read file as string:
#     #string_data = stringio.read()
#     #st.write("String data")
#     #st.write(string_data)
   


















#----------------------------------------------------------------------------CODE FOR EDITTING EXISTING INFO--------------------------------------------------------------------------------#

#addinfo_options=st.multiselect("Add Information", ['SVLMMx', 'SVLFMx', 'SVLMx', 'Longevity', 'NestingSite', 'ClutchMin',	'ClutchMax',
#                             'Clutch', 'ParityMode',	'EggDiameter', 'Activity',	'Microhabitat', 'GeographicRegion',	'IUCN',	
#                             'PopTrend',	'RangeSize', 'ElevationMin','ElevationMax','Elevation'])

#st.write(addinfo_options)

#df.loc[0, 'A'] = 10

#get_missing_info_columns(results)

# def update_results(addinfo_options): #addinfo_options):
#     speciesIndex=results.index[0]
#     results_updated = results.copy()
    # for column in addinfo_options:
    #     results_updated.at[speciesIndex, column] = st.session_state[column]
#     # return results_updated


# dataframeapproach=st.checkbox("Replacing values with dataframe approach - hard coded")

# if dataframeapproach:
#     speciesIndex=results.index[0]
#     st.write("Results before")
#     st.write(results)
#     st.write("After results..copying old df and using df_new.at[index_label, 'column_name'] = new_value")
#     results_updated = results.copy()
#     results_updated.at[speciesIndex, 'SVLMMx'] = 99
#     #results.at[speciesIndex, 'Order']="Order updated"
#     st.write(results_updated)
#     st.write("Updating multiple at once -")
#     #df_new.at[index_label, ['column_name1', 'column_name2']] = [new_value1, new_value2]
#     results_multiple=results.copy()
#     results_multiple.at[speciesIndex, ('Order', 'Family', 'SVLMMx')] = ["New order", "New Family", 88 ]
#     st.write(results_multiple)

    



    
# jsonarraywithsessionstate=st.checkbox("Create json array using session state and columns")

# if jsonarraywithsessionstate:
#     create_json_data()
#     st.write(jsondata)

#dfaskeyvaluedict=st.checkbox("Turn df into key value pair dictionary")

# if dfaskeyvaluedict:
#     st.write("dict=results.to_dict()")
#     dict=results.to_dict()
#     st.write(dict)
#     st.write("dict.get('Species')")
#     st.write(dict.get("Species"))
#     st.write("Back to dataframe - dictreverted=pd.DataFrame(dict)")
#     dictreverted=pd.DataFrame(dict)
#     st.write(dictreverted)
#     st.write("dictorient=results.to_dict(orient='index')")
#     dictorient=results.to_dict(orient='index')
#     st.write(dictorient)
#     #dictnorec=results.to_dict('records')
#     #st.write(dictnorec.get("Family"))

# methodcheck=st.checkbox("Practicing value replacement using results as a dictionary - hardcoded")
# if methodcheck:
#     #st.write("code pending") 
#     dict=results.to_dict() 
#     #st.write("dict.update({'Family':'hardcoded update value'})")
#     #dict.update({'non existent column':'hardcoded update family'})
#     dict.update({'Order':'checking index preservation'})
#     st.write(dict)
#     dictreverted=pd.DataFrame(dict)
#     st.write(dictreverted)

# indexmethodcheck=st.checkbox("Practicing value replacement using results as a dictionary and keeping index - hardcoded")

# if indexmethodcheck:
#     #index = df.loc[df['A'] == 2].index[0]
#     #results=current.loc[(current["Species"] == speciesdropdown) & (current['Genus'] == genusdropdown)]
#     speciesIndex=results.index[0]
#     st.write(speciesIndex)
#     dictorient=results.to_dict(orient='index')
#     #st.write(dictorient)
#     dictorient[6]['Family'] = 'Fam update and preserving index for '
#     #dict.update({'Genus':'hardcoded update genus'})
#     st.write(dictorient)
#     dictreverted=pd.DataFrame(dictorient)
#     st.write(dictreverted)
#     st.write("code to be written")











# pythonobjectexperiemnt=st.checkbox("Convert results to a python object")

# if pythonobjectexperiemnt:
#     resultsjsoncols=results.to_json(orient='columns')
#     speciespythonobject= json.loads(resultsjsoncols)
#     st.write(speciespythonobject)
#     st.write("replacing family via speciespythonobject[2]='family replaced' - didnt work ")
#     speciespythonobject[2]="family replaced"
#     st.write(speciespythonobject)




   
  
    
    

