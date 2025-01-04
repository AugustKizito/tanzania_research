import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

# Define the data dictionary with all new features
data = {
    'RegionId': [1, 2, 10, 17, 16, 23, 28],
    'ADM1_EN': [
        'Arusha',
        'Dar -es -salaam',
        'Kigoma',
        'Mbeya',
        'Mwanza',
        'Pwani',
        'Singida'
    ],
    'Poverty%': [4.9, 1.44, 5.47, 3.98, 5.44, 2.76, 4.43],
    'Total Health Facilities': [310, 454, 246, 362, 376, 365, 229],
    'Total Access to Water %': [87.3, 97.5, 64.5, 76.9, 71.7, 72.2, 47.2],
    'Total Access to Electricity': [52.3, 86, 17.7, 44.7, 37.7, 41.9, 21.2],
    'Average Max Annual Temperature': [27.7, 32.1, 28.1, 27.3, 27.6, 32, 27.2],
    'Average Min Annual Temperature': [15.8, 25, 28.1, 17.7, 18.7, 23.8, 17.4],
    'Average Annual Rainfall': [85.3, 111.3, 82.7, 82.7, 102.4, 89.9, 65.8],
    'Change Urban Expansion (km²)': [115.3102579, 86.75255582, 54.62514238, 101.0413778, 188.1562735, 293.0596246,
                                     24.90961156],
    'Crop Land Vegetation Change (km²)': [885.2829362, -8.165786108, 74.35795565, 487.7369531, 257.7308162,
                                          -82.05018416, 770.2241353],
    'Natural Vegetation Change (km²) Deforestation': [2411.241831, -61.61709164, 1061.202675, 2341.93647, 35.6134795,
                                                      -3469.831057, 5764.367187],
    'Range Land Change (km²)': [-1870.299667, 2.858200242, -1380.459221, -2969.975125, -568.2002324, 3214.091469,
                                -7550.661245],
    'INFANT MORTALITY RATE': [41, 79, 92, 101, 87, 101, 82],
    'LIFE EXPECTANCY': [72.6, 63.9, 62.4, 58.9, 63.1, 60.7, 67.1]
}

# Convert the data dictionary into a pandas DataFrame
data_df = pd.DataFrame(data)

# Load the shapefile for Tanzania regions
regions_path = "tanzania_regions/tanzania_regions.shp"
gdf = gpd.read_file(regions_path)

# Merge the GeoDataFrame with the data DataFrame
merged_gdf = gdf.merge(data_df, on='ADM1_EN', how='left')

# List of features to plot
features_to_plot = [
    'Poverty%', 'Total Health Facilities', 'Total Access to Water %',
    'Total Access to Electricity', 'Average Max Annual Temperature',
    'Average Min Annual Temperature', 'Average Annual Rainfall',
    'Change Urban Expansion (km²)', 'Crop Land Vegetation Change (km²)',
    'Natural Vegetation Change (km²) Deforestation', 'Range Land Change (km²)',
    'INFANT MORTALITY RATE', 'LIFE EXPECTANCY'
]

# Generate a map for each feature
for feature in features_to_plot:
    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Plot all regions with their boundaries
    gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.8)

    # Plot the regions with the feature
    merged_gdf.plot(column=feature, cmap='viridis', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

    # Add a scale bar
    scalebar = ScaleBar(1, location='lower right', font_properties={'weight': 'bold', 'size': 10, 'family': 'serif'})
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

    # Add the title
    title = f'Spatial Distribution of {feature} in Tanzania'
    ax.set_title(title, fontdict={'fontsize': 15, 'fontweight': 'normal', 'family': 'serif'})

    # Save the map
    output_folder = "model_output"
    output_path_pdf = f"{output_folder}/{feature.replace(' ', '_')}.pdf"
    output_path_tif = f"{output_folder}/{feature.replace(' ', '_')}.tif"

    plt.savefig(output_path_pdf, format='pdf', bbox_inches='tight')
    plt.savefig(output_path_tif, format='tiff', bbox_inches='tight')

    # Show the map
    plt.show()
