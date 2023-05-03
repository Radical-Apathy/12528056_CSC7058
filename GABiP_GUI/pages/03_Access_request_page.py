import streamlit_authenticator as stauth
import streamlit as st
import smtplib
import ssl
from email.mime.text import MIMEText # to enable html stuff with https://realpython.com/python-send-email/#sending-your-plain-text-email
from email.mime.multipart import MIMEMultipart
from deta import Deta
import os
from dotenv import load_dotenv

#-----------------database connection and method to insert a user-----------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

def insert_user(email, username, firstname, surname, admin, approved, hashed_password):
    """adding user"""
    #defining the email as the key
    return db.put({"key":email, "username": username, "firstname": firstname, "surname":surname, "admin":admin, "approved": approved,"password": hashed_password })

def get_all_users():
    res = db.fetch()
    #print(res.items) #using return here gives an address
    return res.items

#-----------------------converting to list comprehension so it can be passed into the authenticator-----------------------#
#specifically converting values we want for the login part
users=get_all_users()
email=[user["key"] for user in users]
username=[user["username"] for user in users]
firstname=[user["firstname"] for user in users]
surname = [user["surname"] for user in users]
hashed_passwords=[user ["password"] for user in users]
isApproved=[user["approved"]for user in users]
isAdmin=[user["admin"] for user in users]


#method to check that email and username are unique
def duplication_alert(usertext):
    for user in users:
        if user["key"] == usertext:
         st.warning("email already in use...please choose an alternative or await verification email")    
         pass
    
        #st.write("email available")
        if user["username"] ==usertext:
         st.warning("username in use, please choose another")
         pass
        #st.write("username available")

#final alert to user of duplicate username and or email to prevent insertion into the database
def final_warning(userInput):
    for user in users:
        if user["key"]   == userInput:
         return True
        if user["username"] == userInput:
         return True

#method for checking if fields have been left blank

def validate_input(email, firstname, surname, username, password, confirmPassword):
    errors = []
    if not email:
        errors.append("Email address is required")
    if not firstname:
        errors.append("First name is required")
    if not surname:
        errors.append("Surname is required")
    if not username:
        errors.append("Username is required")
    if not password:
        errors.append("Password is required")
    if password != confirmPassword:
        errors.append("Passwords do not match")
    return errors
         
#---------------------------------------------------------------------------------------------SIGN UP PAGE UI----------------------------------------------------------------#

def background():
        st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/248177756.jpg");
                        background-attachment: fixed;
                        background-size: cover;
                        background-position: 50% center;
                        opacity: 0.1
                        color: #ffffff; 
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

background()
    



headercol1, headercol2, headercol3=st.columns(3)

headercol2.markdown('<p style="font-family:sans-serif; color:White; font-size: 30px;"><em><strong>Request Edit Permission</strong></em></p>', unsafe_allow_html=True)


with st.form("my_form"):
      email =st.text_input("Email", "Enter your email address")
      duplication_alert(email)
      firstname =st.text_input("Firstname", "Enter your forename")
      surname =st.text_input("Surname", "Enter your surname")
      username= st.text_input("Username", "Enter a username")
      duplication_alert(username)
      usernameCaption=st.caption("Please enter a unique username...this will be used to login")
      password =st.text_input("password", type='password')
      confirmPassword =st.text_input("Re-type Password",  type='password')

      #need to check if user exists  
      submitted = st.form_submit_button("Submit Request")

      admin="False"
      approved="False"
      bracketPass=[password]
      hashed_password= stauth.Hasher(bracketPass).generate()
      strPass=str(hashed_password)
      removeopenbrack=strPass.replace("[", "")
      removeclosebrack=removeopenbrack.replace("]", "")
      finalPass=removeclosebrack.replace("'","")

      if submitted and final_warning(email) :
        st.error("email address already in use")
      if submitted and final_warning(username) :
        st.error("username address already in use")
      if submitted and password != confirmPassword:
          st.write("passwords do not match")
      if submitted and password =="":# or confirmPassword=="":
        st.warning("Fields can not be left blank") 
      errors = validate_input(email, firstname, surname, username, password, confirmPassword)
      if errors:
          st.error("\n".join(errors))
      elif submitted and len(password)>0 and len(confirmPassword)>0: 
        insert_user(email,username, firstname, surname, admin, approved, finalPass)
        st.markdown('<p style="font-family:sans-serif; color:White; font-size: 30px;"><em><strong>Request submitted!</strong></em></p>', unsafe_allow_html=True)


         
