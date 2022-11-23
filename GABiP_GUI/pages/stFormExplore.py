from re import search
import streamlit as st
import pandas as pd
import numpy as np

#use local css file
@st.cache
def load_cleaned():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

@st.cache
def load_to_edit():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean _towrite.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

dfOriginal=load_cleaned()
dfToEdit = load_to_edit()


def css_file(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


#C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/style.css.txt
css_file("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/style/style.css")
st.header("Form Exploring")

options=st.sidebar.radio("Options", ('Show Database','Add Entry', 'Update an Existing Entry', 'Delete an Entry'))
if options == 'Show Database':
    st.write(dfToEdit)




st.write("HMTL injected form")
html_form=("""<form action="https://formsubmit.co/your@email.com" method="POST">
<input type="text" name="name"  placeholder="Your name" required>
<input type="email" name="email" placeholder = "Your email" required>
<textarea name="message" placeholder="Details of your problem"></textarea>
<button type="submit">Send</button>
</form> 
""")
st.markdown(html_form, unsafe_allow_html=True)

