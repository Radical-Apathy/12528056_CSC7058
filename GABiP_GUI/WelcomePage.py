import streamlit as st
import pandas as pd

st.header("Welcome Page")
#st.sidebar.header("Sections")
#st.sidebar.image('amphibs.jpeg', width=500)

uploaded_file= st.file_uploader("Upload a file")
#dataframe=pd.read_csv(uploaded_file)
#st.write(dataframe.head(10))

#if uploaded_file is not None:
 #   dataFrame=pd.read_csv(uploaded_file)
#return dataFrame
