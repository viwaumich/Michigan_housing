from shiny import *
from shiny import reactive
from shinywidgets import output_widget, render_widget
from shiny.express import render
#from ipywidgets import Label
import ipyleaflet as L
from ipyleaflet import GeoJSON, LayersControl, WidgetControl
# import shapely
# from shapely.geometry import Point
#import matplotlib.pyplot as plt
import seaborn as sns
#import math
#import json
import geojson
import pandas as pd
import geopandas as gpd
#from geopy.geocoders import Nominatim
import numpy as np



# Step 1: Geocoding the address using OpenStreetMap's Nominatim
def geocode_address(address):
    geolocator = Nominatim(user_agent="your_application_name")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Step 2: Check the legislative district [from GPT-4]
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

mhvillage_df = pd.read_csv(path2folder + r"MHVillageDec7_Legislative.csv")
lara_df = pd.read_csv(path2folder + r"LARA_with_coord_and_legislative_district.csv")

# Path to your legislative districts GeoJSON file
house_districts_geojson_path = r"./data/" + r"Michigan_State_House_Districts_2021.geojson"
senate_districts_geojson_path = r"./data/" + r"Michigan_State_Senate_Districts_2021.geojson"
#tracts_shapefile = gpd.read_file(path2folder+r"tl_2019_26_tract.shp")

circlelist = []
mklist = []
upper_layers = []
lower_layers = []

labels_df =  pd.DataFrame(range(1, 51), columns=['Numbers'])


# def extract_coordinates(df):
#     def rev(lst):
#         return [lst[1],lst[0]]
#     features = []
#     for i in range(len(df)):
#         if isinstance( df['geometry'].iloc[i], shapely.geometry.polygon.Polygon):
#             cr = [[rev(list(i)) for i in df['geometry'].iloc[i].exterior.coords]]
#         else:
#             cr = [[rev(list(i)) for i in poly.exterior.coords] for poly in list(df['geometry'].iloc[i].geoms)]
#         features.append(cr)
#     return features



def build_district_layersـalpha(upper=0):
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
        hover_style={
                'color': 'orange', 
                'fill_color': 'orange', 
                'weight': 3
            }
    )
    if upper == 1:
        upper_layers.append(layerk)
    else:
        lower_layers.append(layerk)
    return


def build_district_layers(upper=0):
    if upper == 1:
        if len(upper_layers) > 0:
            return
        tracts_shapefile = gpd.read_file(path2folder+"/cb_2022_26_sldu_500k.shp")
        color = 'green'
        geojson_path = senate_districts_geojson_path
        with open(geojson_path, 'r') as f:
            michigan_districts_data = geojson.load(f)
        #michigan_districts_data = pd.read_json(geojson_path)
        #print(michigan_districts_data)
    else:
        if len(lower_layers) > 0:
            return
        tracts_shapefile = gpd.read_file(path2folder+"/cb_2022_26_sldl_500k.shp")
        sLength = len(tracts_shapefile['geometry'])
        tracts_shapefile['labels'] = pd.Series(np.array(range(sLength))+1)
        color = 'purple'
        geojson_path = house_districts_geojson_path
        with open(geojson_path, 'r') as f:
            michigan_districts_data = geojson.load(f)
    layerk =  L.GeoJSON(
            data=michigan_districts_data,
            name='Michigan House Legislative Districts',
            style={
                'color': color,
                'weight': 1,
                'fillOpacity': 0.3
            },
            hover_style={
                'color': 'orange', 
                'weight': 3
            }
        )

        # Add mouseover event
    #layerk.on_hover(lambda feature, **kwargs: update_tooltip(feature['properties'], **kwargs))


    # L.Polygon(
    #     locations = extract_coordinates(tracts_shapefile),
    #     color=color,
    #     fill_color = color,
    #     dash_array='2, 3',    # Set the dash pattern (5 pixels filled, 10 pixels empty)
    #     weight=2, 
    # )
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

        if pd.isna(lara_df['House'].iloc[ind]) or pd.isna(lara_df['Senate'].iloc[ind]):
            house = "missing"
            senate = "missing"
        else:
            house = round(lara_df['House'].iloc[ind])
            senate = round(lara_df['Senate'].iloc[ind])

        if pd.isna(mhvillage_df['Sites'].iloc[ind]):
            mhsites = "missing"
        else:
            mhsites = round(mhvillage_df['Sites'].iloc[ind])
        #if lat and lon:
            # Check the legislative district
            #district_house = check_legislative_district(lat, lon, house_districts_geojson_path)
            #district_senate = check_legislative_district(lat, lon, senate_districts_geojson_path)

        markeri = L.Marker(
            location=(lat,lon),
            draggable=False,
            title=str(mhvillage_df['Name'].iloc[ind])+
            ' , number of sites: '+str(mhsites)+
            ' , average rent: '+str(mhvillage_df['Average_rent'].iloc[ind])+
            ' , House district: '+str(house)+
            ' , Senate district: '+str(senate)+
            ' , url: %s'%str(mhvillage_df['Url'].iloc[ind]) +
            ' , MHVillage')
        circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")

        circlelist.append(circlei)
        mklist.append(markeri) 


    for ind in range(len(lara_df)):
        lon = float(lara_df['longitude'].iloc[ind])
        lat = float(lara_df['latitude'].iloc[ind])
        house = "missing"
        senate = "missing"

        if pd.isna(lara_df['House'].iloc[ind]) or pd.isna(lara_df['Senate'].iloc[ind]):
            house = "missing"
            senate = "missing"
        else:
            house = round(lara_df['House'].iloc[ind])
            senate = round(lara_df['Senate'].iloc[ind])

        if pd.isna(lara_df['Total_#_Sites'].iloc[ind]):
            larasites = "missing"
        else:
            larasites = round(lara_df['Total_#_Sites'].iloc[ind])

        if lon == 0 and lat == 0:
            continue
        try:
            markeri = L.Marker(
                location=(lat,lon),
                draggable=False,
                title=str(lara_df['Owner / Community_Name'].iloc[ind])+
                ' , number of sites: '+str(round(lara_df['Total_#_Sites'].iloc[ind]))+
                ' , House district: '+ str(house)+
                ' , Senate district: '+ str(senate)+
                ', LARA')
            circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")

        except:
            #print(lon,lat)
            continue

        circlelist.append(circlei)
        mklist.append(markeri)   
    return 


def build_infographics1():
    #def modify(string):
    #    return string[0] + string[1:].lower()
    # Calculating the total number of sites for each unique name
    total_sites_by_name = lara_df[['County',"Total_#_Sites"]].dropna().groupby('County').sum()
    total_sites_by_name = total_sites_by_name.sort_values(by="Total_#_Sites",ascending=False)
    totnum = 20
    total_sites_by_name = total_sites_by_name.iloc[:totnum,:]
    sns.set_color_codes("pastel")
    sns.barplot(x="Total_#_Sites", y="County", data=total_sites_by_name,
                label="Total Number of Sites", color="b")
    #plt.ylabel('Total Number of Sites')
    #plt.title('Total number of sites in each county (LARA)')
    return

def build_infographics2():
    total_sites_by_name = mhvillage_df[['County',"Average_rent"]].dropna().groupby('County').mean()
    total_sites_by_name = total_sites_by_name.sort_values(by="Average_rent",ascending=True)
    # Drop rows where 'second_column' is empty
    df_clean = mhvillage_df[['County',"Average_rent"]].dropna()
    county_counts = df_clean['County'].value_counts()
    total_sites_by_name_count = pd.concat([total_sites_by_name,county_counts], axis=1)
    total_sites_by_name_count_20 = total_sites_by_name_count.sort_values(by="count",ascending=False)
    total_sites_by_name_count_20 = total_sites_by_name_count_20[:20].sort_values(by="Average_rent",ascending=True)
    totnum = -1

    county = total_sites_by_name_count_20[:totnum].index
    count0 = total_sites_by_name_count_20['count'][:totnum]
    y_pos = range(len(total_sites_by_name_count_20[:totnum]))

    ax = sns.barplot(x="Average_rent", y="County", data=total_sites_by_name_count_20,
                label="Average rent", color="b")
    count0 = total_sites_by_name_count_20['count']

    ax.bar_label(ax.containers[0], labels=[f'{c:.0f}' for c in count0],
              label_type = 'center', color='w', fontsize=10)
    return

def build_infographics1_test():
        
    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=(6, 15))

    # Load the example car crash dataset
    crashes = sns.load_dataset("car_crashes").sort_values("total", ascending=False)
    print(crashes)
    # Plot the total crashes
    sns.set_color_codes("pastel")
    sns.barplot(x="total", y="abbrev", data=crashes,
                label="Total", color="b")

    # Plot the crashes where alcohol was involved
    sns.set_color_codes("muted")
    sns.barplot(x="alcohol", y="abbrev", data=crashes,
                label="Alcohol-involved", color="b")

    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=True)
    ax.set(xlim=(0, 24), ylabel="",
           xlabel="Automobile collisions per billion miles")
    sns.despine(left=True, bottom=True)
    return


basemaps = {
  "OpenStreetMap": L.basemaps.OpenStreetMap.Mapnik,
  "Satellite": L.basemaps.Gaode.Satellite,
  "WorldStreetMap": L.basemaps.Esri.WorldStreetMap,
  "NatGeoWorldMap": L.basemaps.Esri.NatGeoWorldMap
}

options = list([])


geographic_regions = [
'County','House','Senate'
]

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
    ui.input_selectize("main_category", "Select a geographic bounary", choices=geographic_regions),
    ui.output_ui("sub_category_ui"),

    ui.input_selectize("datasource", "Select a source", choices=['MHVillage', 'LARA'], ),
    ui.output_table("site_list"),
    #ui.tags.div(ui.output_html("district_map"))
    
)


def server(input, output, session):
# Use a reactive expression to determine the subcategory options
    @reactive.Calc
    def sub_category_options():
        main_category = input.main_category()
        df_name = input.datasource()
        if main_category and df_name == 'MHVillage':
            return mhvillage_df[main_category].dropna().tolist()
        elif main_category :
             return lara_df[main_category].dropna().tolist()
        return []

    # Use render functions to create UI elements, output_text_verbatim is used here for simplicity to show the results
    @output     
    @render.ui
    def sub_category_ui():
        options = sub_category_options()
        options.sort()
        return ui.input_select("sub_category", "Select:", options)
     
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


# # Define server logic
# def server(input, output, session):
    
#     @output
#     @render.html
#     def district_map():
#         map_html = create_map_html(gdf)
#         # Embed the map HTML in an iframe
#         iframe = tags.iframe(style="width:100%;height:500px;border:none;", srcdoc=map_html)
#         return iframe

    
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
            if input.main_category() == 'County':
                return (mhvillage_df[mhvillage_df['County'] == input.sub_category()][['Name','Sites','FullstreetAddress']]).sort_values('Sites', ascending = False)
            else:
                return (mhvillage_df[mhvillage_df[input.main_category()] == int(float(input.sub_category()))][['Name','Sites','FullstreetAddress']]).sort_values('Sites', ascending = False)
        else:
            if input.main_category() == 'County':
                return lara_df[lara_df[input.main_category()] == input.sub_category()][['Owner / Community_Name','Total_#_Sites','Location_Address']].sort_values('Owner / Community_Name',  ascending = False)
            else:
                return lara_df[lara_df[input.main_category()] == int(float(input.sub_category()))][['Owner / Community_Name','Total_#_Sites','Location_Address']].sort_values('Owner / Community_Name',  ascending = False)


    @output
    @render.table
    def site_list2():
        if input.datasource() == 'MHVillage':
            return (mhvillage_df[mhvillage_df['House'] == int(float(input.house()))][['Name','Sites','FullstreetAddress']]).sort_values('Name')
        else:
            return lara_df[lara_df['House'] == input.house().upper()[1:-1]][['Owner / Community_Name','Total_#_Sites','Location_Address','Senate']].sort_values('Owner / Community_Name')

    @render.code
    def info():
        return str([type(hist.widget), type(hist.value)])

#removed to run on shiny.io
app = App(app_ui, server)