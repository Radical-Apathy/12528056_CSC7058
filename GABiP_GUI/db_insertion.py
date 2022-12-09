import streamlit_authenticator as stauth

import db_connection as db

"""
email=['radical_apathy@outlook.com','j_calder@outlook.com']
firstname=['radical_apathy', 'j_calder']
surname= ['Campbell', 'Calder']
username = ['Claire','Jonny']
password=['abc123', 'def456']
admin= ['True', 'False']
hashed_password= stauth.Hasher(password).generate()
"""
email='dbqueryexploring@email.com'
firstname='firstname'
surname= 'surname'
username = 'dbusername'
password='password'
approved='True'
admin= 'False'
hashed_password= stauth.Hasher(password).generate()

#for (email, firstname, surname, username, hashed_password, admin) in zip(email, firstname, surname, username, password, admin):

#db.create_user(email, username, firstname, surname, admin, approved, password)