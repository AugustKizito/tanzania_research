# 1. Import Necessary Libraries

# Ensure all required libraries are installed. If not, uncomment and run the following line:
# !pip install pandas geopandas pysal statsmodels matplotlib seaborn openpyxl

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pysal.lib import weights
from pysal.explore import esda
from pysal.model import spreg
from statsmodels.api import add_constant

# 2. Data Preparation

# 2.1. Define the Real Data

# Define the data as a dictionary
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

# Create the DataFrame
real_data = pd.DataFrame(data)

# 2.1.2. Data Cleaning

# Check for any anomalies or incorrect formats
print("\nData Types:")
print(real_data.dtypes)

# Convert columns to appropriate data types
numeric_columns = [
    'Poverty%', 'Total Health Facilities', 'Total Access to Water %',
    'Total Access to Electricity', 'Average Max Annual Temperature',
    'Average Min Annual Temperature', 'Average Annual Rainfall',
    'Change Urban Expansion (km²)', 'Crop Land Vegetation Change (km²)',
    'Natural Vegetation Change (km²) Deforestation', 'Range Land Change (km²)',
    'INFANT MORTALITY RATE', 'LIFE EXPECTANCY'
]

# Remove any potential non-numeric characters and convert to float
for col in numeric_columns:
    real_data[col] = pd.to_numeric(real_data[col], errors='coerce')

# Check for missing values
print("\nMissing Values:")
print(real_data[numeric_columns].isnull().sum())

# Handle missing values if any (e.g., drop rows with missing data)
real_data = real_data.dropna(subset=numeric_columns)

# Verify the cleaned data
print("\nCleaned Real Data:")
print(real_data)

# 2.1.6. Standardize 'Region' Names

# Standardize the 'ADM1_EN' column in real_data
real_data['Region'] = real_data['ADM1_EN'].str.strip().str.lower()

# Check the standardized names
print("\nStandardized Region Names:")
print(real_data['Region'].unique())

# 2.2. Load and Merge Geospatial Data (Shapefiles)

# Directory containing all region shapefiles
shapefiles_dir = r'C:\Users\Msi\Desktop\jupyterTest\Shapefiles'  # Update with your actual path

# List of region names matching shapefile subdirectory names
regions_list = ['Arusha', 'Dar_es_Salaam', 'Kigoma', 'Mbeya', 'Mwanza', 'Pwani', 'Singida']

# Initialize an empty list to store individual GeoDataFrames
gdf_list = []

# Loop through each region, read its shapefile, and append to the list
for region in regions_list:
    shapefile_subdir = os.path.join(shapefiles_dir, region)
    shapefile_path = os.path.join(shapefile_subdir, f"{region}.shp")

    if not os.path.exists(shapefile_path):
        print(f"Shapefile for {region} not found at {shapefile_path}. Please check the file name and path.")
        continue

    # Read the shapefile
    try:
        gdf_region = gpd.read_file(shapefile_path, encoding='utf-8')
    except Exception as e:
        print(f"Error reading shapefile for {region}: {e}")
        continue

    # Assign the region name to a new column if not already present
    if 'Region' not in gdf_region.columns:
        # Identify the appropriate column to rename
        possible_columns = ['ADM1_EN', 'region_name', 'NAME_1', 'RegionName', 'Name']
        renamed = False
        for col in possible_columns:
            if col in gdf_region.columns:
                gdf_region = gdf_region.rename(columns={col: 'Region'})
                print(f"Renamed '{col}' to 'Region' for {region}")
                renamed = True
                break
        if not renamed:
            # If no matching column found, assign the region name directly
            gdf_region['Region'] = region.lower()
            print(f"Assigned 'Region' column directly for {region}")
    else:
        # Ensure consistency in region naming
        gdf_region['Region'] = region.lower()
        print(f"'Region' column exists and is set for {region}")

    # Standardize the 'Region' column to match real_data
    gdf_region['Region'] = gdf_region['Region'].str.strip().str.lower()

    # Append to the list
    gdf_list.append(gdf_region)

# Concatenate all GeoDataFrames into one
if len(gdf_list) == 0:
    raise ValueError("No shapefiles were loaded. Please check the shapefiles directory and names.")

merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))

# Ensure the 'Region' column exists and matches exactly with real_data
print("\nMerged GeoDataFrame Columns:")
print(merged_gdf.columns.tolist())

# Merge the combined_data with the GeoDataFrame
merged_gdf = merged_gdf.merge(real_data, on='Region')

# Verify the merge
print("\nMerged GeoDataFrame:")
print(merged_gdf.head())

# 2.3. Coordinate Reference System (CRS) Consistency

# Check CRS of the merged GeoDataFrame
print("\nCRS of Merged GeoDataFrame:", merged_gdf.crs)

# Define the target CRS (e.g., WGS84)
target_crs = "EPSG:4326"

# Reproject if necessary
if merged_gdf.crs != target_crs:
    merged_gdf = merged_gdf.to_crs(target_crs)
    print(f"Reprojected GeoDataFrame to {target_crs}")

# 2.4. Handling Invalid Geometries

# Check for invalid geometries
invalid_geometries = merged_gdf[~merged_gdf.is_valid]
if not invalid_geometries.empty:
    print("\nInvalid geometries found. Attempting to fix...")
    merged_gdf['geometry'] = merged_gdf['geometry'].buffer(0)
    # Re-check validity
    invalid_geometries = merged_gdf[~merged_gdf.is_valid]
    if not invalid_geometries.empty:
        print("Some geometries could not be fixed.")
    else:
        print("All geometries are now valid.")
else:
    print("\nAll geometries are valid.")

# 3. Exploratory Spatial Data Analysis (ESDA)

# 3.1. Create Spatial Weights Matrix

# Create spatial weights matrix using Queen contiguity
w = weights.Queen.from_dataframe(merged_gdf)

# Standardize the weights (row-standardized)
w.transform = 'r'

# Inspect the weights
print("\nSpatial Weights Matrix:")
print(w)

# 3.2. Calculate Global Moran’s I

# Define the dependent variable
poverty_level = merged_gdf['Poverty_Level'].values

# Calculate Global Moran's I for Poverty Level
moran = esda.Moran(poverty_level, w)
print(f"\nGlobal Moran's I: {moran.I}")
print(f"p-value: {moran.p_sim}")
print(f"Z-score: {moran.Z_sim}")

# 3.3. Local Moran’s I (LISA) Analysis

# Calculate Local Moran's I
lisa = esda.Moran_Local(poverty_level, w)

# Add LISA results to GeoDataFrame
merged_gdf['LISA_Significance'] = lisa.p_sim < 0.05  # Significant at 5% level
merged_gdf['LISA_Cluster'] = 'Not Significant'

# Define High-High, Low-Low, High-Low, Low-High clusters
merged_gdf.loc[(lisa.q == 1) & (lisa.p_sim < 0.05), 'LISA_Cluster'] = 'High-High'
merged_gdf.loc[(lisa.q == 3) & (lisa.p_sim < 0.05), 'LISA_Cluster'] = 'Low-Low'
merged_gdf.loc[(lisa.q == 2) & (lisa.p_sim < 0.05), 'LISA_Cluster'] = 'High-Low'
merged_gdf.loc[(lisa.q == 4) & (lisa.p_sim < 0.05), 'LISA_Cluster'] = 'Low-High'

# Display the clusters
print("\nLISA Clusters:")
print(merged_gdf[['ADM1_EN', 'LISA_Cluster']])

# 3.4. Visualize LISA Clusters

# Define colors for clusters
cluster_colors = {
    'High-High': 'red',
    'Low-Low': 'blue',
    'High-Low': 'lightcoral',
    'Low-High': 'lightblue',
    'Not Significant': 'lightgrey'
}

# Map LISA clusters to colors
merged_gdf['Cluster_Color'] = merged_gdf['LISA_Cluster'].map(cluster_colors)

# Plot LISA clusters
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
merged_gdf.plot(color=merged_gdf['Cluster_Color'], edgecolor='black', linewidth=0.5, ax=ax)

# Create custom legend
import matplotlib.patches as mpatches

legend_patches = [
    mpatches.Patch(color='red', label='High-High'),
    mpatches.Patch(color='blue', label='Low-Low'),
    mpatches.Patch(color='lightcoral', label='High-Low'),
    mpatches.Patch(color='lightblue', label='Low-High'),
    mpatches.Patch(color='lightgrey', label='Not Significant')
]

plt.legend(handles=legend_patches, loc='upper right')
plt.title('LISA Clusters for Poverty Level')
plt.axis('off')
plt.show()

# 4. Spatial Regression Modeling

# 4.1. Prepare the Data for Modeling

# Define the dependent variable
y = merged_gdf['Poverty_Level'].values.reshape(-1, 1)

# Define the independent variables
X = merged_gdf[[
    'Hospitals_Percent_Change',
    'Health_Centers_Percent_Change',
    'Dispensaries_Percent_Change',
    'Mortality_Rate_Percent_Change',
    'Water_Access_Percent_Change',
    'Electricity_Access_Percent_Change',
    'Average Max Annual Temperature',
    'Average Min Annual Temperature',
    'Average Annual Rainfall',
    'Change Urban Expansion (km²)',
    'Crop Land Vegetation Change (km²)',
    'Natural Vegetation Change (km²) Deforestation',
    'Range Land Change (km²)'
]].values

# Add a constant term
X = add_constant(X)

# Define variable names for reference
variable_names = ['const', 'Hospitals_Percent_Change', 'Health_Centers_Percent_Change',
                  'Dispensaries_Percent_Change', 'Mortality_Rate_Percent_Change',
                  'Water_Access_Percent_Change', 'Electricity_Access_Percent_Change',
                  'Average Max Annual Temperature', 'Average Min Annual Temperature',
                  'Average Annual Rainfall', 'Change Urban Expansion (km²)',
                  'Crop Land Vegetation Change (km²)', 'Natural Vegetation Change (km²) Deforestation',
                  'Range Land Change (km²)']

# 4.2. Spatial Lag Model (SAR)

# Initialize and fit the Spatial Lag Model (SAR)
sar_model = spreg.GM_Lag(
    y, X, w=w, name_y='Poverty_Level',
    name_x=variable_names,
    name_ds='Dataset'
)

# Display the summary of the SAR model
print("\nSpatial Lag Model (SAR) Summary:")
print(sar_model.summary)

# 4.3. Spatial Durbin Model (SDM)

# Initialize and fit the Spatial Durbin Model (SDM)
sdm_model = spreg.GM_Lag(
    y, X, w=w, name_y='Poverty_Level',
    name_x=variable_names,
    name_ds='Dataset',
    lag_q=True  # Include spatial lags of independent variables
)

# Display the summary of the SDM model
print("\nSpatial Durbin Model (SDM) Summary:")
print(sdm_model.summary)

# 4.4. Model Comparison

# Compare AIC values
print("\nModel Comparison based on AIC:")
print(f"SAR Model AIC: {sar_model.aic}")
print(f"SDM Model AIC: {sdm_model.aic}")

# Select the model with the lowest AIC (best fit)
if sar_model.aic < sdm_model.aic:
    print("SAR Model has a better fit based on AIC.")
    selected_model = sar_model
    model_type = 'SAR'
else:
    print("SDM Model has a better fit based on AIC.")
    selected_model = sdm_model
    model_type = 'SDM'

# 5. Extract and Display Coefficients

# Extract coefficients from the selected model
coefficients = pd.DataFrame({
    'Variable': selected_model.name_x,
    'Coefficient': selected_model.betas.flatten(),
    'Std_Error': selected_model.std_errs.flatten(),
    'p_Value': selected_model.p_values.flatten()
})

print(f"\n{model_type} Model Coefficients:")
print(coefficients)

# 6. Visualization of Regression Results

# 6.1. Plot Residuals

# Calculate residuals for the selected model
merged_gdf['Residuals'] = selected_model.u.flatten()

# Plot Residuals
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
merged_gdf.plot(column='Residuals', cmap='coolwarm', legend=True,
                edgecolor='black', linewidth=0.5, ax=ax)
plt.title(f'{model_type} Model Residuals')
plt.axis('off')
plt.show()

# 6.2. Moran’s I on Residuals

# Calculate Moran's I for Residuals
residuals = merged_gdf['Residuals'].values
moran_residuals = esda.Moran(residuals, w)
print(f"\nMoran's I for {model_type} Residuals: {moran_residuals.I}")
print(f"p-value: {moran_residuals.p_sim}")
print(f"Z-score: {moran_residuals.Z_sim}")

# 7. Final Mapping of Coefficients

# 7.1. Bar Plot of Selected Model Coefficients

# Exclude the constant term for plotting
coefficients_plot = coefficients[coefficients['Variable'] != 'const']

# Plot Coefficients
plt.figure(figsize=(12, 8))
sns.barplot(x='Coefficient', y='Variable', data=coefficients_plot, palette='viridis')
plt.title(f'{model_type} Model Coefficients')
plt.xlabel('Coefficient Value')
plt.ylabel('Variables')
plt.axvline(x=0, color='black', linewidth=0.8)
plt.show()

# 7.2. Heatmap of Coefficients (Optional)

# Note: Since SAR and SDM provide global coefficients, heatmap visualization is more relevant for local models like GWR.
