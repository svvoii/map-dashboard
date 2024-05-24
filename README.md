#### Map Dashboard Visualization of Electric Vehicle Charging Stations Project
(this tutorial is not complete yet, it is still in progress)

The datasets used in this project must be placed in the `data` folder. Sources of the datasets are:  
`https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/` - the link to the data source from `data.gouv.fr` website for electric vehicle charging stations in France. The current name of this dataset used in `streamlit_app.py` is `charging_points.csv`. Data based on (v2.3.1) update as of 2024-04-18.  
If you choos to name this file differently, you must change the name in the `streamlit_app.py` file: `df = pd.read_csv('data/charging_points.csv')`.  



OTHER RESOURCES:  

`https://data.opendatasoft.com/pages/home/` - the link to the data source from `opendatasoft` website.  
`https://geoservices.ign.fr/telechargement-api` - the link to the data source from `IGN` website.  
`https://docs.streamlit.io/` - the link to the `streamlit` documentation.  

#### Before running the streamlit app, the following steps must be taken

##### Preparing the virtual environment
Run these commands in the root directory of this project before running the streamlit app:  
`python -m venv .venv` - to create a virtual environment  
`source .venv/bin/activate` - to activate the virtual environment  
`python -m pip install pandas` - to install pandas  
`python -m pip install python-dotenv` - to install python-dotenv (for loading Google API key as an environment variable)  
`python -m pip install tqdm` - to install tqdm which is a progress bar library which is used in `exract_geocode.py`. Not necessary is the `location_data.csv` file is already in the `data` folder.    
`python -m pip install streamlit` - to install streamlit  
`python -m pip install streamlit-folium` - to install streamlit-folium which is a streamlit wrapper for folium to create interactive maps.  
`python -m pip install unidecode` - to install unicode (used to deal with french specific characters in the data).  
`python -m pip install plotly` - to install plotly (used to create interactive plots, barcharts).  

`pip install --upgrade pip` - to upgrade pip  

TO LAUNCH THE SCRIPT FOR ALL THE INSTALLATIONS:  
`chmod +x setup.sh` - to make the script executable  
`./setup.sh` - to run the script  

##### Preprocessing the data !!! careful with google API - it is EXPENSIVE !!!
In this project we filter the data by regions in France. The open-data is incomplete and some of the atributes of the addresses are missing. We use Google API to extract the missing data. In `data` folder there shall be `location_data.csv` file which contains the extracted data from Google API.  
If the file is not there proceed with the following command (google maps API key required !!!).    
If the file is there, proceed skip the following command.  
So, before running the streamlit app, we run the following:  
`python extract_geocode.py` - to extract the address data from Google API given the gps coordinates. There will be a progress bar to show the progress of the extraction (it took around 45 min to receive the data via Google API the first time).    
Requested data was only fo the missing values in `code_postal` wich are unique based on the `consolidated_longitude` and `consolidated_latitude` columns from the initial open source dataset from `data.gouv.fr` [here](https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/)  
(there was 25154 unique values, which cost around 75EUR of free trial credit !!).  

##### Running the streamlit app
Once the data is preprocessed, we can run the streamlit app:
`streamlit run streamlit_app.py` - to run the streamlit app  


#### ABOUT THE PROJECT  

##### Department Structure in France

There are 101 departments which belong to France.  
96 departments compose the mainland France (from 01 to 95 where 20 is the Corsica island devided into 2A and 2B as 2 departments).  
5 departments are overseas territories (971, 972, 973, 974, 976).  

In this project we are visualizing the electric vehicle charging stations in France by departments excluding the overseas territories.  

More information about the departments in France can be found [here](https://www.regions-et-departements.fr/departements-francais?utm_content=cmp-true)  


...  
