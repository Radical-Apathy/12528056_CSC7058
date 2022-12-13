from deta import Deta
import os
from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
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



users=get_all_users()
email=[user["key"] for user in users]
username=[user["username"] for user in users]
firstname=[user["firstname"] for user in users]
surname = [user["surname"] for user in users]
hashed_passwords=[user ["password"] for user in users]
isApproved=[user["approved"]for user in users]
isAdmin=[user["admin"] for user in users]

def if_in_method_email(usertext):
    for user in users:
        if usertext in user["key"]:
            st.write("email already exists with this email")
        #else:
         #   st.write("email address available")
        
st.title("db exploring")


st.write("using check_email with break")

def check_email(emailSignup):
    for user in users:
        if user["key"] == emailSignup:
         st.write("email in use")    
         break
    else:
        st.write("email available")
    

#check_email("admin2@email.com")


st.write("trying an all duplication check with pass")

def duplication_check(usertext):
    for user in users:
        if user["key"] == usertext:
         st.write("email in use")    
         pass
    
        #st.write("email available")
        if user["username"] ==usertext:
         st.write("username in use")
         pass
        #st.write("username available")
    

#duplication_check("admin")

st.write("Trying a email check with return statement")

def final_warning(userInput):
    for user in users:
        if user["key"]   == userInput:
         return True
        if user["username"] == userInput:
         return True
         
    

#if final_warning("admin@email2.com"):
 #   st.write("Email or username already in use, please correct before submitting")
#else:
 #   st.write("Good to go!")

email1=['hashedpassword@email.com']
firstname1=['firstname']
surname1= ['surname']
username1 = ['dbusername']
password1=['password']
approved1=['True']
admin1= ['False']
hashed_password1= stauth.Hasher(password1).generate()

st.write("password hashing stuff")
#insert_user(email, username, firstname, surname, admin, approved, password)
#for (email, username, firstname, surname, admin, approved, hashed_password  ) in zip(email, username, firstname, surname, admin, approved, hashed_password):
#insert_user(email1, username1, firstname1, surname1, admin1, approved1, hashed_password1)

st.write("member inserted")