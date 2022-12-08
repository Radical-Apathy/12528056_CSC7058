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

#get_user returns none for some reason
#relies on the key being passed instead of username, that's why...
def get_current_user(email):
    print (db.get(email))

def update_user(email, updates):
    return db.update(updates, email)


def delete_user(email):
    return db.delete(email)


#get_all_users()
#get_user("ccampbell")

#update_user("email@email2.com", updates={"username":"ccampbellUpdated"})

#delete_user("email@email2.com")


#get_current_user('admin@email.com')

#get_current_user('admin@email.com')
