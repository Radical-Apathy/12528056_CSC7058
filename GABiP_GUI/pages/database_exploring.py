import streamlit_authenticator as stauth
import streamlit as st
#import db_connection as db

from deta import Deta
import os
from dotenv import load_dotenv

#need to figure out folder hierarchy so db key can be stored in this .env file
# C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

#st.session_state
#names=['Claire Campbell', 'Jonny Calder']
#usernames = ['Claire','Jonny']

def insert_user(email, username, firstname, surname, admin, approved, hashed_password):
    """adding user"""
    #defining the email as the key
    return db.put({"key":email, "username": username, "firstname": firstname, "surname":surname, "admin":admin, "approved": approved,"password": hashed_password })

def get_all_users():
    res = db.fetch()
    #print(res.items) #using return here gives an address
    return res.items

def get_current_user(email):
    print (db.get(email))

if 'username' not in st.session_state:
    st.session_state['username'] = 'guest'

st.session_state   
users=get_all_users() #returns users as dictionary of key value pairs

#converting to list comprehension so it can be passed into the authenticator
#specifically converting values we want for the login part
email=[user["key"] for user in users]
username=[user["username"] for user in users]
firstname=[user["firstname"] for user in users]
surname = [user["surname"] for user in users]
hashed_passwords=[user ["password"] for user in users]
isApproved=[user["approved"]for user in users]
isAdmin=[user["admin"] for user in users]


  
authenticator = stauth.Authenticate(email, username, hashed_passwords,
    "change_database", "abcdef")

username, authentication_status, password = authenticator.login("Login", "main") #main here refers to position


if authentication_status == False:
      st.error("Username/password is not recognised")

if authentication_status == None:
      st.warning("Please enter username and password")

if authentication_status:
    for user in users:
        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "True":
            st.write(f"Welcome ",user["firstname"], " you have Admin status")          
        if user["username"] == st.session_state['username'] and user["approved"] == "True" and user["admin"] == "False":
            st.write(f"Welcome ",user["firstname"], " you're a trusted member")
        if user["username"] == st.session_state['username'] and user["approved"] == "False":
            st.write(f"Welcome ",user["firstname"], " your access request is pending approval. We'll send you an e-mail alert to inform you of the status")
    #else:
     #   st.write(f"Welcome: ", user["surname"])
      #  st.warning("Your access request is pending approval")
      #st.sidebar.title(f"Welcome {st.session_state['username']}") 
      #st.write(users)
      #st.write(isApproved[2])
      

#st.write("Testing getting all user info with email i.e. what's set as the key in the db")
#for user in users:
 #   if user["username"] == st.session_state['username']:
  #      st.write(f"Welcome: ", user["firstname"])

#st.write("Checking only printing firstname is user is approved")
#for user in users:
 #   if user["username"] == st.session_state['username'] and user["approved"] == "True":
  #      st.write(f"Welcome: ", user["firstname"])
   # else:
    #    st.write(f"Welcome: ", user["surname"],)











#st.write(users)

authenticator.logout("Logout", "main")