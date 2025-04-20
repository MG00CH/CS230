# nuclear_explosions_analysis.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# --------------------------
# DATA PREPARATION & CLEANING
# --------------------------

COUNTRY_MAPPING = {
    'USA': 'United States',
    'USSR': 'Soviet Union',
    'UK': 'United Kingdom',
    'FRANCE': 'France',
    'CHINA': 'China',
    'INDIA': 'India'
}


def load_and_clean_data():
    """Load and preprocess nuclear explosions data"""
    df = pd.read_csv("nuclear_explosions.csv")

    # Rename columns to match code expectations
    df.rename(columns={
        'WEAPON SOURCE COUNTRY': 'Country',
        'Data.Purpose': 'Purpose',
        'Location.Cordinates.Latitude': 'Latitude',
        'Location.Cordinates.Longitude': 'Longitude',
        'Data.Yeild.Lower': 'Yield'
    }, inplace=True)

    # Create proper date column from components
    df['Date'] = pd.to_datetime(
        df[['Date.Year', 'Date.Month', 'Date.Day']].rename(columns={
            'Date.Year': 'year',
            'Date.Month': 'month',
            'Date.Day': 'day'
        }),
        errors='coerce'
    )

    # Extract temporal features using pandas
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month_name()
    df['Decade'] = (df['Year'] // 10) * 10

    # Clean country names using mapping
    df['Country'] = df['Country'].apply(
        lambda x: COUNTRY_MAPPING.get(x, x)
    )

    # Handle missing values in Yield
    df['Yield'] = df['Yield'].fillna(0).astype(float)

    return df


def filter_dataset(df, start_date, end_date):
    """Filter data by date range using pandas Timestamps"""
    return df[
        (df['Date'] >= pd.to_datetime(start_date)) &
        (df['Date'] <= pd.to_datetime(end_date))
        ]


# --------------------------
# STREAMLIT UI
# --------------------------

def main():
    st.set_page_config(
        page_title="Nuclear Detonation Explorer",
        page_icon="💥",
        layout="wide"
    )

    st.title("☢️ Nuclear Detonation Analysis (1945-1998)")
    st.sidebar.header("Control Panel")

    df = load_and_clean_data()

    # -------------------
    # INTERACTIVE WIDGETS
    # -------------------

    # Date range selector
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Purpose multi-select
    purposes = st.sidebar.multiselect(
        "Select Detonation Purposes",
        options=df['Purpose'].unique(),
        default=["Wr", "We"]
    )

    # Country radio buttons
    selected_country = st.sidebar.radio(
        "Focus Country",
        options=sorted(df['Country'].unique())
    )

    # -------------------
    # DATA PROCESSING
    # -------------------

    # Multi-condition filtering
    filtered_df = df[
        (df['Purpose'].isin(purposes)) &
        (df['Country'] == selected_country)
        ]

    # Apply date filtering
    if len(selected_dates) == 2:
        filtered_df = filter_dataset(filtered_df, selected_dates[0], selected_dates[1])

    # -------------------
    # VISUALIZATIONS
    # -------------------

    # Temporal Analysis
    st.subheader("Detonation Timeline")
    fig, ax = plt.subplots(figsize=(10, 4))

    time_series = filtered_df.resample('Y', on='Date').size()

    ax.plot(time_series.index.year, time_series.values,
            color='#ff4b4b', marker='o', linestyle='--')
    ax.set_title("Nuclear Detonations Timeline", fontsize=14, pad=15)
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Number of Detonations", fontsize=10)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # PyDeck Map
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

    # -------------------
    # DATA ANALYTICS
    # -------------------

    # Yield categorization
    filtered_df['Yield Category'] = pd.cut(
        filtered_df['Yield'],
        bins=[0, 1, 10, 100, 1000, float('inf')],
        labels=['<1kt', '1-10kt', '10-100kt', '100-1000kt', '>1000kt']
    )

    # Error handling for stats
    try:
        total = len(filtered_df)
        max_yield = filtered_df['Yield'].max()
        avg_yield = filtered_df['Yield'].mean()
        st.metric(f"Total {selected_country} Detonations", total)
        st.metric("Largest Yield", f"{max_yield:,.1f} kt")
        st.metric("Average Yield", f"{avg_yield:,.1f} kt")
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")


if __name__ == "__main__":
    main()