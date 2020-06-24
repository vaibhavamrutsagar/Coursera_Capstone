#!/usr/bin/env python
# coding: utf-8

# In[4]:


get_ipython().system('pip install geocoder')


# In[5]:


import geocoder


# In[9]:


import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner

link = "http://cocl.us/Geospatial_data"
df1 = pd.read_csv(link)

df1.head()


# In[10]:


df1.shape


# In[11]:


df1.columns = ['Postcode','Latitude','Longitude']

cols = df1.columns.tolist()
cols


# In[12]:


link = "https://raw.githubusercontent.com/Shekhar-rv/Coursera_Capstone/master/df_can.csv"
df = pd.read_csv(link,index_col=0)
df.head()


# In[13]:


df_new = pd.merge(df, df1, on='Postcode')
df_new.head()


# In[14]:


df_new.to_csv(r'week2.csv')


# In[ ]:




