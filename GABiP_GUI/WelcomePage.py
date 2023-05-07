import streamlit as st
import pandas as pd
from PIL import Image

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://www.amphibianbiodiversity.org/uploads/9/8/6/8/98687650/background-images/1356094370.png");
             background-attachment: fixed;
             background-size: cover
             background-position: bottom 50px right;
             
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 
welcol1,welcol2,welcol3 = st.columns(3)
welcol3.header("Welcome Page")
welcol3.markdown("**Future welcome note to go here and explain the purpose of this app and what the GABiP is**")

