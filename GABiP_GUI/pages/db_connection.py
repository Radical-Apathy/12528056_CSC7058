from deta import Deta
import os
from dotenv import load_dotenv


load_dotenv(".env")
#deta_key=os.getenv("deta_key")
deta_key='a0se6run_nNcePVbuF6evHfxEp5gWMm9sWjWRaVm9'

deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

#names=['Claire Campbell', 'Jonny Calder']
#usernames = ['Claire','Jonny']

def create_user(email,firstname, surname,username, password, admin):
    """adding user"""
    return db.put({"Key": email, "firstname":firstname, "surname":surname, "username": username, "password": password, "admin":admin })

create_user("radical_apathy@outlook.com", "Claire","Campbell2", "Radical-Apathy", "abc123", "True")

def get_users():
    members=db.fetch()
    return members.items

def get_user(username):
    return db.get(username)

#print(get_users("j_calder"))

