import streamlit_authenticator as stauth
import streamlit as st
#import db_connection as db
import smtplib
import ssl
from email.mime.text import MIMEText # to enable html stuff with https://realpython.com/python-send-email/#sending-your-plain-text-email
from email.mime.multipart import MIMEMultipart
import pandas as pd
import numpy as np
import os
from deta import Deta
import csv
from dotenv import load_dotenv
from datetime import datetime
st.set_page_config(page_icon='amphibs.jpeg')

#------------------------------------------------------------DATABASE CONNECTIONS-----------------------------------------------------------------------------------------#
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
#-------------------------------------------------------------USERS_DB METHODS--------------------------------------------------------------------------------------------#


#------------------------------------------------------------DATABASE_METADATA DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#initialising a deta object
deta_connection= Deta(deta_key)

database_metadata=deta_connection.Base("database_metadata")

#------------------------------------------------------------ DATABASE_METADATA DATABASE METHODS-----------------------------------------------------------------------------------------#

#fetching info from the database
def get_all_paths():
    res = database_metadata.fetch()
    return res.items


#calling method and creating a list comprehension
databases=get_all_paths()

date_time= sorted([database["key"] for database in databases], reverse=True)
status=[database["Status"] for database in databases]
path = [database["Current Dataset"] for database in databases]

#getting the most recent approved csv file
def get_latest():
    for database in databases:
     for i in date_time:
        
      if database["key"]== i and database["Status"] =="Approved":
        break
    return(database["Current Dataset"])

#add user's entries to csv 
def add_to_database(date_time, changes_file_Path, dataset_pre_change, edit_type, species_affected, genus_affected, username, user_comment, status, reason_denied, approved_by, date_approved, current_database_path):
    """adding user"""
    #defining the email as the key
    return database_metadata.put({"key":date_time, "Changes": changes_file_Path, "Dataset_Pre_Change": dataset_pre_change, "Edit_Type": edit_type, "Species_Affected": species_affected, "Genus_Affected": genus_affected,"Edited_By":username,"User_Comment": user_comment, "Status":status, "Reason_Denied":reason_denied, "Approved_By":approved_by, "Date_Approved":date_approved, "Current Dataset":current_database_path })


path=get_latest()

@st.cache
def load_latest():
    current_db = pd.read_csv(path, encoding= 'unicode_escape', low_memory=False)
    return current_db


current_db=load_latest()

#------------------------------------------------------------SESSION STATE INITIATION--------------------------------------------------------------------------------------------#

if 'comment' not in st.session_state:
    st.session_state['comment']=""

#creating session state variables for each column in dataset
def create_session_states(dbColumns):
    for column in dbColumns:
        if column not in st.session_state:
           st.session_state[column] =""
         
#st.session_state

#-------------------------------------------------------------------------LOGIN DISPLAY PAGE METHODS-----------------------------------------------------------------------------#
def welcome_screen():
    st.image("amphibs.jpeg", width=200)


#--------------------------------------------------------------------------SHOW DATABASE PAGE------------------------------------------------------------------------------------#

def show_db():
    st.write(current_db)

#--------------------------------------------------------------------------ADD ENTRY PAGE------------------------------------------------------------------------------------#

def add_entry_page():
    #-----------------Methods for adding an entry---------------------------#
#enforcing mandatory fields
    def blank_validation(states=['order','family','genus','species']):
        for i in states:
         if i=="":
            st.warning("Order, Family, Genus, Species fields can not be left blank. Please recheck mandatory field section")

    #displays text fields for optional information
    def display_extra_fields():
        for option in more_options:
            userText=st.text_input(option, key=option)
            st.session_state[option] == userText

    #sets session state values for optional extra fields
    def get_extra_userinfo():
     for option in more_options:
        
        userText=st.text_input(option, key=option)
        if userText:
         st.session_state[option] == userText
        elif not userText :
            st.session_state[option]==""


    #stores user info in an array      
    def populate_userinfo():
        for column in dbColumns:
            userInfo.append(st.session_state[column])

    #checking that both the genus and species submitted don't exist on current csv    
    def check_current_db(genus, species):
        if genus.lower() in current_db["Genus"].str.lower().values and species.lower() in current_db["Species"].str.lower().values:
            st.warning(f"Data already exists for " +genus+ " " +species+ " Check full dataset option and consider making and edit to current dataset instead of an addition") 

    #contructs a dataframe for user to see summary of their addition
    def construct_review_dataframe(userinfo, columns=current_db.columns):
        completed = pd.DataFrame(userInfo, current_db.columns)
        #st.write(completed)
        st.dataframe(completed, width=300) 

    #creates a csv file with users addition
    def create_csv(columnrow, inforow):
        with open(newPath,  'w', encoding= 'UTF8', newline='') as f:
            writer=csv.writer(f)
            writer.writerow(columnrow)
            writer.writerow(inforow)


    

 #st.write(current_db)
    path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"
    dbColumns=current_db.columns

 #creating session state variables for csv columns
    create_session_states(dbColumns)


    userInfo=[]

    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 30px;"><strong>***      * Mandatory Fields *        ***</strong></p>', unsafe_allow_html=True)
    order =st.text_input("Order","Order - e.g. Anura", key='Order') 

    family =st.text_input("Family","Family - e.g. Allophrynidae", key='Family')

    genus =st.text_input("Genus", "Genus - e.g. Allophryne", key='Genus')

    species =st.text_input("Species","Species - e.g. Relicta", key='Species')


 #----------------------------------------------------------------MANAGING ADDITIONAL FIELDS -------------------------------------------------------#
    st.markdown('***')
    st.markdown('<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>More Options</strong></p>', unsafe_allow_html=True)
    more_options=st.multiselect("Add more Information", ['SVLMMx', 'SVLFMx', 'SVLMx', 'Longevity', 'NestingSite', 'ClutchMin',	'ClutchMax',
                             'Clutch', 'ParityMode',	'EggDiameter', 'Activity',	'Microhabitat', 'GeographicRegion',	'IUCN',	
                             'PopTrend',	'RangeSize', 'ElevationMin','ElevationMax','Elevation'])


    if more_options:
     get_extra_userinfo()


   
    review_information=st.button("Review Information")
       

    if review_information:
    
     populate_userinfo()
     blank_validation([st.session_state['Order'], st.session_state['Family'], st.session_state['Genus'], st.session_state['Species']])
     check_current_db(st.session_state['Genus'], st.session_state['Species']) 
     userdf=construct_review_dataframe(userInfo, columns=current_db.columns)
    

    user_message=st.text_area("Please leave a comment citing the source for this addition", key='comment')
    

    commit_changes=st.button("Submit for review")

    now=datetime.now()
    timeStamp=now.strftime("%d.%m.%Y-%H.%M.%S")
    path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/pending changes/Additions/"
    path_end = timeStamp
    newPath=path_prefix+path_end+"-"+st.session_state['username']+".csv"



    
    
    if commit_changes and user_message=="":  
     st.error("Please add a source")
    if commit_changes and genus.lower() in current_db["Genus"].str.lower().values and species.lower() in current_db["Species"].str.lower().values:
     st.error("Information already exists for "+ st.session_state['Genus'] + " "+st.session_state['Species'] +" check Full Database and make an addition via an edit") 
    elif commit_changes and user_message:
      populate_userinfo()
      columnrow=current_db.columns
      inforow=userInfo
      create_csv(columnrow, inforow)
      add_to_database(str(now), newPath, get_latest(), "Addition", st.session_state["Species"], st.session_state["Genus"], st.session_state["username"], st.session_state["comment"], "Pending", "n/a", "n/a", "n/a", get_latest())
      st.markdown('<p style="font-family:sans-serif; color:Red; font-size: 30px;"><strong>***      ADDITION SUBMITTED        ***</strong></p>', unsafe_allow_html=True)    

    
    
    
    




#--------------------------------------------------------------------------GABiP EDIT OPTIONS------------------------------------------------------------------------------------#
def show_options():
    options=st.sidebar.radio("Options", ('Show Full Database','New Species Entry', 'Update an Existing Entry',  'Delete an Entry'), key='current_option')     
    
    if options == "Show Full Database":
        show_db()
    if options == "New Species Entry":
        add_entry_page()












#-------------------------------------------------------------------------SEND EMAIL METHOD---------------------------------------------------------------------------#
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


#-----------------------------------------------------------------------HOME PAGE-----------------------------------------------------------------------------------------------------------------------------#  

st.header(":lower_left_ballpoint_pen: :lower_left_fountain_pen: :pencil: :pencil2: :lizard: Change GABiP")



authenticator = stauth.Authenticate(email, username, hashed_passwords,
    "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


if authentication_status == False:
      st.error("Username/password is not recognised")

if authentication_status == None:
      st.warning("Please enter username and password")

       


if authentication_status:
        
    for user in users:
        if user["username"] == st.session_state['username'] and user["approved"] == "False":
            st.write(f"Welcome ",user["firstname"], " your access request is pending approval. We'll send you an e-mail alert to inform you of the status")
        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "True":
            welcome_screen(), show_options()         
        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "False":
            st.write(f"Welcome ",user["firstname"], " you're a trusted member")
            welcome_screen(), show_options()
        

authenticator.logout("Logout", "sidebar")



#------------------------------------------------------------PASSWORD REMINDER SECTION-----------------------------------------------------------------------------------------#

st.write("Forgotten username/password? Enter your email below and we'll send a reminder")

sendReminder = st.checkbox("Send Password Reminder")
if sendReminder:
    email=st.text_input("Email address")
    sendbutton=st.button("Send reminder")
    if sendbutton and email:
        sendEmail(email)
        st.success("Email sent...please check your inbox for a password reset link")
    elif sendbutton:
        st.warning("Please enter an email address")