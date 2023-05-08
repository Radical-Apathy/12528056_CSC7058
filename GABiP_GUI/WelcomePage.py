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
welcol3.markdown(f'<p style="font-family:sans-serif; color:white; font-size: 30px;"><strong>Welcome!</strong></p>', unsafe_allow_html=True)
welcol3.markdown("**The Global Amphibian Biodiversity Project (GABiP) is an international scientific initiative aimed to advance knowledge on the diversity, distribution and declines of the world's amphibians.**")
welcol3.markdown("**This app allows the exploration of our amphibian dataset that contains over 8000 species! Got information? Wish to make changes? Use our Access Request page to sign up as a user. Happy exploring, amphibifans!**")

