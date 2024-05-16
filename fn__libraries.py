import os, streamlit as st, pandas as pd, numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_super_slider import st_slider








#####
def ab_create_AgGrid(df):
    
    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=100)  # Add pagination    
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False,
        )  # Enable single row selection

    # Set default column properties
    gb.configure_default_column(
        minWidth=100,
        resizable=True,
        wrapText=True,
        )

    # Example: Set specific column widths
    # gb.configure_column("manufacturer", width=60)
    # gb.configure_column("product_name", width=120)
    gb.configure_column("product_type", width=120)
    # gb.configure_column("epd_issue_date",   width=135)
    # gb.configure_column("epd_expiry_date",  width=135)
    # gb.configure_column("reg_number",       width=135)

    # Set table height
    grid_options = gb.build()
    grid_options['domLayout'] = 'normal'  # Allow custom layout
    grid_options['rowHeight'] = 25  # Adjust row height
    grid_options['minHeight'] = 300  # Minimum height of the grid
    grid_options['maxHeight'] = 650  # Maximum height of the grid

    # Display the DataFrame using AgGrid
    grid_response = AgGrid(
        df,
        height=700,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,  # Allowing HTML in AgGrid
        theme='streamlit',
    )

    return grid_response


#####


def find_matching_pdf(directory, reg_number):
    # List all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):  # Ensure it's a PDF file
            # Split filename at the first "_" and check if it matches the registration number
            prefix = filename.split("_", 1)[0]
            print(prefix)
            if prefix == reg_number:
                return os.path.join(directory, filename)
    return None  # Return None if no matching file is found


#####


def ab_find_file_on_ftp(url, file_ext, prefix):

    files_url = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming files are listed in a specific HTML element you can identify
    for link in soup.find_all('a'):  # Adjust tag and attributes as needed
        file_url = link.get('href')
        files_url.append(file_url)

        if file_url.endswith(file_ext):
            files_url.append(file_url)

    # return files_url
    return soup


#####



# Function to get the value from the dictionary
def get_value_from_dict(dictionary, key):
    try:
        # Attempt to get the value associated with the key
        value = dictionary[key]
        print(f"Value found for {key}: {value}")
        return value
    except KeyError:
        # Handle the case where the key is not found
        print(f"No value found for the key: {key}")
        return None
