import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="Smart Shopping Recommender", layout="wide")

# === Load Data ===
@st.cache_data
def load_data():
    # Load customer and product data
    customer_df = pd.read_csv("data/customers.csv")
    product_df = pd.read_csv("data/products.csv")
    return customer_df, product_df

# === Recommendation System ===
class Recommender:
    def __init__(self, customers, products):
        self.customers = customers
        self.products = products
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Create product embeddings
        self.products["embedding"] = self.products["description"].apply(self.embed_text)

    def embed_text(self, text):
        return self.model.encode(text)

    def recommend(self, customer_id, top_k=5):
        customer = self.customers[self.customers["customer_id"] == customer_id]
        if customer.empty:
            return pd.DataFrame()

        interests = customer["interests"].values[0]
        customer_embedding = self.embed_text(interests)

        product_embeddings = np.vstack(self.products["embedding"].values)
        similarities = cosine_similarity([customer_embedding], product_embeddings)[0]
        self.products["similarity"] = similarities

        top_products = self.products.sort_values(by="similarity", ascending=False).head(top_k)
        return top_products[["product_id", "name", "category", "price", "similarity"]]

# === Main ===
def main():
    st.title("🛒 Smart Shopping: AI-Based Product Recommender")
    st.markdown("This app uses AI to recommend personalized products to customers based on their interests and past behavior.")

    customer_df, product_df = load_data()
    recommender = Recommender(customer_df, product_df)

    st.sidebar.title("User Input")
    customer_ids = customer_df["customer_id"].unique()
    selected_id = st.sidebar.selectbox("Select Customer ID", customer_ids)

    if st.sidebar.button("Get Recommendations"):
        recommendations = recommender.recommend(selected_id)
        if recommendations.empty:
            st.warning("No recommendations found.")
        else:
            st.subheader("Top Product Recommendations")
            st.dataframe(recommendations.reset_index(drop=True))

if __name__ == "__main__":
    main()
