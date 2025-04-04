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
    interests = customer['interests'].split('|')
    recommendations = products_df[products_df['category'].isin(interests)]
    
    if recommendations.empty:
        recommendations = products_df.sample(3)
    
    return recommendations

# -------------------------------
# Streamlit UI
# -------------------------------

def main():
    st.set_page_config(page_title="Smart Shopping: AI-Based Product Recommender", layout="wide")
    st.title("🛒 Smart Shopping: AI-Based Product Recommender")
    st.markdown("This AI-powered app recommends personalized products based on customer interests and behavior. Select a customer to see what they'd love! 🔍")
    
    try:
        customers_df, products_df = load_data()
    except FileNotFoundError:
        st.error("🚫 Required data files not found. Make sure 'customers.csv' and 'products.csv' are in the same folder as this app.py.")
        return

    customer_names = customers_df['customer_name'].tolist()
    selected_name = st.selectbox("Choose a Customer", customer_names)

    selected_customer = customers_df[customers_df['customer_name'] == selected_name].iloc[0]
    st.subheader(f"👤 Customer Profile: {selected_customer['customer_name']}")
    st.write(f"**Age:** {selected_customer['age']}  \n**Gender:** {selected_customer['gender']}  \n**Interests:** {selected_customer['interests']}")

    st.subheader("🎯 Recommended Products")
    recommended = recommend_products(selected_customer, products_df)

    for _, product in recommended.iterrows():
        st.markdown(f"### {product['product_name']}")
        st.write(f"**Category:** {product['category']}  \n**Price:** ${product['price']}  \n**Description:** {product['description']}")
        st.markdown("---")

if __name__ == "__main__":
    main()
