from deta import Deta
import os
from dotenv import load_dotenv

#need to figure out folder hierarchy so db key can be stored in this .env file
load_dotenv(".env")
#deta_key=os.getenv("deta_key")
deta_key='a0se6run_nNcePVbuF6evHfxEp5gWMm9sWjWRaVm9'

#initialising a deta object
deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

#names=['Claire Campbell', 'Jonny Calder']
#usernames = ['Claire','Jonny']

def insert_user(email, username, firstname, surname, admin, approved, hashed_password):
    """adding user"""
    #defining the email as the key
    return db.put({"key":email, "username": username, "firstname": firstname, "surname":surname, "admin":admin, "approved": approved,"password": hashed_password })

def get_all_users():
    res = db.fetch()
    print(res.items) #using return here gives an address

#get_all_users()
#print(get_users("j_calder"))

#testing insert_user method
#insert_user("email@email2.com", "ccampbell", "claire", "campbell2", "True", "True", "password01")

#get_user returns none for some reason
#relies on the key being passed instead of username...
def get_user(email):
    print (db.get(email))

def update_user(email, updates):
    return db.update(updates, email)


def delete_user(email):
    return db.delete(email)


#get_user("ccampbell")

#update_user("email@email2.com", updates={"username":"ccampbellUpdated"})

delete_user("email@email2.com")