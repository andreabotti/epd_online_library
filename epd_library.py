# IMPORT LIBRARIES
# from fn__libraries import *

import streamlit as st
import pandas as pd
import os






##### ##### PAGE CONFIG
st.set_page_config(page_title="EPD Italy Viz",   page_icon=':mostly_sunny:', layout="wide")
st.markdown(
    """<style>.block-container {padding-top: 0.5rem; padding-bottom: 0rem; padding-left: 2.5rem; padding-right: 2.5rem;}</style>""",
    unsafe_allow_html=True)


##### ##### TOP CONTAINER
top_col1, top_col2 = st.columns([6,1])
with top_col1:
    st.markdown("## Visualisation of EPD Italy data")
    st.caption('Developed by AB.S.RD - https://absrd.xyz/')

st.divider()




def load_data():
    # Define the path to the CSV file
    data_path = os.path.join('epdx_data', 'epditaly_gwp.csv')
    
    # Check if the file exists
    if os.path.exists(data_path):
        # Load the data into a DataFrame
        df = pd.read_csv(data_path)
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if file is not found


# Set the title of the app
st.markdown('##### Parsed data from EPD Italy')

# Load data
data = load_data()

# Check if the DataFrame is not empty
if not data.empty:
    st.dataframe(
        data,
        height=600,
        )
else:
    st.error("Error: No data found. Please check the file path and name.")

