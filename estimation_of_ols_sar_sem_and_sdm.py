import pandas as pd
import geopandas as gpd
import libpysal as lp
import statsmodels.api as sm
from pysal.lib import weights
from pysal.model import spreg # For spatial regression models

# --- 1. Load Your Data (Make sure this loads ALL 26 regions) ---
# Assuming your merged GeoDataFrame for 26 regions is named 'merged_gdf'
# and contains 'Poverty_Level' and your socio-economic indicators.
# Example:
merged_gdf = gpd.read_file("data_for_the_26_regions/kIZITO.shp")

# If you loaded it previously and are sure it contains 26 regions, just use that variable.
# For demonstration, let's assume 'gdf_26_regions' is your GeoDataFrame with 26 regions
# and the relevant columns.

# --- 2. Define Dependent and Independent Variables ---

# Dependent Variable (Poverty Level for 2024)
y = merged_gdf['Poverty_Level']

# Independent Variables (Socio-economic indicators for 26 regions)
# Adjust this list based on your actual column names and which socio-economic
# variables you are including (e.g., exclude 'Education_Level' if not available for all 26).
X_cols = [
    'Total Health Facilities',
    'Total Access to Water %',
    'Total Access to Electricity',
    # Add other socio-economic variables available for all 26 regions, e.g., 'Education_Level'
]
X = merged_gdf[X_cols]

# Add a constant term to the independent variables (required for most regression models)
X_constant = sm.add_constant(X)

# --- 3. Create Spatial Weights Matrix for 26 Regions ---
# IMPORTANT: Ensure this W is built on your GeoDataFrame with 26 regions
# Example for Queen contiguity:
your_weights_matrix_26_regions = lp.weights.Queen.from_dataframe(merged_gdf)
your_weights_matrix_26_regions. 섬listw.transform = 'R' # Row-standardize the weights matrix

# --- 4. Run Each Model and Print Summaries ---

print("--- Running OLS Model (Non-Spatial) ---")
ols_model = sm.OLS(y, X_constant).fit()
print(ols_model.summary())
print("-" * 50)

print("\n--- Running Spatial Autoregressive (SAR) Model ---")
# spreg.ML_Lag is suitable for SAR (and SDM if type="Durbin")
sar_model = spreg.ML_Lag(y.values, X_constant.values, w=your_weights_matrix_26_regions)
print(sar_model.summary) # Note: .summary is an attribute, not a method for spreg models
print(f"SAR Model AIC: {sar_model.aic}")
print(f"SAR Model BIC: {sar_model.bic}")
print(f"SAR Model Log-Likelihood: {sar_model.loglik}")
print("-" * 50)


print("\n--- Running Spatial Error Model (SEM) ---")
sem_model = spreg.ML_Error(y.values, X_constant.values, w=your_weights_matrix_26_regions)
print(sem_model.summary)
print(f"SEM Model AIC: {sem_model.aic}")
print(f"SEM Model BIC: {sem_model.bic}")
print(f"SEM Model Log-Likelihood: {sem_model.loglik}")
print("-" * 50)


print("\n--- Running Spatial Durbin Model (SDM) ---")
# spreg.ML_Durbin explicitly runs an SDM
sdm_model = spreg.ML_Durbin(y.values, X_constant.values, w=your_weights_matrix_26_regions)
print(sdm_model.summary)
print(f"SDM Model AIC: {sdm_model.aic}")
print(f"SDM Model BIC: {sdm_model.bic}")
print(f"SDM Model Log-Likelihood: {sdm_model.loglik}")
print("-" * 50)

# --- 5. Extracting Likelihood Ratio Test Results (PySAL/spreg specific) ---
# PySAL's spreg models store the results of some internal tests,
# but direct 'anova' style comparison functions like in R might not be as explicit.
# However, you can use the log-likelihood values to manually calculate LR tests
# if spreg doesn't provide a direct function for comparison of arbitrary nested models.

# Manual LR Test Calculation (for SDM vs SAR and SDM vs SEM)
# LR test statistic = 2 * (LogLik_unrestricted - LogLik_restricted)
# DF = difference in number of parameters

print("\n--- Likelihood Ratio (LR) Test Results ---")

# LR Test: SDM vs. SAR (Testing if WX_theta terms are jointly zero)
# In spreg, ML_Durbin is the unrestricted model, ML_Lag (SAR) is the restricted model if WX_theta = 0.
# The degrees of freedom for this test is the number of independent variables (X_cols)
# because those are the additional terms in WX_theta compared to SAR.
lr_sdm_vs_sar = 2 * (sdm_model.loglik - sar_model.loglik)
df_sdm_vs_sar = len(X_cols) # Number of additional parameters in WX_theta
# You'd typically use a chi-squared distribution to get the p-value
from scipy.stats import chi2
p_value_sdm_vs_sar = 1 - chi2.cdf(lr_sdm_vs_sar, df_sdm_vs_sar)
print(f"LR Test (SDM vs. SAR): Statistic = {lr_sdm_vs_sar:.4f}, DF = {df_sdm_vs_sar}, p-value = {p_value_sdm_vs_sar:.4f}")

# LR Test: SDM vs. SEM (Testing if WX_theta terms and rho (lagged Y) are jointly zero,
# OR more commonly just WX_theta terms are zero and error model parameters are equivalent.)
# This comparison is a bit more nuanced. A common test for SDM vs SEM in PySAL is the
# `LR_SAR_diag` test within spreg if you ran an `OLS_lag_error` or similar.
# For simplicity, if `spreg.diagnostics` doesn't provide a direct method for `ML_Durbin` vs `ML_Error`
# that's explicitly testing for the spatially lagged X terms,
# you can use the same logic as SDM vs SAR, recognizing that the "restricted" model is SEM.
# The degrees of freedom would again be `len(X_cols)`.
lr_sdm_vs_sem = 2 * (sdm_model.loglik - sem_model.loglik)
df_sdm_vs_sem = len(X_cols) # Assuming this is the difference in parameters due to WX_theta
p_value_sdm_vs_sem = 1 - chi2.cdf(lr_sdm_vs_sem, df_sdm_vs_sem)
print(f"LR Test (SDM vs. SEM): Statistic = {lr_sdm_vs_sem:.4f}, DF = {df_sdm_vs_sem}, p-value = {p_value_sdm_vs_sem:.4f}")

print("-" * 50)