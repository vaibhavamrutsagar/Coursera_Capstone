#!/usr/bin/env python
# coding: utf-8

# # Capstone Project - The Battle of Neighborhoods
# # Finding the Best Neighborhood in New York

# ## Introduction:
# Recently, one of my client has approached me to find out the most suitable place in New York to live.
# He wants to move to the most happening place in New York.
# ### Business Problem
# Given that there are many neighbourhoods in New York
# Exploring the neighbouhoods 
# Using the Foursquare API to analyse 
# Find the most sought after, trendy, popular and commented venues. 

# ## Importing Necessary Libraries

# In[ ]:


import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

import folium # map rendering library


# # Data Collection
# ## Web Scrapping with BeautifulSoup

# In[ ]:


from bs4 import BeautifulSoup
import requests
import re

url = "https://www.google.com/search?q=new+york+neighbourhoods&oq=new+york+neighbourhoods&aqs=chrome..69i57j0l7.12674j0j7&sourceid=chrome&ie=UTF-8"
response = requests.get(url)
NY_data = BeautifulSoup(response.text, 'lxml')
contents=NY_data.find_all('div', class_='RWuggc kCrYT')
columns = ['Neighborhood']
NY_neighborhood = pd.DataFrame(columns = columns)
for content in contents:
    #coordinate = content.find('div', class_='BNeawe s3v9rd AP7Wnd')
    neighbor_ = content.find('div').find('div').text
    NY_neighborhood = NY_neighborhood.append({'Neighborhood': neighbor_}, ignore_index=True)
NY_neighborhood


# ## Defining a funtion to get the new york city data such as Boroughs Neighborhoods along with their Latitude and Longitude.
# 
# 

# In[ ]:


NY_coord = pd.DataFrame(columns = ['Latitude','Longitude'])
geolocator = Nominatim(user_agent="New York")
for row in NY_neighborhood['Neighborhood']:
    location = geolocator.geocode(row)
    NY_coord = NY_coord.append({'Latitude':location.latitude, 'Longitude':location.longitude}, ignore_index=True)
NY_neighborhood = NY_neighborhood.join(NY_coord)
NY_neighborhood


# ### Plotting the map with Folium

# In[ ]:


address = 'New York'

geolocator = Nominatim(user_agent="New York")
location = geolocator.geocode(address)
latitude_NY = location.latitude
longitude_NY = location.longitude
map_NY = folium.Map(location=[latitude_NY, longitude_NY], zoom_start=12)

# add markers to map
for lat, lng, postal in zip(NY_neighborhood['Latitude'],NY_neighborhood['Longitude'],NY_neighborhood['Neighborhood']):
    label = str(postal)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [float(lat), float(lng)],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_NY)  
    
map_NY


# ## Getting Venues List via FourSquare API

# In[ ]:


CLIENT_ID = 'ILLMWN3IEHII4JAWIVV13BLYXJ31QCGQ23FL2KG552DNEFPD' #Foursquare ID
CLIENT_SECRET ='BXPXXEIO4AUTWA2IJDFFTY1JGLJYIWO4GPCSSSRVQBFAYOP1'
VERSION = '20180605' # Foursquare API version

radius=5000
LIMIT=100
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        print(results)
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)
NY_venues = getNearbyVenues(names=NY_neighborhood['Neighborhood'],
                                   latitudes=NY_neighborhood['Latitude'],
                                   longitudes=NY_neighborhood['Longitude']
                                  )


# In[ ]:


NY_venues


# In[ ]:


NY_venues.head()


# In[ ]:


NY_venues_count = NY_venues.groupby('Neighborhood').count().reset_index()
NY_venues_count[['Neighborhood', 'Venue']]


# In[ ]:


print('So {} uniques categories.'.format(len(NY_venues['Venue Category'].unique())))


# ### There are 335 uniques venues.

# ## Onehot Encoding

# In[ ]:


NY_onehot = pd.get_dummies(NY_venues[['Venue Category']], prefix="", prefix_sep="") 

# add neighborhood column back to dataframe
NY_onehot['Neighborhood'] = NY_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [NY_onehot.columns[-1]] + list(NY_onehot.columns[:-1])
NY_onehot = NY_onehot[fixed_columns]

NY_onehot.head()


# In[ ]:


NY_grouped = NY_onehot.groupby('Neighborhood').mean().reset_index()
NY_grouped


# In[ ]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[ ]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = NY_grouped['Neighborhood']

for ind in np.arange(NY_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(NY_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted


# ## Running Clusttering Algorithum

# In[ ]:


kclusters = 4

NY_grouped_clustering = NY_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(NY_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[:] 


# In[ ]:


neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

NY_merged = NY_neighborhood

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
NY_merged = NY_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

NY_merged.head() # check the last columns!
NY_merged = NY_merged.dropna()


# In[ ]:



map_clusters = folium.Map(location=[latitude_NY, longitude_NY], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(NY_merged['Latitude'], NY_merged['Longitude'], NY_merged['Neighborhood'], NY_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[int(cluster)-1],
        fill=True,
        fill_color=rainbow[int(cluster)-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# 

# In[ ]:


print("Cluster 1")
NY_merged.loc[NY_merged['Cluster Labels'] == 0, NY_merged.columns[[0] + list(range(4, NY_merged.shape[1]))]]


# In[ ]:


print("Cluster 2")
NY_merged.loc[NY_merged['Cluster Labels'] == 1, NY_merged.columns[[0] + list(range(4, NY_merged.shape[1]))]]


# In[ ]:


print("Cluster 3")
NY_merged.loc[NY_merged['Cluster Labels'] == 2, NY_merged.columns[[0] + list(range(4, NY_merged.shape[1]))]]


# In[ ]:


print("Cluster 4")
NY_merged.loc[NY_merged['Cluster Labels'] == 3, NY_merged.columns[[0] + list(range(4, NY_merged.shape[1]))]]


# # Conclusion:
# After doing the K means clustering and other analysis described in the python notebook we are of the Opinion that the person should reside in Cluster 1. This is because the person wants to live in a happening place nearby. Cluster one has all the facilities the client is looking for. 
# 
