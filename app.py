import pandas as pd

import streamlit as st

from bs4 import BeautifulSoup
import requests
from requests import get

import datetime

import xlrd

import numpy as np

import plotly.express as px
import altair as alt

st.set_page_config('Critical illness stats',layout='wide')




# url = 'https://www.income.com.sg/claims/claims-statistics/'
# r = requests.get(url)
# data = BeautifulSoup(r.text,'html.parser')
#
# urllist = []
#
# for link in data.find_all('a'):
#     urllist.append(link.get('href'))
#
# statslist = []
#
# for item in urllist:
#     try:
#         if 'claims-statistics' in item:
#             statslist.append(item)
#     except:
#         pass
#
# statslist = statslist[2:]
# newlist = []
#
# for i in statslist:
#     newlist.append(i.partition('/claims/claims-statistics/')[2])

st.title('Analysis of critical illness insurance')
st.markdown('The supporting data for this analysis comes from https://www.income.com.sg/claims/claims-statistics/')

col1,col2,col3 = st.beta_columns(3)

with col1:
    st.image('https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60')
with col2:
    st.image('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60')
with col3:
    st.image('https://images.unsplash.com/photo-1593538313188-7a6ab30a8ae4?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60')

def cleanmonth(string):
    return string.replace('-claims-summary','')

def getyear(string):
    return string[-4:]

def cutmonth(string):
    return string[:-5].capitalize()

def monthtodate(string):
    return datetime.datetime.strptime(string,'%B')

def monthyeardate(a,b):
    return datetime.datetime(year=b,month=a,day=1)

monthlist = ['January','February','March','April','May','June','July','August','September','October','November','December']

def getmonthnumber(string):
    return monthlist.index(string)+1

def typoremove(string):
    return string.replace('disablity','disability')

def dollarremove(string):
    string = string.replace('$','')
    string = string.replace('S','')
    string = string.replace(',','')
    return string

def renametpd(string):
    if string == 'Permanent & total disability':
        string = 'TPD'
    return string

@st.cache
def allclaimsdownload():
    df = pd.DataFrame()
    df = pd.read_html(url+newlist[0])[0].iloc[:-1,:]
    df['Month'] = newlist[0]
    for i in newlist[1:]:
        newurl = url + i
        newdf = pd.read_html(newurl)[0].iloc[:-1,:]
        newdf['Month'] = i
        df = pd.concat([df,newdf])
    df['Amount (S$)'] = df['Amount (S$)'].apply(dollarremove)
    df.iloc[:,1] = pd.to_numeric(df.iloc[:,1],errors='coerce')
    df['Amount (S$)'] = pd.to_numeric(df['Amount (S$)'],errors='coerce')
    df['Month'] = df['Month'].apply(cleanmonth)
    df['Year'] = df['Month'].apply(getyear)
    df['Year'] = pd.to_numeric(df['Year'],errors='coerce')
    df['Month'] = df['Month'].apply(cutmonth)
    df['Month number'] = df['Month'].apply(getmonthnumber)
    df['Month/Year'] = df.apply(lambda x: monthyeardate(x['Month number'],x['Year']),axis=1)
    df['Type of Claims'] = df['Type of Claims'].apply(typoremove)
    df['Type of Claims'] = df['Type of Claims'].apply(renametpd)
    df = df.iloc[:,[0,1,2,6]]
    return df


# df = allclaimsdownload()
# df.to_excel('allclaimsdownload.xlsx')

df = pd.read_excel('allclaimsdownload.xlsx')

st.header('Summary of claims')


col1,col2 = st.beta_columns(2)

highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])

fig1 = alt.Chart(df).mark_bar().encode(alt.X('Month/Year:T'),alt.Y('Number:Q'),color='Type of Claims',tooltip=[
      {"type": "temporal", "field": "Month/Year"},
      {"type": "quantitative", "field": "Number"}]).add_selection(highlight).configure_legend(orient='bottom')


highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])

fig2 = alt.Chart(df).mark_bar().encode(alt.X('Month/Year:T'),alt.Y('Amount (S$):Q'),color='Type of Claims',tooltip=[
      {"type": "temporal", "field": "Month/Year"},
      {"type": "quantitative", "field": "Amount (S$)"}]).add_selection(highlight).configure_legend(orient='bottom')


with col1:
    st.subheader('Number of claims')
    st.altair_chart(fig1,use_container_width=True)
with col2:
    st.subheader('Amount of claims')
    st.altair_chart(fig2,use_container_width=True)


with st.beta_expander('Show data'):
    st.table(df)

df = df.groupby(by='Type of Claims').sum()
df.reset_index(inplace=True)

@st.cache
def bigclaimsdownload():
    df = pd.DataFrame()
    df = pd.read_html(url+newlist[0])[1].iloc[:-1,:]
    df['Month'] = newlist[0]
    for i in newlist[1:]:
        newurl = url + i
        newdf = pd.read_html(newurl)[1].iloc[:-1,:]
        newdf['Month'] = i
        df = pd.concat([df,newdf])

    df['Age'] = pd.to_numeric(df['Age'],errors='coerce')
    df['Amount (S$)'] = pd.to_numeric(df['Amount (S$)'],errors='coerce')
    df['Month'] = df['Month'].apply(cleanmonth)
    df['Year'] = df['Month'].apply(getyear)
    df['Year'] = pd.to_numeric(df['Year'],errors='coerce')
    df['Month'] = df['Month'].apply(cutmonth)
    df['Month number'] = df['Month'].apply(getmonthnumber)
    df['Month/Year'] = df.apply(lambda x: monthyeardate(x['Month number'],x['Year']),axis=1)
    # df['Type of Claims'] = df['Type of Claims'].apply(typoremove)
    df = df.iloc[:,[0,1,2,3,4,8]]
    return df

# bigclaims = bigclaimsdownload()
# bigclaims.to_excel('bigclaims.xlsx')
bigclaims = pd.read_excel('bigclaims.xlsx')


newdf = bigclaims.groupby(by='Type').count()
newdf.reset_index(inplace=True)

df = df[['Type of Claims','Number','Amount (S$)']]


bigclaimsgroup = bigclaims.groupby(by='Type').count()
bigclaimsgroup.reset_index(inplace=True)

df['Number over 100k'] = bigclaimsgroup['Cause']

bigclaimsgroup = bigclaims.groupby(by='Type').sum()
bigclaimsgroup.reset_index(inplace=True)

df['Amount (S$) over 100k'] = bigclaimsgroup['Amount (S$)']
df['Average Amount all claims'] = df['Amount (S$)'] / df['Number']
df['Average Amount claims over 100k'] = df['Amount (S$) over 100k'] / df['Number over 100k']
df['Percentage over 100k'] = df['Number over 100k'] / df['Number']

st.subheader('Percentage of claims over 100k')

highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
fig = alt.Chart(df).mark_bar().encode(alt.X('Percentage over 100k:Q',axis=alt.Axis(format='%')),alt.Y('Type of Claims:N'),color='Type of Claims',tooltip=[
      {"type": "quantitative", "field": "Percentage over 100k",'format':'.2%'},
      {"type": "nominal", "field": "Type of Claims"}]).add_selection(highlight).configure_legend(orient='bottom')
st.altair_chart(fig,use_container_width=True)



col1,col2 = st.beta_columns(2)


with col1:
    st.subheader('All claims')
    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(df).mark_bar().encode(alt.X('Number:Q'),alt.Y('Type of Claims:N'),color='Type of Claims',tooltip=[
          {"type": "quantitative", "field": "Number"},
          {"type": "nominal", "field": "Amount (S$)"}]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)

    fig = px.pie(df, values='Number', names='Type of Claims', color_discrete_sequence=px.colors.sequential.Blackbody)
    st.plotly_chart(fig,use_container_width=True,sharing='streamlit')

    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(df).mark_bar().encode(alt.X('Average Amount all claims:Q'),alt.Y('Type of Claims:N'),color='Type of Claims',tooltip=[
          {"type": "quantitative", "field": "Average Amount all claims",'format':'.2s'},
          {"type": "nominal", "field": "Type of Claims"}]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)


with col2:
    st.subheader('Claims above 100k')
    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(bigclaims).mark_bar().encode(alt.X('count()'),alt.Y('Type:N'),color='Type',tooltip=[
          {"type": "nominal", "field": "Type"}]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)

    fig = px.pie(newdf, values='No.', names='Type', color_discrete_sequence=px.colors.sequential.Blackbody)
    st.plotly_chart(fig,use_container_width=True,sharing='streamlit')

    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(df).mark_bar().encode(alt.X('Average Amount claims over 100k:Q'),alt.Y('Type of Claims:N'),color='Type of Claims',tooltip=[
          {"type": "quantitative", "field": "Average Amount claims over 100k",'format':'.2s'},
          {"type": "nominal", "field": "Type of Claims"}]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)

st.header('Claims greater than 100k SGD and Number of claims > 5')


def typetypo(string):
    if 'Coronary' in string:
        string = 'Coronary Artery By-pass Surgery'
    elif 'Heart' and 'Valve' in string:
        string = 'Heart Valve Surgery'
    elif 'PTD' in string:
        string = 'PTD due to other medical condition besides stroke'
    elif 'Lung' in string:
        string = 'Chronic Lung Disease'
    elif 'Others,' in string:
        string = 'Others, Unknown'
    return string

selectcause = st.radio('Select cause of claim',['Critical illness','Death','TPD'])

ciclaims = bigclaims[bigclaims['Type']==selectcause]

df = ciclaims.groupby('Cause').count()
df = df[df['Type']>5]
df.reset_index(inplace=True)
df['Cause'] = df['Cause'].apply(typetypo)

df.sort_values(by='Type',ascending=False,inplace=True)


highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])

fig = alt.Chart(df).mark_bar().encode(alt.X('Type:Q'),alt.Y('Cause:N',sort='y'),color='Cause:N',tooltip=[
      {"type": "nominal", "field": "Cause"}]).add_selection(highlight).configure_legend(orient='bottom')

st.altair_chart(fig,use_container_width=True)


fig = px.pie(df, values='Type', names='Cause', color_discrete_sequence=px.colors.sequential.Blackbody)
st.plotly_chart(fig,use_container_width=True,sharing='streamlit')



avebigclaims = bigclaims.groupby('Type').mean()
avebigclaims.reset_index(inplace=True)

col1, col2 = st.beta_columns(2)

with col1:
    st.subheader('Average age when claim occurs')
    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(avebigclaims).mark_bar().encode(alt.X('Age:Q',sort='y'),alt.Y('Type:N'),color='Type:N',tooltip=[
          {"type": "nominal", "field": "Type"},
          {"type": "quantitative", "field": "Age",'format':'.2s'},
          ]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)

with col2:
    st.subheader('Average claim amount')
    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(avebigclaims).mark_bar().encode(alt.X('Amount (S$):Q',sort='y'),alt.Y('Type:N'),color='Type:N',tooltip=[
          {"type": "nominal", "field": "Type"},
          {"type": "quantitative", "field": "Amount (S$)",'format':'.2s'},
          ]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)

avecause = bigclaims.groupby(['Type','Cause']).mean()
avecause.reset_index(inplace=True)

avecause['Cause']=avecause['Cause'].apply(typetypo)

st.header('Claims by cause')

selecttype = st.radio('Select type of claim',['Critical illness','Death','TPD'])


avecause=avecause[avecause['Type']==selecttype]

def amendtext(string):
    return string



avecause = avecause[['Type','Cause','Age','Amount (S$)']]

def amendcause(string):
    if 'Tumour' in string:
        string = 'Benign Brain Tumour'
    elif 'Artery' in string:
        string = 'Coronary Artery By-Pass Surgery'
    elif 'Valve' in string:
        string = 'Heart Valve Surgery'
    elif 'Kidney' in string:
        string = 'Kidney Failure'
    elif 'Motor' in string:
        string = 'Motor Neurone Disease'
    elif 'Parkinson' in string:
        string = "Parkinson's Disease"
    return string

avecause['Cause'] = avecause['Cause'].apply(amendcause)

avecause = avecause.groupby('Cause').mean()
avecause.reset_index(inplace=True)

col1,col2 = st.beta_columns(2)

with col1:
    st.subheader('Average age when claim occurs, by cause')
    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(avecause).mark_bar().encode(alt.X('Age:Q'),alt.Y('Cause:N',sort='-y'),tooltip=[
          {"type": "nominal", "field": "Cause"},
          {"type": "quantitative", "field": "Age",'format':'.2s'},
          ]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)

with col2:
    st.subheader('Average claim amount, by cause')
    highlight = alt.selection(type='interval',bind='scales',encodings=['x','y'])
    fig = alt.Chart(avecause).mark_bar().encode(alt.X('Amount (S$):Q'),alt.Y('Cause:N',sort='-y'),tooltip=[
          {"type": "nominal", "field": "Cause"},
          {"type": "quantitative", "field": "Amount (S$)",'format':'.2s'},
          ]).add_selection(highlight).configure_legend(orient='bottom')
    st.altair_chart(fig,use_container_width=True)
