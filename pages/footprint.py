import streamlit as st
import calc_footprint_FFP3 as myfootprint
from loadingfluxdata import getfluxes

st.set_page_config(
    page_title="Flux Footprint",
    page_icon=":footprints:")

df = getfluxes()

footprintdf = df[["L","(z-d)/L","wind_speed","wind_dir","v_unrot","u*"]].copy()
# Renaming column by index
footprintdf.columns.values[1] = "stabilityparam"
zm = footprintdf.L*footprintdf.stabilityparam
footprintdf['zm']=zm
footprintdf.drop(columns=['stabilityparam'],inplace=True)
footprintdf = footprintdf.mean(axis = 0)
test = footprintdf.dropna()

if test.empty:
	test = (footprintdf.interpolate())
	test.dropna(inplace=True)
	if test.empty:
		FFP = myfootprint.FFP2(central_lat=29.509019,central_lon=-91.440917,zm=20., z0=0.1, h=2000., ol=-100., sigmav=0.6,
		ustar=0.4, wind_dir=30,rs= [20., 40., 60., 80.],crop=False,fig = 1,show_heatmap=False)
	else:
		FFP = myfootprint.FFP2(central_lat=29.509019,central_lon=-91.440917,zm=test['zm'], z0=0.1,
		umean=test['wind_speed'], h=2000., ol=test['L'], sigmav=test['v_unrot'],
		ustar=test['u*'], wind_dir=test['wind_dir'],rs= [20., 40., 60., 80.],crop=False,fig = 1,show_heatmap=False)
else:
	FFP = myfootprint.FFP2(central_lat=29.509019,central_lon=-91.440917,zm=test['zm'], z0=0.1,
	umean=test['wind_speed'], h=2000., ol=test['L'], sigmav=test['v_unrot'],
	ustar=test['u*'], wind_dir=test['wind_dir'],rs= [20., 40., 60., 80.],crop=False,fig = 1,show_heatmap=False)

st.write("Footprint model by [Kljun et al (2015)](https://gmd.copernicus.org/articles/8/3695/2015/)")
st.write("Python code for map is [available online](https://footprint.kljun.net/index.php)")
