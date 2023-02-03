import streamlit_authenticator as stauth
import streamlit as st
#import db_connection as db
import smtplib
import ssl
from email.mime.text import MIMEText # to enable html stuff with https://realpython.com/python-send-email/#sending-your-plain-text-email
from email.mime.multipart import MIMEMultipart
from deta import Deta
import os
from dotenv import load_dotenv


#------------------------------------------------------------DATABASE CONNECTION-----------------------------------------------------------------------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#deta_key = st.secrets["deta"]["deta_key"]
#initialising a deta object
deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

def get_all_users():
    res = db.fetch()
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
#-------------------------------------------------------------ADMIN ONLY METHODS--------------------------------------------------------------------------------------------#

def insert_user(email, username, firstname, surname, admin, approved, hashed_password):
    """adding user"""
    #defining the email as the key
    return db.put({"key":email, "username": username, "firstname": firstname, "surname":surname, "admin":admin, "approved": approved,"password": hashed_password })

def get_current_user(email):
    print (db.get(email))

def approve_user(username, updates):
    return db.update(updates, username)

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


#-------------------------------------------------------------------------DISPLAY METHODS-----------------------------------------------------------------------------#
def welcome_screen():
    st.image("amphibs.jpeg", width=200)

def admin_welcome_screen():
    st.header("**************************:lock:Admin Section:lock_with_ink_pen:**************************")
    st.subheader("Welcome to the Admin Area.")

    adminOptions= st.selectbox(" Admin Options", ['Click here to see Admin options','View Access Requests', 'View approved users','See pending changes'  ])
    if adminOptions=="Click here to see Admin options":
        welcome_screen()
    if adminOptions=="View Access Requests":
         display_pending_users()

    #st.markdown("***")

#--------------------------------------------------------------------------GABiP EDIT OPTIONS-------------------------------------------------------------------------#
def show_options():
    options=st.sidebar.radio("Options", ('HTML Form','Show Database','Add Entry', 'Update an Existing Entry',  'Delete an Entry'), key='current_option')     
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





#-----------------------------------------------------------------------MAIN PAGE-----------------------------------------------------------------------------------------------------------------------------#  

st.header(":lower_left_ballpoint_pen: :lower_left_fountain_pen: :pencil: :pencil2: :lizard: Change GABiP")



authenticator = stauth.Authenticate(email, username, hashed_passwords,
    "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


if authentication_status == False:
      st.error("Username/password is not recognised")

if authentication_status == None:
      st.warning("Please enter username and password")

#if authentication_status:
#    options=st.sidebar.radio("Options", ('HTML Form','Show Database','Add Entry', 'Update an Existing Entry',  'Delete an Entry'))#, key='current_option')
#    for user in users:
#        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "True":
#            admin_welcome_screen()         
#        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "False":
#            st.write(f"Welcome ",user["firstname"], " you're a trusted member")
#        if user["username"] == st.session_state['username'] and user["approved"] == "False":
#            st.write(f"Welcome ",user["firstname"], " your access request is pending approval. We'll send you an e-mail alert to inform you of the status")


        


if authentication_status:
    
    #options=st.sidebar.radio("Options", ('HTML Form','Show Database','Add Entry', 'Update an Existing Entry',  'Delete an Entry'))#, key='current_option')
    for user in users:
        if user["username"] == st.session_state['username'] and user["approved"] == "False":
            st.write(f"Welcome ",user["firstname"], " your access request is pending approval. We'll send you an e-mail alert to inform you of the status")
        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "True":
            admin_welcome_screen(), show_options()         
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