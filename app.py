import streamlit as st
import pandas as pd

# -------------------------------
# Load Data with Error Handling
# -------------------------------
@st.cache_data
def load_data():
    try:
        # Load customer data
        customers = pd.read_csv("customers.csv")
        products = pd.read_csv("products.csv")
        
        # Define required columns
        required_customer_cols = ['CustomerName', 'Age', 'Gender', 'Interests']
        required_product_cols = ['ProductName', 'Category', 'Price', 'Description']
        
        # Check for missing columns in customers.csv
        missing_customer_cols = [col for col in required_customer_cols if col not in customers.columns]
        if missing_customer_cols:
            raise ValueError(f"Missing required columns in customers.csv: {', '.join(missing_customer_cols)}")
        
        # Check for missing columns in products.csv
        missing_product_cols = [col for col in required_product_cols if col not in products.columns]
        if missing_product_cols:
            raise ValueError(f"Missing required columns in products.csv: {', '.join(missing_product_cols)}")
        
        return customers, products
    
    except FileNotFoundError as e:
        st.error(f"🚫 Data file not found: {str(e)}. Please ensure 'customers.csv' and 'products.csv' are present.")
        return None, None
    except ValueError as e:
        st.error(f"🚫 Data validation error: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"🚫 Unexpected error loading data: {str(e)}")
        return None, None

# -------------------------------
# Recommend Products
# -------------------------------
def recommend_products(customer, products_df):
    try:
        interests = customer['Interests'].split('|')
        # Case-insensitive matching
        recommendations = products_df[products_df['Category'].str.lower().isin([i.lower() for i in interests])]
        
        # Fallback if no matches
        if recommendations.empty:
            recommendations = products_df.sample(3)  # Random 3 products as fallback
        return recommendations.head(3)  # Limit to 3 recommendations
    except Exception as e:
        st.error(f"🚫 Error generating recommendations: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    # Page Configuration
    st.set_page_config(
        page_title="Smart Shopping",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for enhanced UI
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
    if customers_df is None or products_df is None:
        st.markdown("### Please fix the data files and restart the app.")
        return

    # Sidebar
    with st.sidebar:
        st.header("📋 Select Customer")
        customer_names = customers_df['CustomerName'].tolist()
        selected_name = st.selectbox("Choose a Customer", customer_names, key="customer_select")
        
        st.markdown("---")
        st.info("Select a customer to view their profile and get tailored recommendations.")

    # Main Content
    selected_customer = customers_df[customers_df['CustomerName'] == selected_name].iloc[0]
    
    col1, col2 = st.columns([1, 2], gap="medium")
    
    with col1:
        st.subheader("👤 Customer Profile")
        with st.expander("View Details", expanded=True):
            st.markdown(f"""
            **Name:** {selected_customer['CustomerName']}  
            **Age:** {selected_customer['Age']}  
            **Gender:** {selected_customer['Gender']}  
            **Interests:** {selected_customer['Interests'].replace('|', ', ')}
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
            st.warning("No recommendations available. Showing random products instead.")

if __name__ == "__main__":
    main()
