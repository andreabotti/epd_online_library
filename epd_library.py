# IMPORT LIBRARIES
# from fn__libraries import *

import os, streamlit as st, pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode







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



#####
def load_data():
    # Define the path to the CSV file
    # data_path = os.path.join(
    #     'epdx_data',
    #     'epditaly_gwp.csv',
    #     )
    data_path = os.path.join(
        'epdx_data',
        'master_epd_data.csv',
        )
    
    # Check if the file exists
    if os.path.exists(data_path):
        # Load the data into a DataFrame
        df = pd.read_csv(data_path)
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if file is not found



#####

col_01, col_02 = st.columns([3,2])

# Load data
df = load_data()
df_plot = load_data()

# Function to make links clickable
def make_clickable(url, text):
    return f'<a href="{url}" target="_blank">{text}</a>'


# Apply the make_clickable function to URL and PDF Link columns
df_plot['entry_url'] = df_plot.apply(
    lambda x: make_clickable(x['entry_url'], 'Entry link'), axis=1,
    )
df_plot['pdf_url'] = df_plot.apply(
    lambda x: make_clickable(x['pdf_url'], 'EPD PDF Link'), axis=1,
    )

df.drop(
    ['entry_url', 'pdf_url', 'image', 'CPC_code', 'cat',
     'product_description', 'production_unit', 'additional_info',
     'epd_update_date', 'ref_year',
    ],
    axis=1, inplace=True)



with col_01:

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False,
        )  # Enable single row selection

    grid_options = gb.build()

    # Display the DataFrame using AgGrid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,  # Allowing HTML in AgGrid
        # theme='STREAMLIT',
    )

    # Get selected rows
    selected_rows = grid_response['selected_rows']

# Check if any row is selected
if selected_rows:
    selected_reg_number = selected_rows[0]['reg_number']
    
    # Filter the second DataFrame based on the selected Registration Number
    sel_df_plot = df_plot[df_plot['reg_number'] == selected_reg_number]


    sel_df_plot.drop(
        ['image',
        #  'product_description', 'production_unit',
         'additional_info', 'CPC_code',
        'epd_update_date', 'ref_year', 'cat',
        ],
        axis=1, inplace=True)

    sel_df_plot = sel_df_plot[[
        'manufacturer',
        'product_name',
        'production_unit',
        'product_type',
        'entry_url',
        'pdf_url',
        'product_description',
        'reg_number', 'epd_issue_date', 'epd_expiry_date',
    ]]

    col_02.markdown('##### Data for...')
    col_02.markdown(
        sel_df_plot.transpose().to_html(escape=False, index=True),
        unsafe_allow_html=True,
    )


else:
    col_02.write("Select a row to see details.")

