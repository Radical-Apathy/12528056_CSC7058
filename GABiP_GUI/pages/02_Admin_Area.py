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


@st.cache
def load_latest():
    current_db = pd.read_csv(latestds, encoding= 'unicode_escape', low_memory=False)
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

#-----------------------------------------------------------------------DISPLAY METHODS-----------------------------------------------------------------------------------------------------------------------------#  

def new_species_review():
    current=load_latest()

    st.write("New species additions in order of date submitted")
    datesubmitted = st.selectbox(
    'Date submitted',
    (ordered))


    
    #get_changes_csv(ordered[0])

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
                    #tab2.write(((user["firstname"],user["surname"], user["key"])))
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
            #result = df1.append(df2, ignore_index=True).append(df3, ignore_index=True)
            
            proposed=df1.append(df2, ignore_index=True)
            last_row=proposed.iloc[-1]
            st.dataframe(proposed.style.applymap(lambda _: 'background-color: yellow', subset=pd.IndexSlice[last_row.name, :]))



        now=datetime.now()
        version=now.strftime("%d.%m.%Y-%H.%M.%S")
        path_prefix="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/"
        #path_end = version
        newPath=path_prefix+version+"-"+st.session_state['username']+"-approved"+".csv"

        

        def create_new_dataset():
            newDataset=current.append(user_changes, ignore_index=True)
            newDataset.to_csv(newPath, index=False)
        
        #updates the status, 
        def update_GABiP():
            updates = {"Status":"Approved", "Reason_Denied":"n/a", "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":newPath, "Dataset_Pre_Change":latestds }
            metaData.update(updates, datesubmitted)
        
        def reject_addition():
            updates = {"Status":"Denied", "Reason_Denied":reason, "Decided_By":st.session_state['username'], "Decision_Date":str(now), "Dataset_In_Use":latestds, "Dataset_Pre_Change":latestds }
            metaData.update(updates, datesubmitted)



        if preview:
            try:
                newDataset=preview_addition(current, user_changes)
                col1,col2=st.columns(2)

                accept=col1.button("Approve Addition")
                reject=col2.button("Deny Addition")

                        
                if accept:
                    create_new_dataset()
                    update_GABiP()
                    st.write("GABiP updated!")


            
                reason=col2.text_area("Reasons for declining", key='reason') 

                

                if reject and reason:           
                    reject_addition()
                    col2.write("Addition rejected")
                elif reject:
                    col2.warning("Please add a reason for rejection")
            except:
             st.write("User entered non numerical data in number fields. Unable to append new addition to current dataset")
                



    
    





























def welcome_screen():
    st.image("amphibs.jpeg", width=200)

def admin_edit_options():
    options=st.sidebar.radio("Options", ('Show Current Database','New Species Entry', 'Add Species Information',  'Remove Species Information', 'Edit Species Information'), key='admin_current_option')
    if options == "Show Current Database":
        st.write("Current Database")
        current=load_latest()
        #currentstyled=current.style.set_properties(**{'background-color':'white', 'color':'black'})
        st.write(current) 

    if options == "New Species Entry":
        new_species_review()



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

st.header("**************************:lock:Admin Section:lock_with_ink_pen:**************************")



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
            admin_welcome_screen()        
        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "False":
            st.write(f"Welcome ",user["firstname"], " you're a trusted member. However, This section is for members with admin status only. You may request admin status")
          
        

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