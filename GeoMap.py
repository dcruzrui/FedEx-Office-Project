import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import folium
import branca
import matplotlib.cm

# API endpoint that returns GeoJSON data
url = "C:\\Users\\User\\Desktop\\Practice Coding\\PythonProjects\\FedEx Office Project\\NewGitProject\\filtered_blockgroups.geojson"
tracts = gpd.read_file(url)
tracts = tracts[tracts['ALAND'] > 0]

# Load your CSV file into a DataFrame
df = pd.read_csv("C:\\Users\\User\\Desktop\\Practice Coding\\PythonProjects\\FedEx Office Project\\NewGitProject\\combined_merged_geocoded_addresses.csv",low_memory=False)

# Create a new DataFrame to hold the latitude and longitude as Points
geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
geo_df = gpd.GeoDataFrame(df, geometry=geometry)
geo_df = geo_df.set_crs("EPSG:4326")

# Perform a spatial join between the two GeoDataFrames
joined = gpd.sjoin(geo_df, tracts, predicate='within')

# Calculate the number of businesses per Census Tract
density = joined['GEOIDFQ'].value_counts().reset_index()
density.columns = ['Block Group', 'Number of Businesses']
density = density[density['Number of Businesses'].notna()]

# Calculate the percentiles
density['BusinessPercentile'] = pd.qcut(density['Number of Businesses'], q=10, labels=False)

density = pd.merge(density, tracts[['GEOIDFQ', 'geometry']], left_on='Block Group', right_on='GEOIDFQ', how='inner')

# Convert density to a GeoDataFrame
density = gpd.GeoDataFrame(density, geometry='geometry')

# Create a map centered around New York City
nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=13, tiles='cartodb positron')

# Add the choropleth map to the map
folium.Choropleth(
    geo_data=tracts,
    name='choropleth',
    data=density[density['Number of Businesses'].notna()],
    columns=['Block Group', 'BusinessPercentile'],
    key_on='feature.properties.GEOIDFQ',
    fill_color='Set3',
    fill_opacity=3,
    line_opacity=0.2,
    legend_name='Businesses Percentile',
    bins=10,
    nan_fill_color='black'
).add_to(nyc_map)


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
nyc_map.save("nyc_businesses_choropleth.html")

print("Map saved to nyc_businesses_choropleth.html")
