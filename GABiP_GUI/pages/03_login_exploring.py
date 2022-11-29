from re import search
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridUpdateMode, JsCode #gridupdate mode remebers edited entries
from st_aggrid.grid_options_builder import GridOptionsBuilder
import streamlit_authenticator as stauth
import pickle as pk
from pathlib import Path

@st.cache
def load_to_edit():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean _towrite.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

dfToEdit = load_to_edit()

st.header("Authentication Behaviour Exploring")


names=['Claire Campbell', 'Jonny Calder']
usernames = ['Claire','Jonny']
file_path= Path(__file__).parent/"hashed_pws.pkl"

with file_path.open("rb") as file:
  hashed_passwords = pk.load(file)

#creating an authentication object
#abcdef is a random generated key used to hash cookie signature
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef")

name, authentication_status, username = authenticator.login("Login", "main") #main here refers to position

if authentication_status == False:
  st.error("Username/password is not recognised")

if authentication_status == None:
  st.warning("Please enter username and password")

if authentication_status:
  st.write("you're logged in now!")
  options=st.sidebar.radio("Options", ('Show Database','Add Entry', 'Update an Existing Entry',  'Delete an Entry'), key='current_option')
  if options == 'Show Database':
    #col_opt = st.selectbox(label ='Select column',options = dfToEdit.columns)
    gd=GridOptionsBuilder.from_dataframe(dfToEdit.head())   
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)
    cell_js=JsCode("""
        function(params){
            if (params.value == 'Allophrynidae') {
                return {
                    'color': 'black',
                    'backgroundColor' : 'orange'
            }
            }
            if (params.value == 'Alsodes') {
                return{
                    'color'  : 'black',
                    'backgroundColor' : 'red'
                }
            }
            else{
                return{
                    'color': 'green',
                    'backgroundColor': 'white'
                }
            }
       
    };
    """)
    gd.configure_columns(dfToEdit.columns, cellStyle=cell_js)
    gridStyle=gd.build()
    st.header("Showing different styles of showing database")
    st.write("Not using AG grid", dfToEdit.head())
    show_table = AgGrid(dfToEdit.head(), gridOptions=gridStyle,
                 enable_enterprise_modules=True,
                 update_mode = GridUpdateMode.SELECTION_CHANGED,
                 allow_unsafe_jscode=True)
  
  
  
  
  
  
  if options == 'Add Entry':
    st.header('Add Entry page')
    with st.form("my_form"):
      st.write("Inside the form")
      order =st.text_input("Order","Order - e.g. Anura", key='Order')
      family =st.text_input("Family","Family - e.g. Allophrynidae", key='Family')
      genus =st.text_input("Genus", "Genus - e.g. Allophryne", key='Genus')
      submitted = st.form_submit_button("Submit")
      if submitted:
       st.write(order, family, genus)
 
    

    
  if options == 'Update an Existing Entry':
    st.header('Update Entry page')
    gd=GridOptionsBuilder.from_dataframe(dfToEdit.head())   
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)
    gd.configure_selection(use_checkbox=True)
    gridStyle=gd.build()
    edit_table = AgGrid(dfToEdit.head(), gridOptions=gridStyle,
                 update_mode = GridUpdateMode.SELECTION_CHANGED,
                 allow_unsafe_jscode=True)

authenticator.logout("Logout", "sidebar")

st.sidebar.title(f"Welcome {name}")

















#creating names and passwords - helper script to create credentials, comments out so doesnt constantly
#be ran 

#names=['Claire Campbell', 'Jonny Calder']
#usernames = ['Claire','Jonny']
#passwords = ['123', '456'] (commented out so i remember them)
#hashing passwords using streamlit authenticator
#streamlit authneticator uses "bcrypt" hashing algo which is considered very secure
#hashed_passwords= stauth.Hasher(passwords).generate()

#file_path= Path(__file__).parent/"hashed_pws.pkl"

#with file_path.open("wb") as file:
 # pk.dump(hashed_passwords, file)

#----user authentication.....