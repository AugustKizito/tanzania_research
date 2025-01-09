from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW
from statsmodels.api import add_constant
import numpy as np
import matplotlib.pyplot as plt


def run_gwr_analysis(merged_gdf, independent_vars, dependent_var):
    """
    Run Geographically Weighted Regression (GWR) and visualize local R-squared values.

    Parameters:
    - merged_gdf: GeoDataFrame with all regions and data.
    - independent_vars: List of independent variable column names.
    - dependent_var: Dependent variable column name (string).

    Returns:
    - gwr_results: GWR model results.
    """
    try:
        # Ensure the GeoDataFrame is in a projected CRS for accurate centroid calculation
        if merged_gdf.crs.is_geographic:
            print("\nReprojecting GeoDataFrame to a projected CRS for accurate centroid calculation...")
            merged_gdf = merged_gdf.to_crs(epsg=3395)  # Use a projected CRS like EPSG:3395 (Mercator)

        # Prepare data for GWR
        coords = np.array(list(zip(merged_gdf.geometry.centroid.x, merged_gdf.geometry.centroid.y)))
        y = merged_gdf[dependent_var].values.reshape(-1, 1)  # Dependent variable
        X = merged_gdf[independent_vars].values  # Independent variables

        # Add a constant to X
        X = add_constant(X)

        # 1. Check for collinearity and remove problematic variables
        print("\nChecking for multicollinearity...")
        corr_matrix = np.corrcoef(X.T)
        if np.linalg.cond(corr_matrix) > 1e10:
            raise ValueError("Multicollinearity detected in the independent variables. Adjust the model.")

        # 2. Use Bandwidth Selection
        print("\nRunning bandwidth selection for GWR...")
        bw_selector = Sel_BW(coords, y, X)
        bandwidth = bw_selector.search()
        print(f"Optimal bandwidth for GWR: {bandwidth}")

        # 3. Fit GWR Model
        print("\nFitting GWR model...")
        gwr_model = GWR(coords, y, X, bandwidth)
        gwr_results = gwr_model.fit()

        # Print Summary
        print("\nGWR Summary:")
        print(gwr_results.summary)

        # 4. Add Local R-squared to GeoDataFrame
        merged_gdf['Local_R2'] = gwr_results.localR2

        # Visualize Geographical Heterogeneity (Local R-squared values)
        print("\nVisualizing Local R-squared values...")
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        merged_gdf.plot(column='Local_R2', cmap='viridis', legend=True, edgecolor='black', ax=ax)
        plt.title('Local R-squared Values from GWR (Infrastructure vs. Poverty)')
        plt.axis('off')

        # Save the plot
        plt.savefig("model_output/local_r2_map_gwr.png", dpi=300)
        plt.show()

        return gwr_results

    except ValueError as ve:
        print(f"ValueError during GWR analysis: {ve}")
    except Exception as e:
        print(f"Error during GWR analysis: {e}")
        raise
