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
             background-position: top 50px right;
             
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 
st.header("Welcome Page")
#st.sidebar.header("Sections")
#st.sidebar.image('amphibs.jpeg', width=500)

uploaded_file= st.file_uploader("Upload a file")
#dataframe=pd.read_csv(uploaded_file)
#st.write(dataframe.head(10))

#if uploaded_file is not None:
 #   dataFrame=pd.read_csv(uploaded_file)
#return dataFrame
