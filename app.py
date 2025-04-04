import streamlit as st
import pandas as pd
import ast  # To parse string lists in Browsing_History and Purchase_History

# -------------------------------
# Load Data with Fallback
# -------------------------------
@st.cache_data
def load_data():
    try:
        # Load customer data
        customers = pd.read_csv("customers.csv")
        products = pd.read_csv("products.csv")
        
        # Define required columns
        required_customer_cols = ['Customer_ID', 'Age', 'Gender', 'Browsing_History']
        required_product_cols = ['ProductName', 'Category', 'Price', 'Description']
        
        # Check for missing columns in customers.csv
        missing_customer_cols = [col for col in required_customer_cols if col not in customers.columns]
        if missing_customer_cols:
            raise ValueError(f"Missing required columns in customers.csv: {', '.join(missing_customer_cols)}")
        
        # Check for missing columns in products.csv
        missing_product_cols = [col for col in required_product_cols if col not in products.columns]
        if missing_product_cols:
            raise ValueError(f"Missing required columns in products.csv: {', '.join(missing_product_cols)}")
        
        # Convert string lists to actual lists
        customers['Browsing_History'] = customers['Browsing_History'].apply(ast.literal_eval)
        return customers, products
    
    except FileNotFoundError as e:
        st.warning(f"🚫 Data file not found: {str(e)}. Using sample data instead.")
        customers_data = {
            'Customer_ID': ['C1000', 'C1001', 'C1002'],
            'Age': [28, 27, 34],
            'Gender': ['Female', 'Male', 'Other'],
            'Browsing_History': [['Books', 'Fashion'], ['Books', 'Fitness', 'Fashion'], ['Electronics']]
        }
        products_data = {
            'ProductName': ['Biography Book', 'Trendy Jeans', 'Smartphone'],
            'Category': ['Books', 'Fashion', 'Electronics'],
            'Price': [19.99, 59.99, 299.99],
            'Description': ['Engaging biography', 'Stylish jeans', 'Latest smartphone']
        }
        return pd.DataFrame(customers_data), pd.DataFrame(products_data)
    
    except ValueError as e:
        st.error(f"🚫 Data validation error: {str(e)}")
        st.markdown("Falling back to sample data.")
        customers_data = {
            'Customer_ID': ['C1000', 'C1001', 'C1002'],
            'Age': [28, 27, 34],
            'Gender': ['Female', 'Male', 'Other'],
            'Browsing_History': [['Books', 'Fashion'], ['Books', 'Fitness', 'Fashion'], ['Electronics']]
        }
        products_data = {
            'ProductName': ['Biography Book', 'Trendy Jeans', 'Smartphone'],
            'Category': ['Books', 'Fashion', 'Electronics'],
            'Price': [19.99, 59.99, 299.99],
            'Description': ['Engaging biography', 'Stylish jeans', 'Latest smartphone']
        }
        return pd.DataFrame(customers_data), pd.DataFrame(products_data)

# -------------------------------
# Recommend Products
# -------------------------------
def recommend_products(customer, products_df):
    try:
        interests = customer['Browsing_History']  # Already a list from ast.literal_eval
        recommendations = products_df[products_df['Category'].str.lower().isin([i.lower() for i in interests])]
        if recommendations.empty:
            recommendations = products_df.sample(3)
        return recommendations.head(3)
    except Exception as e:
        st.error(f"🚫 Recommendation error: {str(e)}")
        return products_df.sample(3)

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.set_page_config(page_title="Smart Shopping", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    .stButton>button {background-color: #007bff; color: white; border-radius: 8px;}
    .product-card {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 15px;}
    .sidebar .sidebar-content {background-color: #f0f0f0;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🛍️ Smart Shopping")
    st.subheader("AI-Powered Product Recommendations")
    st.markdown("Discover personalized product suggestions tailored to your interests!")

    # Load Data
    customers_df, products_df = load_data()

    # Sidebar
    with st.sidebar:
        st.header("📋 Select Customer")
        customer_ids = customers_df['Customer_ID'].tolist()
        selected_id = st.selectbox("Choose a Customer", customer_ids, key="customer_select")
        st.markdown("---")
        st.info("Select a customer to see their profile and recommendations.")

    # Main Content
    selected_customer = customers_df[customers_df['Customer_ID'] == selected_id].iloc[0]
    
    col1, col2 = st.columns([1, 2], gap="medium")
    
    with col1:
        st.subheader("👤 Customer Profile")
        with st.expander("View Details", expanded=True):
            st.markdown(f"""
            **Customer ID:** {selected_customer['Customer_ID']}  
            **Age:** {selected_customer['Age']}  
            **Gender:** {selected_customer['Gender']}  
            **Interests:** {', '.join(selected_customer['Browsing_History'])}
            """)
    
    with col2:
        st.subheader("🎯 Your Recommendations")
        recommended = recommend_products(selected_customer, products_df)
        
        if not recommended.empty:
            for _, product in recommended.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="product-card">
                        <h4>🛒 {product['ProductName']}</h4>
                        <p><b>Category:</b> {product['Category']}</p>
                        <p><b>Price:</b> ${product['Price']}</p>
                        <p><b>Description:</b> {product['Description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No recommendations available.")

if __name__ == "__main__":
    main()
