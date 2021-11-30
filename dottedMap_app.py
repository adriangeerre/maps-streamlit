# Dependencies
import streamlit as st
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import json
import random
from PIL import Image

## HEADER
st.title("Coordinates in Map")

st.markdown("""
#### This app is capable of plotting a map of a region of the world and add dotted points over it.
""")
st.markdown("""**Navigation:** \n""")
st.markdown("""
&emsp; _Country:_ Choose a country and the height and width. The larger the values the larger the zoom out and viceversa.
""")
st.markdown("""
&emsp; _Coordinates:_ provide North/South and East/West coordinates to select the world's region. The larger the distance between N/S and E/W the larger the zoom out and viceversa.
""")
st.markdown("""**Plot data-points:** \n""")
st.markdown("""
&emsp; _Dataset:_ csv file containing longitud and latitude of the points to draw.
""")
st.markdown("""--- \n""")


## INPUT

# Navigation
st.sidebar.header("Navigation")
nav = st.sidebar.radio("Location definition:",["Country", "Coordinates"])

# Countries
f = open('country_coords.json')
coords = json.load(f)
f.close()

if nav == "Country":
	st.sidebar.header("Coordinates")
	country = st.sidebar.selectbox("Country", list(coords.keys()))
	height = st.sidebar.number_input("Height", value=10, min_value=1, max_value=56)
	width = st.sidebar.number_input("Width", value=10, min_value=1, max_value=190)

	st.sidebar.markdown("""**You selected:**""")
	st.sidebar.write(country, "({},{})".format(coords[country][0], coords[country][1]))

	north = coords[country][0] + height
	south = coords[country][0] - height
	east = coords[country][1] + width
	west = coords[country][1] - width

# Coordinates
if nav == "Coordinates":
	st.sidebar.header("Map Coordinates")
	north = st.sidebar.number_input("North", value=-7)
	south = st.sidebar.number_input("South", value=-20)
	east = st.sidebar.number_input("East", value=35)
	west = st.sidebar.number_input("West", value=20)

# Dataframe
df = None
st.sidebar.header("Load CSV file")
file = st.sidebar.file_uploader("Dataframe")
if file is not None:
	df = pd.read_csv(file)
	if len(df.columns) <= 2:
		st.error("Error: dataset must contain at least 2 columns reprsenting latitude and longitud.")

# Column selection
if df is not None:
	opts = list(df.columns)
	opts.append(None)
	lon = st.sidebar.selectbox("Longitud column", options=opts)
	lat = st.sidebar.selectbox("Latitude column", options=[i for i in opts if i != lon])
	c = [lon, lat]
	dots = st.sidebar.selectbox("Color column", options=[i for i in opts if i not in c])
	if lon == None or lat == None:
		st.error("Error: Longitud or Latitud must be selected.")
	if (dots != None and lon == dots) or (dots != None and lat == dots):
		st.error("Error:Coordinates should not be used to color dots.")

	# Sliders
	size = st.sidebar.slider("Dot size", min_value=1, max_value=100)
	legend_size = st.sidebar.slider("Legend size", min_value=5, max_value=20)

# Expander
with st.sidebar.expander("Errors?"):
	st.write("""
			Not all countries accept the _heigth_ and _width_ define and produce an error (e.g. Zambia below 7 for both values). Please, modify the _height_ and _width_.

			_Color_ column should not be equal to _Longitud_ or _Latitude_ columns of the dataframe.
		""")

## Functions
# Map
def plot_basic_map(n, s ,e, w):
	#  Map with dots
	if df is not None:

		# Base Plot
		fig,ax = plt.subplots()
		map = Basemap(projection='merc', resolution = 'l', area_thresh = 1000.0, urcrnrlat=n, llcrnrlat=s, urcrnrlon=e, llcrnrlon=w)
		map.drawcoastlines()
		map.drawcountries()
		map.shadedrelief()
		map.fillcontinents(color = 'white', alpha = 0.3)

		# Colors
		if dots != None:
			colors = {}
			labels = df[dots].unique().tolist()
			random_colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(len(labels))]

			for i in range(len(labels)):
				colors[labels[i]] = random_colors[i]

			df["dotColor"] = [colors[i] for i in df[dots]]

		# Dots
		xs,ys = map(np.asarray(df.Longitud), np.asarray(df.Latitud))
		df['xm'] = xs.tolist()
		df['ym'] = ys.tolist()
		for index,row in df.iterrows():
			map.scatter(row.xm, row.ym, marker = 'o', color = row.dotColor, s = size, alpha = 0.85, label=row[dots])
		# Avoid legend to repeat labels
		handles, labels = ax.get_legend_handles_labels()
		unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
		ax.legend(*zip(*unique), loc="upper left", title = dots, prop=dict(size=legend_size))
		st.write(fig)
	else:
	#  Map without dots
		fig,ax = plt.subplots()
		map = Basemap(projection='merc', resolution = 'l', area_thresh = 1000.0, urcrnrlat=n, llcrnrlat=s, urcrnrlon=e, llcrnrlon=w)
		map.drawcoastlines()
		map.drawcountries()
		map.shadedrelief()
		map.fillcontinents(color = 'white', alpha = 0.3)
		st.write(fig)

def create_dict_colors(dots):
	ncols = df[dots].unique()


# Call function
if st.button("Plot map"):
	plot_basic_map(north, south, east, west)

# Example
with st.expander("Example"):
	image = Image.open('ZambiaExample.png')
	st.image(image, caption='Hunting traps in Zambia (Dot size: 10 & Legend size: 8)')