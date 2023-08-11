import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from st_aggrid.shared import ColumnsAutoSizeMode

################### MAIN AREA: PRODUCT LIST #####################

products = {
    "No.": [1, 2, 3],
    "Name": [' Chair', ' Cabinet', ' Table'],
    "Price": [4, 12, 10],
    "Stocks": [100, 50, 60],
    "Details": [
        "https://i.imgur.com/fH2LHvo.png",
        "https://i.imgur.com/bvHZX5j.png",
        "https://i.imgur.com/D7xDwT9.png"
    ]
}

df = pd.DataFrame(products)
ob = GridOptionsBuilder.from_dataframe(df)

image_cr = JsCode("""
    function(params) {
        var element = document.createElement("span");
        var imageElement = document.createElement("img");
        var anchorElement = document.createElement("a");
        imageElement.src = params.data.Details;
        imageElement.width="80";
        imageElement.height="80";
        element.appendChild(imageElement);
        anchorElement.href = params.data.Details;
        anchorElement.target = "_blank";
        anchorElement.innerHTML = params.value;
        element.appendChild(anchorElement);
        return element;
    }""")

ob.configure_column('Name', cellRenderer=image_cr)

low_supply = JsCode("""
    function(params) {
        if (params.value < 60) {
            return {
                'color': 'red',
                'font-size': '20px'
            };
        }
    }""")
ob.configure_column("Stocks", cellStyle=low_supply)

ob.configure_selection(selection_mode="multiple", use_checkbox=True)
ob.configure_grid_options(rowHeight=100)
ob.configure_column("Details", hide=True)
grid_options = ob.build()

st.markdown('#### Streamlit-AgGrid')

grid_return = AgGrid(
    df,
    grid_options,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
    key='products',
    custom_css={'.ag-row .ag-cell': {'display': 'flex',
                                     'justify-content': 'center',
                                     'align-items': 'center'},
                '.ag-header-cell-label': {'justify-content': 'center'}}
) 

selected_rows = grid_return["selected_rows"]
if len(selected_rows):
    st.markdown('#### Selected')
    dfs = pd.DataFrame(selected_rows)
    dfsnet = dfs.drop(columns=['_selectedRowNodeInfo', 'Details'])
    AgGrid(
        dfsnet,
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        reload_data=True,
        key='product_selected'
    )   

################### SIDE BAR #####################

# Function to handle form submission
def submit():
    emergency_data = {
        "Item": ["Water", "Food", "Medication", "Flashlight", "Battery"],
        "Quantity": [3 * st.session_state.num_people, 5 * st.session_state.num_people, 2, 1, 4]
    }
    st.session_state['output'] = pd.DataFrame(emergency_data)

st.sidebar.title('Emergency Advisor')
st.sidebar.subheader('Let us prepare your emergency inventory list!')

if 'output' not in st.session_state:
    st.session_state['output'] = '--'

with st.sidebar.form(key='emergency_form'):
    c1, c2, c3 = st.sidebar.columns(3)
    with c1:
        st.subheader('Basic Details')
        st.text_input('Location', value='New York', key='location')
        st.selectbox('Type of Emergency', ('Wildfire', 'Flood', 'Earthquake', 'Power Outage', 'Tornado', 'Other'), key='type_of_emergency')
        st.number_input('Number of People', value=1, min_value=1, key='num_people')
    with c2:
        st.subheader('Specific Needs')
        st.radio('Pets', ['Yes', 'No'], key='pets')
        st.text_area('Special Needs (e.g., medications, disabilities)', height=100, key='special_needs')
    with c3:
        st.subheader('Duration & Notes')
        st.selectbox('Anticipated Duration', ('24 hours', '3 days', '1 week', 'More than a week'), key='duration')
        st.text_area('Additional Notes', height=100, value='I have a toddler.', key='additional_notes')
    st.form_submit_button('Submit', on_click=submit)

# Main area
st.subheader('Emergency Inventory List')
if isinstance(st.session_state.output, pd.DataFrame):
    AgGrid(st.session_state.output)
else:
    st.write(st.session_state.output)
