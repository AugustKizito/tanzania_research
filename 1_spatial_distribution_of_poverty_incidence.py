import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import shape
from matplotlib_scalebar.scalebar import ScaleBar

# Define the regions and their corresponding poverty incidence
regions = ['Arusha', 'Dar es Salaam', 'Pwani', 'Mbeya', 'Singida', 'Kigoma', 'Mwanza']
poverty_incidence = [42, 43, 44, 48, 50, 52, 46]

# Create a DataFrame with regions and their corresponding poverty incidence
data = {'Region': regions, 'Poverty Incidence': poverty_incidence}
poverty_df = pd.DataFrame(data)

# Load the shapefile for Tanzania regions
regions_path = "tanzania_regions/tanzania_regions.shp"
gdf = gpd.read_file(regions_path)

# Merge the GeoDataFrame with the poverty incidence DataFrame
merged_gdf = gdf.merge(poverty_df, left_on='ADM1_EN', right_on='Region', how='left')

# Plot the map
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Plot all regions with their boundaries
gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.8)

# Plot the regions with the poverty incidence
merged_gdf.plot(column='Poverty Incidence', cmap='Reds', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

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

# Add the title and Moran's I statistic
ax.set_title('Spatial Distribution of Poverty Incidence in Tanzania', fontdict={'fontsize': '15', 'fontweight': '3'})


plt.show()
