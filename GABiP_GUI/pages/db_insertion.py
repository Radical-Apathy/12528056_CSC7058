
"""
import streamlit_authenticator as stauth

import db_connection as db

email=['admin@email.com','notadmin@email.com','notapproved@email.com']
username=['admin', 'notadmin', 'notapproved']
firstname = ['Claire','Jonny', 'Request']
surname= ['Campbell', 'Calder', 'Request']
password=['password', 'password', 'password']
admin= ['True', 'False', 'False']
approved=['True','True','False']
hashed_password= stauth.Hasher(password).generate()

#zip here creating a tupple of the variables above
#for (email, username, firstname, surname, admin, approved, hashed_password  ) in zip(email, username, firstname, surname, admin, approved, hashed_password):
 #  db.insert_user(email, username, firstname, surname, admin, approved, hashed_password)

#print(db.get_all_users())
"""