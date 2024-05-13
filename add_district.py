#add liegislative districts to lara and mhvillage data

import pandas as pd
import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import Point
import geopy
from geopy.geocoders import Nominatim


def check_legislative_district(lat, lng, districts_geojson):
    point = Point(lng, lat)
    # Load the legislative districts GeoJSON file
    districts = gpd.read_file(districts_geojson)
    
    # Create a spatial index
    spatial_index = districts.sindex
    
    # Possible matches indices using spatial index
    possible_matches_index = list(spatial_index.query(point))
    possible_matches = districts.iloc[possible_matches_index]
    
    # Check which district the point is in
    precise_matches = possible_matches[possible_matches.contains(point)]
    
    if not precise_matches.empty:
        # Assuming 'district_name' is the column name with the district names.
        return precise_matches.iloc[0]['NAME']  # Replace 'district_name' with the actual column name
    
    return None

path2folder = r"./data/" # fill in the path to your folder here.
assert len(path2folder) > 0

mhvillage_df = pd.read_csv(path2folder + r"MHVillageAll_Dec7_dropna.csv")
lara_df = pd.read_csv(path2folder + r"LARA_with_all_coord.csv")
# Path to your legislative districts GeoJSON file
house_districts_geojson_path = "/Users/hkt/Michigan_housing/Michigan_State_House_Districts_2021.geojson"
senate_districts_geojson_path = "/Users/hkt/Michigan_housing/Michigan_State_Senate_Districts_2021.geojson"
#tracts_shapefile = gpd.read_file(path2folder+r"tl_2019_26_tract.shp")

# sLength = len(mhvillage_df['Longitude'])
# mhvillage_df['House'] = pd.Series(np.zeros(sLength), index=mhvillage_df.index)
# mhvillage_df['Senate'] = pd.Series(np.zeros(sLength), index=mhvillage_df.index)


# for ind in range(len(mhvillage_df)):
#     lon = float(mhvillage_df['Longitude'].iloc[ind])
#     lat = float(mhvillage_df['Latitude'].iloc[ind])
#     if lat and lon:
#             # Check the legislative district
#     	district_house = check_legislative_district(lat, lon, house_districts_geojson_path)
#     	district_senate = check_legislimative_district(lat, lon, senate_districts_geojson_path)
#     	if district_senate and district_house:
#     		print(district_senate)
#     		print(district_house)
#     		mhvillage_df.loc[ind,'House'] = int(district_house)
#     		mhvillage_df.loc[ind,'Senate'] = int(district_senate)

sLength = len(lara_df['longitude'])
lara_df['House'] = pd.Series(np.zeros(sLength), index=lara_df.index)
lara_df['Senate'] = pd.Series(np.zeros(sLength), index=lara_df.index)

for ind in range(len(lara_df)):
    lon = float(lara_df['longitude'].iloc[ind])
    lat = float(lara_df['latitude'].iloc[ind])
    if lat and lon:
            # Check the legislative district
    	district_house = check_legislative_district(lat, lon, house_districts_geojson_path)
    	district_senate = check_legislative_district(lat, lon, senate_districts_geojson_path)
    	if district_senate and district_house:
    		print(district_senate)
    		print(district_house)
    		lara_df.loc[ind,'House'] = int(district_house)
    		lara_df.loc[ind,'Senate'] = int(district_senate)

#mhvillage_df.to_csv('data/MHVillageDec7_Legislative.csv') 
lara_df.to_csv('data/LARA_with_coord_and_legislative_district.csv')

 