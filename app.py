import streamlit as st
import pandas as pd

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    customers = pd.read_csv("customers.csv")
    products = pd.read_csv("products.csv")
    return customers, products

# -------------------------------
# Recommend Products
# -------------------------------
def recommend_products(customer, products_df):
    interests = customer['Interests'].split('|')
    recommendations = products_df[products_df['Category'].isin(interests)]

    if recommendations.empty:
        recommendations = products_df.sample(3)
    return recommendations

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.set_page_config(page_title="Smart Shopping: AI-Based Product Recommender", layout="wide")
    st.title("🛍️ Smart Shopping: AI-Based Product Recommender")
    st.markdown("""
        Welcome to **Smart Shopping** – an AI-powered app that delivers personalized product suggestions 
        based on customer profiles and interests.  
        Select a customer from the dropdown below to explore what products best match their preferences. 🔎
    """)

    try:
        customers_df, products_df = load_data()
    except FileNotFoundError:
        st.error("🚫 Required data files not found. Make sure 'customers.csv' and 'products.csv' are in the same folder as this app.py.")
        return

    st.sidebar.header("📋 Choose a Customer")
    customer_names = customers_df['CustomerName'].tolist()
    selected_name = st.sidebar.selectbox("Select Customer", customer_names)

    selected_customer = customers_df[customers_df['CustomerName'] == selected_name].iloc[0]

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("👤 Customer Profile")
        st.markdown(f"""
        **Name:** {selected_customer['CustomerName']}  
        **Age:** {selected_customer['Age']}  
        **Gender:** {selected_customer['Gender']}  
        **Interests:** {selected_customer['Interests'].replace('|', ', ')}
        """)

    with col2:
        st.subheader("🎯 Personalized Product Recommendations")
        recommended = recommend_products(selected_customer, products_df)

        for _, product in recommended.iterrows():
            st.markdown(f"""
            #### 🛒 {product['ProductName']}
            - **Category:** {product['Category']}
            - **Price:** ${product['Price']}
            - **Description:** {product['Description']}
            ---
            """)

if __name__ == "__main__":
    main()
