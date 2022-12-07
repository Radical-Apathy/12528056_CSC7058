from re import search
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridUpdateMode, JsCode #gridupdate mode remebers edited entries
from st_aggrid.grid_options_builder import GridOptionsBuilder
import streamlit_authenticator as stauth
import smtplib
import ssl
#import pickle
#from pathlib import Path
from email.mime.text import MIMEText # to enable html stuff with https://realpython.com/python-send-email/#sending-your-plain-text-email
from email.mime.multipart import MIMEMultipart
import db_connection as db


st.set_page_config(page_icon='amphibs.jpeg')

@st.cache
def load_to_edit():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean _towrite.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

dfToEdit = load_to_edit()
#email_address
if 'email_address' not in st.session_state:
    st.session_state['email_address'] = ""

#email_receiver = 'radical_apathy@outlook.com'
#st.session_state['email_address']
def sendEmail(email_receiver):
  email_sender='amphib.app@gmail.com'
  email_password = 'mfqk hxrk qtpp qqdp'
  message = MIMEMultipart("alternative")
  message["Subject"] = "Password Reset Request"
  message["From"] = email_sender
  message["To"] = email_sender

 #plain text and html versions of message for comparison
  text = """
  Hi AmphibiFan it's text,
  Please click on the link below to reset your password:
  https://radical-apathy-deployment-practice-forgotten-password-lu3mqh.streamlit.app/

  Requested password in error? No worries, continue logging in using your previous password.

  """
  html = """
  <html>
    <body>
      <p>Hi AmphibiFan it's from streamlit,<br>
        Please click on the link below to reset your password:<br>
        <a href="https://radical-apathy-deployment-practice-forgotten-password-lu3mqh.streamlit.app/">Reset Password</a> 
        
        Requested password in error? No worries, continue logging in using your previous password.
      </p>
    </body>
  </html>
  """

  # Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)
  message.attach(part2)
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context= context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, message.as_string())
    


st.header(":lower_left_ballpoint_pen: :lower_left_fountain_pen: :lower_left_paintbrush: :lower_left_crayon: Change GABiP")

#st.session_state
#email=['radical_apathy@outlook.com','j_calder@outlook.com']
#firstname=['radical_apathy', 'j_calder']
#surname= ['Campbell', 'Calder']
#username = ['Claire','Jonny']
#password=['abc123', 'def456']
#admin= ['True', 'False']
#file_path= Path(__file__).parent/"hashed_pws.pkl"


#with file_path.open("rb") as file:
 # hashed_passwords = pk.load(file)

#getting all users from db


users=db.get_all_users() #returns users as dictionary of key value pairs

#converting to list comprehension so it can be passed into the authenticator
#specifically converting values we want for the login part
email=[user["key"] for user in users]
username=[user["username"] for user in users]
hashed_passwords=[user ["password"] for user in users]

  
authenticator = stauth.Authenticate(username, hashed_passwords,
    "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


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

    st.sidebar.title(f"Welcome {username}")
st.write("Forgotten username/password? Enter your email below and we'll send a reminder")
email_receiver=st.text_input("Email Address")
remindme=st.button("send a reminder")
if remindme:
    sendEmail(email_receiver)




#------------Attempts at button and text for send email...parking it for now


#formTest=st.button("Using a form")

#if formTest:
 #   with st.form("my_form"):
 #    st.write("Inside the form")
 #    email_address =st.text_input("Enter email address")
 #    submitted = st.form_submit_button("Show email")
 #    if submitted:
  #     st.write(submitted)
   # emailForm=st.form("my_form")
   
  #  email_address =emailForm.text_input("Email Address")

   # sendit = emailForm.form_submit_button("Send")
   # if sendit:
    #    sendEmail(email_address)
  
 
   # Every form must have a submit button.
   

#testing=st.button("hard coded email address")
#if testing:
 #   st.write("Calling email method")
 #   email_receiver = 'radical_apathy@outlook.com'
 #   sendEmail(email_receiver)



#reminder = st.button("Send Reset Link")
#if reminder:
#       email_receiver=st.text_input("Enter your email address and we'll send you a link")#, key='email_address')
#       if email_receiver:
         #st.write(email_receiver)
#         sendEmail(email_receiver)

#reminder2 = st.button("Trying session state")
#if reminder2:
#       email_receiver=st.text_input("Enter your email address and we'll send you a link", key='email_address')

#       sendit=st.button("Send now")
#       if email_receiver and sendit:
#          sendEmail(st.session_state['email_address'])      
                 
        
