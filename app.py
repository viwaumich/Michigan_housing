from shiny import *
from shinywidgets import output_widget, render_widget
import ipyleaflet as L
from ipyleaflet import Map, GeoJSON, LayersControl, WidgetControl
from ipywidgets import Label
import shapely
from shapely.geometry import Point
from branca.colormap import linear
import matplotlib.pyplot as plt
import math
import json
import pandas as pd
import geopandas as gpd
import requests
from geopy.geocoders import Nominatim



# Step 1: Geocoding the address using OpenStreetMap's Nominatim
def geocode_address(address):
    geolocator = Nominatim(user_agent="your_application_name")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Step 2: Check the legislative district
# Step 2: Check the legislative district
def check_legislative_district(lat, lng, districts_geojson):
    point = Point(lng, lat)
    # Load the legislative districts GeoJSON file
    districts = gpd.read_file(districts_geojson)
    
    # Check which district the point is in
    for _, district in districts.iterrows():
        if point.within(district['geometry']):  # 'geometry' is a special key used by GeoPandas
            # Returning the entire row as a dictionary
            return district['NAME']
    
    return None

path2folder = r"./data/" # fill in the path to your folder here.
assert len(path2folder) > 0

mhvillage_df = pd.read_csv(path2folder + r"MHVillageAll_Dec7_dropna.csv")
lara_df = pd.read_excel(path2folder + r"LARA_with_coord.xlsx")
# Path to your legislative districts GeoJSON file
house_districts_geojson_path = "/Users/hkt/Michigan_housing/Michigan_State_House_Districts_2021.geojson"
senate_districts_geojson_path = "/Users/hkt/Michigan_housing/Michigan_State_Senate_Districts_2021.geojson"
#tracts_shapefile = gpd.read_file(path2folder+r"tl_2019_26_tract.shp")

circlelist = []
mklist = []
upper_layers = []
lower_layers = []




def extract_coordinates(df):
    def rev(lst):
        return [lst[1],lst[0]]
    features = []
    for i in range(len(df)):
        if isinstance( df['geometry'].iloc[i], shapely.geometry.polygon.Polygon):
            cr = [[rev(list(i)) for i in df['geometry'].iloc[i].exterior.coords]]
        else:
            cr = [[rev(list(i)) for i in poly.exterior.coords] for poly in list(df['geometry'].iloc[i].geoms)]
        features.append(cr)
    return features


def build_district_layers(upper=0):
    if upper == 1:
        if len(upper_layers) > 0:
            return
        tracts_shapefile = gpd.read_file(path2folder+"/cb_2022_26_sldu_500k.shp")
        color = 'green'
    else:
        if len(lower_layers) > 0:
            return
        tracts_shapefile = gpd.read_file(path2folder+"/cb_2022_26_sldl_500k.shp")
        color = 'purple'
    layerk = L.Polygon(
        locations = extract_coordinates(tracts_shapefile),
        color=color,
        fill_color = color,
        dash_array='2, 3',    # Set the dash pattern (5 pixels filled, 10 pixels empty)
        weight=2, 
    )
    if upper == 1:
        upper_layers.append(layerk)
    else:
        lower_layers.append(layerk)
    return
    

def build_marker_layer():
    if len(circlelist) >0  and len(mklist)>0:
        return
    leng = 0
    for ind in range(len(mhvillage_df)):
        lon = float(mhvillage_df['Longitude'].iloc[ind])
        lat = float(mhvillage_df['Latitude'].iloc[ind])
        if lat and lon:
            # Check the legislative district
            district_house = check_legislative_district(lat, lon, house_districts_geojson_path)
            district_senate = check_legislative_district(lat, lon, senate_districts_geojson_path)

        markeri = L.Marker(
            location=(lat,lon),
            draggable=False,
            title=str(mhvillage_df['Name'].iloc[ind])+
            ' , number of sites: '+str(mhvillage_df['Sites'].iloc[ind])+
            ' , average rent: '+str(mhvillage_df['Average_rent'].iloc[ind])+
            ' , House district: '+str(district_house)+
            ' , Senate district: '+str(district_senate)+
            ' , url: %s'%str(mhvillage_df['Url'].iloc[ind]) +
            ' , MHVillage')
        circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")

        circlelist.append(circlei)
        mklist.append(markeri) 


    for ind in range(len(lara_df)):
        lon = float(lara_df['Longitude'].iloc[ind])
        lat = float(lara_df['Latitude'].iloc[ind])
        if lat and lon:
            # Check the legislative district
            district_house = check_legislative_district(lat, lon, house_districts_geojson_path)
            district_senate = check_legislative_district(lat, lon, senate_districts_geojson_path)

        if lon == 0 and lat == 0:
            continue
        markeri = L.Marker(
            location=(lat,lon),
            draggable=False,
            title=str(lara_df['Owner / Community_Name'].iloc[ind])+
            ' , number of sites: '+str(lara_df['Total_#_Sites'].iloc[ind])+
            ' , House district: '+str(district_house)+
            ' , Senate district: '+str(district_senate)+
            ', LARA')
        circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")

        circlelist.append(circlei)
        mklist.append(markeri)   
    return 

def build_infographics1():
    def modify(string):
        return string[0] + string[1:].lower()
    # Calculating the total number of sites for each unique name
    total_sites_by_name = lara_df[['County',"Total_#_Sites"]].dropna().groupby('County').sum()
    total_sites_by_name = total_sites_by_name.sort_values(by="Total_#_Sites",ascending=False)
    totnum = -1
    plt.clf()
    plt.close()    
    plt.bar(range(len(total_sites_by_name))[:totnum], total_sites_by_name['Total_#_Sites'][:totnum])
    plt.xticks(range(len(total_sites_by_name))[:totnum], [modify(na) for na in total_sites_by_name.index[:totnum]], fontsize=4, rotation=60)
    plt.ylabel('Total Number of Sites')
    plt.title('Total number of sites in each county (LARA)')
    return

def build_infographics2():
    total_sites_by_name = mhvillage_df[['County',"Average_rent"]].dropna().groupby('County').mean()
    total_sites_by_name = total_sites_by_name.sort_values(by="Average_rent",ascending=False)
    totnum = -1
    plt.clf()
    plt.close()    
    plt.bar(range(len(total_sites_by_name))[:totnum], total_sites_by_name['Average_rent'][:totnum])
    
    plt.xticks(range(len(total_sites_by_name))[:totnum], total_sites_by_name.index[:totnum], fontsize=4, rotation=60)
    plt.ylabel('Average rent')
    plt.title('Average rent in each county (MHVillage)')
    return

basemaps = {
  "OpenStreetMap": L.basemaps.OpenStreetMap.Mapnik,
  "Satellite": L.basemaps.Gaode.Satellite,
  "WorldStreetMap": L.basemaps.Esri.WorldStreetMap,
  "NatGeoWorldMap": L.basemaps.Esri.NatGeoWorldMap
}

layernames = ["Marker (name, address, # sites, source)", "Circle (location only)", "Legislative districts (Michigan State Senate)", "Legislative districts (Michigan State House of Representatives)"]
app_ui = ui.page_fluid(
    ui.HTML("<hr> <h1>Maps</h1>"),
    output_widget("map"),
    ui.input_select(
        "basemap", "Choose a basemap",
        choices=list(basemaps.keys())
    ),
    ui.input_selectize("layers", "Layers to visualize", layernames, multiple=True),
    
    ui.HTML("<hr> <h1>Infographics</h1>"),
    ui.output_plot("infographics1"),
    ui.output_plot("infographics2"),

    ui.HTML("<hr> <h1>Tables</h1>"),
    ui.input_selectize("county", "Select a county", sorted(list(mhvillage_df['County'].unique())), ),
    ui.input_selectize("datasource", "Select a source", choices=['MHVillage', 'LARA'], ),
    ui.output_table("site_list"),
    
)

def server(input, output, session):
    @output
    @render_widget
    def map():
        basemap = basemaps[input.basemap()]
        layerlist = input.layers()

        the_map = L.Map(basemap=basemap, 
                     center=[41.84343571548758,-84.36155640717737], 
                     zoom=5)
        markerorcircle = False
        if "Marker (name, address, # sites, source)" in layerlist:
            build_marker_layer()
            marker_cluster = L.MarkerCluster(
                name='location markers',
                markers=tuple(mklist)
                )
            the_map.add_layer(marker_cluster)
            markerorcircle = True
        if "Circle (location only)" in layerlist:
            if not markerorcircle:
                build_marker_layer()
            layergroup = L.LayerGroup(name = 'location circles',layers=circlelist)
            the_map.add_layer(layergroup)
            markerorcircle = True
        if "Legislative districts (Michigan State Senate)" in layerlist:
            build_district_layers(upper = 1)
            the_map.add_layer(upper_layers[0])
        if "Legislative districts (Michigan State House of Representatives)" in layerlist:
            build_district_layers(upper = 0)
            the_map.add_layer(lower_layers[0])
        return the_map
    
    @output
    @render.plot
    def infographics1():
        build_infographics1()

    @output
    @render.plot
    def infographics2():
        build_infographics2()
     
    @output
    @render.table
    def site_list():
        if input.datasource() == 'MHVillage':
            return (mhvillage_df[mhvillage_df['County'] == input.county()][['Name','Sites','FullstreetAddress']]).sort_values('Name')
        else:
            return lara_df[lara_df['County'] == input.county().upper()[1:-1]][['Owner / Community_Name','Total_#_Sites','Location_Address']].sort_values('Owner / Community_Name')
app = App(app_ui, server)