import pandas as pd
import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import Point
import re
from regex_add import regex, regex1
import geopy
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3


# !!!!!!!!!! free but doesn't work as well as google API
geolocator = Nominatim(user_agent="you're email")
##
#geolocator = GoogleV3(api_key='you're API here')

# two functions from medium article: 
# link:https://towardsdatascience.com/transform-messy-address-into-clean-data-effortlessly-using-geopy-and-python-d3f726461225
def extract_clean_address(address):
    try:
        location = geolocator.geocode(address)
        return location.address
    except:
        return ''


def extract_lat_long(address):
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude]
    except:
        return ''


# add clean addresses

lara_df = pd.read_excel(path2folder + r"LARA_with_coord.xlsx")

lara_df_address = copy.deepcopy(lara_df['Location_Address'])

lara_df_address['no punc.'] = lara_df[['Location_Address']].apply(lambda x: x['Location_Address'].translate(str.maketrans('', '', string.punctuation)),axis=1)
lara_df_address = pd.concat([lara_df['Location_Address'],lara_df_address['no punc.']], axis=1)
lara_df_address.columns = ['Location_Address', 'no punc.']

lara_df_address['clean address'] = lara_df_address[['no punc.']].apply(lambda x: extract_clean_address(x['no punc.']) , axis=1  )
lara_df_address = pd.concat([lara_df['Location_Address'],lara_df_address['clean address']], axis=1)
lara_df_address.columns = ['LARA_Address','no punc.' 'clean address']

lara_df_address['lat_long'] = lara_df_address[['clean address']].apply(lambda x: extract_lat_long(x['clean address']) , axis =1)
lara_df_address['latitude'] = lara_df_address.apply(lambda x: x['lat_long'][0] if x['lat_long'] != '' else '', axis =1)
lara_df_address['longitude'] = lara_df_address.apply(lambda x: x['lat_long'][1] if x['lat_long'] != '' else '', axis =1)
lara_df_address.drop(columns = ['lat_long'], inplace = True)

#fill in one missing row
lara_df_address.loc[109,'latitude'] = 42.9259227
lara_df_address.loc[109,'longitude'] = -85.2199399

final_lara = pd.concat([lara_df, lara_df_address['latitude'], lara_df_address['longitude']], axis=1)
final_lara.drop(columns = ['Longitude','Latitude'], inplace = True)

final_lara.to_csv('data/LARA_with_all_coord.csv')

