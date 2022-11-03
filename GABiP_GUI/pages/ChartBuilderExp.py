import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly_express as px
import cufflinks as cf

@st.cache
def load_original():
    dfFull = pd.read_csv('C:/Users/Littl/OneDrive/Desktop/GABiP_July.csv', encoding= 'unicode_escape', low_memory=False)
    return dfFull

dfFull=load_original()

#st.header("This is the chart build exp page")
#st.sidebar.write("Chart ingredients")
#st.write("This is a hard coded bar chart using streamlit")
#fig = dfFull.head(20)

#col1,col2,col3=st.columns(3)
#st.line_chart(fig, x="Species", y="SVLMMn", width=500, height=500)
#st.bar_chart(fig, x="Species", y="SVLMMn")

#pie_chart= dfFull.iplot(kind="pie", labels=dfFull["Species"], values=dfFull["SVLMMn"], textinfo='percent+label', hole=.4)

#pie_chart

st.title("Interactive Chart")

st.write("Choose a chart type")

chartOptions=st.selectbox("Choose a chart type",('Scatter Chart', 'Bar Chart', 'Line Chart', 'Pie Chart'))

x_axis=st.selectbox("Select X value", options=dfFull.columns)
y_axis=st.selectbox("Select Y value", options=dfFull.columns)
z_axis=st.selectbox("Select Z Value", options=dfFull.columns)
def dynamicChart(dataframe):
    if chartOptions == ('Scatter Chart'):
       # x_axis=st.selectbox("Select Xx value", options=dfFull.columns)
        #y_axis=st.selectbox("Select Yy value", options=dfFull.columns)
        plot=px.scatter(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)
    elif chartOptions==('Bar Chart'):
         plot=px.bar(dataframe, x=x_axis, y=y_axis)
         st.plotly_chart(plot)
    elif chartOptions==('Line Chart'):
        plot=px.line(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)
    elif chartOptions==('Pie Chart'):
        plot=px.pie(dataframe, x=x_axis, y=y_axis)
        st.plotly_chart(plot)

    
   
(dynamicChart(dfFull))







