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

#--------------------------------UI display methods------------------------------------------#
def welcome_screen():
    st.image("amphibs.jpeg", width=200)

def view_approved_users():
    st.write("This is a blank page")






#-----------------------------------------st title-------------------------------------------#
#"<p style="font-family:sans-serif; color:Red; font-size: 400px;"><strong><center>Admin Control</center></strong></p>"""
st.header("**************************:lock:Admin Section:lock_with_ink_pen:**************************")
st.subheader("Welcome to the Admin Area.")

adminOptions= st.selectbox("Options", ['Click here to see Admin options','View pending users', 'View approved users','See pending changes'  ])
if adminOptions=="Click here to see Admin options":
    welcome_screen()
if adminOptions=="View pending users":
    view_approved_users()

st.markdown("***")
     
