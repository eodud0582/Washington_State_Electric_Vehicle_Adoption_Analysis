"""
MIT License

Copyright (c) 2024 Daeyoung Kim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import streamlit as st

# ================================== #
# Global setting

# Set page config
st.set_page_config(page_title="Washington EV Adoption Insights", page_icon=":battery:", layout="wide")
# emoji: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

# Adjust sizes
st.markdown("""
    <style>
    /* Adjust the body font size */
    /* Reduces font size to 80% of default */
    html, body, [data-testid="stAppViewContainer"] {
        font-size: 80%;
    }

    /* Reduces the heading size */
    /* 
    h1, h2, h3, h4, h5, h6 {
        font-size: 100%;
    }
    */

    /* Scale down Plotly charts */
    /* 
    [data-testid="stPlotlyChart"] {
        transform: scale(0.8); 
    */
    }
    </style>
""", unsafe_allow_html=True)

highlight_color = '#0068C9'
unhighlight_color = 'lightgray'

# ================================== #
# Title and introduction
st.title("Washington Electric Vehicle (EV) Adoption Insights")
st.markdown("### Dataset Overview")

st.divider()

st.header("1. Data Sources")
st.markdown("""
The dataset is compiled from various reputable sources to ensure accuracy and relevance for analysis:
1. [**Electric Vehicle Registrations by State**](https://afdc.energy.gov/data/10962)
2. [**Washington State Electric Vehicle Population Data**](https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2/about_data)
3. [**Washington State 2022 Legislative Election Results**](https://www.kaggle.com/datasets/josephdemey/2022-washington-state-legislative-election-results)
4. [**Washington State Alternative Fuel Stations (Charging Stations)**](https://afdc.energy.gov/data_download)
5. [**Washington State Median Household Income (ACS 2022 5-year)**](https://censusreporter.org/data/table/?table=B19013&geo_ids=610|04000US53#)
6. [**Washington State Legislative Districts 2022 (Geospatial)**](https://geo.wa.gov/datasets/c2b31e7e2b6f464a92d1bed7ab1d7539_0/explore?location=47.056733%2C-120.812244%2C7.15)
7. [**Washington State Voter Demographics Tables (Age)**](https://www.sos.wa.gov/elections/data-research/election-data-and-maps/reports-data-and-statistics/voter-demographics)
""")

st.header("2. Data Cleaning Process")
st.markdown("""
To ensure high-quality and reliable data for analysis and predictions, the following cleaning steps were applied:
- **Filtering Non-Relevant Data**  
  Data from states other than Washington were excluded to maintain a focused analysis.
- **Handling Missing Values**  
  Missing data were addressed by identifying patterns and relationships:  
  - Example: All GMC EVs were identified as 'HUMMER EV PICKUP' based on consistent make-model associations.  
  - Example: For records with `2024` as `model_year`, `electric_range` and `base_msrp` were imputed using known values for `MERCEDES-BENZ` S-Class EVs.
- **Outlier Management**  
  Charger density outliers were transformed using a square root function to reduce skewness and improve correlation analysis with EV registrations.
- **Scaling for Modeling**  
  Standard scaling was applied to features for consistent input during prediction modeling.
- **Legislative District Geocoding**  
  For EV charger stations without district information, geographic coordinates (latitude and longitude) were processed using the US Census geocoding API to assign legislative districts accurately.
""")

st.header("3. Feature Engineering")
st.markdown("""
After cleaning, datasets were merged and additional meaningful variables were created to enhance analysis and prediction. Below are key features and their descriptions:
""")

st.table({
    "Variable": [
        "legislative_district", "ev_count", "dem_votes", "rep_votes", 
        "charger_count", "median_household_income", "charger_density", "charger_ev_ratio",
        "voters_18_24", "charger_per_voter_18_24", "transformed_ev_count"
    ],
    "Description": [
        "Legislative district ID in Washington State",
        "Number of registered electric vehicles (EVs)",
        "Votes received by candidate Patty Murray (Democratic) ",
        "Votes received by candidate Tiffany Smiley (Republican)",
        "Total number of EV chargers",
        "Median household income in the district",
        "EV charger density per unit of area",
        "Ratio of EV chargers to EVs",
        "Number of voters aged 18–24",
        "EV chargers per voter aged 18–24",
        "Transformed EV count for analysis"
    ]
})

st.markdown("""
For a complete list of features, refer to the README document on the [GitHub page](https://github.com/eodud0582/Washington_State_Electric_Vehicle_Adoption_Analysis).
""")

# ================================== #
# Add a sidebar for additional information or controls

# Table of Contents
st.sidebar.header("Table of Contents")
st.sidebar.markdown("""
- [Home](#electric-vehicle-adoption-in-washington-state)
- [1. Data Sources](#1-data-sources)
- [2. Data Cleaning Process](#2-data-cleaning-process)
- [3. Feature Engineering](#3-feature-engineering)
""")

# Sidebar for navigation guidance
st.sidebar.header("Next Steps")
st.sidebar.info("""
After reviewing the dataset and cleaning process, explore the following pages for more insights:
- **EV Analysis**: Visualize trends in EV adoption across Washington State.
- **EV Prediction**: Use key variables to predict EV registration trends and analyze potential impacts.
""")

# ================================== #
# Additional information about the project

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Insights by Daeyoung Kim")
    st.write(
        "Email: kimdae15@msu.edu | [GitHub](https://github.com/eodud0582) | [LinkedIn](https://linkedin.com/in/eodud0582)"
    )

with col2:
    st.markdown("### License")
    st.write("MIT")
