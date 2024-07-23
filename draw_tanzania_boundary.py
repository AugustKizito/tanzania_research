import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.patches as mpatches

# Upgrade libraries (uncomment these lines to run once)
# !pip install --upgrade geopandas shapely fiona matplotlib-scalebar

# Load the shapefile for Tanzania international boundary
boundary_path = "tanzania_boundary/tz_boundary.shp"
tanzania_boundary = gpd.read_file(boundary_path)

# Plot the map
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

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

# Set the title and remove axis
ax.set_title('Tanzania International Boundary', fontdict={'fontsize': '15', 'fontweight': '3'})

plt.show()
