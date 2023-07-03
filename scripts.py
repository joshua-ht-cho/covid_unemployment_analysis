import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import re

plt.style.use('fivethirtyeight')
pd.set_option('display.max_columns', 500)
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]

from fredapi import Fred
fred_key = '63782c836dc9865eacb857ba91fd6139'

# 1. Create the Fred object
fred = Fred(api_key='63782c836dc9865eacb857ba91fd6139')

# 2. Search for economic data from Fred
sp_search = fred.search('S&P')
sp_search.shape

# 3. Pull raw data and plot
sp500 = fred.get_series(series_id='SP500')
sp500.plot(figsize=(10, 3), title='S&P 500', lw=1.5)

# 4. Pull and join multiple data series
uemp_search = fred.search('unemployment')
unrate = fred.get_series(series_id='UNRATE')
uemp_df = fred.search('unemployment rate state', filter=('frequency','Monthly'))
uemp_df = uemp_df.query('seasonal_adjustment=="Seasonally Adjusted" and units=="Percent"')
uemp_df = uemp_df.loc[uemp_df['title'].str.contains('Unemployment Rate')]

st_uemp_df = uemp_df.loc[~uemp_df['id'] \
    .str.contains('000|m0892|lns|USAURAMS|lrun|lrhu|UNRATE|U2RATE|CMWRUR|CNEWUR|CSOUUR|CNERUR|PRUR', \
        flags=re.I, regex=True)]

all_results = []
for myid in st_uemp_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)
    all_results.append(results)

st_uemp_results = pd.concat(all_results, axis=1)
st_uemp_results = st_uemp_results.drop('West Census Region',axis=1)
st_uemp_results = st_uemp_results.drop('East South Central Census Division',axis=1)
st_uemp_results.isna().sum(axis=1).plot()

st_uemp_results = st_uemp_results.dropna()
id_to_state = st_uemp_df['title'].str.replace('Unemployment Rate in ','').to_dict()
st_uemp_results.columns = [id_to_state[c] for c in st_uemp_results.columns]

# Plot states' unemployment ratees
px.line(st_uemp_results)

## Pull April 2020 unemployment rate per state
ax = st_uemp_results.loc[st_uemp_results.index == '2020-04-01'].T.sort_values('2020-04-01') \
    .plot(kind='barh', figsize=(8, 12), width=0.85, edgecolor='black', title='Unemployment Rate by State, 2020')
ax.legend().remove()
plt.show()

# Pull participation rate
part_df = fred.search('labor force participation rate by state', filter=('frequency','Monthly'))
part_df = part_df.query('seasonal_adjustment=="Seasonally Adjusted" and units=="Percent"')
part_df = part_df.filter(like = 'LBSSA', axis=0)

ax = st_uemp_results.loc[st_uemp_results.index == '2020-04-01'].T.sort_values('2020-04-01') \
    .plot(kind='barh', figsize=(8, 12), width=0.85, edgecolor='black', title='Unemployment Rate by State, 2020')
ax.legend().remove()
plt.show()part_id_to_state = part_df['title'].str.replace('Labor Force Participation Rate for ','').to_dict()

all_results = []
for myid in part_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)
    all_results.append(results)
    
st_part_results = pd.concat(all_results, axis=1)

part_id_to_state = part_df['title'].str.replace('Labor Force Participation Rate for ','').to_dict()
st_part_results.columns = [part_id_to_state[c] for c in st_part_results.columns]

# Final plot of unemployment vs participation by state
# Fix DC first
st_uemp_results = st_uemp_results.rename(columns={'the District of Columbia':'District of Columbia'})

fig, axs = plt.subplots(10, 5, figsize=(30, 30), sharex=True)
axs = axs.flatten()
i = 0
for state in st_uemp_results.columns:
    if state == "District of Columbia":
        continue
    ax2 = axs[i].twinx()
    st_uemp_results.query('index >= 2020 and index < 2024')[state]\
    .plot(ax=axs[i], label='Unemployment')
    st_part_results.query('index >= 2020 and index < 2024')[state]\
    .plot(ax=ax2, label='Participation', color=color_pal[1])
    ax2.grid(False)
    axs[i].set_title(state)
    i += 1
plt.tight_layout()
plt.show()
