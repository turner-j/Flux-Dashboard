import streamlit as st
import sys
import calc_footprint_FFP3 as myfootprint
from loadingfluxdata import getfluxes
import folium
from streamlit_folium import st_folium
from ridge_map import RidgeMap
import matplotlib.pyplot as plt
from geopandas.tools import geocode
sys.path.append(r'\FFP_Python')

st.set_page_config(
    page_title="Flux Tower Dashboard",
    page_icon=":large_green_circle:")

st.write("# :rainbow[Welcome to the Atchafalaya Delta Flux Tower Dashboard]")

st.markdown("""
    **👈 Select a plot type from the sidebar** to plot real-time data from US-Atf.""")

df = getfluxes()

# drop columns with all NaN's
df.dropna(axis=1, how='all',inplace= True)


# Function to plot ridge map
def plot_ridge_map(bbox, num_lines, lake_flatness, water_ntile, vertical_ratio, linewidth, colormap, map_name):
    rm = RidgeMap(bbox)
    values = rm.get_elevation_data(num_lines=num_lines)
    values = rm.preprocess(values=values, lake_flatness=lake_flatness, water_ntile=water_ntile, vertical_ratio=vertical_ratio)
    fig, ax = plt.subplots(figsize=(12, 8))
    rm.plot_map(values=values, ax=ax, label=map_name, label_y=0.1, label_x=0.55, label_size=40, linewidth=linewidth, line_color=plt.get_cmap(colormap), kind='elevation')
    st.pyplot(fig)

# Sidebar plot parameters
map_name = ""
num_lines = 100
linewidth = 2.0
vertical_ratio = 150
lake_flatness = 2.0
water_ntile = 0
colormap = 'coolwarm'

lat, lon = 29.509019, -91.440917  # Default center location

# Extract bbox coordinates from the current map view
bbox = (-91.46521568298341, 29.492953421864062, -91.42230033874513, 29.519097995625405)

st.write("Bounding box with coordinates:", bbox)
plot_ridge_map(bbox, num_lines, lake_flatness, water_ntile, vertical_ratio, linewidth, colormap, map_name)    

st.markdown(
    """
    ### Want to view more data?
    - Download source code from [github](https://github.com/turner-j)
    - Search for data on [AmeriFlux](https://ameriflux.lbl.gov/login/?redirect_to=/data/download-data/)
"""
)

st.write("View source code for [Streamlit Ridge Map](https://github.com/deepcharts/Ridge-Map-Streamlit/tree/main).")

st.dataframe(df)
