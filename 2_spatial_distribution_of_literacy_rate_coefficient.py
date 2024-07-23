import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import fiona
from shapely.geometry import shape
from matplotlib_scalebar.scalebar import ScaleBar

# Define the regions and their corresponding literacy coefficients
regions = ['Arusha', 'Dar es Salaam', 'Pwani', 'Mbeya', 'Singida', 'Kigoma', 'Mwanza']
literacy_coefficients = [13.8, 15.2, 10.5, 12.1, 8.3, 7.2, 9.8]

# Create a DataFrame with regions and their corresponding literacy coefficients
data = {'Region': regions, 'Literacy Coefficient': literacy_coefficients}
coeff_df = pd.DataFrame(data)

# Load the shapefile for Tanzania regions
regions_path = "tanzania_regions/tanzania_regions.shp"
with fiona.open(regions_path) as shp:
    crs = shp.crs
    features = [feature for feature in shp]

# Extract geometries and attributes for Tanzania regions
geometries = [shape(feature['geometry']) for feature in features]
attributes = [feature['properties'] for feature in features]

# Create a GeoDataFrame for Tanzania regions
gdf = gpd.GeoDataFrame(attributes, geometry=geometries, crs=crs)

# Merge the GeoDataFrame with the literacy coefficients DataFrame
merged_gdf = gdf.merge(coeff_df, left_on='ADM1_EN', right_on='Region', how='left')

# Plot the map
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Plot all regions with their boundaries
gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.8)

# Plot the regions with the literacy coefficients
merged_gdf.plot(column='Literacy Coefficient', cmap='YlGnBu', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

# Add a scale bar
scalebar = ScaleBar(1, location='lower right')  # Adjust the scale bar to your needs
ax.add_artist(scalebar)

# Add a north arrow
x, y, arrow_length = 0.95, 0.95, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=12, xycoords='axes fraction')

# Add region names for all regions
for idx, row in gdf.iterrows():
    region_name = row['ADM1_EN']
    if pd.notna(region_name):
        ax.annotate(text=region_name, xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                    horizontalalignment='center', fontsize=8, color='black')

# Set the title and remove axis
ax.set_title('Spatial Distribution of Literacy Rate Coefficients in Tanzania', fontdict={'fontsize': '15', 'fontweight': '3'})

plt.show()
