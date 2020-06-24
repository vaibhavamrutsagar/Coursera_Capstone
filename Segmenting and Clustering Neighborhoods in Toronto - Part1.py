#!/usr/bin/env python
# coding: utf-8

# In[5]:


get_ipython().system('pip install geopy')


# In[6]:


import geopy


# 1. Setting up the environment

# In[8]:


import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json

#!conda install -c conda-forge geopy --yes
from geopy.geocoders import Nominatim

from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from pandas.io.json import json_normalize

import matplotlib.cm as cm
import matplotlib.colors as colors

from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes
import folium

print('Libraries imported.')


# 2. Parsing the html

# In[9]:


url = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
page = urlopen(url).read().decode('utf-8')
soup = BeautifulSoup(page, 'html.parser')

wiki_table = soup.body.table.tbody


# 3. Extracting data from the table to the data frame

# In[10]:


def get_cell(element):
    cells = element.find_all('td')
    row = []
    
    for cell in cells:
        if cell.a:            
            if (cell.a.text):
                row.append(cell.a.text)
                continue
        row.append(cell.string.strip())
        
    return row


# In[11]:


def get_row():    
    data = []  
    
    for tr in wiki_table.find_all('tr'):
        row = get_cell(tr)
        if len(row) != 3:
            continue
        data.append(row)        
    
    return data


# In[12]:


data = get_row()
columns = ['Postcode', 'Borough', 'Neighbourhood']
df = pd.DataFrame(data, columns=columns)
df.head()


# In[13]:


df.shape


# 4. CLEANING THE DATA

# In[14]:


df1 = df[df.Borough != 'Not assigned']
df1 = df1.sort_values(by=['Postcode','Borough'])

df1.reset_index(inplace=True)
df1.drop('index',axis=1,inplace=True)

df1.head()


# In[15]:


df_postcodes = df1['Postcode']
df_postcodes.drop_duplicates(inplace=True)
df2 = pd.DataFrame(df_postcodes)
df2['Borough'] = '';
df2['Neighbourhood'] = '';


df2.reset_index(inplace=True)
df2.drop('index', axis=1, inplace=True)
df1.reset_index(inplace=True)
df1.drop('index', axis=1, inplace=True)

for i in df2.index:
    for j in df1.index:
        if df2.iloc[i, 0] == df1.iloc[j, 0]:
            df2.iloc[i, 1] = df1.iloc[j, 1]
            df2.iloc[i, 2] = df2.iloc[i, 2] + ',' + df1.iloc[j, 2]
            
for i in df2.index:
    s = df2.iloc[i, 2]
    if s[0] == ',':
        s =s [1:]
    df2.iloc[i,2 ] = s


# In[16]:


df2.shape


# In[19]:


df.to_csv(week1.csv)


# In[20]:


df.to_csv(r'week1.csv')


# In[ ]:




