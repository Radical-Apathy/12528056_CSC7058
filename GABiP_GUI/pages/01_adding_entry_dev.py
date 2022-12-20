from re import search
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_icon='amphibs.jpeg')

#def css_file(file_name):
 #   with open(file_name) as f:
  #      st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#css_file("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/style/style.css")
#@st.cache
#def load_original():
#    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/GABiP_July.csv', encoding= 'unicode_escape', low_memory=False)
#    return dfFull

@st.cache
def load_cleaned():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull