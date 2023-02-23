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
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
import io
st.set_page_config(page_icon='amphibs.jpeg')

# Use the client ID and secret to create an OAuth 2.0 flow
creds = Credentials.from_authorized_user_info(st.secrets["gcp_drive_account"])

# Access the user's Google Drive

service = build("drive", "v3", credentials=creds)


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

#------------------------------------------------------------META DATABASE CONNECTION-----------------------------------------------------------------------------------------#
metaData=deta_connection.Base("database_metadata")

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


latest_approved_ds=get_latest_ds(approvedordered[0])

folder_id="1sXg0kEAHvRRmGTt-wq9BbMk_aAEhu1vN"

def get_latest_file_id(latest_approved_ds):
     
     results = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false and parents in '{0}'".format(folder_id), fields="nextPageToken, files(id, name)").execute()
     items = results.get('files', [])

     if not items:
         st.write('No files found.')
     else:
        for item in items:
             if item['name'] == latest_approved_ds:
                 
                 return item['id']



latest_id=get_latest_file_id(latest_approved_ds)


#@st.cache_data
def load_latest():
    current_db = pd.read_csv(f"https://drive.google.com/uc?id={latest_id}", encoding= 'unicode_escape')#, low_memory=False)
    return current_db

def add_changes(dataframe, dataframe2):
    updated=dataframe.append(dataframe2, ignore_index = True)
    return updated

#gets dates for new species additions needing approval
pending=[]


def get_pending():
    for database in databases:
        
            if database["Edit_Type"]=="New Species Addition" and database["Status"] =="Pending":
                
             pending.append(database["key"])

get_pending()

ordered=sorted(pending,reverse=True)

#------------------------------------------------------------IMAGES DATABASE CONNECTION-----------------------------------------------------------------------------------------#
users_images=deta_connection.Base("user_images")

def add_to_image_db(date_submitted, genus, species, submitted_by,  decision_date, decided_by, image_ids):
     return users_images.put({"key":date_submitted, "Genus": genus, "Species": species, "Submitted_By": submitted_by,"Decision_Date": decision_date, "Decided_By": decided_by, "Images": image_ids  })

     
#-------------------------------------------------------------ADMIN USERS_DB METHODS--------------------------------------------------------------------------------------------#

def get_current_user(email):
    print (users_db.get(email))

def approve_user(username, updates):
    return users_db.update(updates, username)

#gets and displays users pending approval
def display_pending_users():
    st.markdown("***")
    for user in users:
     if user["approved"]=="False":
       with st.form(user["username"]):
        st.markdown(f"""<p style="font-family:sans-serif; color:ForestGreen; font-size: 20px;"><strong>***********{user["username"]}'s Request**********</strong></p>""" , unsafe_allow_html=True)
        st.text(f"Username : " +user["username"])
        st.text(f"Firstname : " +user["firstname"])
        st.text(f"Surname : " +user["surname"])
        st.text(f"Email : " +user["key"])
        checkbox1 = st.checkbox(f"Allow " + user["firstname"] + " access")
        checkbox2 = st.checkbox(f"Place " +user["firstname"] +" in review list")
        confirmForm = st.form_submit_button(f"Submit Decision for  : " + user["username"])
        if checkbox1 and checkbox2 and confirmForm:
            st.error("Warning! Both options have been selected. Please review decision")
        elif checkbox1 and confirmForm:
            approve_user(user["key"], updates={"approved": "True"})
            st.success(f"Accepted! "+user["username"]+ " can now access the GABiP. You can revoke access at any time using the View Approved user's option")
        elif checkbox2 and confirmForm:
            st.warning(f"User now place in to review section. " +user["username"]+ " 's access can be decided upon another date" )
      
        st.markdown("""<p style="font-family:sans-serif; color:ForestGreen; font-size: 20px;"><strong>**************************************************************************************</strong></p>""", unsafe_allow_html=True )
        st.write("***")

#-----------------------------------------------------------------------SCREEN DISPLAY METHODS-----------------------------------------------------------------------------------------------------------------------------#  
     #---------------------------------------------------------------NEW ADDITION REVIEW SCREEN -------------------------------------------------------------------------------------------------#
def new_species_review():
    current=load_latest()

    st.write("New species additions in order of date submitted")
    datesubmitted = st.selectbox(
    'Date submitted',
    (ordered))



    if datesubmitted:

        tab1, tab2, tab3, tab4 = st.tabs(["Species Added", "User Info", "User Source", "User Edit History"])

        #tab1 methods
        for database in databases:
                if database["key"]==datesubmitted:
                    newAdd=database["Changes"]
        
        user_changes= pd.read_json(newAdd)
        tab1.write(user_changes)

        tab1.write("Displaying vertically")
        tab1.dataframe(user_changes.iloc[0], width=300)


        #tab2 methods
        for database in databases:
                if database["key"]==datesubmitted:
                    author=database["Edited_By"]
                    authorComment=database["User_Comment"]
        for user in users:
                if user["username"]==author:
                    authorName=user["firstname"]
                    authorSurname = user["surname"] 
                    authorEmail= user["key"]
                    
        tab2.write("Author firstname: "+" "+" "+authorName)
        tab2.write("Author surname: "+" "+" "+authorSurname)
        tab2.write("Author email: "+" "+" "+authorEmail)

        tab3.write("User comments: "+ " "+" "+ authorComment)

        tab4.subheader("User edit history")
        tab4.write("This is tab 4")


        preview=st.checkbox("Preview new addition to current dataset")




        def preview_addition(df1,df2):
            
            
            proposed=df1.append(df2, ignore_index=True)
            st.dataframe(proposed)
            

        now=datetime.now()
        version=now.strftime("%d.%m.%Y-%H.%M.%S")
        
        newPath=version+"-"+st.session_state['username']+"-approved"+".csv"

        def create_new_addition_dataset():

            
            newDataset=current.append(user_changes, ignore_index=True)
            csv_bytes = io.StringIO()
            newDataset.to_csv(csv_bytes, index=False)
            csv_bytes = csv_bytes.getvalue().encode('utf-8')
    
            # upload bytes to Google Drive
            file_metadata = {'name': newPath, 'parents': [folder_id], 'mimeType': 'text/csv'}
            media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

       
        
        #updates the status, 
        def update_GABiP():
            updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath, "Dataset_Pre_Change":latest_approved_ds }
            metaData.update(updates, datesubmitted)
        
        def reject_new_addition():
            updates = {"Status":"Denied", "Reason_Denied":reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latest_approved_ds, "Dataset_Pre_Change":latest_approved_ds }
            metaData.update(updates, datesubmitted)



        if preview:
            try:
                newDataset=preview_addition(current, user_changes)
                col1,col2=st.columns(2)

                accept=col1.button("Approve Addition")
                reject=col2.button("Deny Addition")

                        
                if accept:
                    create_new_addition_dataset()
                    update_GABiP()
                    st.write("GABiP updated!")


            
                reason=col2.text_area("Reasons for declining", key='reason') 

                

                if reject and reason:           
                    reject_new_addition()
                    col2.write("Addition rejected")
                elif reject:
                    col2.warning("Please add a reason for rejection")
            except:
             st.write("User entered non numerical data in number fields. Unable to append new addition to current dataset")
                

#-----------------------------------------------------------------------NEW INFORMATION ADDITION DISPLAY-----------------------------------------------------------------------------------------------------------------------------#

    
    





























def welcome_screen():
    def load_welcome_bg():
        st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr31l_orig.jpg.jpg");
                    background-attachment: fixed;
                    background-size: cover;
                    background-position: center;
                    opacity: 0.1
                    color: #ffffff; 
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    load_welcome_bg()
    
#-----------------------------------------------------------------------------------EDIT REQUEST OPTIONS SCREEN-------------------------------------------------------------------------------------------------------#
def admin_edit_options():
    options=st.sidebar.radio("Options", ('Show Current Database','New Species Entry', 'New Species Information', 'Species Edit Requests', 'Information Removal Requests', "Species Removal Requests" ), key='admin_current_option')
    if options == "Show Current Database":
        st.write("Current Database")
        current=load_latest()
        #currentstyled=current.style.set_properties(**{'background-color':'white', 'color':'black'})
        st.write(current) 

    if options == "New Species Entry":
        new_species_review()
    if options== "New Species Information":
        st.write("coming soon")




#---------------------------------------------------------------------------------MAIN WELCOME SCREEN--------------------------------------------------------------------------------------------------------#
def admin_welcome_screen():
    
    st.subheader("Welcome to the Admin Area.")

    adminOptions= st.selectbox(" Admin Options", ['Manually upload a new Database','View Access Requests', 'View existing users','See edit requests'  ])
    if adminOptions=="Click here to see Admin options":
        welcome_screen()
    if adminOptions=="View Access Requests":
         display_pending_users()
    if adminOptions == "See edit requests":
        admin_edit_options()


    #st.markdown("***")

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

def load_login_bg():
        st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/cr31l_orig.jpg");
                        background-attachment: fixed;
                        background-size: cover;
                        background-position: center;
                        opacity: 0.1
                        color: #ffffff; 
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

load_login_bg()



authenticator = stauth.Authenticate(email, username, hashed_passwords,
    "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


if authentication_status == False:
     st.warning("**Username/password is not recognised**")
     st.write("**Forgotten username/password? Enter your email below and we'll send a reminder**")

     sendReminder = st.checkbox("Send Password Reminder")
     if sendReminder:
         email=st.text_input("Email address")
         sendbutton=st.button("Send reminder")
         if sendbutton and email:
             sendEmail(email)
             st.success("Email sent...please check your inbox for a password reset link")
         elif sendbutton:
             st.warning("Please enter an email address")
elif authentication_status == None:
     st.warning("Please enter username and password")
else:
     for user in users:
         if user["username"] == st.session_state['username'] and user["admin"] == "True":
             st.write("Welcome, you're an admin.")
             admin_welcome_screen()         
         elif user["username"] == st.session_state['username'] and user["admin"] == "False":
             if user["approved"] == "True" and user["admin"] == "False":
                 st.write(f"**Welcome {user['firstname']}, you're a trusted member. However, this section is for Admin users only**")
                 
             else:
                 st.write(f"Welcome {user['firstname']}, your access request is pending approval. We'll send you an e-mail alert to inform you of the status.")
  
authenticator.logout("Logout", "sidebar")

       




          
        




#------------------------------------------------------------PASSWORD REMINDER SECTION-----------------------------------------------------------------------------------------#

# st.write("Forgotten username/password? Enter your email below and we'll send a reminder")

# sendReminder = st.checkbox("Send Password Reminder")
# if sendReminder:
#     email=st.text_input("Email address")
#     sendbutton=st.button("Send reminder")
#     if sendbutton and email:
#         sendEmail(email)
#         st.success("Email sent...please check your inbox for a password reset link")
#     elif sendbutton:
#         st.warning("Please enter an email address")