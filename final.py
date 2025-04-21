"""
CS230 Final Project
April 20, 2025
Matthew Gooch

This program will analyze and chart out information from a dataset using streamlit, pandas, pyplot, and pydeck
"""

# Import all tools
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


# Data Dictionaries

COUNTRIES = {
    'USA': 'United States',
    'USSR': 'Soviet Union',
    'UK': 'United Kingdom',
    'FRANCE': 'France',
    'CHINA': 'China',
    'INDIA': 'India'
}

PURPOSE_DICT = {
    'Combat': 'Combat',
    'Wr': 'Weapons development',
    'We': 'Weapons Evaluation',
    'Fms': 'Soviet Phenomenon Study',
    'Me': 'Military Exercise',
    'Pne': 'Peaceful Nuclear Explosion',
    'Sam': 'Soviet Emergency Test',
    'Se': 'Safety Testing',
    'Transp': 'Transportation purposes'
}

TYPE_DICT = {
    'Atmosph': 'Atmospheric',
    'Airdrop': 'Airplane Deployed',
    'Tower': 'Constructed Tower',
    'Surface': 'Ground Level',
    'UW': 'Underwater',
    'Shaft': 'Underground Shaft',
    'Tunnel': 'Underground Tunnel',
    'Barge': 'Barge Platform',
    'Balloon': 'Aerial Balloon',
    'Rocket': 'Missile Launch',
    'Ship': 'Naval Vessel',
    'Crater': 'Surface Crater'
}


# Data Processing

def load_and_clean_data():
    df = pd.read_csv("nuclear_explosions.csv")

    # Column renaming
    df = df.rename(columns={
        'WEAPON SOURCE COUNTRY': 'Country',
        'Data.Purpose': 'Purpose',
        'Data.Type': 'Type',
        'Location.Cordinates.Latitude': 'Latitude',
        'Location.Cordinates.Longitude': 'Longitude',
        'Data.Yeild.Lower': 'Yield'
    })

    # Date handling
    df['Date'] = pd.to_datetime(
        df[['Date.Year', 'Date.Month', 'Date.Day']].rename(columns={
            'Date.Year': 'year',
            'Date.Month': 'month',
            'Date.Day': 'day'
        })
    )
    df['Year'] = df['Date'].dt.year
    df['Decade'] = (df['Year'] // 10) * 10

    # Data enrichment
    df['Country'] = df['Country'].map(COUNTRIES).fillna('Other')
    df['Purpose_Label'] = df['Purpose'].map(PURPOSE_DICT).fillna('Other')
    df['Type_Label'] = df['Type'].map(TYPE_DICT).fillna('Other')

    return df


# Main function

def main():
    #Streamlit Configuration
    st.set_page_config(
        page_title="Nuclear Detonation Explorer",
        layout="wide"
    )

    st.title("Nuclear Detonation Analysis (1945-1998)")
    df = load_and_clean_data()

    with st.sidebar:
        st.header("Control Panel")

        # Date Range
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        selected_dates = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        # Country Selection
        st.subheader("Country Selection")
        all_countries = sorted(df['Country'].unique())

        # Select All functionality
        if st.button('Select All Countries'):
            st.session_state.selected_countries = all_countries

        selected_countries = st.multiselect(
            "Choose Countries",
            options=all_countries,
            default=all_countries,
            key='selected_countries'
        )

        # Purpose Selection
        st.subheader("Detonation Purpose")
        purpose_options = sorted(df['Purpose_Label'].unique())
        selected_purposes = st.multiselect(
            "Select Purposes",
            options=purpose_options,
            default=purpose_options
        )

        # Type Selection
        st.subheader("Detonation Type")
        type_options = sorted(df['Type_Label'].unique())
        selected_types = st.multiselect(
            "Select Types",
            options=type_options,
            default=type_options
        )

    # -------------------
    # DATA FILTERING
    # -------------------
    filtered_df = df[
        (df['Country'].isin(selected_countries)) &
        (df['Purpose_Label'].isin(selected_purposes)) &
        (df['Type_Label'].isin(selected_types))
        ]

    if len(selected_dates) == 2:
        filtered_df = filtered_df[
            (filtered_df['Date'] >= pd.to_datetime(selected_dates[0])) &
            (filtered_df['Date'] <= pd.to_datetime(selected_dates[1]))
            ]


    # Visualizations

    col1, col2 = st.columns([2, 1])

    with col1:
        # Global Map
        st.subheader("Global Detonation Map")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=['Longitude', 'Latitude'],
            get_radius=50000,
            get_fill_color=[255, 75, 75, 180],
            pickable=True
        )
        #USED STACK OVERFLOW ARTICLE ABOUT MAKING CHARTS FOR FORMATTING HELP AND WAYS TO MAKE CHARTS LOOK BETTTER
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v10',
            initial_view_state=pdk.ViewState(
                latitude=30,
                longitude=0,
                zoom=1,
                pitch=40
            ),
            layers=[layer]
        ))

        # Static Country Totals
        st.subheader("Total Detonations by Country (1945-1998)")
        country_counts = df['Country'].value_counts().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 4))
        country_counts.plot(kind='bar', color='#ff7f7f', edgecolor='#ff4b4b', ax=ax)
        ax.set_title("Nuclear Tests by Country", fontsize=16)
        ax.set_xlabel("Country", fontsize=12)
        ax.set_ylabel("Number of Detonations", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', alpha=0.3)
        for i in range(len(country_counts)):
            v = country_counts[i]
            ax.text(i, v + 2, str(v), ha='center', va='bottom', fontsize=9)
        st.pyplot(fig)

    with col2:
        # Statistics
        st.subheader("Summary Statistics")
        st.metric("Total Detonations", len(filtered_df))
        st.metric("Average Yield", f"{filtered_df['Yield'].mean():.1f} kt")
        st.metric("Maximum Yield", f"{filtered_df['Yield'].max():.1f} kt")

        # Temporal Analysis
        st.subheader("Detonations Timeline")
        time_series = filtered_df.resample('Y', on='Date').size()
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.plot(time_series.index.year, time_series.values,
                 color='#ff4b4b', marker='o', linestyle='--')
        ax2.set_xlabel("Year", fontsize=10)
        ax2.set_ylabel("Detonations", fontsize=10)
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

    # Additional Charts
    st.subheader("Detailed Breakdown")
    col3, col4 = st.columns(2)

    with col3:
        # Purpose Distribution
        st.write("### Purpose Distribution")
        purpose_counts = filtered_df['Purpose_Label'].value_counts()
        fig3, ax3 = plt.subplots()
        purpose_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax3)
        st.pyplot(fig3)

    with col4:
        # Type Distribution
        st.write("### Detonation Types")
        type_counts = filtered_df['Type_Label'].value_counts()
        fig4, ax4 = plt.subplots()
        type_counts.plot(kind='barh', color='#ff4b4b', ax=ax4)
        ax4.set_xlabel("Number of Detonations")
        st.pyplot(fig4)


if __name__ == "__main__":
    main()