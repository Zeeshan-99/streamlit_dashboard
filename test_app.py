
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px


st.title('Welcome')
@st.cache_data
def load_data(path: str):
    data = pd.read_excel(path)
    return data
with st.sidebar:
    st.header('Configuration')
    uploaded_file= st.file_uploader("Choose a file")

if uploaded_file is None:
    st.info("Upload a file through config")
    st.stop()

df= load_data("Financial Data Clean.xlsx")

with st.expander("Data Preview"):
    st.dataframe(df, column_config={"Year": st.column_config.NumberColumn(format="%d")})


all_months= ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def plot_bottom_left():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            SELECT
            Scenario, {','.join(all_months)}
            FROM df
            WHERE Year='2023'
            AND Account='Sales'
            AND business_unit='Software'
            )
            UNPIVOT sales_data
            ON {','.join(all_months)}
            INTO 
                NAME month
                VALUE sales
            """
    ).df()
    st.dataframe(sales_data)
    st.line_chart(sales_data, x='month',y='sales')
    
    fig=px.line(
        sales_data,
        x='month',
        y='sales',
        color='Scenario',
    )
    st.plotly_chart(fig, use_container_width=True)
    
        
    fig=px.bar(
        sales_data,
        x='Year',
        y='sales',
        color='Account',
        title='Actual yearly sales per Account',
    )
    st.plotly_chart(fig, use_container_width=True)
    
plot_bottom_left()    