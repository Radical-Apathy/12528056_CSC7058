from re import search
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridUpdateMode #gridupdate mode remebers edited entries
from st_aggrid.grid_options_builder import GridOptionsBuilder

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

gd = GridOptionsBuilder.from_dataframe(dfToEdit)
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=True, groupable=True)
sel_mode=st.radio('Selection Type', options=['Edit a Single Entry', 'Edit Multiple Entries'])

gd.configure_selection( selection_mode=sel_mode, use_checkbox=True)
gridStyle=gd.build()
#styling dataframe using AG grid

if 'current_option' not in st.session_state:
    st.session_state['current_option'] = 'Show Database'

def css_file(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.session_state


css_file("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/style/style.css")
st.header("Form Exploring")
st.write("Not using AG grid", dfToEdit.head())

options=st.sidebar.radio("Options", ('Show Database','Add Entry', 'Update an Existing Entry', 'Delete an Entry'), key='current_option')
if options == 'Show Database':
    st.write("Using AG grid, without gridoptionbuilder styling")
    AgGrid(dfToEdit.head())
if options == 'Add Entry':
    st.header("Edit the Database")
    st.write("Database head, displayed using AgGrid with gridoptionbuilder styling, checkboxes for editing")

    edit_table=AgGrid(dfToEdit.head(), gridOptions=gridStyle,) #theme='fresh')
    #gridOptions = gb.build()

#st.dataframe(data=dfToEdit)











#C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/style.css.txt
#gb = GridOptionsBuilder.from_dataframe(dfToEdit)
#gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
#gb.configure_side_bar() #Add a sidebar
#gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
#gridOptions = gb.build()
#grid_response = AgGrid(
#    dfToEdit,
#    gridOptions=gridOptions,
#    data_return_mode='AS_INPUT', 
#    update_mode='MODEL_CHANGED', 
#    fit_columns_on_grid_load=False,
    #theme='blue', #Add theme color to the table
#    enable_enterprise_modules=True,
#    height=350, 
#    width='100%',
#    reload_data=True
#)


#dfToEdit = grid_response['dfToEdit']
#selected = grid_response['selected_rows'] 
#dfToEdit = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df








#st.write("HMTL injected form")
#html_form=("""<form action="https://formsubmit.co/your@email.com" method="POST">
#<input type="text" name="name"  placeholder="Your name" required>
#<input type="email" name="email" placeholder = "Your email" required>
#<textarea name="message" placeholder="Details of your problem"></textarea>
#<button type="submit">Send</button>
#</form> 
#""")
#st.markdown(html_form, unsafe_allow_html=True)

