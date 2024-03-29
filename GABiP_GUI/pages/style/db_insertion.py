

import streamlit_authenticator as stauth

import db_connection as db

def add_user_bracket(email, username, firstname, surname, admin, approved, hashed_password):
    """adding user"""
    #defining the email as the key
    return db.put({"key":[email], "username": [username], "firstname": [firstname], "surname":[surname], "admin":[admin], "approved": [approved],"password": [hashed_password] })



#------------------------------------------------------------------------------#
import json

email='strpassaddbrack@email.com'
username='strpassaddbrack'
firstname = 'replacedstr4brack'
surname= 'hashed'
password='1234'
bracketPass=[password]
admin= 'True'
approved='True'
hashed_password= stauth.Hasher(bracketPass).generate()
#str_hashed_password = json.dumps(hashed_password)
strPass=str(hashed_password)
removeopenbrack=strPass.replace("[", "")
removeclosebrack=removeopenbrack.replace("]", "")
final=removeclosebrack.replace("'","")
#print((str_hashed_email))
#for (email, username, firstname, surname, admin, approved, hashed_password) in zip(email, username, firstname, surname, admin, approved, zip_hashed_array):

#db.insert_user(email, username, firstname, surname, admin, approved, hashed_password[0])
db.insert_user(email, username, firstname, surname, admin, approved, final)


#------------------------------------------------------------------------------#
"""
email='adduserpassword@email.com'
username='addusermethod'
firstname = 'zipbracket'
surname= 'hashed'
password='password'
admin= 'True'
approved='True'
hashed_password= stauth.Hasher(password).generate()
arrhashed_password=[hashed_password]

zipped= zip(arrhashed_password)

#print(zipped)
"""
"""
def add_user_password(email, username, firstname, surname, admin, approved, hashed_password):
    return db.insert(email, username, firstname, surname, admin, approved, hashed_password)
    """
#for (email, username, firstname, surname, admin, approved, hashed_password  ) in zip(email, username, firstname, surname, admin, approved, hashed_password):
  #db.insert_user(email, username, firstname, surname, admin, approved, hashed_password)






#-----------------------------correctly stores hashed password in db------------------------------------------#
"""
userInput=""
email=['brackethashed@email.com']
username=['brackethashed']
firstname = ['hashed']
surname= ['hashed']
password=['password']
admin= ['True']
approved=['True']
hashed_password= stauth.Hasher(password).generate()


#for (email, username, firstname, surname, admin, approved, hashed_password  ) in zip(email, username, firstname, surname, admin, approved, hashed_password):
 
 #db.insert_user(email, username, firstname, surname, admin, approved, hashed_password)
"""
#-----------------------------------------------------#
"""
#db.insert_user("["+email+"]", "["+username+"]", "["+firstname+"]", "["+surname+"]", "["+admin+"]", "["+approved+"]", "["+hashed_password+"]")
email='jsonhashed@email.com'
username='jsonhashed'
firstname = 'zipbracket'
surname= 'hashed'
password='password'
admin= 'True'
approved='True'
hashed_password= stauth.Hasher(password).generate()
import json
jsonhashed=json.dumps([dict(zip(hashed_password))])

#db.insert_user(email, username, firstname, surname, admin, approved, jsonhashed)
"""
#---------------------------------------------------#
"""
bemail="["+email+"]"
busername="["+username+"]"
bfirstname = "["+firstname+"]"
bsurname= "["+surname+"]"
bpassword="["+password+"]"
badmin= "["+admin+"]"
bapproved= "["+approved+"]"
bhashed_password= stauth.Hasher(password).generate()
bzipHashedPassword=zip(password,hashed_password)
"""
#import json

#print(hashed_password)

#zippedjson=json.dumps(zipHashedPassword)

#print(zippedjson)

#print(hashed_password)
#print(zipHashedPassword)
#for (bemail, busername, bfirstname, bsurname, badmin, bapproved, bhashed_password) in zip(bemail, busername, bfirstname, bsurname, badmin, bapproved, bhashed_password):
 
 #   db.insert_user(bemail, busername, bfirstname, bsurname, badmin, bapproved, bhashed_password)
#---------------------------Separates out string into indivdual letters---------------------------------------------------------------------------------#
"""
email='nobrackethashed@email.com'
username='nobrackethashed'
firstname = 'hashed'
surname= 'hashed'
password='password'
admin= 'True'
approved='True'
hashed_password= stauth.Hasher(password).generate()


#db.insert_user(email, username, firstname, surname, admin, approved, hashed_password)
"""

"""
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
"""
email1=['hashedpassword@email.com']
firstname1=['firstname']
surname1= ['surname']
username1 = ['dbusername']
password1=['password']
approved1=['True']
admin1= ['False']
hashed_password1= stauth.Hasher(password1).generate()

#for (email, username, firstname, surname, admin, approved, hashed_password  ) in zip(email1, username1, firstname1, surname1, admin1, approved1, hashed_password1):
db.insert_user(email1, username1, firstname1, surname1, admin1, approved1, hashed_password1)
"""
