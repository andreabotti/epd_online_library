# IMPORT LIBRARIES
from fn__libraries import *
import os, json, streamlit as st, pandas as pd
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









# Create a dictionary to hold DataFrames sliced by 'product_type'
dfs = {}
df = table_slim

# Loop through each unique value in the 'product_type' column
product_types = df['product_type'].unique().tolist()
product_types = sorted([str(item) for item in product_types])


for product_type in product_types:
    dfs[product_type] = df[df['product_type'] == product_type]





with col_table:
    selected_type = st.selectbox(label='Product Type', options=product_types)
    filtered_table = table_slim[table_slim.product_type==selected_type]
    grid_response = ab_create_AgGrid(df=filtered_table)

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




col_details.markdown(f'##### {selected_reg_number}')

# Define the tab names
tab1, tab2, tab3 = col_details.tabs(['Product Details', 'Product Description', 'PDF Preview'])

with tab1:

    # Display the styled HTML in Streamlit
    html = df_display.to_html(escape=False, index=True, header=False)
    styled_html = html
    styled_html = f'<div style="font-size: 14px;">{html}</div>'.replace('/n','')
    st.markdown(styled_html, unsafe_allow_html=True)


with tab2:
    product_description = filtered_table.iloc[0]['product_description']
    styled_html = f'<div style="font-size: 14px;">{product_description}</div>'.replace('/n','')
    st.markdown(styled_html, unsafe_allow_html=True)




#####



with tab3:

    folder_url = 'https://absrd.xyz/streamlit_apps/epd_online_library/epd_pdfs/'

    # Loading the dictionary back from the json file
    json_file_path = 'file_dict.json'
    with open(json_file_path, 'r') as f:
        loaded_dict = json.load(f)

    file_path = get_value_from_dict(dictionary=loaded_dict, key=selected_reg_number)
    file_name = file_path[0].rsplit('\\',1)[1]
    file_url = folder_url + file_name 


    # Add a button that the user can click to show or hide the PDF
    if 'show_pdf' not in st.session_state:
        st.session_state.show_pdf = False  # Default the PDF to not show

    toggle_button = st.button('Show/Hide PDF')

    if toggle_button:
        st.session_state.show_pdf = not st.session_state.show_pdf

    if st.session_state.show_pdf:

        # Embed PDF in an iframe within Streamlit
        width = '440'
        height = '425'
        scale = '0.15'  # Adjust scale as per requirement

        st.markdown(
            f'''
            <style>
                iframe {{
                    width: {width}px;
                    height: {height}px;
                    border: none;  # Removes the border around the iframe
                    transform: scale({scale});
                    transform-origin: top left;  # Ensures the zoom is from top left
                }}
            </style>
            <iframe src="{file_url}#toolbar=1" width="{width}" height="{height}" type="application/pdf"></iframe>
            ''',
            unsafe_allow_html=True
        )
