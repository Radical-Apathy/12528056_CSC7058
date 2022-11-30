import streamlit as st 
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder



# Functions

@st.cache
def data_upload():
    df =pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean _towrite.csv', encoding= 'unicode_escape', low_memory=False)
    return df


def css_file(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#st.session_state
if 'Order' not in st.session_state:
    st.session_state['Order'] = "Order"
if 'Family' not in st.session_state:
    st.session_state['Family'] = "Family"
if 'Genus' not in st.session_state:
    st.session_state['Genus'] = "Genus"

css_file("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/style/style.css")
st.header("Style Exploring")

#st.header("This is Streamlit Default Dataframe")
dfToEdit = data_upload()
# st.dataframe(data=df)
# st.info(len(df))


st.success("This is a streamlit success message i.e. st.success ('Text')")
st.write("HTML injected form")

html_form=("""<form action="google.com" method="POST">
    <h3 id = "header"><strong>Order<strong></h3>
    <input type="text" name="name"  placeholder="Order - e.g. Anura" required>
   <h3 id = "header"><strong>Family<strong></h3>
    <input type="text" name="name"  placeholder="Family - e.g. Allophrynidae" required>
    <h3 id = "header"><strong>Genus<strong></h3>
    <input type="text" name="name"  placeholder="Genus - e.g. Allophryne" required>
    <h3 id = "header"><strong>Species<strong></h3>
    <input type="text" name="name"  placeholder="Species - e.g. Relicta" required>
    <button type="submit">Send</button>
    </form> 
    """)
st.markdown(html_form, unsafe_allow_html=True)


st.write("Streamlit  modal")

with st.form("my_form"):
   st.write("Inside the form")
   order =st.text_input("Order", key='Order')
   family =st.text_input("Family", key='Family')
   genus =st.text_input("Genus", key='Genus')
 

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       st.write(order, family, genus)