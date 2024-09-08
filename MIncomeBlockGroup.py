import geopandas as gpd
import pandas as pd
import folium
import branca
import numpy as np
import matplotlib.colors as mcolors

# Load the GeoJSON data into a GeoDataFrame
url = "C:\\Users\\User\\Desktop\\Practice Coding\\PythonProjects\\FedEx Office Project\\NewGitProject\\filtered_blockgroups.geojson"
tracts = gpd.read_file(url)
tracts = tracts[tracts['ALAND'] > 0]

# Load your CSV file into a DataFrame
df = pd.read_csv("C:\\Users\\User\\Desktop\\Practice Coding\\PythonProjects\\FedEx Office Project\\NewGitProject\\ACSDT5Y2020.B19013-Data.csv", low_memory=False)

# Replace '-' with np.nan and '250,000+' with 250001
df['Income'] = df['Income'].replace(['-', '2,500-'], np.nan)
df['Income'] = df['Income'].replace('250,000+', 250001)

# Convert the 'Income' column to a numeric data type
df['Income'] = pd.to_numeric(df['Income'])

# Define the income bins and labels
bins = [0, 10000, 25000, 40000, 55000, 70000, 85000, 100000, 150000, 250000, float('inf')]
labels = ['0-10,000', '10,000-25,000', '25,000-40,000', '40,000-55,000', '55,000-70,000', '70,000-85,000', '85,000-100,000', '100,000-150,000', '150,000-250,000', '>250,000']

# Divide the 'Income' column into the defined bins
df['IncomeRank'] = pd.cut(df['Income'], bins=bins, labels=labels, right=False, include_lowest=True)

# Map the string labels to numeric values
rank_mapping = {label: i+1 for i, label in enumerate(labels)}
df['IncomeRankNumeric'] = df['IncomeRank'].map(rank_mapping)

# Merge df with tracts on the 'GEOIDFQ' column
df = pd.merge(df, tracts[['GEOIDFQ', 'geometry']], on='GEOIDFQ', how='inner')

# Convert df to a GeoDataFrame
df = gpd.GeoDataFrame(df, geometry='geometry')

# Create a map centered around New York City
nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=13, tiles='cartodb positron')

# Add the choropleth map to the map with income data
choropleth = folium.Choropleth(
    geo_data=tracts,
    name='choropleth',
    data=df[df['Income'].notna()],
    columns=['GEOIDFQ', 'IncomeRankNumeric'],  # Use the numeric column here
    key_on='feature.properties.GEOIDFQ',  # Use the correct key here
    fill_color='Set3',  # Change the color palette here
    fill_opacity=3,
    line_opacity=0.2,
    line_color='Black',  # Change the border color here
    legend_name='Median Income Rank',
    nan_fill_color='black',
    bins=10,
    show=False  # Hide the default legend
).add_to(nyc_map)

# Colors used by folium for the Set3 palette
colors = [
    "#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462",
    "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd"
]

# Add a red dot for your coordinates
folium.CircleMarker(
    [40.6209374, -74.0256168],  # Your coordinates
    radius=5,  # Defines the radius of the circle marker in pixels. You can adjust this value as needed.
    color='red',
    fill=True,
    fill_color='red'
).add_to(nyc_map)

# Create a string of HTML code for the legend with matching colors
legend_html = '''
<div style="position: fixed; top: 50px; right: 50px; width: 200px; height: 400px; 
            border:2px solid grey; z-index:9999; font-size:14px; background-color:white;
            ">
    <p><strong>Legend:</strong></p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 0-10,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 10,000-25,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 25,000-40,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 40,000-55,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 55,000-70,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 70,000-85,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 85,000-100,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 100,000-150,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> 150,000-250,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:{}"></i> >250,000</p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:black"></i> Information Not Available</p>
</div>
'''.format(*colors)

# Create a branca element with the HTML code
legend = branca.element.Element(legend_html)

# Add the legend to the map
nyc_map.get_root().html.add_child(legend)

# Save the map to an HTML file
nyc_map.save("nyc_income_choropleth.html")

print("Map saved to nyc_income_choropleth.html")
