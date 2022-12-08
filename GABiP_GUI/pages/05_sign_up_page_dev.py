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


#---------------------------------------Sign up form.............................................#

signup_title_style = '<p style="font-family:sans-serif; color:Green; font-size: 42px;"><strong>Sign Up</strong></p>'

st.markdown(signup_title_style, unsafe_allow_html=True) 
st.title(":lizard: :frog:")

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
