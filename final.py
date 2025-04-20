import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from datetime import date

# --------------------------
# DATA PREPARATION & CLEANING
# --------------------------

# [PY5] Dictionary for country code mapping
COUNTRY_MAPPING = {
    'USA': 'United States',
    'USSR': 'Soviet Union',
    'UK': 'United Kingdom',
    'FR': 'France',
    'CH': 'China',
    'IND': 'India',
    'PAK': 'Pakistan',
    'KP': 'North Korea'
}


# [DA1] Data cleaning function with lambda
def load_and_clean_data():
    """Load and preprocess nuclear explosions data"""
    df = pd.read_csv("nuclear_explosions.csv")

    # Convert dates and handle errors
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Add temporal features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month_name()
    df['Decade'] = (df['Year'] // 10) * 10

    # Clean country names using lambda function
    df['Country'] = df['Country'].apply(
        lambda x: COUNTRY_MAPPING.get(x, 'Unknown')
    )

    # Handle missing values
    df['Yield'] = df['Yield'].fillna(0).astype(float)

    return df


# [PY1] Function with default parameters
def filter_dataset(df, start_date=date(1945, 7, 16), end_date=date(1998, 12, 31)):
    """Filter data by date range with Trinity Test default"""
    return df[
        (df['Date'].dt.date >= start_date) &
        (df['Date'].dt.date <= end_date)
        ]


# [PY2] Multi-return function
def get_country_stats(df, country):
    """Get statistics for a specific country"""
    country_data = df[df['Country'] == country]
    return (
        len(country_data),
        country_data['Yield'].max(),
        country_data['Yield'].mean()
    )


# -------------
# STREAMLIT UI
# -------------

def main():
    st.set_page_config(
        page_title="Nuclear Detonation Explorer",
        layout="wide"
    )

    # [ST4] Custom page design
    st.title("Nuclear Detonation Analysis (1945-1998)")
    st.sidebar.header("Control Panel")

    # Load data
    df = load_and_clean_data()

    # -------------------
    # INTERACTIVE WIDGETS
    # -------------------

    # [ST1] Date range selector
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # [ST2] Purpose multi-select
    purposes = st.sidebar.multiselect(
        "Select Detonation Purposes",
        options=df['Purpose'].unique(),
        default=["WEAPONS", "TESTING"]
    )

    # [ST3] Country radio buttons
    selected_country = st.sidebar.radio(
        "Focus Country",
        options=sorted(df['Country'].unique()))

    # ----------------
    # DATA PROCESSING
    # ----------------

    # [DA5] Multi-condition filtering
    filtered_df = df[
        (df['Purpose'].isin(purposes)) &
        (df['Country'] == selected_country)
        ]

    # [DA4] Date filtering
    if len(selected_dates) == 2:
        filtered_df = filter_dataset(filtered_df, selected_dates[0], selected_dates[1])

    # [DA3] Top yields
    top_yields = filtered_df.nlargest(5, 'Yield')

    # ------------
    # VISUALIZATIONS
    # ------------

    # [VIZ1] Temporal Analysis (Matplotlib)
    st.subheader("Detonation Timeline")
    fig, ax = plt.subplots(figsize=(10, 4))

    time_series = filtered_df.groupby(
        filtered_df['Date'].dt.to_period('Y')).size()

    ax.plot(time_series.index.astype(str), time_series.values,
            color='#ff4b4b', marker='o', linestyle='--')
    ax.set_title("Nuclear Detonations Over Time", fontsize=14, pad=15)
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Number of Detonations", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # [VIZ2] Country Comparison
    st.subheader("Global Comparison")
    col1, col2 = st.columns(2)

    with col1:
    # Bar chart - Detonations by Country
        country_counts = df['Country'].value_counts()
    st.bar_chart(country_counts.head(10))

    with col2:
    # [DA6] Pivot Table
        decade_pivot = pd.pivot_table(
            df,
            values='ID',
            index='Decade',
            columns='Country',
            aggfunc='count'
        ).fillna(0)
    st.dataframe(decade_pivot.style.background_gradient(cmap='Reds'))

    # [MAP] PyDeck Visualization
    st.subheader("Global Detonation Map")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=['Longitude', 'Latitude'],
        get_radius=50000,
        get_fill_color=[255, 75, 75, 180],
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=pdk.ViewState(
            latitude=30,
            longitude=0,
            zoom=1,
            pitch=40
        ),
        layers=[layer],
        tooltip={
            "html": """
            <b>Country:</b> {Country}<br>
            <b>Date:</b> {Date}<br>
            <b>Yield:</b> {Yield} kt
            """
        }
    ))

    # ----------------
    # DATA ANALYTICS
    # ----------------

    # [DA9] Yield categorization
    filtered_df['Yield Category'] = pd.cut(
        filtered_df['Yield'],
        bins=[0, 1, 10, 100, 1000, float('inf')],
        labels=['<1kt', '1-10kt', '10-100kt', '100-1000kt', '>1000kt']
    )

    # [PY4] List comprehension
    yield_categories = [cat for cat in filtered_df['Yield Category'].unique() if pd.notnull(cat)]

    # [PY3] Error handling
    try:
        total, max_yield, avg_yield = get_country_stats(filtered_df, selected_country)
        st.metric(f"Total {selected_country} Detonations", total)
        st.metric("Largest Yield", f"{max_yield:,.1f} kt")
        st.metric("Average Yield", f"{avg_yield:,.1f} kt")
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")

    # -----------
    # FOOTNOTES
    # -----------
    st.markdown("---")
    st.caption("Data Source: Nuclear Explosions 1945-1998 Dataset from Kaggle")


if __name__ == "__main__":
    main()