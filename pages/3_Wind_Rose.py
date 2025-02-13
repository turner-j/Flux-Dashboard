import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
import pandas as pd
import colormaps as cmaps
import datetime
import paramiko
import sys
import getpass
import pysftp as sftp
from stat import S_ISDIR, S_ISREG
from dash import Dash, html, dcc, callback, Output, Input
import csv
import fnmatch
import ipaddress

st.set_page_config(
    page_title="Windrose",
    page_icon=":rose:")

st.markdown("# Plotting Windrose")

st.write(
    """Display a windrose of hourly data from the last 30 days."""
)

target_host = st.secrets["target_host"]
target_port = st.secrets["target_port"]
un  = st.secrets["un"]
pwd = st.secrets["pwd"]

def getfluxes(target_host,target_port,un,pwd):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client.connect(hostname = target_host , username = un, password = pwd, port = target_port)
	stdin,stdout,stderr=ssh_client.exec_command('ls')
	output = stdout.readlines()
	
	sftp = ssh_client.open_sftp()
	sftp.chdir('data/summaries/')
	remote_path = '.'
	
	filenames = []
	
	for entry in sftp.listdir_attr(remote_path):
		if fnmatch.fnmatch(entry.filename, "2025*.txt") and sftp.stat(entry.filename).st_size != 0:
			filenames.append(entry.filename)
	
	df_list = []
	# select the last n files
	n = 30
	filenames = filenames[-n:]
	
	for f in filenames:
		remote_file = sftp.open(f) # locate file
		df = pd.read_csv(remote_file,sep='\t', header = 0,skiprows = [1])
		df_list.append(df) # store dataframe in list
		remote_file.close() # close file
	
	big_df = pd.concat(df_list) # merge into single large dataframe
	
	cols = [0,1]
	big_df.drop(big_df.columns[cols],axis=1,inplace=True)
	big_df['TIMESTAMP_END'] = pd.to_datetime(big_df['date'] + ' ' + big_df['time'])
	big_df.drop(['date', 'time'],axis=1,inplace=True)
	
	# Remove low-quality and unrealistic fluxes
	big_df.loc[big_df.qc_co2_flux==2,'co2_flux']= np.nan
	big_df.loc[big_df.co2_flux > 50, 'co2_flux'] = np.nan
	big_df.loc[big_df.co2_flux < -50, 'co2_flux'] = np.nan
	
	big_df.loc[big_df.qc_ch4_flux==2,'ch4_flux']= np.nan
	big_df.loc[big_df.ch4_flux > .500, 'ch4_flux'] = np.nan
	big_df.loc[big_df.ch4_flux < -.500, 'ch4_flux'] = np.nan
	
	big_df.loc[big_df.qc_LE==2,'LE']= np.nan
	big_df.loc[big_df.LE > 600, 'LE'] = np.nan
	big_df.loc[big_df.LE < -100, 'LE'] = np.nan
	
	big_df.loc[big_df.qc_H==2,'H']= np.nan
	big_df.loc[big_df.H > 600, 'H'] = np.nan
	big_df.loc[big_df.H < -300, 'H'] = np.nan
	
	return big_df

df = getfluxes(target_host,target_port,un,pwd)

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
df.rename(columns={'co2_flux': 'CO2 (\u03bcmolm\u00b-2s\u00b2-1)'}, inplace=True)

if day and not night:
    st.write("You selected daytime.")
    df = df[df.daytime == 1]
    df = df[df['CO2 (\u03bcmolm\u00b-2s\u00b2-1)'] <= 0]
    
    fig = px.scatter_polar(df, r="wind_speed", theta="wind_dir",
    color="CO2 (\u03bcmolm\u00b-2s\u00b2-1)", color_discrete_sequence=px.colors.sequential.Plasma_r)
    
    # Update the traces to add a thin black border around each point
    fig.update_traces(marker=dict(line=dict(width=1, color='black')))
    st.plotly_chart(fig)

elif night and not day:
	st.write("You selected nighttime.")
	df = df[df.daytime == 0]
	df = df[df['CO2 (\u03bcmolm\u00b-2s\u00b2-1)']>0]
	
	fig = px.scatter_polar(df, r="wind_speed", theta="wind_dir", color="CO2 (\u03bcmolm\u00b-2s\u00b2-1)", color_discrete_sequence=px.colors.sequential.Plasma_r)
    
    # Update the traces to add a thin black border around each point
	fig.update_traces(marker=dict(line=dict(width=1, color='black')))
	st.plotly_chart(fig)
	
elif night and day:
	st.write("You selected both day and nighttime.")
	
	fig = px.scatter_polar(df, r="wind_speed", theta="wind_dir",color="CO2 (\u03bcmolm\u00b-2s\u00b2-1)", color_discrete_sequence=px.colors.sequential.Plasma_r)
    
    # Update the traces to add a thin black border around each point
	fig.update_traces(marker=dict(line=dict(width=1, color='black')))
	st.plotly_chart(fig)
