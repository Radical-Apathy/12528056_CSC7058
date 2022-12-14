import streamlit as st
import pandas as pd
from methods_main import hello

st.header("Welcome Page")

hello.streamlit_hello()
#st.sidebar.header("Sections")
#st.sidebar.image('amphibs.jpeg', width=500)

uploaded_file= st.file_uploader("Upload a file")
#dataframe=pd.read_csv(uploaded_file)
#st.write(dataframe.head(10))

#if uploaded_file is not None:
 #   dataFrame=pd.read_csv(uploaded_file)
#return dataFrame
