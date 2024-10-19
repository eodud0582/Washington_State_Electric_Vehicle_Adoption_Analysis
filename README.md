# Washington State Electric Vehicle (EV) Adoption Analysis
---

<p align="center">
  <img src="https://github.com/user-attachments/assets/a599e7a7-8468-4ba7-808b-95e71a799a87" style="width:50%" alt="washington ev">
</p>
<p align="center" style="font-size: 10px; margin-top: 1px;">
  Image created with the help of ChatGPT by OpenAI
</p>

Welcome to the **Washington State Electric Vehicle (EV) Adoption Analysis** project! This dashboard provides a detailed analysis of EV adoption in Washington State, examining trends in relation to political factors, economic indicators, and infrastructure development.

This analysis is designed for:
- **Policymakers** looking to make informed decisions about EV promotion.
- **Industry stakeholders** seeking insights into market trends.
- **Researchers and other states** aiming to understand the key factors driving EV adoption.

## Key Features
- **EV Adoption Overview**: Analyze the distribution of electric vehicles across Washington State and compare it with other U.S. states.
- **Economic Insights**: Understand how median household income relates to EV adoption rates.
- **Infrastructure Analysis**: Explore the relationship between EV adoption and the availability of charging infrastructure.
- **Political Landscape**: See how EV adoption correlates with political trends and legislative districts.
- **Customizable Filters**: Users can select different legislative districts for a more tailored analysis.

## How to Access the Dashboard

This dashboard is deployed and can be accessed at:
- https://waevanalysis.streamlit.app

## How to Run the Dashboard Locally

This project is built with **Streamlit**, a tool that allows you to easily create interactive dashboards and web apps in Python. Follow these steps to run the dashboard locally on your machine.

### Prerequisites

Python installed:
- Python 3.12.6

Packages installed:
- pandas 2.2.3
- numpy 1.26.4
- statsmodels 0.14.2
- plotly 5.24.1
- streamlit 1.38.0

### Step-by-Step Instructions

1. **Clone the repository**:  
   First, clone this repository to your local machine:
   
   ```
   git clone https://github.com/eodud0582/Washington_State_Electric_Vehicle_Adoption_Analysis.git
   cd Washington_State_Electric_Vehicle_Adoption_Analysis
   ```

2. **Create and activate a virtual environment (optional but recommended)**

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages**:

   The easiest way to install the necessary packages is by using the `requirements.txt` file::
   
   ```
   pip install -r requirements.txt
   ```

   Alternatively, you can manually install the packages:

   ```
   pip install pandas==2.2.3 numpy==1.26.4 statsmodels==0.14.2 plotly==5.24.1 streamlit==1.38.0
   ```

4. **Download the data**:  
   Ensure the data files (`ev.pickle`, `ev_merged.pickle`, `ev_state.pickle`) are available in the `data_processed/` folder. If these files are not included in the repository due to size limits, you will need to manually download or provide these files.

5. **Run the Streamlit app**:  
   Once everything is set up, you can launch the Streamlit app by running the following command:

   ```
   streamlit run ev_analysis_streamlit.py
   ```

7. **Access the dashboard**:
   After running the command:
   - The Streamlit dashboard will automatically open in your browser on `http://localhost:8501`.
   - Or, a local URL such as `http://localhost:8501` will be provided in the terminal. Open that link in your browser to view and interact with the dashboard.

### Project Structure

```
Washington_State_Electric_Vehicle_Adoption_Analysis/
│
├── data_processed/           # Folder containing the processed data files in pickle format
├── ev_analysis_streamlit.py  # Main Python file for Streamlit app
├── requirements.txt          # Python dependencies
└── README.md                 # Project overview and instructions (this file)
```

## Data Sources

This dashboard leverages the following data:
- **Electric Vehicle Population in Washington State**
- **Washington State General Election Results 2022**
- **Alternative Fuel Stations (Charging Stations) in Washington**
- **Median Household Income by Legislative District**
- **Electric Vehicle Registration Counts by State**

## Acknowledgements

Special thanks to the open data sources and tools that made this analysis possible. This project was built using:
- **Streamlit** for the interactive web app.
- **Plotly** for visualizing data in dynamic, interactive plots.
- **Pandas** and **NumPy** for data manipulation and analysis.
