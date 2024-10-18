# ev_analysis.py

import pickle
import pandas as pd
import numpy as np
import statsmodels.api as sm

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# OLS regression for trendline
def calculate_ols(df, x_col, y_col):
    # Data preparation
    X = sm.add_constant(df[x_col]) # Add constant term for intercept
    y = df[y_col]
    # Get OLS parameters
    model = sm.OLS(y, X).fit()
    slope = model.params[1]
    intercept = model.params[0]
    r_squared = model.rsquared
    return slope, intercept, r_squared

# ================================== #
# Global setting

# Set page config
st.set_page_config(page_title="Washington State EV Adoption Analysis", layout="wide")

highlight_color = '#0068C9'
unhighlight_color = 'lightgray'

# ================================== #
# Data preparation

# Load data
@st.cache_data
def load_data():
    with open('MSU/Fall_2024/CMSE_830/midterm/data/ev.pickle', 'rb') as f:
        ev = pickle.load(f)
    with open('MSU/Fall_2024/CMSE_830/midterm/data/ev_merged.pickle', 'rb') as f:
        ev_merged = pickle.load(f)
    with open('MSU/Fall_2024/CMSE_830/midterm/data/ev_state.pickle', 'rb') as f:
        ev_state = pickle.load(f)
    return ev, ev_merged, ev_state

ev, ev_merged, ev_state = load_data()

# Selection option for legislative districts
st.sidebar.header("Select Legislative District(s)")
districts = sorted(ev_merged['legislative_district'].unique(), key=lambda x: int(x)) # 1~49 order

selected_districts = st.sidebar.multiselect(
    "Choose from the list below:",  # This is still the label
    districts
)

# Filter the data based on selected districts
if selected_districts:
    ev_filtered = ev[ev['legislative_district'].isin(selected_districts)]
    ev_merged_filtered = ev_merged[ev_merged['legislative_district'].isin(selected_districts)]
else:
    ev_filtered = ev
    ev_merged_filtered = ev_merged

# ================================== #
# Title and introduction

st.title("Electric Vehicle Adoption in Washington State: Trends, Economy, Infrastructure, and Politics")

st.markdown("""
This dashboard explores the relationship between electric vehicle (EV) adoption in Washington State, economic factors, infrastructure developments, and political trends. My goal is to provide insights for policymakers, industry stakeholders, and researchers interested in promoting sustainable transportation.

**Presenting to:**
- Washington State government policymakers
- Electric vehicle manufacturers and related industry professionals
- Policymakers and researchers from other states

Washington State is a major player in the U.S. electric vehicle (EV) market, consistently demonstrating its commitment to sustainable transportation. Currently, it ranks 4th in the nation for total registered EVs and 2nd in per capita ownership, with 195 EVs per 10,000 people. This leadership is crucial for promoting green policies, providing lessons for other states, and fostering innovation in sustainable transportation.
""")

# ================================== #
### 1. Overview of EV Adoption in Washington

st.header("1. Overview of EV Adoption in Washington")

## 1.1) Electric Vehicle Population by State

# Set colors, highlighting Washington state
ev_state['state_category'] = np.where(
    ev_state['state'] == 'Washington',
    'Washington', 
    'Other'
)

fig_state = px.bar(
    ev_state, 
    x='state', 
    y='registration_count', 
    title='Electric Vehicle Registrations by State', 
    color='state_category', # Use the color column to set the bar colors
    color_discrete_map={'Other': unhighlight_color, 'Washington': highlight_color}, 
    category_orders={'state': ev_state['state']} # Maintain the original order of 'state'
) 
fig_state.update_xaxes(title='State')
fig_state.update_yaxes(title='Number of EVs')
fig_state.update_layout(showlegend=False)
fig_state.update_traces(hovertemplate='State: %{x}<br>EV Count: %{y}')

st.plotly_chart(fig_state)

## 1.2) EV Type Distribution

# Set colors for each ev_type: largest gets '#0068C9', others get 'lightgray'
ev_type_counts = ev_filtered.groupby('ev_type').size() # Calculate the counts for each ev_type
largest_ev_type = ev_type_counts.idxmax() # Index of ev_type with the largest count
custom_colors = [highlight_color if ev_type == largest_ev_type else unhighlight_color for ev_type in ev_filtered['ev_type']]

# Create the pie chart with the custom colors
fig_ev_type = px.pie(
    ev_filtered,
    names='ev_type',
    title='EV Type Distribution in Washington'
)

# Set hovertemplate
fig_ev_type.update_traces(
    hovertemplate='EV Type: %{label}<br>Count: %{value}<br>Percentage: %{percent:.2%}',
    marker=dict(colors=custom_colors) # Apply colors
)

## 1.3) Top EV Manufacturers (ft. with avg electric range)

top_manufacturers = ev_filtered['make'].value_counts().nlargest(10) # EV counts by maker within the districts
top_manufacturers_names = top_manufacturers.index # Top maker name
top_manufacturers_counts = top_manufacturers.values # Top makers' ev counts

# Calculate average electric range for every manufacturer from the original data
# - Will be fixed values despite districts selection
cond = (ev['electric_range'] != 0.0) & (ev['electric_range'].isna() == False) # Exclude 0 and null
avg_electric_range = ev[cond].groupby('make')['electric_range'].mean()

# Extract avg electric range of filtered top makers that have avg electric range value
cond = top_manufacturers_names.isin(avg_electric_range.index) # Get the names of filtered top makers (currently within selected districts)
top_manufacturers_with_range = top_manufacturers_names[cond] 
avg_electric_range = avg_electric_range[top_manufacturers_with_range] # And finally avg electric range values of them

# Create a figure
fig_manufacturers = go.Figure()

# Add EV count bar (main y-axis)
fig_manufacturers.add_trace(
    go.Bar(
        x=top_manufacturers_names,
        y=top_manufacturers_counts,
        name='', # Hide trace name
        marker_color=highlight_color,
        hoverinfo='text', # Set text on hover
        hovertemplate='Manufacturer: %{x}<br>EV Count: %{y}', 
        yaxis='y' # Main y-axis
    )
)

# Add secondar y-axis for average electric range marker
fig_manufacturers.update_layout(
    title='Top 10 EV Manufacturers: EV Count and Average Electric Range',
    xaxis_title='Manufacturer',
    yaxis_title='EV Count',
    # Secondary y-axis
    yaxis2=dict(
        title='Average Electric Range (miles)',
        overlaying='y',
        side='right',
        showgrid=False, # Disable grid for secondary y-axis
        zeroline=False # Disable zero line for clarity
    ),
    legend=dict(title='Metrics'),
    barmode='group' # Keep this to avoid bars overlapping
)

# Add average electric range annotations as "markers" (secondary y-axis)
for x, y in zip(avg_electric_range.index, avg_electric_range.values):
    fig_manufacturers.add_annotation(
        x=x,
        y=y,
        text=str(y), # Empty text to create a marker effect
        showarrow=False, # Hide the arrow associated with an annotation
        bgcolor=unhighlight_color, # Marker color
        height=3, # Height of the annotation
        width=38, # Width of the annotation
        font=dict(color=unhighlight_color),
        # bordercolor='black' # Border color for better visibility
        # borderwidth=1 # Border width for better visibility
        opacity=0.8, # Adjust opacity
        yref='y2' # At secondary y-axis
    )

# Plot side by side (Streamlit columns)
col1, col2 = st.columns(2)
with col1: st.plotly_chart(fig_ev_type) # Plot 1-2
with col2: st.plotly_chart(fig_manufacturers) # Plot 1-3

st.markdown("""
Observations:
- Battery Electric Vehicles (BEVs) represent the majority of Washington's EV market, accounting for a significant portion of the adoption trend. 
- Tesla leads as the dominant manufacturer, highlighting the state's strong preference for high-performance, long-range electric vehicles.
""")

# ================================== #
### 2. EV Adoption Trends

st.header("2. EV Adoption Trends")

## 2.1) EV Adoption by Model Year
# ev_by_year = ev_filtered['model_year'].value_counts().sort_index()
ev_by_year = ev_filtered['model_year'].value_counts().sort_index().reset_index()
ev_by_year.columns = ['model_year', 'ev_count']

fig_adoption = px.line(
    ev_by_year,
    x='model_year', # ev_by_year.index,
    y='ev_count', # ev_by_year.values,
    title='EV Distribution by Model Year',
    labels={'model_year': 'Model Year', 'ev_count': 'EV Count'}, # Labels for axes
    hover_data={'model_year', 'ev_count'}, # Enable hover for both
)
fig_adoption.update_xaxes(title='Model Year')
fig_adoption.update_yaxes(title='EV Count')
fig_adoption.update_traces(
    hovertemplate='Model Year: %{x}<br>EV Count: %{y}',
    line=dict(color=highlight_color)
)

## 2.2) EV Type by Model Year

# Count EV by each model year and ev type
model_counts = ev_filtered.groupby(['model_year', 'ev_type']).size().reset_index(name='count')

# Sum total counts for each EV type
total_counts = model_counts.groupby('ev_type')['count'].sum().reset_index()

# Get the EV type with the largest count
largest_ev_type = total_counts.loc[total_counts['count'].idxmax(), 'ev_type'] # EV type name

# Set colors based on the larger count EV type
color_map = {largest_ev_type: highlight_color} # Default color for the largest EV type
for ev_type in total_counts['ev_type']:
    if ev_type != largest_ev_type:
        color_map[ev_type] = unhighlight_color # Assign lightgray to the other EV type

# Create the line plot with fixed colors
fig_type = px.line(
    model_counts,
    x='model_year',
    y='count',
    color='ev_type',
    title='EV Type by Model Year (BEV vs. PHEV)',
    color_discrete_map=color_map # Apply the color map
)

# Legend setting (top center)
fig_type.update_layout(
    showlegend=True,
    legend=dict(
        orientation='h', # Horizontal orientation
        yanchor='bottom', # Anchor the legend to the bottom
        y=1.02, # Position it above the chart
        xanchor='center', # Anchor the legend to the center
        x=0.5, # Center the legend horizontally
        title=None # Hide the legend title
    )
)

# fig_type.update_traces(hovertemplate='Model Year: %{x}<br>EV Count: %{y}')
fig_type.for_each_trace(lambda t: t.update(hovertemplate='EV Type: ' + str(t.name) + '<br>Model Year: %{x}<br>Count: %{y}')) # Update hovertemplate for each trace

# fig_type.update_layout(showlegend=False)
fig_type.update_xaxes(title='Model Year')
fig_type.update_yaxes(title='EV Count')

# Plot side by side (Streamlit columns)
col1, col2 = st.columns(2)
with col1: st.plotly_chart(fig_adoption) # Plot 2-1
with col2: st.plotly_chart(fig_type) # Plot 2-2

st.markdown("""
Observations:
- This chart shows the distribution of EVs by their model year. While this isn't a direct measure of adoption over time, it provides insights into the increasing popularity of EV models.
- The trend towards more recent model years could indicate growing consumer interest, improved technology, and increased availability of EVs (though it's not a perfect representation of new EV adoption rates).
""")

# ================================== #
### 3. Economic Analysis

st.header("3. Economic Analysis")

## 3.1) EV Count vs. Median Household Income by Legislative District
# OLS regression for trendline
slope, intercept, r_squared = calculate_ols(ev_merged, 'median_household_income', 'ev_count')

if selected_districts:
    ev_merged['selected_highlight'] = np.where(
        ev_merged['legislative_district'].isin(selected_districts),
        'Selected',
        'Unselected'
    )
    color_discrete_map = {'Selected': highlight_color, 'Unselected': unhighlight_color}
    
    fig_income = px.scatter(
        ev_merged,
        x='median_household_income',
        y='ev_count',
        title='EV Count vs. Median Household Income by Legislative District',
        color='selected_highlight',
        color_discrete_map=color_discrete_map,
        trendline='ols',
        trendline_scope='overall',
        trendline_color_override=unhighlight_color,
        hover_data=['legislative_district', 'median_household_income', 'ev_count'],
        hover_name='legislative_district',
    )
else:
    fig_income = px.scatter(
        ev_merged.assign(group='Legislative District'), # Assign the same group 'Legislative District' to all data
        x='median_household_income',
        y='ev_count',
        title='EV Count vs. Median Household Income by Legislative District',
        color='group', # Specify color group
        color_discrete_map={'Legislative District': highlight_color}, # Set the designated color
        trendline='ols',
        trendline_scope='overall',
        trendline_color_override=highlight_color,
        hover_data=['legislative_district', 'median_household_income', 'ev_count'],
        hover_name='legislative_district',
    )

# Customize hover template
# Add the OLS equation and R^2 to hovertemplate
ols_equation = f'<br>OLS trendline:<br>y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}'

fig_income.update_traces(
    hovertemplate=(
        'Legislative District: %{hovertext}<br>'
        'Median Household Income: $%{x:,.0f}<br>'
        'EV Count: %{y}<br>'
        f'{ols_equation}'
    )
)

fig_income.update_layout(legend_title_text='') # Hide the legend title
fig_income.update_xaxes(title='Median Household Income')
fig_income.update_yaxes(title='EV Count')

st.plotly_chart(fig_income)

st.markdown("""
Observations:
- The positive correlation between household income and EV adoption underscores the affordability factor.
""")
# Policymakers should consider incentives for lower-income households to ensure widespread adoption.

# ================================== #
### 4. Charging Infrastructure Analysis

st.header("4. Charging Infrastructure Analysis")

## 4.1) EV Count vs. Charging Infrasturcture Factors

# Create a dropdown for selecting visualization type
viz_type = st.selectbox(
    "Select Visualization", 
    ["EV Count vs. Charger by Legislative District",
     "EV Count vs. Charger-to-EV Ratio by Legislative District",
     "EV Count vs. Charger-to-Area Ratio by Legislative District"
    ]
)

# Create a dropdown for selecting scaling option
scaling_option = st.selectbox("Select Scaling Option", ["Raw", "Scaled"])

# Choose the appropriate data based on the scaling option
# -> Square root transformed
if scaling_option == "Scaled":
    if viz_type == "EV Count vs. Charger by Legislative District":
        x_data = 'transformed_charger_count'
        y_data = 'transformed_ev_count'
        title = 'EV Count vs. Transformed Charger Count by Legislative District'
    elif viz_type == "EV Count vs. Charger-to-EV Ratio by Legislative District":
        x_data = 'transformed_charger_ev_ratio'
        y_data = 'transformed_ev_count'
        title = 'EV Count vs. Transformed Charger-to-EV Ratio by Legislative District'
    else:
        x_data = 'transformed_charger_density'
        y_data = 'transformed_ev_count'
        title = 'EV Count vs. Transformed Charger-to-Area Ratio by Legislative District'
# Raw data
else: 
    if viz_type == "EV Count vs. Charger by Legislative District":
        x_data = 'charger_count'
        y_data = 'ev_count'
        title = 'EV Count vs. Charger by Legislative District'
    elif viz_type == "EV Count vs. Charger-to-EV Ratio by Legislative District":
        x_data = 'charger_ev_ratio'
        y_data = 'ev_count'
        title = 'EV Count vs. Charger-to-EV Ratio by Legislative District'
    else:
        x_data = 'charger_density'
        y_data = 'ev_count'
        title = 'EV Count vs. Charger-to-Area Ratio by Legislative District'

# OLS regression for trendline
slope, intercept, r_squared = calculate_ols(ev_merged, x_data, y_data)

# Dictionary to label the x-axis based on selected data
x_labels = {
    'transformed_charger_count': 'Scaled Charger Count',
    'transformed_ev_count': 'Scaled EV Count',
    'transformed_charger_ev_ratio': 'Scaled Charger-to-EV Ratio',
    'transformed_charger_density': 'Scaled Charger Density',
    'charger_count': 'Charger Count',
    'ev_count': 'EV Count',
    'charger_ev_ratio': 'Charger-to-EV Ratio',
    'charger_density': 'Charger Density',
    # 'median_household_income': 'Median Household Income'
}

if selected_districts:
    ev_merged['selected_highlight'] = np.where(
        ev_merged['legislative_district'].isin(selected_districts),
        'Selected', 
        'Unselected'
    )
    color_discrete_map = {'Selected': highlight_color, 'Unselected': unhighlight_color}
    
    fig_charger = px.scatter(
        ev_merged,
        x=x_data,
        y=y_data,
        title=title,
        color='selected_highlight',
        color_discrete_map=color_discrete_map,
        trendline='ols',
        trendline_scope='overall',
        trendline_color_override=unhighlight_color,
        hover_data=['legislative_district'],#, x_data, y_data],
        hover_name='legislative_district',
    )
else:
    fig_charger = px.scatter(
        ev_merged.assign(group='Legislative District'), # Assign the same group 'Legislative District' to all data
        x=x_data,
        y=y_data,
        title=title,
        color='group', # Specify color group
        color_discrete_map={'Legislative District': highlight_color}, # Set the designated color
        trendline='ols',
        trendline_scope='overall',
        trendline_color_override=highlight_color,
        hover_data=['legislative_district'],#, x_data, y_data],
        hover_name='legislative_district',
    )

# Custom dynamic hovertemplate based on x_data label
# Add the OLS equation and R^2 to hovertemplate
ols_equation = f'<br>OLS trendline:<br>y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}'

fig_charger.update_traces(
    hovertemplate=(
        'Legislative District: %{hovertext}<br>'
        f'{x_labels.get(x_data, "X Value")}: ' + '%{x}<br>'
        'EV Count: %{y}<br>'
        f'{ols_equation}'
    )
)

fig_charger.update_layout(legend_title_text='') # Hide the legend title
fig_charger.update_xaxes(title=x_data)
fig_charger.update_yaxes(title=y_data)

st.plotly_chart(fig_charger)

st.markdown("""
Observations:
- This chart shows the relationship between EV adoption and the availability of charging infrastructure.
- Districts with more charging stations generally have higher EV counts, suggesting the importance of infrastructure, and may be better equipped to support further EV adoption.
- In regions with a high number of EVs, the charging infrastructure may not be keeping pace, leading to a lower Charger-to-EV Ratio, indicating the need for additional charging stations to meet demand.
""")
# Investment in charging infrastructure is critical. While some districts have kept pace with EV adoption, others lag behind, highlighting the need for targeted infrastructure expansion to support growing demand.

# ================================== #
### 5. Geographic Distribution and Political Landscape

st.header("5. Geographic Distribution and Political Landscape")

## 5.1) Legislative District and Political Landscape

# Create a dropdown for selecting visualization type
viz_type = st.selectbox(
    "Select Visualization", 
    ["EV Count by Legislative District", 
     "Registered Voters by Legislative District", 
     "EV Count vs. Median Household Income", 
     "EV Count vs. Charging Infrastructure"
    ]
)

party_colors = {'Democratic': '#0068C9', 'Republican': '#D32F2F'} # Material design red; modern UI
# unhighlight_color = 'lightgray' # Color for unselected districts

if viz_type == "EV Count by Legislative District":
    # Sort the dataframe by ev_count in descending order
    # ev_merged_sorted = ev_merged_filtered.sort_values('ev_count', ascending=False)
    ev_merged_sorted = ev_merged.sort_values('ev_count', ascending=False)

    if selected_districts:
        # Create a new column 'selected_highlight' based on whether the district is selected or not
        ev_merged_sorted['selected_highlight'] = np.where(
            ev_merged_sorted['legislative_district'].isin(selected_districts),
            ev_merged_sorted['party_won'], 
            'Unselected'
        )
        # Define the color map, with party_won for selected districts and gray for unselected
        color_discrete_map = {**party_colors, 'Unselected': unhighlight_color}
    else:
        ev_merged_sorted['selected_highlight'] = ev_merged_sorted['party_won']
        color_discrete_map = party_colors

    fig_pp = px.bar(
        ev_merged_sorted, 
        x='legislative_district', 
        y='ev_count', 
        color='selected_highlight', 
        title='EV Count by Legislative District and Political Party',
        color_discrete_map=color_discrete_map,
        # reorder x axis legislative_district by ev_count (descending)
        # category_orders={'legislative_district': ev_merged_sorted['legislative_district'].tolist()}
    ).update_xaxes(
        type='category', 
        categoryorder='total descending' # or max descending
    )

    # Customize hovertemplate
    # Update hovertemplate for each trace
    fig_pp.for_each_trace(lambda t: t.update(hovertemplate='Legislative District: %{x}<br>EV Count: %{y}<br>' + 'Party Won: ' + str(t.name)))

    # fig.update_xaxes(tickangle=45)
    fig_pp.update_layout(
        xaxis_title='Legislative District',
        yaxis_title='EV Count'
    )

elif viz_type == "Registered Voters by Legislative District":
    # Sort the dataframe by ev_count in descending order
    ev_merged_sorted = ev_merged.sort_values('ev_count', ascending=False)
    # Use the same order for 'legislative_district' from the first chart
    ld_order = ev_merged_sorted['legislative_district'].tolist()

    if selected_districts:
        ev_merged_sorted['selected_highlight'] = np.where(
            ev_merged_sorted['legislative_district'].isin(selected_districts),
            ev_merged_sorted['party_won'],
            'Unselected'
        )
        color_discrete_map = {**party_colors, 'Unselected': unhighlight_color}
    else:
        ev_merged_sorted['selected_highlight'] = ev_merged_sorted['party_won']
        color_discrete_map = party_colors
    
    fig_pp = px.bar(
        ev_merged_sorted,
        x='legislative_district',
        y='registered_voters',
        color='selected_highlight',
        title='Registered Voters by Legislative District and Political Party',
        color_discrete_map=color_discrete_map,
        category_orders={'legislative_district': ld_order}
    ).update_xaxes(type='category')

    # Customize hovertemplate
    # Update hovertemplate for each trace
    fig_pp.for_each_trace(lambda t: t.update(hovertemplate='Legislative District: %{x}<br>Registered Voters: %{y}<br>' + 'Party Won: ' + str(t.name))) 
    
    fig_pp.update_layout(
        xaxis_title='Legislative District',
        yaxis_title='Registered Voters'
    )

elif viz_type == "EV Count vs. Median Household Income":

    if selected_districts:
        ev_merged['selected_highlight'] = np.where(
            ev_merged['legislative_district'].isin(selected_districts),
            ev_merged['party_won'],
            'Unselected')
        color_discrete_map = {**party_colors, 'Unselected': unhighlight_color}

        fig_pp = px.scatter(
            ev_merged,
            x='median_household_income',
            y='ev_count',
            color='selected_highlight',
            title='EV Count vs. Median Household Income by Legislative District',
            color_discrete_map=color_discrete_map,
            hover_data=['legislative_district','selected_highlight'],
            hover_name='legislative_district'
        )

        # Customize hovertemplate
        # Update hovertemplate for each trace
        fig_pp.for_each_trace(lambda t: t.update(
            hovertemplate=(
                'Legislative District: %{hovertext}<br>Party Won: ' + str(t.name) + '<br>Median Household Income: $%{x:,.0f}<br>EV Count: %{y}')
        ))
        
        # fig_pp.update_traces(
        #     hovertemplate=(
        #         'Legislative District: %{hovertext}<br>'
        #         'Median Household Income: $%{x:,.0f}<br>'
        #         'EV Count: %{y}<br>'
        #     )
        # )
    
    else:
        ev_merged['selected_highlight'] = ev_merged['party_won']
        color_discrete_map = party_colors

        # (Add) calculate OLS params for each party_won(selected_highlight)
        ols_params = {}
        for party in ev_merged['party_won'].unique():
            party_data = ev_merged[ev_merged['party_won'] == party]
            slope, intercept, r_squared = calculate_ols(party_data, 'median_household_income', 'ev_count')
            ols_params[party] = {'slope': slope, 'intercept': intercept, 'r_squared': r_squared}
        
        fig_pp = px.scatter(
            ev_merged,
            x='median_household_income',
            y='ev_count',
            color='selected_highlight',
            title='EV Count vs. Median Household Income by Legislative District',
            color_discrete_map=color_discrete_map,
            hover_data=['legislative_district','party_won'],
            hover_name='legislative_district',
            trendline='ols',
            trendline_scope='trace' # 'trace' or 'overall'
            # trendline_color_override=unhighlight_color
        )

        # (Add) Add the OLS equation and R^2 to hovertemplate
        for trace in fig_pp.data:
            party = trace.name  # 'selected_highlight' 이름 (party_won 이름)
            
            if party in ols_params:
                slope = ols_params[party]['slope']
                intercept = ols_params[party]['intercept']
                r_squared = ols_params[party]['r_squared']
                
                # ols_equation = f"y = {slope:.2f}x + {intercept:.2f}"
                ols_equation = f'<br>OLS trendline:<br>y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}'
                
                # Hovertemplate
                trace.hovertemplate = (
                    'Legislative District: %{hovertext}<br>'
                    'Party Won: ' + party + '<br>'
                    'Median Household Income: $%{x:,.0f}<br>'
                    'EV Count: %{y}<br>'
                    f'{ols_equation}<extra></extra>'
                )
    
    fig_pp.update_xaxes(title='Median Household Income')
    fig_pp.update_yaxes(title='EV Count')

else:
    if selected_districts:
        ev_merged['selected_highlight'] = np.where(
            ev_merged['legislative_district'].isin(selected_districts),
            ev_merged['party_won'],
            'Unselected'
        )
        color_discrete_map = {**party_colors, 'Unselected': unhighlight_color}

        fig_pp = px.scatter(
            ev_merged,
            x='charger_count',
            y='ev_count',
            color='selected_highlight',
            title='EV Count vs. Charging Infrastructure by Legislative District',
            color_discrete_map=color_discrete_map,
            hover_data=['legislative_district','selected_highlight'],
            hover_name='legislative_district'
        )

        # Customize hovertemplate
        # Update hovertemplate for each trace
        fig_pp.for_each_trace(lambda t: t.update(
            hovertemplate=(
                'Legislative District: %{hovertext}<br>Party Won: ' + str(t.name) + '<br>Number of Charging Stations: %{x}<br>EV Count: %{y}')
        ))
    
        # fig_pp.update_traces(
        #     hovertemplate=(
        #         'Legislative District: %{hovertext}<br>'
        #         'Number of Charging Stations: %{x}<br>'
        #         'EV Count: %{y}<br>'
        #     )
        # )
    
    else:
        ev_merged['selected_highlight'] = ev_merged['party_won']
        color_discrete_map = party_colors

        # (Add) calculate OLS params for each party_won(selected_highlight)
        ols_params = {}
        for party in ev_merged['party_won'].unique():
            party_data = ev_merged[ev_merged['party_won'] == party]
            slope, intercept, r_squared = calculate_ols(party_data, 'charger_count', 'ev_count')
            ols_params[party] = {'slope': slope, 'intercept': intercept, 'r_squared': r_squared}
        
        fig_pp = px.scatter(
            ev_merged,
            x='charger_count',
            y='ev_count',
            color='selected_highlight',
            title='EV Count vs. Charging Infrastructure by Legislative District',
            color_discrete_map=color_discrete_map,
            hover_data=['legislative_district','party_won'],
            hover_name='legislative_district',
            trendline='ols',
            trendline_scope='trace'
            # trendline_color_override=unhighlight_color
        )

        # (Add) Add the OLS equation and R^2 to hovertemplate
        for trace in fig_pp.data:
            party = trace.name  # 'selected_highlight' name (party_won)
            
            if party in ols_params:
                slope = ols_params[party]['slope']
                intercept = ols_params[party]['intercept']
                r_squared = ols_params[party]['r_squared']
                
                # ols_equation = f"y = {slope:.2f}x + {intercept:.2f}"
                ols_equation = f'<br>OLS trendline:<br>y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}'
                
                # Hovertemplate
                trace.hovertemplate = (
                    'Legislative District: %{hovertext}<br>'
                    'Party Won: ' + party + '<br>'
                    'Number of Charging Stations: %{x}<br>'
                    'EV Count: %{y}<br>'
                    f'{ols_equation}<extra></extra>'
                )

    fig_pp.update_xaxes(title='Number of Charging Stations')
    fig_pp.update_yaxes(title='EV Count')

fig_pp.update_layout(legend_title_text='') # Hide the legend title
st.plotly_chart(fig_pp)

st.markdown("""
Observations:
- Democratic-leaning districts tend to have higher EV adoption rates, likely driven by supportive environmental policies.
""")
# Expanding awareness and incentives in Republican-leaning districts could foster bipartisan support for EV adoption.

# ================================== #
# 6. Conclusion and Recommendations

st.header("6. Conclusion and Recommendations")

st.markdown("""
Based on the analysis, I can draw the following conclusions and make these recommendations:

1. **Political Landscape**: Democratic-leaning districts show significantly higher EV adoption rates. To bridge the political divide, consider targeted educational campaigns and financial incentive programs in Republican-leaning districts to boost adoption.

2. **Economic Factors**: There's a strong correlation between median household income and EV adoption. Develop programs to make EVs more accessible to lower-income households.

3. **Infrastructure Development**: Charging infrastructure is crucial for EV adoption. Continue investing in charging stations, especially in areas with high potential for EV growth.

4. **Manufacturer Diversity**: While Tesla dominates the market, encouraging diversity in EV options could accelerate adoption across different consumer segments.

5. **Policy Implications**: The success of Washington's EV policies could serve as a model for other states. Consider sharing best practices and lessons learned with policymakers from other regions.

By addressing these factors, Washington State can continue to lead in EV adoption and set an example for sustainable transportation nationwide.
""")

# ================================== #
# Add a sidebar for additional information or controls
st.sidebar.header("About This Dashboard")

st.sidebar.info("This dashboard provides an in-depth analysis of electric vehicle adoption in Washington State, examining factors such as political trends, economic indicators, and infrastructure development. It aims to inform policy decisions and industry strategies to promote sustainable transportation.")

st.sidebar.header("Data Sources")

st.sidebar.markdown("""
- Electric Vehicle Population in Washington State
- General Election Results in Washington State 2022
- Alternative Fuel Stations in Washington State
- Median Household Income in Washington State 2022
- Electric Vehicle Registration Counts by State
- Washington State Legislative Districts 2022 (Geospatial)
""")

# execute in Terminal:
# streamlit run MSU/Fall_2024/CMSE_830/midterm/ev_analysis.py

# ================================== #
# Note:
# 기후/환경 데이터(탄소 배출량 등), 충전소 유형(급속/완속)별 분포, 도시 vs 교외 지역의 EV 채택 비교 등
