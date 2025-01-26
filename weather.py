import numpy, scipy, matplotlib
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import datetime
import numpy as np
from datetime import datetime
from loadingfluxdata import getfluxes
import streamlit as st

st.set_page_config(
    page_title="Flux Tower Dashboard",
    page_icon=":large_green_circle:",
)

st.write("Plotting air temp., latent heat flux, and humidity.")

df = getfluxes()

# Converting time zone from UTC to local
df['TIMESTAMP_END'] = df['TIMESTAMP_END']-pd.Timedelta(6,unit='h')

dd_df = df.groupby([df['TIMESTAMP_END'].dt.date]).mean()
dd_df['date'] = dd_df['TIMESTAMP_END'].dt.date

dd_df['TA'] = dd_df['TA_1_1_1'].fillna(dd_df['air_temperature'])
dd_df['TA'] = dd_df['TA']-273.15

dd_df = dd_df[["date","TA","LE","RH"]]

# Renaming columns
dd_df.rename(columns={'TA': 'air temp (C)', 'LE': 'latent heat flux', 'RH': 'RH (%)'}, inplace=True)

st.scatter_chart(
    dd_df,
    x="date",
    y="air temp (C)",
    color="latent heat flux",
    size="RH (%)",
)

from st_pages import Page, show_pages, add_page_title

# Specify what pages should be shown in the sidebar, and what their titles 
# and icons should be
show_pages(
    [
        Page("dashboard.py", "Home", ":house:"),
        Page("plottingwindrose.py", "Windrose", ":rose:"),
        Page("plottingtimeseries.py", "Time Series", ":alarm_clock:"),
        Page("footprint.py", "Flux Footprint", ":footprints:"),
        Page("weather.py", "Weather", ":sun_with_face:")
    ]
)
