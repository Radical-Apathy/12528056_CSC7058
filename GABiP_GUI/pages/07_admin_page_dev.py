import streamlit_authenticator as stauth
import streamlit as st
#import db_connection as db
import smtplib
import ssl
from email.mime.text import MIMEText # to enable html stuff with https://realpython.com/python-send-email/#sending-your-plain-text-email
from email.mime.multipart import MIMEMultipart
from deta import Deta
import os
from dotenv import load_dotenv

#-----------------database connection and method to insert a user-----------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)

db=deta_connection.Base("users_db")


#-----------------------------------------st title-------------------------------------------#
#st.markdown(f"""<p style="font-family:sans-serif; color:Green; font-size: 20px;"><strong>{user["username"]}</strong></p>""" , unsafe_allow_html=True)
#st.markdown(f"""<p style="font-family:sans-serif; color:Red; font-size: 400px;"><strong><center>Admin Control</center></strong></p>""" , unsafe_allow_html=True)
st.title(":lock:Admin:lock_with_ink_pen:")

st.write("expander example")

st.selectbox("Admin Options", ('View pending users', 'See pending changes', 'View approved users' ))

st.markdown("***")

with st.expander(" Expander 1 no column Username2 Here"):
    st.write("""
        The chart above shows some numbers I picked for you.
        I rolled actual dice for these, so they're *guaranteed* to
        be random.
    """)
    st.checkbox("Approve expander 1 no column")

with st.expander(" Expander 2 no column Username2 Here"):
    st.write("""
        The chart above shows some numbers I picked for you.
        I rolled actual dice for these, so they're *guaranteed* to
        be random.
    """)
    st.checkbox("Approve expander 2 no column")

st.write("Form example in columns")



card_template = """
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                    <div class="card bg-light mb-3" >
                        <H5 class="card-header">.  <a href={} style="display: inline-block" target="_blank">{}</h5>
                            <div class="card-body">
                                <span class="card-text"><b>Author(s): </b>{}</span><br/>
                                <span class="card-text"><b>Year: </b>{}</span><br/>
                                <span class="card-text"><b>Journal: </b>{}</span><br/>
                                <span class="card-text"><b>DOI: </b>{}</span><br/>
                                <span class="card-text"><b>Score: </b>{}</span><br/><br/>
                                <p class="card-text">{}</p>
                            </div>
                        </div>
                    </div>
        """
st.write("Bootstrap Card")

#st.markdown(card_template, unsafe_allow_html=True)        
