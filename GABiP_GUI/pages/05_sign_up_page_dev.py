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
         
#---------------------------------------Sign up form.............................................#

signup_title_style = '<p style="font-family:sans-serif; color:Green; font-size: 42px;"><strong>Sign Up</strong></p>'

st.markdown(signup_title_style, unsafe_allow_html=True) 
st.title(":lock: :lizard: :unlock:")
st.write(users)
st.write("Trying with a standard form")
with st.form("my_form"):
      email =st.text_input("Email", "Enter your email address")
      duplication_alert(email)
      firstname =st.text_input("Firstname", "Enter your forename")#, key='Order')
      surname =st.text_input("Surname", "Enter your surname")#, key='Order')
      username= st.text_input("Username", "Enter a username")
      duplication_alert(username)
      usernameCaption=st.caption("Please enter a unique username...this will be used to login")
      password =st.text_input("password", type='password')#key='Family')
      confirmPassword =st.text_input("Re-type Password",  type='password')# key='Genus')
      #need to check if user exists  
      submitted = st.form_submit_button("Submit Request")

      admin="False"
      approved="True"
      passwordArry=[password]
      hashed_password= stauth.Hasher(passwordArry).generate()

      if submitted and final_warning(email) :
        st.error("email address already in use")
      if submitted and final_warning(username) :
        st.error("username address already in use")
      if submitted and password != confirmPassword:
          st.write("passwords do not match")
          #send an email alert to new users informing them that an dmin will be in touch
          #send an email alert to admin with the new users details i.e. first name, last name, email, message 
      if submitted:
            # look at db insertion 
          insert_user(email, username, firstname, surname, admin, approved, hashed_password)
          st.write("we've submitted your request...an admin will be in touch soon via email")
          #def insert_user(email, username, firstname, surname, admin, approved, hashed_password):

         
