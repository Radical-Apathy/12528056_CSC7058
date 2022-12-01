from re import search
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridUpdateMode, JsCode #gridupdate mode remebers edited entries
from st_aggrid.grid_options_builder import GridOptionsBuilder
import streamlit_authenticator as stauth
import pickle as pk
from pathlib import Path

st.set_page_config(page_icon='amphibs.jpeg')

@st.cache
def load_to_edit():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean _towrite.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

dfToEdit = load_to_edit()

if 'login_option' not in st.session_state:
    st.session_state['login_option'] = "Login"

#if 'logged_in' not in st.session_state:
 #   st.session_state['logged_in'] = False
#if 'login_button' not in st.session_state:
 #   st.session_state['login_button'] = True
st.header(":lower_left_ballpoint_pen: :lower_left_fountain_pen: :lower_left_paintbrush: :lower_left_crayon: Change GABiP")

#st.session_state
names=['Claire Campbell', 'Jonny Calder']
usernames = ['Claire','Jonny']
file_path= Path(__file__).parent/"hashed_pws.pkl"


with file_path.open("rb") as file:
  hashed_passwords = pk.load(file)
  
  
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "change_database", "abcdef")


credentials=st.radio("Login or Sign up", ('Login','Sign Up'), key='login_option')
 #creating an authentication object
 #abcdef is a random generated key used to hash cookie signature
if credentials=="Login" :
    
    #authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    #"sales_dashboard", "abcdef")

    name, authentication_status, username = authenticator.login("Login", "main") #main here refers to position
    #put code here to offer email for password reset
    st.write("Forgotten username/password?")
    reminder = st.button("Send Reset Link")
    if reminder:
        emailAddress=st.text_input("Enter your email address and we'll send you a link")
       #make a method that checks the email array/db





    if authentication_status == False:
      st.error("Username/password is not recognised")

    if authentication_status == None:
      st.warning("Please enter username and password")

    if authentication_status:
      #st.session_state['logged_in'] == True
  
      options=st.sidebar.radio("Options", ('Default Welcome Option','Show Database','Add Entry', 'Update an Existing Entry',  'Delete an Entry'), key='current_option')
  
      if options == 'Default Welcome Option':
        st.write(f"Successfully logged in as {name}")
        st.balloons()
    
    
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
          species =st.text_input("Species","Species - e.g. Relicta", key='Species')
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
      if options == 'Update an Existing Entry':
          st.header('Update Entry page')

      authenticator.logout("Logout", "sidebar")
      if options == 'Delete an Entry':
        st.write("Delete an entry page")    

      st.sidebar.title(f"Welcome {name}")
if credentials=="Sign Up":
   with st.form("my_form"):
      st.write("Register")
      username =st.text_input("Username", "Enter a username")#, key='Order')
      password =st.text_input("Password", "Enter a Password", type='password')#key='Family')
      confirmPassword =st.text_input("Re-type Password", "Re-Enter Password", type='password')# key='Genus')
      #need to check if user exists  
      submitted = st.form_submit_button("Register")
      if submitted and password == confirmPassword:
          st.write(username, password, confirmPassword)
          #send an email alert to new users informing them that an dmin will be in touch
          #send an email alert to admin with the new users details i.e. first name, last name, email, message 
      else:
          st.write("passwords do not match")
          st.write(username, password, confirmPassword)







  












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