#!/usr/bin/env python
# coding: utf-8

# # The Battle of Neighborhoods - Week 1
# 
# ## Data Collection 
# 
# ### 1. Description of the Data
# 
# For the purpose of the report, we will be using the data resources as shown below:
# 
# 1. Link: https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
# 2. Link: https://foursquare.com/explore?mode=url&ne=44.418088%2C-78.362732&q=Restaurant&sw=42.742978%2C-80.554504
# 
# Using the above data resources, we will be able to keep in mind important features such as location coordinates of various venues present in the various neighborhoods in Toronto. With the knowledge of such data collected we can then find the best suited neighborhood for the new business start-ups to be set up. 
# 
# We will need data about different venues in different neighborhoods. In order to gain that information we will use "Foursquare" locational information. Foursquare is a location data provider with information about all manner of venues and events within an area of interest. Such information includes venue names, locations, menus and even photos. As such, the foursquare location platform will be used as the sole data source since all the stated required information can be obtained through the API.
# 

# In[2]:


from bs4 import BeautifulSoup
import requests
import pandas as pd


# In[3]:


List_url = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
source = requests.get(List_url).text


# In[4]:


soup = BeautifulSoup(source, 'xml')
print(soup.prettify())


# In[5]:


table=soup.find('table')


# In[6]:


#define the dataframe columns 
column_names = ['Postalcode','Borough','Neighborhood']

df_table = pd.DataFrame(columns = column_names)
df_table


# In[10]:


for tr_cell in table.find_all('tr'):
    row_data=[]
    for td_cell in tr_cell.find_all('td'):
        row_data.append(td_cell.text.strip())
    if len(row_data)==3:
        df_table.loc[len(df_table)] = row_data
        
df_table


# #### Removing the cells with Not Assigned 

# In[11]:


df_table=df_table[df_table['Borough']!='Not assigned']
df_table


# In[ ]:




