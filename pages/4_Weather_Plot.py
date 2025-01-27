import numpy, scipy, matplotlib
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import datetime
import numpy as np
from datetime import datetime
import streamlit as st
import paramiko
import sys
import getpass
import os
import pysftp as sftp
from stat import S_ISDIR, S_ISREG
from dash import Dash, html, dcc, callback, Output, Input
import csv
import fnmatch
import numpy as np
import ipaddress

st.set_page_config(
    page_title="Weather",
    page_icon=":sun_with_face:")

st.write("Plotting air temp., latent heat flux, and humidity.")

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
    size="RH (%)")
