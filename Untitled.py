#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup
import pandas as pd 
import urllib3
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError
from flask import Flask

url ='https://www.worldometers.info/coronavirus/#c-all'
http = urllib3.PoolManager()
response = http.request('GET', url)
page = response.data


# In[4]:


webpage = BeautifulSoup(page,'html.parser')


# In[5]:


table = webpage.find(id='main_table_countries_today')


# In[6]:


table


# In[7]:


trList = table.find_all('tr')


# In[8]:


data = []


# In[9]:



key = '12ed4bc8d2d0484a9242caa9ae416fd6'
geocoder = OpenCageGeocode(key)


def getDataFromTableRows(trList,skipText):
    count=0
    data = []
    startPointReached = False
    for tr in trList:
        tdList = tr.find_all('td')
        if len(tdList) == 0 : continue
        if not startPointReached:
            if tdList[0].get_text()==skipText:
                startPointReached = True
            else : continue
        if tdList[0].get_text() == 'Total:':
            continue
        countDict = {}
        countDict['Country'] = tdList[0].get_text() 
        countDict['Total Cases'] = tdList[1].get_text() 
        countDict['New Cases'] = tdList[2].get_text() 
        countDict['Total Deaths'] = tdList[3].get_text() 
        countDict['New Deaths'] = tdList[4].get_text() 
        countDict['Total Recovered'] = tdList[5].get_text() 
        countDict['Active Cases'] = tdList[6].get_text() 
        countDict['Serious Critical'] = tdList[7].get_text() 
        countDict['Totalper1Mpop'] = tdList[8].get_text() 
        countDict['Deathsper1Mpop'] = tdList[9].get_text() 
        countDict['TotalTests'] = tdList[10].get_text() 
        countDict['Tests'] = tdList[11].get_text()      
        data.append(countDict)
        count = count + 1
        print(tdList[0].get_text())
    return data  


# In[13]:


data=getDataFromTableRows(trList,'World')


# In[14]:


for point in data:
    print(point['Country'])
    result=geocoder.geocode(point['Country'])
    point['Country Code'] = result[0]['components']['country_code']
    point['coordinates'] = []
    point['coordinates'].append(result[0]['geometry']['lat'])
    point['coordinates'].append(result[0]['geometry']['lng'])
    point['lat'] = result[0]['geometry']['lat']
    point['lng'] = result[0]['geometry']['lng']


# In[15]:



worldCountersTable=pd.DataFrame(data)


# In[16]:


worldCountersTable


# In[17]:


worldCountersTable.to_csv('covid19Counts.csv')


# In[18]:


export = worldCountersTable[['Country','Active Cases','coordinates']]
export = export[~export['Country'].isin(['USA','World'])]
export['activeCases']=export['Active Cases'].str.replace(',','').astype(int)
export['value']=export['activeCases']*1000/export['activeCases'].max()


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'You have reached the COVID19 data api'

@app.route('/world')
def getWorldData():
    return export.to_json(orient='records')


# In[20]:


app.run()






