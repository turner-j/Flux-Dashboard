import streamlit as st
import paramiko
import sys
import getpass
import os
import pandas as pd
import pysftp as sftp
from stat import S_ISDIR, S_ISREG
from dash import Dash, html, dcc, callback, Output, Input
import csv
import fnmatch
import numpy as np
import ipaddress
import warnings
# Suppress all warnings
warnings.filterwarnings("ignore")
import utide as ut
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn import datasets
import pickle

st.set_page_config(
    page_title="Wave Prediction",
    page_icon=":surfer:")

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

lat = 29.5200

def degToCompass(degrees):
	degrees = np.asarray(degrees)
	val = np.floor((degrees / 22.5) + 0.5).astype(int)
	arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
	compass_directions = arr[val % 16]
	return compass_directions

# Call the function
direction = degToCompass(np.nanmean(df['wind_dir']))
speed = np.nanmean(df['wind_speed'])

# Function to determine wind model based on wind speed and direction

high_speed_threshold = 2.3778
	
if speed > high_speed_threshold and direction =='S':
	st.write("Average wind speed yesterday was high and northerly. Using the high winds model.")
	with open('highcoefs.pkl','rb') as bunch:
		coef = pickle.load(bunch)

else:
	st.write("Average wind speed yesterday was not high and northerly. Using the low winds model.")
	with open('lowcoefs.pkl', 'rb') as bunch:
		coef = pickle.load(bunch)
		
# Get the current date and time, with buffer
current_time = datetime.now()
start_time = current_time - timedelta(days=5)
end_time = current_time + timedelta(days=10)

# Generate an array of times with an hourly interval
time_array = np.arange(start_time, end_time, timedelta(hours=1), dtype='datetime64[m]')

# Convert the numpy datetime64 array to Python datetime objects
python_datetime_array = [np.datetime64(t).astype(datetime) for t in time_array]

tide = ut.reconstruct(python_datetime_array, coef)

# Combine the arrays into a DataFrame
ddf = pd.DataFrame({'Date': python_datetime_array, 'Water level (m)': tide.h})

st.line_chart(ddf,x='Date', y='Water level (m)')

st.write("*Fieldwork not recommended for water levels below 4.16 m.*")
