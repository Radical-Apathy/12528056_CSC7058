import streamlit as st 
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

# Functions

@st.cache
def data_upload():
    df =pd.read_csv('C:/Users/Littl/OneDrive/Desktop/dataset_clean _towrite.csv', encoding= 'unicode_escape', low_memory=False)
    return df

#st.header("This is Streamlit Default Dataframe")
df = data_upload()
# st.dataframe(data=df)
# st.info(len(df))

_funct = st.sidebar.radio(label="Functions", options = ['Display','Highlight','Delete'])

st.header("This is AgGrid Table")

gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=True,groupable=True)
# _______________________________________________________________
# Enabling tooltip - YouTube-Query by Alexis-Raja Brachet  
# gd.configure_default_column(editable=True,groupable=True,tooltipField = "variant") 
# hover in any rows( under any columns), the variant of that row, will pop up as tootltip information.However, 
# I'm yet to figure out, how to implement more than one column information (what I mean - let's say - ["variant", "date"] collectively as tooltip information) , 
# also, it's bit slow in the begginig  when I tested. 
# ________________________________________________________________

if _funct == 'Display':
    sel_mode = st.radio('Selection Type', options = ['single', 'multiple'])
    gd.configure_selection(selection_mode=sel_mode,use_checkbox=True)
    gridoptions = gd.build()
    grid_table = AgGrid(df,gridOptions=gridoptions,
                        update_mode= GridUpdateMode.SELECTION_CHANGED,
                        height = 500,
                        allow_unsafe_jscode=True,
                        #enable_enterprise_modules = True,
                        theme = 'fresh')

    sel_row = grid_table["selected_rows"]
    st.subheader("Output")
    st.write(sel_row)
if _funct == 'Highlight':
    col_opt = st.selectbox(label ='Select column',options = df.columns)
    cellstyle_jscode = JsCode("""
        function(params){
            if (params.value == 'Allophrynidae') {
                return {
                    'color': 'black',
                    'backgroundColor' : 'orange'
            }
            }
            if (params.value == 'B.1.258') {
                return{
                    'color'  : 'black',
                    'backgroundColor' : 'red'
                }
            }
            else{
                return{
                    'color': 'black',
                    'backgroundColor': 'lightpink'
                }
            }
       
    };
    """)
    gd.configure_columns(col_opt, cellStyle=cellstyle_jscode)
    gridOptions = gd.build()
    grid_table = AgGrid(df, 
            gridOptions = gridOptions, 
            enable_enterprise_modules = True,
            fit_columns_on_grid_load = True,
            height=500,
            width='100%',
            #theme = "material",
            update_mode = GridUpdateMode.SELECTION_CHANGED,
            reload_data = True,
            allow_unsafe_jscode=True,
            )
