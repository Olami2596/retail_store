import streamlit as st
from langchain_helper import get_few_shot_db_chain
import re
import traceback
import pandas as pd
import mysql.connector
from mysql.connector import Error
import altair as alt
import time
import math

# Set page configuration
st.set_page_config(
    page_title="TeeShirts",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern look
def local_css():
    st.markdown("""
    <style>
    /* Main containers */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #333;
    }
    
    h1 {
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Cards */
    .css-1r6slb0, .css-12oz5g7 {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        background-color: white;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: white;
        background-color: #4285F4;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #3367d6;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f1f3f8;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        padding: 0.5rem 1rem;
    }
    
    /* Success message */
    .element-container:has(.stAlert) {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    .stAlert {
        border-radius: 8px;
    }
    
    /* DataTable styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f3f8;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4 !important;
        color: white !important;
        font-weight: bold;
    }
    
    /* Radio buttons */
    .stRadio > div {
        display: flex;
        justify-content: center;
        gap: 1rem;
    }
    
    /* Card-like containers */
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Discount badge */
    .discount-badge {
        background-color: #FF6B6B;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* Pagination controls */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 1rem;
        gap: 0.5rem;
    }
    
    .page-info {
        font-size: 0.9rem;
        color: #666;
        margin: 0 1rem;
    }
    
    /* Color display */
    .color-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def extract_number_from_sql_result(result_str: str):
    """
    Extracts the first numerical value (int or float) from SQL result strings.
    Handles formats like [(93,)], [(Decimal('55'),)], [(Decimal('24295.100000'),)],
    and other common SQL result formats.
    """
    try:
        # First try to extract Decimal values
        decimal_match = re.search(r"Decimal\(['\"](\d+\.?\d*)['\"](?:, \d+)?\)", result_str)
        if decimal_match:
            number_str = decimal_match.group(1)
            return float(number_str) if '.' in number_str else int(number_str)
        
        # Try to extract numbers in tuple/list format like [(93,)]
        tuple_match = re.search(r"\[\((\d+\.?\d*)(?:,|\))", result_str)
        if tuple_match:
            number_str = tuple_match.group(1)
            return float(number_str) if '.' in number_str else int(number_str)
        
        # Try to extract any standalone number
        number_match = re.search(r"(?<![a-zA-Z])(\d+\.?\d*)(?![a-zA-Z])", result_str)
        if number_match:
            number_str = number_match.group(1)
            return float(number_str) if '.' in number_str else int(number_str)
        
        # If we get here, no number was found
        return "No quantity found"
    
    except Exception as e:
        st.error(f"Error parsing result: {str(e)}")
        return f"Error parsing result: {str(e)}"

def get_database_connection():
    """Create a connection to the MySQL database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MTeejay_2596",
            database="atliq_tshirts"
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None

def get_available_tshirts():
    """Get all available t-shirts with their discount information"""
    try:
        connection = get_database_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor()
        
        # Query to get t-shirts with their discount information (if any)
        query = """
        SELECT 
            t.t_shirt_id,
            t.brand,
            t.color,
            t.size,
            t.price,
            t.stock_quantity,
            IFNULL(d.pct_discount, 0) as discount_pct,
            CASE 
                WHEN d.pct_discount IS NOT NULL THEN t.price * (1 - d.pct_discount/100)
                ELSE t.price
            END as final_price
        FROM 
            t_shirts t
        LEFT JOIN 
            discounts d ON t.t_shirt_id = d.t_shirt_id
        WHERE 
            t.stock_quantity > 0
        ORDER BY 
            t.brand, t.color, t.size
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Create a DataFrame with the results
        columns = [
            "ID", "Brand", "Color", "Size", "Original Price ($)", 
            "Stock Quantity", "Discount (%)", "Final Price ($)"
        ]
        df = pd.DataFrame(result, columns=columns)
        
        # Format the discount percentage and prices
        df["Discount (%)"] = df["Discount (%)"].apply(lambda x: float(x))
        df["Original Price ($)"] = df["Original Price ($)"].apply(lambda x: float(x))
        df["Final Price ($)"] = df["Final Price ($)"].apply(lambda x: float(x))
        
        cursor.close()
        connection.close()
        
        return df
    
    except Error as e:
        st.error(f"Error retrieving t-shirts: {e}")
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        return None

def create_custom_chart(data, x_column, y_column):
    """Create a custom colored chart using Altair"""
    # Define a custom color scheme
    colors = ['#4285F4', '#4ECDC4', '#FFD166', '#6A0572', '#AB83A1']
    
    # Create the chart with custom colors
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(f'{x_column}:N', sort='-y', title=x_column),
        y=alt.Y(f'{y_column}:Q', title='Number of Items'),
        color=alt.Color(f'{x_column}:N', scale=alt.Scale(range=colors), legend=None),
        tooltip=[
            alt.Tooltip(f'{x_column}:N', title=x_column),
            alt.Tooltip(f'{y_column}:Q', title='Count', format=',d')
        ]
    ).properties(
        height=300
    ).interactive()
    
    return chart

def inventory_view():
    """Modern inventory view with cards and charts"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 👕 Available T-Shirts")
    
    # Load t-shirts data
    with st.spinner("Loading inventory..."):
        df = get_available_tshirts()
    
    if df is not None and not df.empty:
        # Create filters for sidebar
        st.sidebar.markdown("### 🔍 Filter Options")
        
        brands = ["All"] + sorted(df["Brand"].unique().tolist())
        colors = ["All"] + sorted(df["Color"].unique().tolist())
        sizes = ["All"] + sorted(df["Size"].unique().tolist())
        
        selected_brand = st.sidebar.selectbox("Brand", brands)
        selected_color = st.sidebar.selectbox("Color", colors)
        selected_size = st.sidebar.selectbox("Size", sizes)
        
        price_range = st.sidebar.slider(
            "Price Range ($)", 
            min_value=int(df["Final Price ($)"].min()), 
            max_value=int(df["Final Price ($)"].max() + 1),
            value=(int(df["Final Price ($)"].min()), int(df["Final Price ($)"].max() + 1))
        )
        
        show_discounted_only = st.sidebar.checkbox("Show only discounted items")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_brand != "All":
            filtered_df = filtered_df[filtered_df["Brand"] == selected_brand]
            
        if selected_color != "All":
            filtered_df = filtered_df[filtered_df["Color"] == selected_color]
            
        if selected_size != "All":
            filtered_df = filtered_df[filtered_df["Size"] == selected_size]
            
        filtered_df = filtered_df[
            (filtered_df["Final Price ($)"] >= price_range[0]) & 
            (filtered_df["Final Price ($)"] <= price_range[1])
        ]
        
        if show_discounted_only:
            filtered_df = filtered_df[filtered_df["Discount (%)"] > 0]
        
        # Display counts
        if not filtered_df.empty:
            total_count = len(filtered_df)
            cols = st.columns(4)
            cols[0].metric("Total Items", total_count)
            cols[1].metric("Brands", filtered_df["Brand"].nunique())
            cols[2].metric("Colors", filtered_df["Color"].nunique())
            cols[3].metric("Sizes", filtered_df["Size"].nunique())
            
            # Display the results in a card layout
            st.markdown("</div>", unsafe_allow_html=True)  # Close the top card
            
            # Visualization of t-shirt inventory with custom colors
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### 📊 Inventory Breakdown")
                chart_type = st.radio("Group by:", ["Brand", "Color", "Size"])
                
                if chart_type == "Brand":
                    chart_data = filtered_df.groupby("Brand").size().reset_index(name="Count")
                    st.altair_chart(create_custom_chart(chart_data, "Brand", "Count"), use_container_width=True)
                elif chart_type == "Color":
                    chart_data = filtered_df.groupby("Color").size().reset_index(name="Count")
                    st.altair_chart(create_custom_chart(chart_data, "Color", "Count"), use_container_width=True)
                else:
                    chart_data = filtered_df.groupby("Size").size().reset_index(name="Count")
                    st.altair_chart(create_custom_chart(chart_data, "Size", "Count"), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### 🛍️ Available Products")
                
                # Display sort options
                sort_col, view_col = st.columns([3, 1])
                sort_option = sort_col.selectbox(
                    "Sort by:", 
                    ["Price (Low to High)", "Price (High to Low)", "Discount (High to Low)"]
                )
                
                # Sort the dataframe based on selected option
                if sort_option == "Price (Low to High)":
                    filtered_df = filtered_df.sort_values("Final Price ($)")
                elif sort_option == "Price (High to Low)":
                    filtered_df = filtered_df.sort_values("Final Price ($)", ascending=False)
                else:  # Discount (High to Low)
                    filtered_df = filtered_df.sort_values("Discount (%)", ascending=False)
                
                # Pagination setup - 6 items per page
                items_per_page = 6
                total_pages = math.ceil(len(filtered_df) / items_per_page)
                
                # Initialize page number in session state if not exists
                if 'page_num' not in st.session_state:
                    st.session_state.page_num = 0
                
                # Function to update page number
                def next_page():
                    st.session_state.page_num = min(total_pages - 1, st.session_state.page_num + 1)
                
                def prev_page():
                    st.session_state.page_num = max(0, st.session_state.page_num - 1)
                
                def first_page():
                    st.session_state.page_num = 0
                
                def last_page():
                    st.session_state.page_num = total_pages - 1
                
                # Get items for current page
                start_idx = st.session_state.page_num * items_per_page
                end_idx = start_idx + items_per_page
                page_df = filtered_df.iloc[start_idx:end_idx]
                
                # Create a grid of products using native Streamlit components
                # instead of HTML - avoiding HTML rendering issues
                items_per_row = 2
                num_rows = math.ceil(len(page_df) / items_per_row)
                
                # Color mapping for visual display
                color_map = {
                    'Red': '#FF6B6B', 
                    'Blue': '#4285F4', 
                    'Black': '#333333', 
                    'White': '#F8F9FA',
                    'Green': '#4ECDC4',
                    'Yellow': '#FFD166',
                    'Purple': '#6A0572',
                    'Pink': '#FF8C94',
                    'Orange': '#FF9F1C',
                    'Brown': '#A57548'
                }
                
                # Display products in a grid using Streamlit columns
                # Replace the nested columns section with this code:

                # Display products in a grid using Streamlit columns
                for row_idx in range(num_rows):
                    cols = st.columns(items_per_row)
                    for col_idx in range(items_per_row):
                        item_idx = row_idx * items_per_row + col_idx
                        if item_idx < len(page_df):
                            item = page_df.iloc[item_idx]
                            
                            with cols[col_idx]:
                                # Create a card-like container with st.container
                                with st.container():
                                    st.markdown("---")
                                    
                                    # Product header with brand and color info
                                    st.markdown(f"""
                                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 12px;">
                                        <div style="background-color: {color_map.get(item['Color'], '#CCCCCC')}; 
                                                color: white; width: 50px; height: 50px; border-radius: 8px;
                                                display: flex; justify-content: center; align-items: center;
                                                font-size: 20px; font-weight: bold;">
                                            {item['Size']}
                                        </div>
                                        <div>
                                            <div style="font-size: 16px; font-weight: bold;">{item['Brand']}</div>
                                            <div style="font-size: 14px; color: #666;">Color: {item['Color']}</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Price information
                                    price_content = f"<div style='font-size: 18px; font-weight: bold; margin-bottom: 8px;'>${item['Final Price ($)']:.2f}</div>"
                                    if item['Discount (%)'] > 0:
                                        price_content += f"""
                                        <div style='display: flex; align-items: center; gap: 8px;'>
                                            <span style='text-decoration: line-through; color: #999;'>${item['Original Price ($)']:.2f}</span>
                                            <span style='background-color: #FF6B6B; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;'>
                                                -{item['Discount (%)']:.1f}%
                                            </span>
                                        </div>
                                        """
                                    st.markdown(price_content, unsafe_allow_html=True)
                                    
                                    # Stock information
                                    st.markdown(f"<div style='font-size: 12px; color: #666; margin-top: 8px;'>{int(item['Stock Quantity'])} in stock</div>", 
                                            unsafe_allow_html=True)
                                    
                                    st.markdown("---")
                                    
                # Stock information
                st.caption(f"{int(item['Stock Quantity'])} in stock")
                
                # Pagination controls
                if total_pages > 1:
                    st.markdown("<div style='display: flex; justify-content: center; margin-top: 20px;'>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
                    
                    with col1:
                        st.button("<<", on_click=first_page, disabled=st.session_state.page_num == 0)
                    
                    with col2:
                        st.button("<", on_click=prev_page, disabled=st.session_state.page_num == 0)
                    
                    with col3:
                        st.markdown(f"<div style='text-align: center; padding-top: 10px;'>Page {st.session_state.page_num + 1} of {total_pages}</div>", unsafe_allow_html=True)
                    
                    with col4:
                        st.button(">", on_click=next_page, disabled=st.session_state.page_num == total_pages - 1)
                    
                    with col5:
                        st.button(">>", on_click=last_page, disabled=st.session_state.page_num == total_pages - 1)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("</div>", unsafe_allow_html=True)  # Close the top card
            st.warning("No items match the selected filters.")
    else:
        st.markdown("</div>", unsafe_allow_html=True)  # Close the top card
        st.error("Unable to retrieve t-shirt data from the database.")

def question_answering_view():
    """Modern question answering view"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Ask About Our Inventory")
    
    # Sample questions as chips
    st.markdown("#### Sample Questions:")
    sample_cols = st.columns(3)
    
    sample_questions = [
        "How many red t-shirts are in stock?",
        "What's the average price of Nike t-shirts?",
        "How many XL size t-shirts do we have?",
        "Which brand has the most t-shirts?",
        "How many t-shirts have discounts?",
        "What's the total value of our inventory?"
    ]
    
    # Create buttons for sample questions
    for i, question in enumerate(sample_questions):
        if sample_cols[i % 3].button(question):
            st.session_state.question = question
    
    # Initialize session state for the question if it doesn't exist
    if 'question' not in st.session_state:
        st.session_state.question = ""
    
    # Question input
    question = st.text_input("Your Question:", value=st.session_state.question)
    
    if question:
        st.markdown("</div>", unsafe_allow_html=True)  # Close the top card
        
        # Changed from "Analyzing your question..." to "Checking inventory..."
        with st.spinner("🔍 Checking inventory..."):
            try:
                # Add a slight delay for UX
                time.sleep(0.5)
                
                # Get the database chain
                chain = get_few_shot_db_chain()
                
                # Invoke the chain with error handling
                try:
                    response = chain.invoke(question)
                    
                    # Extract and format the numerical answer
                    raw_result = response.get("result", "")
                    clean_answer = extract_number_from_sql_result(raw_result)
                    answer_text = response.get("answer", "")
                    
                    # Display results in a nice card
                    st.markdown('<div class="card" style="border-left: 4px solid #4285F4;">', unsafe_allow_html=True)
                    st.markdown("### 💡 Answer")
                    
                    # If we have both a clean numeric answer and text
                    if isinstance(clean_answer, (int, float)) and answer_text:
                        st.markdown(f"**{clean_answer:,}**")
                        st.markdown(f"*{answer_text}*")
                    # If we just have a clean numeric answer
                    elif isinstance(clean_answer, (int, float)):
                        st.markdown(f"**{clean_answer:,}**")
                    # Otherwise show the raw answer from the model
                    else:
                        st.markdown(f"*{answer_text or raw_result}*")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                        
                except Exception as invoke_error:
                    st.markdown("</div>", unsafe_allow_html=True)  # Close the top card
                    st.error(f"Sorry, I couldn't process that question. Please try rephrasing it.")
                    st.expander("Error details").write(str(invoke_error))
                    
            except Exception as chain_error:
                st.markdown("</div>", unsafe_allow_html=True)  # Close the top card
                st.error("There was a problem connecting to the database. Please try again later.")
                st.expander("Error details").write(str(chain_error))
    else:
        st.markdown("</div>", unsafe_allow_html=True)  # Close the top card

# Main app
try:
    # Apply custom CSS
    local_css()
    
    # Create a modern header
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown("""
        <div style="font-size: 3.5rem; font-weight: 800; margin-bottom: -1rem;">👕</div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="margin-top: 0.8rem;">
            <h1 style="margin-bottom: -0.3rem; font-size: 2rem;">TeeShirts</h1>
            <p style="color: #666; font-size: 1rem;">Inventory Management System</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Create tabs for different features
    tab1, tab2 = st.tabs(["🛍️ Browse Inventory", "❓ Ask Questions"])
    
    # Tab 1: Browse Inventory feature
    with tab1:
        inventory_view()
    
    # Tab 2: Q&A functionality
    with tab2:
        question_answering_view()
            
except Exception as app_error:
    st.error(f"Application startup error: {str(app_error)}")
    st.expander("Error details").write(traceback.format_exc())