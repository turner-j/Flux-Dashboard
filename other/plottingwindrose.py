import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
import pandas as pd
import colormaps as cmaps
import datetime
from loadingfluxdata import getfluxes

st.set_page_config(
    page_title="Windrose",
    page_icon=":rose:")

st.markdown("# Plotting Windrose")

st.write(
    """Display a windrose of hourly data from the last 30 days."""
)

df = getfluxes()

df  = df[["daytime","TIMESTAMP_END", "co2_flux","wind_speed","wind_dir"]]

df = df.dropna()

df['TIMESTAMP_END'] = pd.to_datetime(df['TIMESTAMP_END'])

# Plotting CO2 scatter wind rose
dir_rad = np.radians(df['wind_dir'])
df['direction'] = dir_rad

import plotly.express as px

st.write('Select time to display:')
day = st.checkbox('daytime')
night = st.checkbox('nighttime')

if day and not night:
    st.write("You selected daytime.")
    df = df[df.daytime == 1]
    df = df[df['co2_flux'] <= 0]
    
    fig = px.scatter_polar(df, r="wind_speed", theta="wind_dir",
    color="co2_flux", color_discrete_sequence=px.colors.sequential.Plasma_r)
    
    # Update the traces to add a thin black border around each point
    fig.update_traces(marker=dict(line=dict(width=1, color='black')))
    st.plotly_chart(fig)

elif night and not day:
	st.write("You selected nighttime.")
	df = df[df.daytime == 0]
	df = df[df['co2_flux']>0]
	
	fig = px.scatter_polar(df, r="wind_speed", theta="wind_dir", color="co2_flux", color_discrete_sequence=px.colors.sequential.Plasma_r)
    
    # Update the traces to add a thin black border around each point
	fig.update_traces(marker=dict(line=dict(width=1, color='black')))
	st.plotly_chart(fig)
	
elif night and day:
	st.write("You selected both day and nighttime.")
	
	fig = px.scatter_polar(df, r="wind_speed", theta="wind_dir",color="co2_flux", color_discrete_sequence=px.colors.sequential.Plasma_r)
    
    # Update the traces to add a thin black border around each point
	fig.update_traces(marker=dict(line=dict(width=1, color='black')))
	st.plotly_chart(fig)
