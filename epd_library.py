# IMPORT LIBRARIES
# from fn__libraries import *
import os, streamlit as st, pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from geopy.geocoders import Nominatim
import plotly.express as px





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

col_chart, spacing, col_table, spacing, col_details = st.columns([12,1,30,1,16])

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



with col_table:

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=1000)  # Add pagination    
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False,
        )  # Enable single row selection

    # Set default column properties
    gb.configure_default_column(minWidth=100, resizable=True, wrapText=True)

    # Example: Set specific column widths
    gb.configure_column("product_name", width=300)
    gb.configure_column("manufacturer", width=250)
    gb.configure_column("product_type", width=175)
    gb.configure_column("epd_issue_date",   width=135)
    gb.configure_column("epd_expiry_date",  width=135)
    gb.configure_column("reg_number",       width=135)


    # Set table height
    grid_options = gb.build()
    grid_options['domLayout'] = 'normal'  # Allow custom layout
    grid_options['rowHeight'] = 30  # Adjust row height
    grid_options['minHeight'] = 400  # Minimum height of the grid
    grid_options['maxHeight'] = 550  # Maximum height of the grid


    # Display the DataFrame using AgGrid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=600,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,  # Allowing HTML in AgGrid
        theme='streamlit',
    )

    # Get selected rows
    selected_rows = grid_response['selected_rows']

# Ensure that selected_rows is not empty and check its length
# if not selected_rows.empty and len(selected_rows) > 0:
try:
    selected_reg_number = selected_rows[0]['reg_number']
    
    # Filter the second DataFrame based on the selected Registration Number
    sel_df_plot = df_plot[df_plot['reg_number'] == selected_reg_number]

    sel_df_plot = sel_df_plot.drop(
        ['image', 'additional_info', 'CPC_code', 'epd_update_date', 'ref_year', 'cat',
        #  'product_description', 'production_unit',
        ], axis=1)

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

    df_display = sel_df_plot.transpose()
    # col_details.markdown('##### Data for...')
    col_details.markdown(
        df_display.to_html(escape=False, index=True),
        unsafe_allow_html=True,
    )


    col_details.divider()

    df_map = sel_df_plot

    # Geocode the address
    geolocator = Nominatim(user_agent="streamlit_app")
    address = df_map.iloc[0]['production_unit']
    location = geolocator.geocode(address)

    if location:
        col_details.write(f"Geocoded location for address '{address}':")
        col_details.map(
            pd.DataFrame({'lat': [location.latitude], 'lon': [location.longitude]})
            )
    else:
        col_details.write(f"Address '{address}' could not be geocoded.")#



except:
    col_details.write("Select a row to see details.")






# Calculate the count of each product type
product_type_counts = df['product_type'].value_counts()
table_plot = product_type_counts.reset_index()

# Display the DataFrame to show the data that will be used in the chart
# st.dataframe(product_type_counts.reset_index().rename(columns={'index': 'Product Type', 'Type': 'Count'}))
# st.dataframe(table_plot)


fig = px.bar(
    table_plot,
    x='product_type', y='count', orientation='h',
    # labels={'index': 'Type', 'product_type': 'Count'},
    title="Product Type Distribution",
    height=600,
    )
# Update layout for finer control (optional)
fig.update_layout(
    title_text='Product Type Distribution',  # Adding a custom title
    title_x=0.3,  # Centering the title
    yaxis_title='',  # Labeling the Y-axis
    xaxis_title='COUNT',  # Labeling the X-axis
    template='plotly_white',  # Choosing a visual template
    margin=dict(l=0, r=0, t=40, b=0),  # Setting custom margins (left, right, top, bottom)
)

col_chart.plotly_chart(fig, use_container_width=True)