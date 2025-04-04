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
        # Customer Data
        customers_data = """
Customer_ID,Age,Gender,Location,Browsing_History,Purchase_History,Customer_Segment,Avg_Order_Value,Holiday,Season
C1000,28,Female,Chennai,"['Books', 'Fashion']","['Biography', 'Jeans']",New Visitor,4806.99,No,Winter
C1001,27,Male,Delhi,"['Books', 'Fitness', 'Fashion']","['Biography', 'Resistance Bands', 'T-shirt']",Occasional Shopper,795.03,Yes,Autumn
C1002,34,Other,Chennai,['Electronics'],['Smartphone'],Occasional Shopper,1742.45,Yes,Summer
"""
        customers = pd.read_csv(StringIO(customers_data))

        # Product Data
        products_data = """
Product_ID,Category,Subcategory,Price,Brand,Average_Rating_of_Similar_Products,Product_Rating,Customer_Review_Sentiment_Score,Holiday,Season,Geographical_Location,Similar_Product_List,Probability_of_Recommendation
P2000,Fashion,Jeans,1713,Brand B,4.2,2.3,0.26,No,Summer,Canada,"['Jeans', 'Shoes']",0.91
P2001,Beauty,Lipstick,1232,Brand C,4.7,2.1,0.21,Yes,Winter,India,"['Moisturizer', 'Lipstick', 'Lipstick']",0.26
P2002,Electronics,Laptop,4833,Brand B,3.5,2.4,0.74,Yes,Spring,Canada,"['Headphones', 'Headphones', 'Smartphone']",0.6
"""
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
            'Season': ['Summer', 'Winter'],
            'Average_Rating_of_Similar_Products': [4.2, 4.7],
            'Customer_Review_Sentiment_Score': [0.26, 0.21]
        }
        return pd.DataFrame(customers_data), pd.DataFrame(products_data)

# -------------------------------
# Recommend Products
# -------------------------------
def recommend_products(customer, products_df, min_price, max_price):
    interests = set(customer['Browsing_History'] + customer['Purchase_History'])
    recommendations = products_df[
        (products_df['Category'].str.lower().isin([i.lower() for i in interests])) |
        (products_df['Subcategory'].isin(customer['Purchase_History'])) &
        (products_df['Price'].between(min_price, max_price))
    ].sort_values('Probability_of_Recommendation', ascending=False)
    
    if len(recommendations) < 3:
        additional = products_df[products_df['Price'].between(min_price, max_price)].sample(min(3 - len(recommendations), len(products_df)))
        recommendations = pd.concat([recommendations, additional])
    return recommendations.head(3)

# -------------------------------
# Sentiment Insight
# -------------------------------
def get_sentiment_insight(score):
    if score >= 0.7:
        return "Highly Positive Reviews 😊"
    elif score >= 0.4:
        return "Generally Positive Reviews 🙂"
    else:
        return "Mixed or Negative Reviews 😐"

# -------------------------------
# Visualizations
# -------------------------------
def plot_segment_distribution(customers_df):
    if customers_df.empty:
        return None
    fig = px.pie(customers_df, names='Customer_Segment', title='Customer Segment Distribution')
    return fig

def plot_category_interests(customers_df):
    if customers_df.empty:
        return None
    categories = customers_df['Browsing_History'].explode().value_counts()
    if categories.empty:
        return None
    fig = px.bar(x=categories.index, y=categories.values, title='Top Product Categories by Interest',
                 labels={'x': 'Category', 'y': 'Count'})
    return fig

def plot_spending_analysis(customers_df):
    if customers_df.empty:
        return None
    fig = px.histogram(customers_df, x='Avg_Order_Value', nbins=20, title='Average Order Value Distribution')
    return fig

def plot_customer_spending(customer, customers_df):
    if customers_df.empty:
        return None
    fig = px.box(customers_df, y='Avg_Order_Value', points="all", title=f"Your Spending vs Others",
                 hover_data=['Customer_ID'])
    fig.add_hline(y=customer['Avg_Order_Value'], line_dash="dash", annotation_text="Your Avg Spending")
    return fig

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.set_page_config(page_title="Smart Shopping Hub", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

    # Custom CSS with Black and White Theme
    st.markdown("""
    <style>
    .main {background-color: #ffffff;} /* White background */
    .stButton>button {background-color: #000000; color: #ffffff; border-radius: 8px; padding: 10px;} /* Black button, white text */
    .product-card {background-color: #ffffff; padding: 20px; border: 1px solid #000000; border-radius: 12px; margin-bottom: 20px;} /* White card, black border */
    .sidebar .sidebar-content {background-color: #ffffff; padding: 15px; border: 1px solid #000000; border-radius: 10px;} /* White sidebar, black border */
    .tab {font-size: 18px; font-weight: bold; padding: 10px; color: #000000;} /* Black tabs */
    h1, h2, h3, h4, p, span {color: #000000 !important;} /* All text black */
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
        min_price, max_price = st.slider("Price Range ($)", 
                                         int(products_df['Price'].min()), 
                                         int(products_df['Price'].max()), 
                                         (int(products_df['Price'].min()), int(products_df['Price'].max())))
        st.markdown("---")
        st.info("Customize your experience with filters and explore insights!")

    # Filter Data with Fallback
    filtered_customers = customers_df[
        (customers_df['Location'].isin(location_filter)) &
        (customers_df['Season'].isin(season_filter))
    ]
    
    selected_customer_df = filtered_customers[filtered_customers['Customer_ID'] == selected_id]
    if selected_customer_df.empty:
        st.warning(f"⚠️ Customer {selected_id} not found in filtered data. Showing unfiltered customer data.")
        selected_customer_df = customers_df[customers_df['Customer_ID'] == selected_id]
        if selected_customer_df.empty:
            st.error(f"🚫 Customer {selected_id} not found in the dataset. Please select a valid customer.")
            return
    selected_customer = selected_customer_df.iloc[0]

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Recommendations", "Profile", "Insights"])

    with tab1:
        st.subheader("🎯 Personalized Recommendations")
        recommended = recommend_products(selected_customer, products_df, min_price, max_price)
        for _, product in recommended.iterrows():
            holiday_tag = '🎄 Holiday Special' if product['Holiday'] == 'Yes' else ""
            price_diff = product['Price'] - selected_customer['Avg_Order_Value']
            price_comparison = f"{'Above' if price_diff > 0 else 'Below'} your avg spending by ${abs(price_diff):.2f}"
            st.markdown(f"""
            <div class="product-card">
                <h4>🛒 {product['Subcategory']} (ID: {product['Product_ID']}) {holiday_tag}</h4>
                <p>Category: {product['Category']}</p>
                <p>Price: ${product['Price']} ({price_comparison})</p>
                <p>Brand: {product['Brand']}</p>
                <p>Recommendation Score: {product['Probability_of_Recommendation']:.2f}</p>
                <p>Avg Rating of Similar Products: {product['Average_Rating_of_Similar_Products']}/5</p>
                <p>Sentiment Score: {product['Customer_Review_Sentiment_Score']:.2f} ({get_sentiment_insight(product['Customer_Review_Sentiment_Score'])})</p>
                <p>Season: {product['Season']}</p>
                <p>Location: {product['Geographical_Location']}</p>
                <p>Similar Products: {', '.join(product['Similar_Product_List'])}</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Download Recommendations"):
            csv = recommended.to_csv(index=False)
            st.download_button("Download CSV", csv, "recommendations.csv", "text/csv")

    with tab2:
        st.subheader("👤 Customer Profile")
        with st.expander("View Details", expanded=True):
            st.markdown(f"""
            <p>Customer ID: {selected_customer['Customer_ID']}</p>
            <p>Age: {selected_customer['Age']}</p>
            <p>Gender: {selected_customer['Gender']}</p>
            <p>Location: {selected_customer['Location']}</p>
            <p>Interests: {', '.join(selected_customer['Browsing_History'])}</p>
            <p>Past Purchases: {', '.join(selected_customer['Purchase_History'])}</p>
            <p>Segment: {selected_customer['Customer_Segment']}</p>
            <p>Avg Order Value: ${selected_customer['Avg_Order_Value']:.2f}</p>
            <p>Holiday Shopper: {selected_customer['Holiday']}</p>
            <p>Season: {selected_customer['Season']}</p>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("📊 Shopping Insights")
        col1, col2 = st.columns(2)
        with col1:
            segment_fig = plot_segment_distribution(filtered_customers)
            if segment_fig:
                st.plotly_chart(segment_fig, use_container_width=True)
            else:
                st.info("No data available for segment distribution with current filters.")
            spending_fig = plot_spending_analysis(filtered_customers)
            if spending_fig:
                st.plotly_chart(spending_fig, use_container_width=True)
            else:
                st.info("No data available for spending analysis with current filters.")
        with col2:
            category_fig = plot_category_interests(filtered_customers)
            if category_fig:
                st.plotly_chart(category_fig, use_container_width=True)
            else:
                st.info("No data available for category interests with current filters.")
            customer_spending_fig = plot_customer_spending(selected_customer, customers_df)
            if customer_spending_fig:
                st.plotly_chart(customer_spending_fig, use_container_width=True)
            else:
                st.info("No data available for customer spending comparison.")
        st.markdown("""
        **Insight:** Your recommendations are tailored based on your interests, past purchases, and shopping behavior. 
        Check the sentiment scores and ratings to make informed decisions!
        """)

if __name__ == "__main__":
    main()
