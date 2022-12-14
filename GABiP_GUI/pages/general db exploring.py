from deta import Deta
import os
from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
#-----------------database connection and method to insert a user-----------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")

#connecting to bootstrap
st.markdown("""
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

        """,unsafe_allow_html=True)

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


#st.write("using check_email with break")

def check_email(emailSignup):
    for user in users:
        if user["key"] == emailSignup:
         st.write("email in use")    
         break
    else:
        st.write("email available")
    

#check_email("admin2@email.com")


#st.write("trying an all duplication check with pass")

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
    
#st.write(f"Welcome ",user["firstname"], " you have Admin status") 
def find_pending_users():
   waiting=[]
   for user in users:
    if user["approved"]=="False":
      waiting.append(user)
    
   return waiting

#duplication_check("admin")
def display_pending_users(users=[], *args):
    for user in users:
        st.write(user["firstname"])

#updating user details
def approve_user(username, updates):
    return db.update(updates, username)


def find_and_display_expander():
    for user in users:
     if user["approved"]=="False":
        with st.expander(user["username"]):
            st.write(user['firstname'],user["key"])
            approve=st.checkbox(user["username"])
            submit=st.button(user["username"])
        if approve and submit:
                approve_user(user["key"], updates={"approved": "True"})
                st.success(f"Now accepted " + user["username"])




#<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">


def card_template(username, userfirstname):
    return f"""
    
    <div class="card" style="width: 18rem;">
  <div class="card-body">
    <h5 class="card-title">{username}</h5>
    <h6 class="card-subtitle mb-2 text-muted"{userfirstname}</h6>
    <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
    <a href="#" class="card-link">Card link</a>
    <a href="#" class="card-link">Another link</a>
  </div>
</div>
 
    
    
    """

def webcard(username):
    return f"""
    
     
        <div class='card' style= 'width: 18rem;>
            <h3 class='card-title'>{username}</h3>
            <img src='$art' height: auto class='card-img-top' alt='...'>
            <div class='card-body'>
               
                 <a href = 'displaycard.php?showcard=$iddata' class='btn btn-primary'>$iddata</a>
                                 
            </div>
        </div>
        
    
    
    """

def find_and_display_with_card():
    for user in users:
     if user["approved"]=="False":
        st.markdown(webcard(user["username"]), unsafe_allow_html=True)
        checkbox=st.checkbox(f"Approve " + user["username"])
        button=st.button(f"Update " + user["username"]+ "'s permissions")
        if checkbox and button:

            approve_user(user["key"], updates={"approved": "True"})
            st.success(f"Updated!"+user["username"]+ "can now access the GABiP. You can revoke access at any time using the View current user's section")


header="""<div class = "container buffer">
    <div class='row align-items-centre'>"""
footer="""</div>"""

def display_in_cols():
    st.markdown(header, unsafe_allow_html=True)
    for user in users:
     if user["approved"]=="False":
        st.markdown(webcard(user["username"]), unsafe_allow_html=True)

def find_and_display_form():
    for user in users:
     if user["approved"]=="False":
       with st.form(user["username"]):
        st.text(f"Username : " +user["username"])
        st.text(f"Firstname : " +user["firstname"])
        st.text(f"Surname : " +user["surname"])
        st.text(f"Email : " +user["key"])
        checkbox = st.checkbox(f"Allow " + user["firstname"] + "access")
        confirmForm = st.form_submit_button(f"Confirm access permission for : " + user["username"])
        if checkbox and confirmForm:
            approve_user(user["key"], updates={"approved": "True"})
            st.write(f"Updated!"+user["username"]+ "can now access the GABiP. You can revoke access at any time using the View current user's section")



name_colour ="""<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>{user["username"]}</strong></p>""" 


#-----------------------current favoured method------------------------------------------------------------------------#
def find_and_display_form_2checks():
    for user in users:
     if user["approved"]=="False":
       with st.form(user["username"]):
        st.markdown(f"""<p style="font-family:sans-serif; color:ForestGreen; font-size: 20px;"><strong>***********{user["username"]}'s Request**********</strong></p>""" , unsafe_allow_html=True)
        st.text(f"Username : " +user["username"])
        st.text(f"Firstname : " +user["firstname"])
        st.text(f"Surname : " +user["surname"])
        st.text(f"Email : " +user["key"])
        checkbox1 = st.checkbox(f"Allow " + user["firstname"] + " access")
        checkbox2 = st.checkbox(f"Place " +user["firstname"] +" in review list")
        confirmForm = st.form_submit_button(f"Submit Decision for  : " + user["username"])
        if checkbox1 and checkbox2 and confirmForm:
            st.error("Warning! Both options have been selected. Please review decision")
        elif checkbox1 and confirmForm:
            approve_user(user["key"], updates={"approved": "True"})
            st.success(f"Accepted! "+user["username"]+ " can now access the GABiP. You can revoke access at any time using the View Approved user's option")
        elif checkbox2 and confirmForm:
            st.warning(f"User now place in to review section. " +user["username"]+ " 's access can be decided upon another date" )
        #st.write(("*****************************************************************************"))
        st.markdown("""<p style="font-family:sans-serif; color:ForestGreen; font-size: 20px;"><strong>**************************************************************************************</strong></p>""", unsafe_allow_html=True )
        st.write("***")
    

    



#------------------------------form method with colour...................................................................#




#find_and_display_with_card()
#st.write("Card display")
#st.write(find_pending_users())
find_and_display_form_2checks()
#find_and_display_expander()
#st.write(display_pending_users(find_pending_users))

#with st.expander(" Expander 1 no column Username2 Here"):
 #   st.write("""
  #      The chart above shows some numbers I picked for you.
   #     I rolled actual dice for these, so they're *guaranteed* to
    #    be random.
    #""")
    #st.checkbox("Approve expander 1 no column")








def final_warning(userInput):
    for user in users:
        if user["key"]   == userInput:
         return True
        if user["username"] == userInput:
         return True
             
