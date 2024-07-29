import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import shape
from matplotlib_scalebar.scalebar import ScaleBar

# Define the common plotting function
def plot_map(gdf, merged_gdf, column, cmap, title, scalebar_length=1, output_folder="model_output"):
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Plot all regions with their boundaries
    gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.8)

    # Plot the regions with the specified column
    merged_gdf.plot(column=column, cmap=cmap, linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

    # Add a scale bar
    scalebar = ScaleBar(scalebar_length, location='lower right', font_properties={'weight': 'bold', 'size': 10, 'family': 'serif'})
    ax.add_artist(scalebar)

    # Add a north arrow
    x, y, arrow_length = 0.95, 0.95, 0.1
    ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=10, xycoords='axes fraction', fontweight='bold', family='Palatino Linotype')

    # Add region names for all regions
    for idx, row in gdf.iterrows():
        region_name = row['ADM1_EN']
        if pd.notna(region_name):
            ax.annotate(text=region_name, xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                        horizontalalignment='center', fontsize=10, color='black', fontweight='normal', family='serif')

    # Add the title
    ax.set_title(title, fontdict={'fontsize': 15, 'fontweight': 'normal', 'family': 'serif'})

    # Set the boundary line width
    ax.spines['top'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)
    ax.spines['right'].set_linewidth(2)

    # Save the map in PDF and TIF formats
    output_path_pdf = f"{output_folder}/{title}.pdf"
    output_path_tif = f"{output_folder}/{title}.tif"
    plt.savefig(output_path_pdf, format='pdf', bbox_inches='tight')
    plt.savefig(output_path_tif, format='tiff', bbox_inches='tight')

    plt.show()

# Define the regions and their corresponding data
regions = ['Arusha', 'Dar es Salaam', 'Pwani', 'Mbeya', 'Singida', 'Kigoma', 'Mwanza']
poverty_incidence = [42, 43, 44, 48, 50, 52, 46]
literacy_coefficients = [13.8, 15.2, 10.5, 12.1, 8.3, 7.2, 9.8]
local_r2_values = [0.775, 0.650, 0.700, 0.725, 0.675, 0.600, 0.675]
income_levels = [1200, 800, 900, 1100, 1000, 600, 1000]

# Create DataFrames
poverty_df = pd.DataFrame({'Region': regions, 'Poverty Incidence': poverty_incidence})
literacy_df = pd.DataFrame({'Region': regions, 'Literacy Coefficient': literacy_coefficients})
r2_df = pd.DataFrame({'Region': regions, 'Local R^2': local_r2_values})
income_df = pd.DataFrame({'Region': regions, 'Income Level': income_levels})

# Load the shapefile for Tanzania regions
regions_path = "tanzania_regions/tanzania_regions.shp"
gdf = gpd.read_file(regions_path)

# Merge GeoDataFrames
poverty_gdf = gdf.merge(poverty_df, left_on='ADM1_EN', right_on='Region', how='left')
literacy_gdf = gdf.merge(literacy_df, left_on='ADM1_EN', right_on='Region', how='left')
r2_gdf = gdf.merge(r2_df, left_on='ADM1_EN', right_on='Region', how='left')
income_gdf = gdf.merge(income_df, left_on='ADM1_EN', right_on='Region', how='left')

# Plot and save maps
plot_map(gdf, poverty_gdf, 'Poverty Incidence', 'Reds', 'Spatial Distribution of Poverty Incidence in Tanzania')
plot_map(gdf, literacy_gdf, 'Literacy Coefficient', 'YlGnBu', 'Spatial Distribution of Literacy Rate Coefficients in Tanzania')
plot_map(gdf, r2_gdf, 'Local R^2', 'viridis', 'Local R² Map: Explaining Income Levels in Tanzania')
plot_map(gdf, income_gdf, 'Income Level', 'coolwarm', 'Spatial Dependence of Income Levels in Tanzania')
