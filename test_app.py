
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")
st.title('Welcome to the streamlit Dashboard')
@st.cache_data
def load_data(path: str):
    data = pd.read_excel(path)
    return data
with st.sidebar:
    st.header('Configuration')
    uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is None:
    st.info("Upload a file through config")
    st.stop()

df= load_data("Financial Data Clean.xlsx")

with st.expander("Data Preview"):
    st.dataframe(df, column_config={"Year": st.column_config.NumberColumn(format="%d")})

# with st.expander("Data Profiling"):
#     pr = ProfileReport(df)
#     st_profile_report(pr)

all_months= ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def plot_bottom_left():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            SELECT
            Scenario,Year,{','.join(all_months)}
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
    
    sales_data= duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT(
                SELECT Scenario,
                business_unit,
                {','.join(all_months)}
                FROM df 
                WHERE Year='2023'
                AND Account='Sales'
                )
            ON {','.join(all_months)}
            INTO 
                NAME month
                VALUE sales    
                ),
                aggregated_sales AS (
                    SELECT
                    Scenario, business_unit, SUM(sales) AS sales FROM sales_data
                    GROUP BY Scenario, business_unit
                )
                SELECT * FROM aggregated_sales
                """
    ).df()   
    st.dataframe(sales_data)
    fig=px.bar(
        sales_data,
        x='business_unit',
        y='sales',
        color='Scenario',
        barmode="group",
        title='Sales for Year 2023',
        height=400
    )
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)
    
    
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT ( 
                SELECT 
                    Account,Year,{','.join([f'ABS({month}) AS {month}' for month in all_months])}
                    FROM df 
                    WHERE Scenario='Actuals'
                    AND Account!='Sales'
                ) 
            ON {','.join(all_months)}
            INTO
                NAME year
                VALUE sales
        ),

        aggregated_sales AS (
            SELECT
                Account,
                Year,
                SUM(sales) AS sales
            FROM sales_data
            GROUP BY Account, Year
        )
        
        SELECT * FROM aggregated_sales
    """
    ).df()

    fig = px.bar(
        sales_data,
        x="Year",
        y="sales",
        color="Account",
        title="Actual Yearly Sales Per Account",
    )
    st.dataframe(sales_data)
    st.plotly_chart(fig, use_container_width=True)

plot_bottom_left()

