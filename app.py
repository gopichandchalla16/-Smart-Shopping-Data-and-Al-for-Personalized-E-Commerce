import streamlit as st
import pandas as pd
import ast
import plotly.express as px
from io import StringIO

# -------------------------------
# Load Data with Fallback
# -------------------------------
@st.cache_data
def load_data():
    try:
        # Customer Data (from provided document)
        customers_data = """
Customer_ID,Age,Gender,Location,Browsing_History,Purchase_History,Customer_Segment,Avg_Order_Value,Holiday,Season
C1000,28,Female,Chennai,"['Books', 'Fashion']","['Biography', 'Jeans']",New Visitor,4806.99,No,Winter
C1001,27,Male,Delhi,"['Books', 'Fitness', 'Fashion']","['Biography', 'Resistance Bands', 'T-shirt']",Occasional Shopper,795.03,Yes,Autumn
C1002,34,Other,Chennai,['Electronics'],['Smartphone'],Occasional Shopper,1742.45,Yes,Summer
"""  # Truncated for brevity; replace with full data or load from file
        customers = pd.read_csv(StringIO(customers_data))

        # Product Data (from previous interaction)
        products_data = """
Product_ID,Category,Subcategory,Price,Brand,Average_Rating_of_Similar_Products,Product_Rating,Customer_Review_Sentiment_Score,Holiday,Season,Geographical_Location,Similar_Product_List,Probability_of_Recommendation
P2000,Fashion,Jeans,1713,Brand B,4.2,2.3,0.26,No,Summer,Canada,"['Jeans', 'Shoes']",0.91
P2001,Beauty,Lipstick,1232,Brand C,4.7,2.1,0.21,Yes,Winter,India,"['Moisturizer', 'Lipstick', 'Lipstick']",0.26
P2002,Electronics,Laptop,4833,Brand B,3.5,2.4,0.74,Yes,Spring,Canada,"['Headphones', 'Headphones', 'Smartphone']",0.6
"""  # Truncated; replace with full data or load from file
        products = pd.read_csv(StringIO(products_data))

        # Convert string lists to actual lists
        customers['Browsing_History'] = customers['Browsing_History'].apply(ast.literal_eval)
        customers['Purchase_History'] = customers['Purchase_History'].apply(ast.literal_eval)
        products['Similar_Product_List'] = products['Similar_Product_List'].apply(ast.literal_eval)

        return customers, products
    except Exception as e:
        st.error(f"🚫 Data loading error: {str(e)}. Using sample data.")
        customers_data = {
            'Customer_ID': ['C1000', 'C1001'],
            'Age': [28, 27],
            'Gender': ['Female', 'Male'],
            'Location': ['Chennai', 'Delhi'],
            'Browsing_History': [['Books', 'Fashion'], ['Books', 'Fitness']],
            'Purchase_History': [['Biography', 'Jeans'], ['Biography', 'Resistance Bands']],
            'Customer_Segment': ['New Visitor', 'Occasional Shopper'],
            'Avg_Order_Value': [4806.99, 795.03],
            'Holiday': ['No', 'Yes'],
            'Season': ['Winter', 'Autumn']
        }
        products_data = {
            'Product_ID': ['P2000', 'P2001'],
            'Category': ['Fashion', 'Beauty'],
            'Subcategory': ['Jeans', 'Lipstick'],
            'Price': [1713, 1232],
            'Brand': ['Brand B', 'Brand C'],
            'Probability_of_Recommendation': [0.91, 0.26],
            'Holiday': ['No', 'Yes'],
            'Season': ['Summer', 'Winter']
        }
        return pd.DataFrame(customers_data), pd.DataFrame(products_data)

# -------------------------------
# Recommend Products
# -------------------------------
def recommend_products(customer, products_df):
    interests = set(customer['Browsing_History'] + customer['Purchase_History'])
    recommendations = products_df[
        (products_df['Category'].str.lower().isin([i.lower() for i in interests])) |
        (products_df['Subcategory'].isin(customer['Purchase_History']))
    ].sort_values('Probability_of_Recommendation', ascending=False)
    
    if len(recommendations) < 3:
        additional = products_df.sample(3 - len(recommendations))
        recommendations = pd.concat([recommendations, additional])
    return recommendations.head(3)

# -------------------------------
# Visualizations
# -------------------------------
def plot_segment_distribution(customers_df):
    fig = px.pie(customers_df, names='Customer_Segment', title='Customer Segment Distribution',
                 color_discrete_sequence=px.colors.sequential.RdBu)
    return fig

def plot_category_interests(customers_df):
    categories = customers_df['Browsing_History'].explode().value_counts()
    fig = px.bar(x=categories.index, y=categories.values, title='Top Product Categories by Interest',
                 labels={'x': 'Category', 'y': 'Count'}, color=categories.index)
    return fig

def plot_spending_analysis(customers_df):
    fig = px.histogram(customers_df, x='Avg_Order_Value', nbins=20, title='Average Order Value Distribution',
                       color_discrete_sequence=['#00CC96'])
    return fig

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.set_page_config(page_title="Smart Shopping Hub", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

    # Custom CSS
    st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px;}
    .product-card {background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .sidebar .sidebar-content {background-color: #ffffff; padding: 15px; border-radius: 10px;}
    .tab {font-size: 18px; font-weight: bold; padding: 10px;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🛍️ Smart Shopping Hub")
    st.subheader("Your AI-Powered Shopping Companion")
    st.markdown("Explore personalized recommendations, insights, and more!")

    # Load Data
    customers_df, products_df = load_data()

    # Sidebar
    with st.sidebar:
        st.header("🔍 Filters")
        customer_ids = customers_df['Customer_ID'].tolist()
        selected_id = st.selectbox("Select Customer", customer_ids, key="customer_select")
        location_filter = st.multiselect("Location", customers_df['Location'].unique(), default=customers_df['Location'].unique())
        season_filter = st.multiselect("Season", customers_df['Season'].unique(), default=customers_df['Season'].unique())
        st.markdown("---")
        st.info("Customize your experience with filters and explore insights!")

    # Filter Data
    filtered_customers = customers_df[
        (customers_df['Location'].isin(location_filter)) &
        (customers_df['Season'].isin(season_filter))
    ]
    selected_customer = filtered_customers[filtered_customers['Customer_ID'] == selected_id].iloc[0]

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Recommendations", "Profile", "Insights"])

    with tab1:
        st.subheader("🎯 Personalized Recommendations")
        recommended = recommend_products(selected_customer, products_df)
        for _, product in recommended.iterrows():
            holiday_tag = "🎄 Holiday Special" if product['Holiday'] == 'Yes' else ""
            st.markdown(f"""
            <div class="product-card">
                <h4>🛒 {product['Subcategory']} (ID: {product['Product_ID']}) {holiday_tag}</h4>
                <p><b>Category:</b> {product['Category']}</p>
                <p><b>Price:</b> ${product['Price']}</p>
                <p><b>Brand:</b> {product['Brand']}</p>
                <p><b>Recommendation Score:</b> {product['Probability_of_Recommendation']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Download Recommendations"):
            csv = recommended.to_csv(index=False)
            st.download_button("Download CSV", csv, "recommendations.csv", "text/csv")

    with tab2:
        st.subheader("👤 Customer Profile")
        with st.expander("View Details", expanded=True):
            st.markdown(f"""
            **Customer ID:** {selected_customer['Customer_ID']}  
            **Age:** {selected_customer['Age']}  
            **Gender:** {selected_customer['Gender']}  
            **Location:** {selected_customer['Location']}  
            **Interests:** {', '.join(selected_customer['Browsing_History'])}  
            **Past Purchases:** {', '.join(selected_customer['Purchase_History'])}  
            **Segment:** {selected_customer['Customer_Segment']}  
            **Avg Order Value:** ${selected_customer['Avg_Order_Value']:.2f}
            """)

    with tab3:
        st.subheader("📊 Shopping Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_segment_distribution(filtered_customers), use_container_width=True)
            st.plotly_chart(plot_spending_analysis(filtered_customers), use_container_width=True)
        with col2:
            st.plotly_chart(plot_category_interests(filtered_customers), use_container_width=True)
        st.markdown("**Insight:** Tailored recommendations improve based on your segment and spending habits!")

if __name__ == "__main__":
    main()
