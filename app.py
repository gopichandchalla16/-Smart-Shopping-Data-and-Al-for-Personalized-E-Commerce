import streamlit as st
import pandas as pd

# -------------------------------
# Load Data with Error Handling
# -------------------------------
@st.cache_data
def load_data():
    try:
        customers = pd.read_csv("customers.csv")
        products = pd.read_csv("products.csv")
        # Verify required columns exist
        required_customer_cols = ['CustomerName', 'Age', 'Gender', 'Interests']
        required_product_cols = ['ProductName', 'Category', 'Price', 'Description']
        
        if not all(col in customers.columns for col in required_customer_cols):
            raise ValueError("Missing required columns in customers.csv")
        if not all(col in products.columns for col in required_product_cols):
            raise ValueError("Missing required columns in products.csv")
            
        return customers, products
    except FileNotFoundError:
        st.error("🚫 Data files 'customers.csv' or 'products.csv' not found!")
        return None, None
    except Exception as e:
        st.error(f"🚫 Error loading data: {str(e)}")
        return None, None

# -------------------------------
# Recommend Products
# -------------------------------
def recommend_products(customer, products_df):
    interests = customer['Interests'].split('|')
    # Filter products by interest, case-insensitive
    recommendations = products_df[products_df['Category'].str.lower().isin([i.lower() for i in interests])]
    
    # If no matches, return top 3 highest-rated or random products
    if recommendations.empty:
        if 'Rating' in products_df.columns:
            recommendations = products_df.nlargest(3, 'Rating')
        else:
            recommendations = products_df.sample(3)
    return recommendations.head(3)  # Limit to 3 recommendations

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

    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 5px;}
    .product-card {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
    .sidebar .sidebar-content {background-color: #fafafa;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🛍️ Smart Shopping")
    st.subheader("AI-Powered Product Recommendations")
    st.markdown("Discover personalized product suggestions tailored to your interests!")

    # Load Data
    customers_df, products_df = load_data()
    if customers_df is None or products_df is None:
        return

    # Sidebar
    with st.sidebar:
        st.header("📋 Select Customer")
        customer_names = customers_df['CustomerName'].tolist()
        selected_name = st.selectbox("Choose a Customer", customer_names, key="customer_select")
        
        st.markdown("---")
        st.info("Select a customer to see their profile and personalized recommendations.")

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
                    st.markdown("---")
        else:
            st.warning("No recommendations available at this time.")

if __name__ == "__main__":
    main()
