from shiny import *
from shinywidgets import output_widget, render_widget
import ipyleaflet as L

import math
#import shapely
import pandas as pd
#import geopandas as gpd

path2folder = r"Fill in the path to your data"

mhvillage_df = pd.read_csv(path2folder + r"MHVillageAll_Dec7_dropna.csv")
lara_df = pd.read_excel(path2folder + r"LARA_with_coord.xlsx")
#tracts_shapefile = gpd.read_file(path2folder+r"tl_2019_26_tract.shp")

circlelist = []
mklist = []



def build_marker_layer():
    if len(circlelist) >0  and len(mklist)>0:
        return
    leng = 0
    for ind in range(len(mhvillage_df)):
        lon = float(mhvillage_df['Longitude'].iloc[ind])
        lat = float(mhvillage_df['Latitude'].iloc[ind])
    
        markeri = L.Marker(
            location=(lat,lon),
            draggable=False,
            title=str(mhvillage_df['Name'].iloc[ind])+
            ' , number of sites: '+str(mhvillage_df['Sites'].iloc[ind])+
            ' , average rent: '+str(mhvillage_df['Average_rent'].iloc[ind])+
            ' , url: %s'%str(mhvillage_df['Url'].iloc[ind]) +
            ' , MHVillage')
        circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")

        circlelist.append(circlei)
        mklist.append(markeri) 
    for ind in range(len(lara_df)):
        lon = float(lara_df['Longitude'].iloc[ind])
        lat = float(lara_df['Latitude'].iloc[ind])
        if lon == 0 and lat == 0:
            continue
        markeri = L.Marker(
            location=(lat,lon),
            draggable=False,
            title=str(lara_df['Owner / Community_Name'].iloc[ind])+
            ' , number of sites: '+str(lara_df['Total_#_Sites'].iloc[ind])+
            ', LARA')
        circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")

        circlelist.append(circlei)
        mklist.append(markeri)   
    return 


basemaps = {
  "OpenStreetMap": L.basemaps.OpenStreetMap.Mapnik,
  "Satellite": L.basemaps.Gaode.Satellite,
  "WorldStreetMap": L.basemaps.Esri.WorldStreetMap,
  "NatGeoWorldMap": L.basemaps.Esri.NatGeoWorldMap
}

layernames = ['Marker', "Circle"]
app_ui = ui.page_fluid(
    output_widget("map"),
    ui.input_select(
        "basemap", "Choose a basemap",
        choices=list(basemaps.keys())
    ),
    ui.input_selectize("layers", "Layers to visualize", layernames, multiple=True),
    ui.input_selectize("county", "Select a county", sorted(list(mhvillage_df['County'].unique())), ),
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
        if 'Marker' in layerlist:
            build_marker_layer()
            marker_cluster = L.MarkerCluster(
                name='location markers',
                markers=tuple(mklist)
                )
            the_map.add_layer(marker_cluster)
            markerorcircle = True
        if 'Circle' in layerlist:
            if not markerorcircle:
                build_marker_layer()
            layergroup = L.LayerGroup(name = 'location circles',layers=circlelist)
            the_map.add_layer(layergroup)
            markerorcircle = True
        return the_map
    
    @output
    @render.table
    def site_list():
        return (mhvillage_df[mhvillage_df['County'] == input.county()][['Name','Sites','FullstreetAddress']]).sort_values('Name')


app = App(app_ui, server)
