import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape
from matplotlib_scalebar.scalebar import ScaleBar

# Define the regions and their corresponding poverty incidence
regions = ['Arusha', 'Dar es salaam', 'Dodoma', 'Geita', 'Iringa', 'Kagera', 'Katavi', 'Kigoma', 'Kilimanjaro', 'Lindi', 'Manyara', 'Mara', 'Mbeya', 'Mororgoro', 'Mtwara', 'Mwanza', 'Njombe', 'Pwani', 'Rukwa', 'Ruvuma', 'Shinyanga', 'Simiyu', 'Singida', 'Songwe', 'Tabora', 'Tanga']
poverty_incidence = [4.9, 1.44, 3.18, 3.76, 3.61, 3.96, 1.07, 5.94, 3.98, 4.96, 4.57, 5.44, 2.41, 2.76, 2.88, 6.25, 1.92, 5.47, 5.01, 3.42, 4.43, 3.52, 3.24, 2.2, 4.2, 5.48]

# Create a DataFrame with regions and their corresponding poverty incidence
data = {'Region': regions, 'Poverty Incidence': poverty_incidence}
poverty_df = pd.DataFrame(data)

# --- Standardization and Merging ---

# 1. Load the shapefile for Tanzania regions
regions_path = "tanzania_regions/kIZITO.shp" # Make sure this path is correct
gdf = gpd.read_file(regions_path)

# --- DIAGNOSIS: Print unique names to spot mismatches ---
print("Unique Region names in poverty_df (after stripping whitespace):")
print(poverty_df['Region'].str.strip().unique())

print("\nUnique Region names in shapefile's ADM1_EN column (after stripping whitespace):")
print(gdf['ADM1_EN'].str.strip().unique())

# 2. Standardize names in both DataFrames before merging
# Strip whitespace and convert to a consistent case (e.g., title case or lowercase) for merging
poverty_df['Region_Clean'] = poverty_df['Region'].str.strip().str.title() # Convert to Title Case
gdf['ADM1_EN_Clean'] = gdf['ADM1_EN'].str.strip().str.title() # Convert to Title Case

# Fix specific known spelling errors in your poverty_df before merge
# Based on your previous data, "Mororgoro" should be "Morogoro"
poverty_df['Region_Clean'] = poverty_df['Region_Clean'].replace({'Mororgoro': 'Morogoro'})
# Ensure other common mismatches are handled if found from the unique names check
# For example, if 'Dar es salaam' in your data is 'Dar Es Salaam' in shapefile,
# Title case might fix it, but if not, you'd add:
# poverty_df['Region_Clean'] = poverty_df['Region_Clean'].replace({'Dar Es Salaam': 'Dar Es Salaam'})
# Or convert both to .lower() for robustness: .str.lower()


# 3. Merge the GeoDataFrame with the poverty incidence DataFrame using the cleaned names
merged_gdf = gdf.merge(poverty_df, left_on='ADM1_EN_Clean', right_on='Region_Clean', how='left')

# --- DIAGNOSIS: Check for unmatched regions after merge ---
unmatched_in_shapefile = merged_gdf[merged_gdf['Poverty Incidence'].isna()]
if not unmatched_in_shapefile.empty:
    print(f"\nRegions in shapefile with no poverty data after merge (Poverty Incidence is NaN):")
    print(unmatched_in_shapefile['ADM1_EN'].tolist())
else:
    print("\nAll regions in shapefile successfully merged with poverty data.")


# --- Plotting (same as your original code, but using merged_gdf) ---
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Plot all regions with their boundaries
# We plot the full gdf first to ensure all regions are drawn, even if no data
gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.8)

# Plot the regions with the poverty incidence (now hopefully with values for Katavi & Morogoro)
# For regions where merge was unsuccessful, 'Poverty Incidence' will be NaN and they will not be colored by cmap.
# They will remain the 'none' facecolor from the gdf.plot()
merged_gdf.plot(column='Poverty Incidence', cmap='Reds', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True, missing_kwds={"color": "lightgrey", "edgecolor": "black", "hatch": "///"})


# Add a scale bar
scalebar = ScaleBar(1, location='lower right', font_properties={'weight': 'bold', 'size': 10, 'family': 'serif'})
ax.add_artist(scalebar)

# Add a north arrow
x, y, arrow_length = 0.95, 0.95, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=10, xycoords='axes fraction', fontweight='bold', family='serif')

# Add region names for all regions (from original gdf for complete coverage)
for idx, row in gdf.iterrows():
    region_name = row['ADM1_EN'] # Use original name for display
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
title = 'Spatial Distribution of Poverty Incidence in Tanzania for the 26 regions'
ax.set_title(title, fontdict={'fontsize': 15, 'fontweight': 'normal', 'family': 'serif'})

# Save the map
output_folder = "model_output"
import os
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_path_pdf = f"{output_folder}/1 - {title}.pdf"
output_path_tif = f"{output_folder}/1 - {title}.tif"
output_path_without_title_pdf = f"{output_folder}/1 - {title}_without_title.pdf"
output_path_without_title_tif = f"{output_folder}/1 - {title}_without_title.tif"

plt.savefig(output_path_pdf, format='pdf', bbox_inches='tight')
plt.savefig(output_path_tif, format='tiff', bbox_inches='tight')

ax.set_title("") # Clear title for "without title" version
plt.savefig(output_path_without_title_pdf, format='pdf', bbox_inches='tight')
plt.savefig(output_path_without_title_tif, format='tiff', bbox_inches='tight')

plt.show()