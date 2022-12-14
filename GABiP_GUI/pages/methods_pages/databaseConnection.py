from deta import Deta
import os
from dotenv import load_dotenv

load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")

#load_dotenv(".env")
#deta_key=os.getenv("deta_key")
#deta_key='a0se6run_nNcePVbuF6evHfxEp5gWMm9sWjWRaVm9'

deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

#names=['Claire Campbell', 'Jonny Calder']
#usernames = ['Claire','Jonny']

def insert_user(email, username, firstname, surname, admin, approved, hashed_password):
    """adding user"""
    #defining the email as the key
    return db.put({"key":email, "username": username, "firstname": firstname, "surname":surname, "admin":admin, "approved": approved,"password": hashed_password })

#create_user("radical_apathy@outlook.com", "Claire","Campbell", "Radical-Apathy", "abc123", "True")

def get_users():
    members=db.fetch()
    return members.items

def get_user(username):
    return db.get(username)

print(get_users())

