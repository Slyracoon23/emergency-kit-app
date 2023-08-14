import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from st_aggrid.shared import ColumnsAutoSizeMode

import replicate


################### SIDE BAR #####################

# Function to handle form submission
def submit():
    st.session_state.show_product_list = True

st.sidebar.title('Emergency Advisor')
st.sidebar.subheader('Let us prepare your emergency inventory list!')

if 'output' not in st.session_state:
    st.session_state['output'] = '--'

if 'show_product_list' not in st.session_state:
    st.session_state.show_product_list = False

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
if st.session_state.show_product_list:
    ################### MAIN AREA: PRODUCT LIST #####################
    products = {
            "No.": [1, 2, 3],
            "Name": ['Backpack', 'Water Bottle', 'Firestarter'],
            "Price": [25, 5, 10],
            "Stocks": [150, 30, 10],
            "Details": [
                "https://nomad.nl/nl/wp-content/uploads/sites/2/2023/02/BBBAT7K3GB70737_1.jpg",
                "https://5.imimg.com/data5/HZ/NO/IH/SELLER-23767712/plastic-water-bottle-500x500.png",
                "https://m.media-amazon.com/images/I/71fb7xILoyL._AC_UF1000,1000_QL80_.jpg"
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
        
        # Create columns for button placement
        col1, col2 = st.columns([4, 1])  # adjust the ratio to position the button as desired

        # Place the checkout button in the second column
        with col2:
            if st.button("Generate Image"):
                st.session_state.button_pressed = True

    # Only run replicate and fetch the image when the button is pressed, and display it outside of the columns
    if st.session_state.get("button_pressed"):
        with st.spinner("Generating Image..."):  # Display loading spinner
            output = replicate.run(
                "stability-ai/sdxl:a00d0b7dcbb9c3fbb34ba87d2d5b46c56969c84a628bf778a7fdaec30b1b99c5",
                input={"prompt": "Bushcraft Survival Gear on Instagram: 'Preparation 🌲🌲 @Bushcraftshelter 📷@Yabandabiri Equipment for Living in Nature, Survival Kit, Bushcraft Camping. Kit dump, equipment setup display,          "}
            )

        print(output)
        image_url = output[0]
        if image_url:
            print(image_url)
            st.image(image_url, caption="Surviaval Kit" , use_column_width=True)
