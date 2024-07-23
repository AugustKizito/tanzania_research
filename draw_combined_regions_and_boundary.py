import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import fiona
from shapely.geometry import shape
from matplotlib_scalebar.scalebar import ScaleBar

# Upgrade libraries (uncomment these lines to run once)
# !pip install --upgrade geopandas shapely fiona matplotlib-scalebar

# Define the regions and their corresponding enrolment coefficients
regions = ['Arusha', 'Dar es Salaam', 'Pwani', 'Mbeya', 'Singida', 'Kigoma', 'Mwanza']
enrolment_coefficients = [14.5, 12.9, 11.7, 13.4, 9.5, 8.7, 10.2]

# Create a DataFrame with regions and their corresponding enrolment coefficients
data = {'Region': regions, 'Enrolment Coefficient': enrolment_coefficients}
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

# Merge the GeoDataFrame with the enrolment coefficients DataFrame
merged_gdf = gdf.merge(coeff_df, left_on='ADM1_EN', right_on='Region', how='left')

# Load the shapefile for Tanzania international boundary
boundary_path = "tanzania_boundary/tz_boundary.shp"
tanzania_boundary = gpd.read_file(boundary_path)

# Plot the map
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Plot all regions with their boundaries
gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.8)

# Plot the regions with the enrolment coefficients
merged_gdf.plot(column='Enrolment Coefficient', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

# Plot the Tanzania international boundary
tanzania_boundary.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=1.5)

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
ax.set_title('Spatial Distribution of Enrolment Rate Coefficients in Tanzania.', fontdict={'fontsize': '15', 'fontweight': '3'})

plt.show()
