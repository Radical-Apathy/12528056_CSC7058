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
email=['dbquery@email.com']
firstname=['firstname']
surname= ['surname']
username = ['dbusername3']
password=['password']
approved=['False']
admin= ['False']
hashed_password= stauth.Hasher(password).generate()

for (email, username, firstname, surname, admin, approved, hashed_password) in zip(email, username, firstname, surname, admin, approved, hashed_password):
 db.insert_user(email, username, firstname, surname, admin, approved, hashed_password)
#db.create_user(email, username, firstname, surname, admin, approved, password)