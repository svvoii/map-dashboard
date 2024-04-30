import os # for using os.path.exists to check if a file exists
import streamlit as st # for creating the web app with streamlit framework
import pandas as pd # for data manipulation
import ast # for converting string to dictionary using ast.literal_eval
import json # for converting dictionary to string using json.dumps
import folium # for creating maps from GeoJSON data
import streamlit_folium as folium_static # for displaying maps in Streamlit
from streamlit_folium import st_folium # for displaying maps in Streamlit


APP_TITLE = "Map Dashboard"

@st.cache_data # Caching the data to avoid loading it multiple times
def load_dataset():
	charging_points = pd.read_csv("data/charging_points.csv", dtype=str)
	location_data = pd.read_csv("data/location_data.csv", dtype=str)
	voitures = pd.read_csv("data/voitures.csv", sep=";", dtype=str)
	insee_code = pd.read_csv("data/insee_code.csv", sep=";", dtype=str)
	return charging_points, location_data, voitures, insee_code

# @st.cache_data # Caching the data to avoid loading it multiple times
# def load_dataset():
# 	charging_points = pd.read_csv("data/charging_points.csv", low_memory=True)

# 	location_data = pd.read_csv("data/location_data.csv", low_memory=True, dtype={
# 		'consolidated_latitude': 'float',
# 		'consolidated_longitude': 'float',
# 		'location_data': 'str',
# 		'code_postal': 'str',
# 	})

# 	voitures = pd.read_csv("data/voitures.csv", sep=";", low_memory=True, dtype={
# 		'codgeo': 'str',
# 		'libgeo': 'str',
# 		'epci': 'str',
# 		'libepci': 'str',
# 		'date_arrete': 'str',
# 		'nb_vp_rechargeables_el': 'int',
# 		'nb_vp_rechargeables_gaz': 'int',
# 		'nb_vp': 'int',
# 	})

# 	insee_code = pd.read_csv("data/insee_code.csv", sep=";", low_memory=True, dtype={
# 		'Code INSEE': 'str',
# 		'Code Postal': 'str',
# 		'Commune': 'str',
# 		'Département': 'str',
# 		'Région': 'str',
# 		'Statut': 'str',
# 		'Altitude Moyenne': 'int',
# 		'Superficie': 'int',
# 		'population': 'str',
# 		'geo_point_2d': 'str',
# 		'geo_shape': 'object',
# 		'ID Geofla': 'str',
# 		'Code Commune': 'int',
# 		'Code Canton': 'int',
# 		'Code Arrondissement': 'int',
# 		'Code Département': 'object',
# 		'Code Région': 'int', 
# 	})
# 	# insee_code = pd.read_csv("data/INSEE_to_codpostal.csv", delimiter=";", encoding="ISO-8859-1").rename(str.strip, axis='columns')
# 	return charging_points, location_data, voitures, insee_code

@st.cache_data # Caching the data to avoid loading it multiple times
def extract_postal_code(location_data): # This will extract postal code from the location_data file (received via google API)
	location_data_list = []
	postal_codes = []
	for index, row in location_data.iterrows():
		location_data_dict = ast.literal_eval(row["location_data"])
		location_data_list.append(location_data_dict)

		# Extract address components and find postal code
		postal_code = None # there still some missing values so we add None
		address_components = location_data_dict["address_components"]
		for component in address_components:
			if "postal_code" in component["types"]:
				postal_code = component["long_name"]
				break
		postal_codes.append(postal_code)
	
	# Adding new column to location_data
	location_data["code_postal"] = postal_codes
	return location_data

# This will display the number of missing values in each column (missing in RED, no missing in GREEN)
@st.cache_data
def display_missing_values(charging_points):
	st.write(f"DEBUG: Missing values in :")
	for column in charging_points.columns:	
		missing_values = charging_points[column].isna().sum()
		if missing_values > 0:
			st.markdown(f"<font color='red'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
		else:
			st.markdown(f"<font color='green'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)


def render_map(df):

	map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron', scrollWheelZoom=False)

	points_by_department = df['depart_code'].value_counts().reset_index()
	points_by_department.columns = ['depart_code', 'count']

	choropleth = folium.Choropleth(
		geo_data="data/france_departments.geojson",
		# data=df,
		data=points_by_department,
		columns=['depart_code', 'count'],
		key_on='feature.properties.code',	
		line_opacity=0.8,
		line_color='black',
		highlight=True,
	)
	choropleth.geojson.add_to(map)

	# choropleth.geojson.add_child(
	# 	folium.features.GeoJsonTooltip(['nom'], labels=False)
	# )

	st_map = st_folium(map, width=800, height=600)

def display_year_filter(charging_points):
	year_list = ['All'] + sorted(list(charging_points['year'].unique()), reverse=True)
	year = st.sidebar.selectbox('Select Year', year_list, 0)
	st.header(f'{year}')

	if year != "All":
		filtered_data = charging_points[charging_points['year'] == year]
	else:
		filtered_data = charging_points

	# st.write(f"Number of points: {filtered_data.shape[0]}")
	return year

def display_department_filter(charging_points):
	department_list = ['All'] + sorted([str(x) for x in charging_points['depart_code'].unique() if str(x) != 'nan'])
	department_code = st.sidebar.selectbox('Department', department_list, 0)
	# st.session_state['department_code'] = st.sidebar.selectbox('Department', department_list, department_list.index(st.session_state['department_code']))
	# return st.session_state['department_code']
	return department_code

def display_metrics(charging_points, year, department_code):
	col1, col2, col3 = st.columns(3)
	col1.metric("Number of e-points", '{:,}'.format(charging_points.shape[0]))
	col2.metric("Year", year)
	col3.metric("Department", department_code)

def main():
	st.set_page_config(APP_TITLE)
	st.title(APP_TITLE)
	st.caption("A simple dashboard to display maps and data tables. made by: `Serge` and `Nammi`. `Plug-In Progress`")

	charging_points, location_data, voitures, insee_code = load_dataset() # Loading data from CSV files

	location_data = extract_postal_code(location_data) # Extracting postal_code from location_data

	# Renaming columns in location_data to correspond with the charging_points data
	location_data = location_data.rename(columns={'longitude': 'consolidated_longitude', 'latitude': 'consolidated_latitude'})
	location_data.to_csv("data/location_data.csv", index=False) # Saving to the same file

	# Merge postal code data into charging points data (after this still 832 missing values in code_postal column, which is less than 1% of the total data)
	charging_points = pd.merge(charging_points, location_data[['consolidated_longitude', 'consolidated_latitude', 'code_postal']], on=['consolidated_longitude', 'consolidated_latitude'], how='left')
	charging_points['consolidated_code_postal'] = charging_points['consolidated_code_postal'].fillna(charging_points['code_postal']) # Fill missing values in 'consolidated_code_postal' with 'code_postal'	

	# to fill missing 832 values we use the `adresse_station` column and extract it from there with regex and fill the missing values in `consolidated_code_postal`
	charging_points['extracted_code_postal'] = charging_points['adresse_station'].str.extract(r"(\d{5})")
	charging_points['consolidated_code_postal'] = charging_points['consolidated_code_postal'].fillna(charging_points['extracted_code_postal']) # Fill missing values in 'consolidated_code_postal' with 'extracted_code_postal'

	# ##### #
	# After this last extraction and merging the amount of missing values in `consolidated_code_postal' is negligible (~ 12-20))
	# Now we can use the `consolidated_code_postal` column to break down the data by regions and display it on the map !!
	# ##### #

	# Now we can use the `consolidated_code_postal` column to break down the data by regions and display it on the map
	charging_points['depart_code'] = charging_points['consolidated_code_postal'].str[:2] # Extract the first two digits of the postal code to get the commune

	############################################
	# CHARGING POINTS DATA
	postal_code = "consolidated_code_postal"
	missing_postal_code = charging_points[charging_points[postal_code].isna()]
	commune = "consolidated_commune"
	charging_points_by_department = charging_points['depart_code'].value_counts()

	### DISPLAYING FILTERS AND MAP ###
	# the following line will create a new column `year` in the charging_points dataframe
	# charging_points['year'] = pd.to_datetime(charging_points['date_maj']).dt.year
	charging_points['year'] = pd.to_datetime(charging_points['created_at']).dt.year.astype(str)

	year = display_year_filter(charging_points)
	department_code = display_department_filter(charging_points)
	if year != "All":
		charging_points = charging_points[charging_points['year'] == year]
	if department_code != "All":
		charging_points = charging_points[charging_points['depart_code'] == department_code]
 
	# display_missing_values(charging_points)
 
	render_map(charging_points)

	display_metrics(charging_points, year, department_code)

	# st.write(f"DEBUG: Number of rows where [{postal_code}] is missing, TOTAL (with duplicates) [{missing_postal_code.shape[0]}], list without duplicates :")
	# st.write(missing_postal_code[['adresse_station', 'consolidated_code_postal', 'consolidated_commune', 'extracted_code_postal']].drop_duplicates())
	# st.write(missing_postal_code['adresse_station'].unique())

	st.write(f"Charging points. TOTAL (rows, columns):")
	st.write(charging_points.shape)
	st.write(charging_points.head())
	# st.write(charging_points.columns)

	# st.write(charging_points[['year', 'date_maj', 'created_at', 'last_modified', 'depart_code', 'code_insee_commune']])

	############################################
	# INSEE CODE DATA

	insee_code = insee_code.rename(columns={'Code INSEE': 'codgeo'})
	insee_code = insee_code.rename(columns={'Code Postal': 'code_postal'})
	insee_code = insee_code.rename(columns={'Code Département': 'depart_code'})

	# MERGING INSEE CODE INTO VOITURES DATA (on 'codgeo')
	voitures = voitures.merge(insee_code[['codgeo', 'code_postal', 'depart_code']], on='codgeo', how='left')

	############################################
	# VOITURES DATA

	voitures['year'] = pd.to_datetime(voitures['date_arrete']).dt.year.astype(str)
	voitures['nb_vp_rechargeables_el'] = pd.to_numeric(voitures['nb_vp_rechargeables_el'], errors='coerce')

	st.write(f"Voitures. TOTAL (rows, columns):")
	st.write(voitures.shape)
	st.write(voitures.head())

	# AGGREGATING AND MERGING DATA FROM BOTH DATASETS (charging_points and voitures)
	charging_points_agg = charging_points.groupby(['depart_code', 'year']).size().reset_index(name='num_epoints')
	voitures_agg = voitures.groupby(['depart_code', 'year'])['nb_vp_rechargeables_el'].sum().reset_index()

	merged_data = pd.merge(charging_points_agg, voitures_agg, on=['depart_code', 'year'], how='outer')

	st.write(f"Merged data. TOTAL (rows, columns):")
	st.write(merged_data.shape)
	# st.write(merged_data.head())
	st.write(merged_data)

	# show_map(merged_data)
	# render_map(merged_data)


if __name__ == "__main__":
    main()


	# MISSING DATA VISUAL (around 185 unique missing values in code_postal, negligible):
	# missing_data = voitures[voitures['code_postal'].isna()]
	# unique_missing_data = missing_data[['codgeo', 'libgeo', 'code_postal', 'Code Département']].drop_duplicates()
	# st.write(f"Number of rows where [code_postal] is missing, TOTAL (with duplicates) [{missing_data.shape[0]}], list without duplicates [{unique_missing_data.shape[0]}] :")
	# st.write(missing_data[['codgeo', 'libgeo', 'code_postal', 'Code Département']].drop_duplicates())
