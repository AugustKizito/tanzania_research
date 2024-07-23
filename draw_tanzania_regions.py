import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import pandas as pd
from shapely.geometry import shape
import fiona

# Upgrade libraries (uncomment these lines to run once)
# !pip install --upgrade geopandas shapely fiona matplotlib-scalebar

# Load the shapefile for Tanzania regions
regions_path = "tanzania_regions/tanzania_regions.shp"
tanzania_regions = gpd.read_file(regions_path)
# Load the shapefile for Tanzania regions
with fiona.open(regions_path) as shp:
    crs = shp.crs
    features = [feature for feature in shp]

# Plot the map
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Extract geometries and attributes for Tanzania regions
geometries = [shape(feature['geometry']) for feature in features]
attributes = [feature['properties'] for feature in features]

# Create a GeoDataFrame for Tanzania regions
gdf = gpd.GeoDataFrame(attributes, geometry=geometries, crs=crs)

# Plot the Tanzania regions
tanzania_regions.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=1.5)

# Add a scale bar
scalebar = ScaleBar(1, location='lower right')  # Adjust the scale bar to your needs
ax.add_artist(scalebar)

# Add a north arrow
x, y, arrow_length = 0.95, 0.95, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=12, xycoords=ax.transAxes)


# Add region names for all regions
for idx, row in gdf.iterrows():
    region_name = row['ADM1_EN']
    if pd.notna(region_name):
        ax.annotate(text=region_name, xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                    horizontalalignment='center', fontsize=8, color='black')

# Set the title and remove axis
ax.set_title('Tanzania Regions', fontdict={'fontsize': '15', 'fontweight': '3'})

plt.show()
