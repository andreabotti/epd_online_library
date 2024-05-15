# IMPORT LIBRARIES
# from fn__libraries import *
import os, streamlit as st, pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go




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
df0 = load_data()

table = df0.copy()
table_slim = df0.copy()
table_slim.drop(
    ['entry_url', 'pdf_url', 'image', 'CPC_code', 'cat',
     'product_description', 'production_unit', 'additional_info',
     'epd_update_date', 'ref_year',
    ], inplace=True, axis=1,
    )
table_slim = table_slim[[
    'reg_number',
    'manufacturer',
    'product_name',
    'product_type',
    'epd_issue_date', 'epd_expiry_date',
]]



# Function to make links clickable
def make_clickable(url, text):
    return f'<a href="{url}" target="_blank">{text}</a>'

# Apply the make_clickable function to URL and PDF Link columns
table['entry_url'] = table.apply(
    lambda x: make_clickable(x['entry_url'], 'Entry link'), axis=1,
    )
table['pdf_url'] = table.apply(
    lambda x: make_clickable(x['pdf_url'], 'EPD PDF Link'), axis=1,
    )





#####
# BAR CHART

# Calculate the count of each product type
product_type_counts = df0['product_type'].value_counts()
table_plot = product_type_counts.reset_index()
table_plot.columns = ['type','count']


# Create the bar chart using Plotly graph objects
fig = go.Figure(go.Bar(
    x=table_plot['count'],  # Counts of each type
    y=table_plot['type'],  # Product type labels
    orientation='h'  # Horizontal bar chart
))

# Update layout for finer control (optional)
fig.update_layout(
    title_text='Product Type Distribution',  # Adding a custom title
    title_x=0.3,  # Centering the title
    height=650,
    yaxis=dict(
        title='',  # Hiding the Y-axis title (or set your title here)
        ticktext=table_plot['type'],  # Set custom text for each tick based on 'Type' column
        # tickvals=table_plot['type']  # Map tick texts to the correct values on the Y-axis
    ),
    xaxis_title='COUNT',  # Labeling the X-axis
    template='plotly_white',  # Choosing a visual template
    margin=dict(l=0, r=0, t=40, b=0),  # Setting custom margins (left, right, top, bottom)
)

col_chart.plotly_chart(fig, use_container_width=True)











with col_table:

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(table_slim)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=100)  # Add pagination    
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False,
        )  # Enable single row selection

    # Set default column properties
    gb.configure_default_column(
        # minWidth=100,
        resizable=True,
        wrapText=True,
        )

    # Example: Set specific column widths
    # gb.configure_column("manufacturer", width=60)
    # gb.configure_column("product_name", width=120)
    gb.configure_column("product_type", width=175)
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
        table_slim,
        height=700,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,  # Allowing HTML in AgGrid
        theme='streamlit',
    )

    # Get selected rows
    selected_rows = grid_response['selected_rows']




try:
    selected_reg_number = selected_rows['reg_number'][0]
except:
    selected_reg_number = 'EPDITALY0003'



# Filter the second DataFrame based on the selected Registration Number
filtered_table = table[table['reg_number'] == selected_reg_number]

filtered_table = filtered_table.drop(
    ['image', 'additional_info', 'CPC_code', 'epd_update_date', 'ref_year', 'cat',
    #  'product_description', 'production_unit',
    ], axis=1)
filtered_table = filtered_table[[
    'manufacturer',
    'product_name',
    'production_unit',
    'product_type',
    'entry_url',
    'pdf_url',
    'product_description',
    'reg_number', 'epd_issue_date', 'epd_expiry_date',
]]

df_display = filtered_table.drop(['product_description'],axis=1).transpose()



# Define the tab names
tab1, tab2, tab3 = col_details.tabs(['Product Details', 'Product Description', 'Map View'])

with tab1:
    st.markdown(f'##### {selected_reg_number}')


    # Display the styled HTML in Streamlit
    html = df_display.to_html(escape=False, index=True, header=False)
    styled_html = html
    styled_html = f'<div style="font-size: 14px;">{html}</div>'.replace('\n','')
    st.markdown(styled_html, unsafe_allow_html=True)


with tab2:
    product_description = filtered_table.iloc[0]['product_description']
    styled_html = f'<div style="font-size: 14px;">{product_description}</div>'.replace('\n','')
    st.markdown(styled_html, unsafe_allow_html=True)


# with tab3:
#     st.markdown('##### Map Production')

#     df_map = filtered_table

#     # Geocode the address
#     geolocator = Nominatim(user_agent="streamlit_app")
#     address = df_map.iloc[0]['production_unit']
#     location = geolocator.geocode(address)

#     if location:
#         st.write(f"Geocoded location for address '{address}':")
#         st.map(
#             pd.DataFrame({'lat': [location.latitude], 'lon': [location.longitude]})
#             )
#     else:
#         st.write(f"Address '{address}' could not be geocoded.")#

