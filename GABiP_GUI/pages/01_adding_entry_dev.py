from re import search
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_icon='amphibs.jpeg')



#-------------------------------DATABASE CONNECTION------------------------------------#









#------------------------------------METHODS--------------------------------------------#
#check for the most recent approved csv version


#add user's entries to csv 



@st.cache
def load_cleaned():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull
















#-----------------------------------MAIN PAGE--------------------------------------------#
st.header('Add Entry page')

with st.form("my_form"):
          st.write("Inside the form")
          order =st.text_input("Order","Order - e.g. Anura", key='Order')
          family =st.text_input("Family","Family - e.g. Allophrynidae", key='Family')
          genus =st.text_input("Genus", "Genus - e.g. Allophryne", key='Genus')
          species =st.text_input("Species","Species - e.g. Relicta", key='Species')
          submitted = st.form_submit_button("Submit")
          if submitted:
            st.write(order, family, genus, species)