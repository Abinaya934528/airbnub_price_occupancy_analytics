"""
Airbnb Price & Occupancy Analytics Dashboard
A Streamlit application for analyzing Airbnb listings data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sqlite3
import os

# Page configuration
st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detect review score scale (0-5 or 0-100)
def detect_review_scale(df):
    """Detect if review scores are on 0-5 or 0-100 scale."""
    if 'review_scores_rating' not in df.columns:
        return 100  # Default to 100 scale

    max_score = df['review_scores_rating'].max()
    if max_score <= 5:
        return 5
    else:
        return 100

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load the cleaned Airbnb dataset."""
    project_root = Path(__file__).parent.parent
    cleaned_data_path = project_root / 'data' / 'cleaned' / 'listings_cleaned.csv'

    if cleaned_data_path.exists():
        df = pd.read_csv(cleaned_data_path)
        return df
    else:
        return None


@st.cache_data
def load_sql_data():
    """Load data from SQLite database if available."""
    project_root = Path(__file__).parent.parent
    db_path = project_root / 'airbnb.db'

    if db_path.exists():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM listings", conn)
        conn.close()
        return df
    return None


def display_metrics(df):
    """Display key metrics in the dashboard."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Listings",
            value=f"{len(df):,}",
            delta=None
        )

    with col2:
        if 'price' in df.columns:
            st.metric(
                label="Median Nightly Price",
                value=f"${df['price'].median():.2f}",
                delta=None
            )

    with col3:
        if 'price' in df.columns:
            st.metric(
                label="Average Nightly Price",
                value=f"${df['price'].mean():.2f}",
                delta=None
            )

    with col4:
        if 'availability_365' in df.columns:
            st.metric(
                label="Avg Availability (Days/Year)",
                value=f"{df['availability_365'].mean():.1f}",
                delta=None
            )


def home_page(df):
    """Display home page with project overview."""
    st.markdown('<h1 class="main-header">🏠 Airbnb Price & Occupancy Analytics</h1>', unsafe_allow_html=True)

    st.markdown("""
    ## Project Overview

    This portfolio project provides comprehensive data analytics for Airbnb listings to help hosts make
    data-driven decisions about pricing, availability, neighborhood performance, and revenue opportunities.

    ### Project Objectives

    - Analyze pricing patterns across different neighborhoods and property types
    - Understand availability patterns and calendar management
    - Evaluate guest satisfaction through review analysis
    - Provide actionable business insights for hosts
    - Demonstrate Python, SQL, and data visualization skills

    ### Technology Stack

    - **Python**: Data processing and analysis
    - **Pandas & NumPy**: Data manipulation
    - **Plotly**: Interactive visualizations
    - **Streamlit**: Dashboard framework
    - **SQLite**: Database queries
    - **Jupyter Notebook**: Exploratory analysis

    ### Dataset Source

    Public Airbnb listings data from [Inside Airbnb](http://insideairbnb.com/get-the-data.html)

    ### Navigate the Dashboard

    Use the sidebar to explore different analysis sections:
    - **Executive Summary**: Key metrics and overview
    - **Pricing Analysis**: Detailed price patterns with filters
    - **Availability Analysis**: Calendar availability insights
    - **Reviews**: Guest satisfaction analysis
    - **Business Insights**: Strategic recommendations

    """)

    if df is not None:
        st.info("✅ Dataset loaded successfully. Navigate to other sections to explore the data!")
    else:
        st.warning("⚠️ Dataset not found. Please run the data cleaning script first.")

    st.markdown("---")
    st.markdown("### Quick Start")
    st.markdown("""
    1. **Executive Summary** - View key metrics at a glance
    2. **Pricing Analysis** - Filter by neighborhood and room type
    3. **Availability Analysis** - Understand booking patterns
    4. **Reviews** - See neighborhood performance
    5. **Business Insights** - Get strategic recommendations
    """)


def executive_summary(df):
    """Display executive summary page."""
    st.markdown('<h1 class="main-header">📊 Executive Summary</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please download the data and run the data cleaning script first.")
        st.info("""
        **To get started:**
        1. Download listings.csv from Inside Airbnb (http://insideairbnb.com/get-the-data.html)
        2. Place it in the data/raw/ folder
        3. Run: python python/data_cleaning.py
        4. Refresh this dashboard
        """)
        return

    display_metrics(df)

    st.markdown("---")

    # Detect review score scale
    review_scale = detect_review_scale(df)

    # Key Statistics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Room Type Distribution")
        if 'room_type' in df.columns:
            room_counts = df['room_type'].value_counts()
            fig = px.pie(values=room_counts.values, names=room_counts.index,
                         title="Listings by Room Type")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⭐ Review Score Distribution")
        if 'review_scores_rating' in df.columns:
            fig = px.histogram(df, x='review_scores_rating', nbins=20,
                             title=f"Review Score Distribution (0-{review_scale} scale)")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Key Insights
    st.subheader("💡 Key Insights")
    insights = []

    if 'price' in df.columns:
        insights.append(f"• The dataset contains **{len(df):,} listings** with an average price of **${df['price'].mean():.2f}** per night.")

    if 'availability_365' in df.columns:
        highly_available = (df['availability_365'] > 300).sum()
        insights.append(f"• **{highly_available} listings** ({highly_available/len(df)*100:.1f}%) are highly available (>300 days/year).")

    if 'review_scores_rating' in df.columns:
        if review_scale == 5:
            high_rated = (df['review_scores_rating'] >= 4.5).sum()
            insights.append(f"• **{high_rated} listings** ({high_rated/len(df)*100:.1f}%) have excellent ratings (≥4.5/5).")
        else:
            high_rated = (df['review_scores_rating'] >= 90).sum()
            insights.append(f"• **{high_rated} listings** ({high_rated/len(df)*100:.1f}%) have excellent ratings (≥90/100).")

    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)


def pricing_analysis(df):
    """Display pricing analysis page."""
    st.markdown('<h1 class="main-header">💰 Pricing Analysis</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please load the data first.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'neighbourhood_cleansed' in df.columns:
            neighborhoods = ['All'] + sorted(df['neighbourhood_cleansed'].unique().tolist())
            selected_neighborhood = st.selectbox("Filter by Neighborhood", neighborhoods)

    with col2:
        if 'room_type' in df.columns:
            room_types = ['All'] + sorted(df['room_type'].unique().tolist())
            selected_room_type = st.selectbox("Filter by Room Type", room_types)

    with col3:
        if 'price' in df.columns:
            min_price = int(df['price'].min())
            max_price = int(df['price'].max())
            price_range = st.slider("Price Range ($)", min_price, max_price, (min_price, max_price))

    # Apply filters
    filtered_df = df.copy()

    if 'neighbourhood_cleansed' in df.columns and selected_neighborhood != 'All':
        filtered_df = filtered_df[filtered_df['neighbourhood_cleansed'] == selected_neighborhood]

    if 'room_type' in df.columns and selected_room_type != 'All':
        filtered_df = filtered_df[filtered_df['room_type'] == selected_room_type]

    if 'price' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['price'] >= price_range[0]) &
            (filtered_df['price'] <= price_range[1])
        ]

    st.info(f"Showing {len(filtered_df):,} listings after filtering")

    # Price Distribution
    if 'price' in filtered_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Price Distribution")
            fig = px.histogram(filtered_df, x='price', nbins=50,
                             title="Price Distribution",
                             labels={'price': 'Price ($)'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Price Box Plot")
            fig = px.box(filtered_df, y='price',
                        title="Price Distribution (Box Plot)",
                        labels={'price': 'Price ($)'})
            st.plotly_chart(fig, use_container_width=True)

    # Price by Room Type
    if 'room_type' in filtered_df.columns and 'price' in filtered_df.columns:
        st.subheader("Price by Room Type")
        fig = px.box(filtered_df, x='room_type', y='price',
                    title="Price Distribution by Room Type",
                    labels={'room_type': 'Room Type', 'price': 'Price ($)'})
        st.plotly_chart(fig, use_container_width=True)

    # Price by Neighborhood
    neighborhood_col = 'neighbourhood_cleansed' if 'neighbourhood_cleansed' in filtered_df.columns else 'neighbourhood'
    if neighborhood_col in filtered_df.columns and 'price' in filtered_df.columns:
        st.subheader("Price by Neighborhood (Top 20)")
        neighborhood_stats = filtered_df.groupby(neighborhood_col)['price'].agg(['mean', 'median', 'count']).reset_index()
        neighborhood_stats.columns = ['Neighborhood', 'Mean Price', 'Median Price', 'Count']
        neighborhood_stats = neighborhood_stats.sort_values('Median Price', ascending=False).head(20)

        fig = px.bar(neighborhood_stats, x='Neighborhood', y='Median Price',
                    title="Top 20 Neighborhoods by Median Price",
                    labels={'Median Price': 'Median Price ($)'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def availability_analysis(df):
    """Display availability analysis page."""
    st.markdown('<h1 class="main-header">📅 Availability Analysis</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please load the data first.")
        return

    st.warning("""
    ⚠️ **Important Note:** This shows calendar availability, NOT actual occupancy/bookings.
    High availability means the listing is open for booking, not that it's unoccupied.
    """)

    # Availability filter
    if 'availability_365' in df.columns:
        avail_min = int(df['availability_365'].min())
        avail_max = int(df['availability_365'].max())
        availability_filter = st.slider(
            "Filter by Days Available per Year",
            avail_min, avail_max, (avail_min, avail_max)
        )

        filtered_df = df[
            (df['availability_365'] >= availability_filter[0]) &
            (df['availability_365'] <= availability_filter[1])
        ]
    else:
        filtered_df = df

    st.info(f"Showing {len(filtered_df):,} listings")

    # Availability Distribution
    if 'availability_365' in filtered_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Availability Distribution")
            fig = px.histogram(filtered_df, x='availability_365', nbins=50,
                             title="Days Available per Year",
                             labels={'availability_365': 'Days Available'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Availability Categories")
            filtered_df['availability_category'] = pd.cut(
                filtered_df['availability_365'],
                bins=[0, 30, 90, 180, 365],
                labels=['0-30 days', '31-90 days', '91-180 days', '181-365 days']
            )
            avail_counts = filtered_df['availability_category'].value_counts().reset_index()
            avail_counts.columns = ['Availability Range', 'Count']

            fig = px.pie(avail_counts, values='Count', names='Availability Range',
                        title="Distribution by Availability Range")
            st.plotly_chart(fig, use_container_width=True)

    # Price vs Availability
    if 'price' in filtered_df.columns and 'availability_365' in filtered_df.columns:
        st.subheader("Price vs Availability")
        sample_df = filtered_df.sample(min(5000, len(filtered_df))) if len(filtered_df) > 5000 else filtered_df

        fig = px.scatter(sample_df, x='availability_365', y='price',
                        title="Price vs Availability Relationship",
                        labels={'availability_365': 'Days Available', 'price': 'Price ($)'},
                        opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)

        correlation = filtered_df['price'].corr(filtered_df['availability_365'])
        st.info(f"Correlation between Price and Availability: {correlation:.3f}")


def reviews_analysis(df):
    """Display reviews analysis page."""
    st.markdown('<h1 class="main-header">⭐ Reviews Analysis</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please load the data first.")
        return

    # Detect review score scale
    review_scale = detect_review_scale(df)

    # Review score filter
    if 'review_scores_rating' in df.columns:
        score_min = float(df['review_scores_rating'].min())
        score_max = float(df['review_scores_rating'].max())
        score_filter = st.slider(
            f"Filter by Review Score (0-{review_scale} scale)",
            score_min, score_max, (score_min, score_max)
        )

        filtered_df = df[
            (df['review_scores_rating'] >= score_filter[0]) &
            (df['review_scores_rating'] <= score_filter[1])
        ]
    else:
        filtered_df = df

    st.info(f"Showing {len(filtered_df):,} listings")

    # Review Score Distribution
    if 'review_scores_rating' in filtered_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Review Score Distribution")
            fig = px.histogram(filtered_df, x='review_scores_rating', nbins=20,
                             title=f"Review Score Distribution (0-{review_scale} scale)",
                             labels={'review_scores_rating': 'Review Score'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Review Score Categories")
            if review_scale == 5:
                bins = [0, 3.5, 4.0, 4.5, 5.0]
                labels = ['<3.5', '3.5-3.9', '4.0-4.4', '4.5-5.0']
            else:
                bins = [0, 70, 80, 90, 100]
                labels = ['<70', '70-79', '80-89', '90-100']

            filtered_df['score_category'] = pd.cut(
                filtered_df['review_scores_rating'],
                bins=bins,
                labels=labels
            )
            score_counts = filtered_df['score_category'].value_counts().reset_index()
            score_counts.columns = ['Score Range', 'Count']

            fig = px.bar(score_counts, x='Score Range', y='Count',
                        title="Listings by Review Score Range")
            st.plotly_chart(fig, use_container_width=True)

    # Price vs Review Score
    if 'price' in filtered_df.columns and 'review_scores_rating' in filtered_df.columns:
        st.subheader("Price vs Review Score")
        sample_df = filtered_df.sample(min(5000, len(filtered_df))) if len(filtered_df) > 5000 else filtered_df

        fig = px.scatter(sample_df, x='review_scores_rating', y='price',
                        title="Price vs Review Score",
                        labels={'review_scores_rating': f'Review Score (0-{review_scale})', 'price': 'Price ($)'},
                        opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)

        correlation = filtered_df['price'].corr(filtered_df['review_scores_rating'])
        st.info(f"Correlation between Price and Review Score: {correlation:.3f}")

    # Reviews by Neighborhood
    neighborhood_col = 'neighbourhood_cleansed' if 'neighbourhood_cleansed' in filtered_df.columns else 'neighbourhood'
    if neighborhood_col in filtered_df.columns and 'review_scores_rating' in filtered_df.columns:
        st.subheader("Reviews by Neighborhood (Top 20)")
        neighborhood_reviews = filtered_df.groupby(neighborhood_col).agg({
            'review_scores_rating': 'mean',
            'number_of_reviews': 'mean',
            'id': 'count'
        }).reset_index()
        neighborhood_reviews.columns = ['Neighborhood', 'Avg Review Score', 'Avg Num Reviews', 'Count']
        neighborhood_reviews = neighborhood_reviews[neighborhood_reviews['Count'] >= 10]
        neighborhood_reviews = neighborhood_reviews.sort_values('Avg Review Score', ascending=False).head(20)

        fig = px.bar(neighborhood_reviews, x='Neighborhood', y='Avg Review Score',
                    title="Top 20 Neighborhoods by Average Review Score",
                    labels={'Avg Review Score': f'Average Review Score (0-{review_scale})'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def advanced_analytics(df):
    """Display advanced analytics page with additional features."""
    st.markdown('<h1 class="main-header">📈 Advanced Analytics</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please load the data first.")
        return

    # Price per Accommodation Analysis
    if 'price' in df.columns and 'accommodates' in df.columns:
        st.subheader("💰 Price per Person Analysis")
        df_copy = df.copy()
        df_copy['price_per_person'] = df_copy['price'] / df_copy['accommodates']
        df_copy = df_copy[df_copy['accommodates'] > 0]

        col1, col2 = st.columns(2)

        with col1:
            fig = px.scatter(df_copy.sample(min(3000, len(df_copy))), x='accommodates', y='price_per_person',
                           title="Price per Person vs Accommodation Capacity",
                           labels={'accommodates': 'Accommodates', 'price_per_person': 'Price per Person ($)'},
                           opacity=0.5)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            accommodates_stats = df_copy.groupby('accommodates')['price_per_person'].agg(['mean', 'median', 'count']).reset_index()
            accommodates_stats.columns = ['Accommodates', 'Avg Price/Person', 'Median Price/Person', 'Count']
            accommodates_stats = accommodates_stats[accommodates_stats['Count'] >= 10].head(10)

            fig = px.bar(accommodates_stats, x='Accommodates', y='Avg Price/Person',
                       title="Average Price per Person by Capacity",
                       labels={'Avg Price/Person': 'Avg Price per Person ($)'})
            st.plotly_chart(fig, use_container_width=True)

    # Minimum Nights Impact
    if 'price' in df.columns and 'minimum_nights' in df.columns:
        st.subheader("📅 Minimum Nights Impact on Price")
        df_copy = df.copy()
        df_copy['min_nights_category'] = pd.cut(
            df_copy['minimum_nights'],
            bins=[0, 1, 3, 7, 30, 365],
            labels=['1 night', '2-3 nights', '4-7 nights', '8-30 nights', '30+ nights']
        )

        min_nights_stats = df_copy.groupby('min_nights_category')['price'].agg(['mean', 'median', 'count']).reset_index()
        min_nights_stats.columns = ['Min Nights', 'Avg Price', 'Median Price', 'Count']

        fig = px.bar(min_nights_stats, x='Min Nights', y='Avg Price',
                   title="Average Price by Minimum Nights Requirement",
                   labels={'Avg Price': 'Average Price ($)'})
        st.plotly_chart(fig, use_container_width=True)

    # Property Type Analysis
    if 'price' in df.columns and 'property_type' in df.columns:
        st.subheader("🏡 Property Type Analysis")
        property_stats = df.groupby('property_type').agg({
            'price': ['mean', 'median', 'count'],
            'id': 'count'
        }).reset_index()
        property_stats.columns = ['Property Type', 'Mean Price', 'Median Price', 'Price Count', 'Total Count']
        property_stats = property_stats.sort_values('Total Count', ascending=False).head(15)

        fig = px.bar(property_stats, x='Property Type', y='Median Price',
                   title="Median Price by Property Type (Top 15)",
                   labels={'Median Price': 'Median Price ($)'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Instant Bookable Analysis
    if 'price' in df.columns and 'instant_bookable' in df.columns:
        st.subheader("⚡ Instant Bookable Analysis")
        instant_stats = df.groupby('instant_bookable')['price'].agg(['mean', 'median', 'count']).reset_index()
        instant_stats.columns = ['Instant Bookable', 'Avg Price', 'Median Price', 'Count']

        fig = px.bar(instant_stats, x='Instant Bookable', y='Avg Price',
                   title="Average Price by Instant Bookable Status",
                   labels={'Avg Price': 'Average Price ($)'})
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"Instant bookable listings: {instant_stats[instant_stats['Instant Bookable'] == 't']['Count'].values[0] if len(instant_stats[instant_stats['Instant Bookable'] == 't']) > 0 else 0}")


def property_features(df):
    """Display property features analysis."""
    st.markdown('<h1 class="main-header">🛏️ Property Features Analysis</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please load the data first.")
        return

    # Bedrooms and Beds Analysis
    if 'price' in df.columns and 'bedrooms' in df.columns:
        st.subheader("🛏️ Bedrooms vs Price")
        df_copy = df[df['bedrooms'].notna() & (df['bedrooms'] > 0)].copy()

        bedroom_stats = df_copy.groupby('bedrooms')['price'].agg(['mean', 'median', 'count']).reset_index()
        bedroom_stats.columns = ['Bedrooms', 'Avg Price', 'Median Price', 'Count']
        bedroom_stats = bedroom_stats[bedroom_stats['Count'] >= 10].head(10)

        fig = px.bar(bedroom_stats, x='Bedrooms', y='Avg Price',
                   title="Average Price by Number of Bedrooms",
                   labels={'Avg Price': 'Average Price ($)'})
        st.plotly_chart(fig, use_container_width=True)

    # Bathrooms Analysis
    if 'price' in df.columns and 'bathrooms' in df.columns:
        st.subheader("🚿 Bathrooms vs Price")
        df_copy = df[df['bathrooms'].notna() & (df['bathrooms'] > 0)].copy()

        bathroom_stats = df_copy.groupby('bathrooms')['price'].agg(['mean', 'median', 'count']).reset_index()
        bathroom_stats.columns = ['Bathrooms', 'Avg Price', 'Median Price', 'Count']
        bathroom_stats = bathroom_stats[bathroom_stats['Count'] >= 10].head(10]

        fig = px.bar(bathroom_stats, x='Bathrooms', y='Avg Price',
                   title="Average Price by Number of Bathrooms",
                   labels={'Avg Price': 'Average Price ($)'})
        st.plotly_chart(fig, use_container_width=True)

    # Superhost Analysis
    if 'price' in df.columns and 'host_is_superhost' in df.columns:
        st.subheader("⭐ Superhost Status Impact")
        superhost_stats = df.groupby('host_is_superhost').agg({
            'price': ['mean', 'median'],
            'review_scores_rating': 'mean',
            'id': 'count'
        }).reset_index()
        superhost_stats.columns = ['Superhost', 'Avg Price', 'Median Price', 'Avg Review Score', 'Count']

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(superhost_stats, x='Superhost', y='Avg Price',
                       title="Average Price by Superhost Status",
                       labels={'Avg Price': 'Average Price ($)'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(superhost_stats, x='Superhost', y='Avg Review Score',
                       title="Average Review Score by Superhost Status",
                       labels={'Avg Review Score': 'Average Review Score'})
            st.plotly_chart(fig, use_container_width=True)


def business_insights(df):
    """Display business insights and recommendations."""
    st.markdown('<h1 class="main-header">💡 Business Insights</h1>', unsafe_allow_html=True)

    if df is None:
        st.error("Dataset not found. Please load the data first.")
        return

    # Detect review score scale
    review_scale = detect_review_scale(df)

    # Calculate key metrics
    insights = []

    if 'price' in df.columns:
        avg_price = df['price'].mean()
        median_price = df['price'].median()
        insights.append({
            'category': 'Pricing',
            'metric': f'Average Price: ${avg_price:.2f}',
            'recommendation': 'Research neighborhood-specific pricing before setting rates. Consider dynamic pricing based on seasonal demand.'
        })

    if 'room_type' in df.columns:
        most_common = df['room_type'].value_counts().index[0]
        insights.append({
            'category': 'Room Type',
            'metric': f'Most Common: {most_common}',
            'recommendation': 'Understand what travelers prefer in your area and position your listing accordingly.'
        })

    if 'availability_365' in df.columns:
        avg_avail = df['availability_365'].mean()
        insights.append({
            'category': 'Availability',
            'metric': f'Avg Availability: {avg_avail:.1f} days/year',
            'recommendation': 'Keep your calendar updated to attract more bookings. Consider offering discounts for longer stays.'
        })

    if 'review_scores_rating' in df.columns:
        avg_score = df['review_scores_rating'].mean()
        insights.append({
            'category': 'Reviews',
            'metric': f'Avg Review Score: {avg_score:.2f}/{review_scale}',
            'recommendation': 'Maintain high review scores to attract more guests. Respond to guest feedback promptly.'
        })

    # Display insights
    for i, insight in enumerate(insights, 1):
        st.markdown(f"### {i}. {insight['category']}")
        st.metric(insight['metric'], insight['recommendation'])
        st.markdown("---")

    # Additional recommendations
    st.subheader("🎯 Strategic Recommendations")

    recommendations = [
        "1. **Pricing Strategy**: Monitor competitor pricing in your area and adjust rates accordingly.",
        "2. **Property Positioning**: Highlight unique features in your listing with professional photos.",
        "3. **Guest Experience**: Invest in property maintenance and cleanliness to earn positive reviews.",
        "4. **Calendar Management**: Balance availability with personal use preferences for optimal revenue.",
        "5. **Market Research**: Study successful listings in your neighborhood to understand what works.",
        "6. **Instant Booking**: Enable instant booking to increase visibility and booking rate.",
        "7. **Minimum Nights**: Consider flexible minimum night requirements to attract more guests.",
        "8. **Superhost Status**: Aim for superhost status by maintaining high ratings and quick response times."
    ]

    for rec in recommendations:
        st.markdown(f'<div class="insight-box">{rec}</div>', unsafe_allow_html=True)

    # Limitations
    st.subheader("⚠️ Limitations")
    st.warning("""
    - This dataset shows calendar availability, NOT actual occupancy rates.
    - Revenue estimates are based on availability, not confirmed bookings.
    - Seasonal patterns may not be captured without date-level booking data.
    - The analysis reflects a snapshot in time and may not represent current market conditions.
    - Extreme price outliers have been removed using IQR method for analysis reliability.
    """)


def about_project():
    """Display About Project page."""
    st.markdown('<h1 class="main-header">ℹ️ About This Project</h1>', unsafe_allow_html=True)

    st.markdown("""
    ## Project Description

    This is a professional portfolio project demonstrating end-to-end data analytics skills using Python, SQL,
    and interactive visualization. The project analyzes Airbnb listings data to provide actionable insights for hosts.

    ## Technologies Used

    ### Data Processing & Analysis
    - **Python 3.14**: Core programming language
    - **Pandas**: Data manipulation and analysis
    - **NumPy**: Numerical computing
    - **SQLite**: Database queries and analysis

    ### Visualization & Dashboard
    - **Plotly**: Interactive data visualizations
    - **Streamlit**: Web application framework for dashboards

    ### Development Tools
    - **Jupyter Notebook**: Exploratory data analysis
    - **Git**: Version control

    ## Project Components

    1. **Data Cleaning Pipeline** (`python/data_cleaning.py`)
       - Handles missing values and duplicates
       - Validates data quality
       - Removes extreme outliers using IQR method
       - Generates quality reports

    2. **Exploratory Analysis** (`python/airbnb_analysis.ipynb`)
       - Price distribution analysis
       - Neighborhood comparisons
       - Availability patterns
       - Review score correlations

    3. **SQL Analysis** (`sql/`)
       - Data quality checks
       - Pricing analysis with GROUP BY and CTEs
       - Neighborhood performance queries
       - Availability and review analysis

    4. **Interactive Dashboard** (`app/app.py`)
       - Real-time filtering and visualization
       - Multiple analysis views
       - Responsive design for all devices

    5. **Automated Tests** (`tests/`)
       - Data cleaning validation
       - SQL syntax verification
       - End-to-end testing

    ## Dataset

    Public Airbnb listings data from [Inside Airbnb](http://insideairbnb.com/get-the-data.html)

    ## Important Notes

    - **Availability ≠ Occupancy**: This dataset shows calendar availability, not actual bookings
    - **Revenue Estimates**: Any revenue calculations are rough estimates based on availability
    - **Data Snapshot**: Analysis reflects a point in time, not current market conditions
    - **Price Outliers**: Extreme prices have been removed using IQR method for reliability

    ## GitHub Repository

    📁 **Repository**: [Your GitHub Username]/05_Airbnb_Price_Occupancy_Analytics

    *To be added when repository is created*

    ## Contact & Feedback

    This is a portfolio project demonstrating data analytics skills. For questions or feedback,
    please reach out through GitHub.

    ---

    **Built with ❤️ using Python, Streamlit, and Plotly**
    """)


def main():
    """Main application function."""
    # Load data
    df = load_data()

    # Sidebar navigation
    st.sidebar.title("🏠 Airbnb Analytics")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate to:",
        ["Home", "Executive Summary", "Pricing Analysis", "Availability Analysis", "Reviews", "Advanced Analytics", "Property Features", "Business Insights", "About Project"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Info")
    st.sidebar.info("""
    This dashboard analyzes Airbnb listings data to help hosts make data-driven decisions.

    **Note:** Actual occupancy cannot be determined from this dataset. Availability shown is calendar availability, not confirmed bookings.
    """)

    # Display selected page
    if page == "Home":
        home_page(df)
    elif page == "Executive Summary":
        executive_summary(df)
    elif page == "Pricing Analysis":
        pricing_analysis(df)
    elif page == "Availability Analysis":
        availability_analysis(df)
    elif page == "Reviews":
        reviews_analysis(df)
    elif page == "Advanced Analytics":
        advanced_analytics(df)
    elif page == "Property Features":
        property_features(df)
    elif page == "Business Insights":
        business_insights(df)
    elif page == "About Project":
        about_project()


if __name__ == "__main__":
    main()
