import geopandas as gpd
import pandas as pd
import folium
import branca
import numpy as np

# Load the GeoJSON data into a GeoDataFrame
url = "C:\\Users\\User\\Desktop\\Practice Coding\\PythonProjects\\FedEx Office Project\\NewGitProject\\filtered_blockgroups.geojson"
tracts = gpd.read_file(url)
tracts = tracts[tracts['ALAND'] > 0]

# Load your CSV file into a DataFrame
df = pd.read_csv("C:\\Users\\User\\Desktop\\Practice Coding\\PythonProjects\\FedEx Office Project\\NewGitProject\\ACSDT5Y2020.B01003-Data.csv", low_memory=False)

# Merge df with tracts on the 'GEOIDFQ' column
df = pd.merge(df, tracts[['GEOIDFQ', 'geometry']], on='GEOIDFQ', how='inner')

# Convert df to a GeoDataFrame
df = gpd.GeoDataFrame(df, geometry='geometry')

# Create a percentile column for population
df = df[df['Population'] >0]
df['PopulationPercentile'] = pd.qcut(df['Population'], q=10, labels=False)

# Create a map centered around New York City
nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=13, tiles='cartodb positron')

# Add the choropleth map to the map with population data
choropleth = folium.Choropleth(
    geo_data=tracts,
    name='choropleth',
    data=df[df['Population'] > 0],  # Exclude rows where 'Population' is 0
    columns=['GEOIDFQ', 'PopulationPercentile'],  # Use the correct column names here
    key_on='feature.properties.GEOIDFQ',  # Use the correct key here
    fill_color='Set3',  # Change the color palette here
    fill_opacity=3,
    line_opacity=0.2,
    legend_name='Population Percentile',
    bins=10
).add_to(nyc_map)


# Add a red dot for your coordinates
folium.CircleMarker(
    [40.6209374, -74.0256168],  # Your coordinates
    radius=5,  # Defines the radius of the circle marker in pixels. You can adjust this value as needed.
    color='red',
    fill=True,
    fill_color='red'
).add_to(nyc_map)

# Create a string of HTML code for the legend
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 90px; 
            border:2px solid grey; z-index:9999; font-size:14px; background-color:white;
            ">
    <p><strong>Legend:</strong></p>
    <p style="margin-left:10px;"><i class="fa fa-circle fa-1x" style="color:black"></i> Information Not Available</p>
</div>
'''

# Create a branca element with the HTML code
legend = branca.element.Element(legend_html)

# Add the legend to the map
nyc_map.get_root().html.add_child(legend)

# Save the map to an HTML file
nyc_map.save("nyc_population_choropleth.html")

print("Map saved to nyc_population_choropleth.html")


