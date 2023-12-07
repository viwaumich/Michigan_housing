from shiny import *
from shinywidgets import output_widget, render_widget
import ipyleaflet as L

#import shapely
import pandas as pd
#import geopandas as gpd

path2folder = r"Fill in your path!"

full_df = pd.read_csv(path2folder + r"MHVillageAll_Dec7_dropna.csv")

#tracts_shapefile = gpd.read_file(path2folder+r"tl_2019_26_tract.shp")

circlelist = []
mklist = []



def build_marker_layer():
    if len(circlelist) >0  and len(mklist)>0:
        return
    leng = 0
    for ind in range(len(full_df)):
        lon = float(full_df['Longitude'].iloc[ind])
        lat = float(full_df['Latitude'].iloc[ind])
    
        markeri = L.Marker(location=(lat,lon),draggable=False,title=str(full_df['Name'].iloc[ind])+' , number of sites: '+str(full_df['Sites'].iloc[ind])+' , average rent: '+str(full_df['Average_rent'].iloc[ind]))
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
    ui.input_selectize("county", "Select a county", sorted(list(full_df['County'].unique())), ),
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
        return full_df[full_df['County'] == input.county()][['Name','Sites','FullstreetAddress']]


app = App(app_ui, server)
