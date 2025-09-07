import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date, timedelta

# --- Configuration for Simulated NYC Road Traffic Data ---
LAT_MIN, LAT_MAX = 40.70, 40.80
LON_MIN, LON_MAX = -74.02, -73.93

# --- Functions for Simulated Road Traffic Analytics ---

def generate_simulated_traffic_data():
    """Generates a DataFrame of random traffic data for a small area in NYC."""
    lat_vals = np.linspace(LAT_MIN, LAT_MAX, 15)
    lon_vals = np.linspace(LON_MIN, LON_MAX, 15)
    records = []
    for lat in lat_vals:
        for lon in lon_vals:
            records.append({
                "lat": lat,
                "lon": lon,
                "currentSpeed": np.random.uniform(10, 60),
                "freeFlowSpeed": np.random.uniform(40, 70),
                "jamFactor": np.random.uniform(0, 10),
                "confidence": np.random.uniform(0.5, 1)
            })
    return pd.DataFrame(records)

def display_road_traffic_analytics():
    """Displays maps and charts for the simulated road traffic data."""
    st.markdown("## Simulated NYC Road Traffic Analytics")
    st.info("This section displays randomly generated traffic data for a sample area in New York City.")
    
    df = generate_simulated_traffic_data()
    st.dataframe(df.head(10))

    # --- Traffic Jam Heatmap ---
    st.markdown("### Traffic Jam Factor Heatmap")
    fig_map = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="jamFactor",
        size="jamFactor",
        size_max=15,
        color_continuous_scale=px.colors.sequential.OrRd,
        hover_name="currentSpeed",
        hover_data={"currentSpeed": True, "freeFlowSpeed": True, "jamFactor": True},
        zoom=12,
        height=500,
        title="Higher 'Jam Factor' indicates worse traffic conditions",
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # --- Speed Comparison Line Chart ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Traffic Speed Analysis")
        fig_speed = px.line(
            df.sort_values(by="lat"),
            x="lat",
            y=["currentSpeed", "freeFlowSpeed"],
            title="Current Speed vs Free Flow Speed",
            labels={"value": "Speed (km/h)", "lat": "Latitude"}
        )
        st.plotly_chart(fig_speed, use_container_width=True)

    # --- Jam Factor Distribution ---
    with col2:
        st.markdown("### Jam Factor Distribution")
        fig_jam = px.histogram(
            df,
            x="jamFactor",
            nbins=20,
            title="Distribution of Traffic Jam Factor",
            labels={"jamFactor": "Jam Factor"}
        )
        st.plotly_chart(fig_jam, use_container_width=True)

    # --- Aggregate Metrics ---
    avg_speed = df["currentSpeed"].mean()
    avg_free_speed = df["freeFlowSpeed"].mean()
    avg_jam = df["jamFactor"].mean()
    max_jam = df["jamFactor"].max()

    st.markdown("### Aggregate Traffic Insights")
    st.markdown(f"- Average Current Speed: **{avg_speed:.2f} km/h**")
    st.markdown(f"- Average Free Flow Speed: **{avg_free_speed:.2f} km/h**")
    st.markdown(f"- Average Jam Factor: **{avg_jam:.2f}**")
    st.markdown(f"- Maximum Jam Factor: **{max_jam:.2f}**")


# --- Functions for Wikipedia Article Traffic Analytics ---

def fetch_wikipedia_pageviews(article, start_date, end_date):
    """
    Fetches daily pageview data for a Wikipedia article using the Wikimedia API.
    This API is free and requires no authentication.
    """
    headers = {
        'User-Agent': 'StreamlitApp/1.0 (https://your-app-url.com; your-email@example.com)'
    }
    # Format dates for the API URL
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    # Replace spaces with underscores for the article title
    article_formatted = article.replace(' ', '_')
    
    url = (
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{article_formatted}/daily/{start_str}/{end_str}"
    )
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            st.error(f"API Error 404: Not Found. This often means the article '{article}' does not exist on English Wikipedia. Please check the spelling and try again.")
            return None
        response.raise_for_status()
        data = response.json()
        
        if 'items' in data:
            df = pd.DataFrame(data['items'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d00')
            df = df.rename(columns={'views': 'pageviews', 'timestamp': 'date'})
            return df[['date', 'pageviews']]
        else:
            return None
            
    except requests.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred while processing data: {e}")
        return None

def display_wikipedia_analytics():
    """Displays UI for fetching and showing Wikipedia pageview data."""
    st.markdown("## Wikipedia Article Traffic Analytics")
    st.info("Analyze the daily pageviews (traffic) for any English Wikipedia article. This uses a free, public API from the Wikimedia Foundation.")

    # --- User Inputs ---
    article = st.text_input("Enter a Wikipedia Article Title (e.g., 'Artificial intelligence')", "Streamlit")
    
    today = date.today()
    last_month = today - timedelta(days=30)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", last_month, max_date=today)
    with col2:
        end_date = st.date_input("End Date", today, max_date=today)

    if st.button("Get Article Analytics"):
        if not article:
            st.warning("Please enter an article title.")
            return
        if start_date > end_date:
            st.warning("Start date cannot be after the end date.")
            return

        with st.spinner(f"Fetching pageview data for '{article}'..."):
            views_df = fetch_wikipedia_pageviews(article, start_date, end_date)

        if views_df is not None and not views_df.empty:
            st.success(f"Successfully retrieved data for '{article}'!")
            
            # --- Key Metrics ---
            total_views = views_df['pageviews'].sum()
            avg_views = views_df['pageviews'].mean()
            max_views_row = views_df.loc[views_df['pageviews'].idxmax()]
            
            st.markdown("### Key Metrics")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Pageviews", f"{total_views:,.0f}")
            kpi2.metric("Average Daily Views", f"{avg_views:,.0f}")
            kpi3.metric("Peak Day Views", f"{max_views_row['pageviews']:,.0f}", f"{max_views_row['date'].strftime('%b %d, %Y')}")

            # --- Pageviews Line Chart ---
            st.markdown("### Daily Pageviews Over Time")
            fig = px.line(
                views_df,
                x='date',
                y='pageviews',
                title=f"Daily Traffic for '{article}'",
                labels={'pageviews': 'Number of Pageviews', 'date': 'Date'}
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            # --- Raw Data ---
            with st.expander("Show Raw Data"):
                st.dataframe(views_df)
        else:
            st.error(f"Could not retrieve or process data for '{article}'. Please check the article title and try again.")

# --- Main App ---

st.set_page_config(page_title="Analytics Dashboard", layout="wide")
st.title("Traffic & Website Analytics Dashboard")

st.sidebar.header("Choose Analytics Type")
option = st.sidebar.radio(
    "Select a view:",
    ["Simulated NYC Road Traffic", "Wikipedia Article Traffic"]
)

if option == "Simulated NYC Road Traffic":
    display_road_traffic_analytics()
else:
    display_wikipedia_analytics()
