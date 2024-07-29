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
scalebar = ScaleBar(1, location='lower right', font_properties={'weight': 'bold', 'size': 10, 'family': 'serif'})  # Adjust the scale bar to your needs
ax.add_artist(scalebar)

# Add a north arrow
x, y, arrow_length = 0.95, 0.95, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=10, xycoords='axes fraction', fontweight='bold', family='serif')

# Add region names for all regions
for idx, row in gdf.iterrows():
    region_name = row['ADM1_EN']
    if pd.notna(region_name):
        ax.annotate(text=region_name, xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                    horizontalalignment='center', fontsize=10, color='black', fontweight='normal', family='serif')

# Set the boundary line width
ax.spines['top'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)

ax_without_title = ax
# Add the title
title = 'Spatial Distribution of Poverty Incidence in Tanzania'
ax.set_title(title, fontdict={'fontsize': 15, 'fontweight': 'normal', 'family': 'serif'})

# Save the map
output_folder = "model_output"
output_path_pdf = f"{output_folder}/1 - {title}.pdf"
output_path_tif = f"{output_folder}/1 - {title}.tif"
output_path_without_title_pdf = f"{output_folder}/1 - {title}_without_title.pdf"
output_path_without_title_tif = f"{output_folder}/1 - {title}_without_title.tif"

plt.savefig(output_path_pdf, format='pdf', bbox_inches='tight')
plt.savefig(output_path_tif, format='tiff', bbox_inches='tight')

ax.set_title("")
plt.savefig(output_path_without_title_pdf, format='pdf', bbox_inches='tight')
plt.savefig(output_path_without_title_tif, format='tiff', bbox_inches='tight')

plt.show()
