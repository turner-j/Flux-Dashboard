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
    page_title="Time Series",
    page_icon=":alarm_clock:",
)

target_host = st.secrets["target_host"]
target_port = st.secrets["target_port"]
un  = st.secrets["un"]
pwd = st.secrets["pwd"]

df = getfluxes(target_host,target_port,un,pwd)

# Converting time zone from UTC to local
df['TIMESTAMP_END'] = df['TIMESTAMP_END']-pd.Timedelta(6,unit='h')
df['hr'] = df['TIMESTAMP_END'].dt.strftime("%H")
df['hr'] = df['hr'].astype(int)
df['hr'] = df['hr']*100

df['mn'] = df['TIMESTAMP_END'].dt.strftime("%M")
df['mn'] = df['mn'].astype(int)
df['times'] = df['hr'] + df['mn']


timestepfreq = st.radio(label=':red[Choose an averaging frequency:]',options=("Hourly", "Daily"))
var = st.radio(label=':red[Choose a variable:]',options=("CO2", "CH4"))

st.markdown("""<style>
div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
    font-size: 32px;
}
    </style>
    """, unsafe_allow_html=True)
    
st.write(
    """Choose a gas and averaging frequency to display. Bar color corresponds to standard deviation."""
)

if timestepfreq == "Hourly" and var == "CO2":
	st.write("Displaying hourly means of CO2.")
	hh_df = df.groupby([df['TIMESTAMP_END'].dt.hour,df['TIMESTAMP_END'].dt.minute]).mean()
	hh_df['hour'] = hh_df['TIMESTAMP_END'].dt.hour
	hh_df['deviation'] = hh_df['co2_flux'] - hh_df['co2_flux'].mean()
	st.bar_chart(hh_df, x="times", y="co2_flux", color="deviation")
	
elif timestepfreq == "Daily" and var == "CO2":
	st.write("Displaying daily means of CO2.")
	dd_df = df.groupby([df['TIMESTAMP_END'].dt.date]).mean()
	dd_df['date'] = dd_df['TIMESTAMP_END'].dt.date
	dd_df['deviation'] = dd_df['co2_flux'] - dd_df['co2_flux'].mean()
	st.bar_chart(dd_df, x="date", y="co2_flux", color="deviation")

elif timestepfreq == "Hourly" and var == "CH4":
	st.write("Displaying hourly means of CH4.")
	hh_df = df.groupby([df['TIMESTAMP_END'].dt.hour,df['TIMESTAMP_END'].dt.minute]).mean()
	hh_df['hour'] = hh_df['TIMESTAMP_END'].dt.hour
	hh_df['deviation'] = hh_df['ch4_flux'] - hh_df['ch4_flux'].mean()
	st.bar_chart(hh_df, x="times", y="ch4_flux", color="deviation")
	
else:
	st.write("Displaying daily means of CH4.")
	dd_df = df.groupby([df['TIMESTAMP_END'].dt.date]).mean()
	dd_df['date'] = dd_df['TIMESTAMP_END'].dt.date
	dd_df['deviation'] = dd_df['ch4_flux'] - dd_df['ch4_flux'].mean()
	st.bar_chart(dd_df, x="date", y="ch4_flux", color="deviation")
