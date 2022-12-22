from deta import Deta
import os
from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from csv_diff import load_csv, compare
#-----------------database connection and method to insert a user-----------------------------#
load_dotenv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058\GABiP_GUI/.env.txt")
deta_key=os.getenv("deta_key")


#initialising a deta object
deta_connection= Deta(deta_key)


metaData=deta_connection.Base("database_versions")

@st.cache
def load_old_df():
    current_db = pd.read_csv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv", encoding= 'unicode_escape', low_memory=False)
    return current_db


@st.cache
def load_new_df():
    current_db = pd.read_csv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/newDB.csv", encoding= 'unicode_escape', low_memory=False)
    return current_db

@st.cache
def load_edited_df():
    current_db = pd.read_csv("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/editedtestDB.csv", encoding= 'unicode_escape', low_memory=False)
    return current_db


testDb="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv"
newDB="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/newDB.csv"
editednewDB="C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/editedtestDB.csv"





df1=load_old_df()
df2=load_new_df()
df3=load_edited_df()

st.write("testDB")
st.write(df1)
st.write("newDB")
st.write(df2)
st.write("editednewDB")
st.write(df3)

#------------------------------------------------------------COMPARING CSVS-----------------------------------------------------------------------------------------#
st.header("Using Pandas")
#using isin()

resultisin=df1[df1.apply(tuple,1).isin(df2.apply(tuple,1))]
st.write("using isnt() method for addition")
st.write(resultisin)
st.write("using isin() for edited df2, df3")
resultisinedit=df1[df2.apply(tuple,1).isin(df3.apply(tuple,1))]
st.write(resultisinedit)

resultmerge=(pd.merge(df1,df2))
st.write("Using merge method for addition")
st.write(resultmerge)
st.write("Using merge method for edited df2 df3")
resultmergeedit=(pd.merge(df2,df3))
st.write(resultmergeedit)

st.write("Using compare")
addition=df2.compare(df1, keep_equal=True)
st.write(addition)

st.header("Using pure python")

st.write("comparing an additon edit")
with open("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/newDB.csv", 'r') as file1, open ("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv", 'r') as file2:
    f1_contents=file1.readlines()
    f2_contents=file2.readlines()

for line in f1_contents:
    if line not in f2_contents:
        st.write(f"Addition "+line)

#for line in f2_contents:
 #   if line not in f1_contents:
        
  #      st.write(line)

st.header("using csv-diff library")

def compare_dbs(file1,file2):
    diff= compare(
        load_csv(open(file1), key="file1"),
        load_csv(open(file2), key="file2")
    )
    return diff

st.subheader("Comparing an addition")
#st.write(compare_dbs("C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/testDB.csv","C:/Users/Littl/OneDrive/Documents/GitHub/12528056_CSC7058/GABiP_GUI/pages/GABiP_Databases/newDB.csv" ))