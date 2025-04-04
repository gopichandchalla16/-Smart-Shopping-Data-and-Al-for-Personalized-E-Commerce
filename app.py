import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load Data (Cached for Speed)
# -----------------------------
@st.cache_data
def load_data():
    customer_df = pd.read_csv("data/customers.csv")
    product_df = pd.read_csv("data/products.csv")
    return customer_df, product_df

# -----------------------------
# Recommend Products Function
# -----------------------------
def recommend_products(customer_profile, product_descriptions, top_n=3):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([customer_profile] + product_descriptions)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    top_indices = cosine_similarities.argsort()[::-1][:top_n]
    return top_indices, cosine_similarities

# -----------------------------
# Streamlit App UI
# -----------------------------
def main():
    st.set_page_config(page_title="Smart Shopping: AI Product Recommender", layout="wide")
    st.title("🛍️ Smart Shopping: AI-Based Product Recommender")
    st.markdown("""
        This AI-powered app recommends personalized products based on customer interests and behavior.
        Select a customer to see what they'd love! 🔍
    """)

    try:
        customer_df, product_df = load_data()
    except FileNotFoundError:
        st.error("🚫 Required data files not found. Make sure `data/customers.csv` and `data/products.csv` exist.")
        return

    with st.sidebar:
        st.header("👤 Select Customer")
        customer_ids = customer_df["customer_id"].tolist()
        selected_id = st.selectbox("Customer ID", customer_ids)

    customer = customer_df[customer_df["customer_id"] == selected_id].iloc[0]
    customer_profile = customer["interests"]
    product_descriptions = product_df["description"].tolist()

    if st.button("🎯 Recommend Products"):
        top_indices, scores = recommend_products(customer_profile, product_descriptions)

        st.subheader("🎁 Top Recommendations")
        for i, idx in enumerate(top_indices):
            product = product_df.iloc[idx]
            with st.container():
                st.markdown(f"### {i+1}. {product['name']}")
                st.markdown(f"- 🏷️ **Category:** {product['category']}")
                st.markdown(f"- 💵 **Price:** ${product['price']}")
                st.markdown(f"- 📝 **Description:** {product['description']}")
                st.markdown("---")

    st.markdown("---")
    st.caption("Created by Gopi Challa | Powered by Streamlit + Scikit-Learn")

if __name__ == "__main__":
    main()
