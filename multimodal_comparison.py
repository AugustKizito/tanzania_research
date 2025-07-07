import geopandas as gpd
import libpysal as lp
import numpy as np
import pandas as pd
import spreg
import statsmodels.api as sm
from scipy.stats import norm
from spreg import ML_Lag
import warnings

warnings.filterwarnings("ignore", message="Method 'bounded' does not support relative tolerance in x; defaulting to "
                                          "absolute tolerance.")

# --- Provided Data Arrays ---
regions = ['Arusha', 'Dar es salaam', 'Dodoma', 'Geita', 'Iringa', 'Kagera', 'Katavi', 'Kigoma', 'Kilimanjaro', 'Lindi',
           'Manyara', 'Mara', 'Mbeya', 'Mororgoro', 'Mtwara', 'Mwanza', 'Njombe', 'Pwani', 'Rukwa', 'Ruvuma',
           'Shinyanga', 'Simiyu', 'Singida', 'Songwe', 'Tabora', 'Tanga']
poverty_incidence = [4.9, 1.44, 3.18, 3.76, 3.61, 3.96, 1.07, 5.94, 3.98, 4.96, 4.57, 5.44, 2.41, 2.76, 2.88, 6.25,
                     1.92, 5.47, 5.01, 3.42, 4.43, 3.52, 3.24, 2.2, 4.2, 5.48]
total_health_facilities = [310.0, 454.0, 402.0, 290.0, 379.0, 301.0, 100.0, 246.0, 362.0, 253.0, 236.0, 280.0, 362.0,
                           415.0, 257.0, 376.0, 271.0, 365.0, 228.0, 307.0, 323.0, 243.0, 229.0, 200.0, 337.0, 412.0]
total_access_to_water = [87.3, 97.5, 67.8, 59.4, 78.5, 48.0, 56.4, 64.5, 92.8, 59.2, 62.1, 49.9, 76.9, 72.0, 66.3, 71.7,
                         80.0, 72.2, 55.8, 75.0, 67.2, 68.3, 47.2, 57.1, 41.9, 62.4]
total_access_to_electricity = [52.3, 86.0, 28.9, 19.9, 43.1, 21.3, 20.3, 17.7, 63.1, 18.8, 23.1, 26.1, 44.7, 33.4, 16.6,
                               37.7, 35.9, 41.9, 19.5, 24.8, 25.9, 15.9, 21.2, 28.1, 20.2, 33.5]

# --- 1. Create a DataFrame from the provided arrays ---
# Note: The column name for poverty incidence is adjusted to match 'Poverty_Level'
# expected later in the script for consistency.
data_dict = {
    'RegionName': regions,
    'Poverty_Level': poverty_incidence,  # Renamed to match the variable 'y'
    'Total Health Facilities': total_health_facilities,
    'Total Access to Water %': total_access_to_water,
    'Total Access to Electricity': total_access_to_electricity
}
df_from_arrays = pd.DataFrame(data_dict)

# --- Load Shapefile and Merge Data ---
regions_path = "tanzania_regions/kIZITO.shp"  # Ensure this path is correct
gdf = gpd.read_file(regions_path)

# Standardize names for merging (important for correct alignment)
df_from_arrays['RegionName_Clean'] = df_from_arrays['RegionName'].str.strip().str.title()
gdf['ADM1_EN_Clean'] = gdf['ADM1_EN'].str.strip().str.title()

# Fix specific known spelling errors in your data before merge (e.g., "Mororgoro" to "Morogoro")
df_from_arrays['RegionName_Clean'] = df_from_arrays['RegionName_Clean'].replace({'Mororgoro': 'Morogoro'})

# Merge the GeoDataFrame with the data from arrays
# Use 'left' merge to keep all geometries from the shapefile
merged_gdf = gdf.merge(df_from_arrays, left_on='ADM1_EN_Clean', right_on='RegionName_Clean', how='left')

# --- Check for successful merge (optional, but good for debugging) ---
if merged_gdf['Poverty_Level'].isna().any():
    print("WARNING: Some regions did not merge successfully and have NaN for Poverty_Level.")
    print("Unmerged regions (based on shapefile names):",
          merged_gdf[merged_gdf['Poverty_Level'].isna()]['ADM1_EN'].tolist())
else:
    print("All regions successfully merged with data from arrays.")

# --- 2. Define Dependent and Independent Variables from merged_gdf ---
y = merged_gdf['Poverty_Level']

# Independent Variables (Socio-economic indicators for 26 regions)
X_cols = [
    'Total Health Facilities',
    'Total Access to Water %',
    'Total Access to Electricity',
]
X = merged_gdf[X_cols]

# Add a constant term to the independent variables (required for most regression models)
X_constant = sm.add_constant(X)

# --- 3. Create Spatial Weights Matrix for 26 Regions ---
your_weights_matrix_26_regions = lp.weights.Queen.from_dataframe(merged_gdf, use_index=False)
your_weights_matrix_26_regions.transform = 'R'  # Row-standardize the weights matrix

# --- 4. Run Each Model and Print Summaries ---

print("--- Running OLS Model (Non-Spatial) ---")
ols_model = sm.OLS(y, X_constant).fit()
print(ols_model.summary())
print("-" * 50)

print("\n--- Running Spatial Autoregressive (SAR) Model ---")
# ML_Lag is suitable for SAR (and SDM if type="Durbin")
sar_model = ML_Lag(y.values, X_constant.values, w=your_weights_matrix_26_regions)
print(sar_model.title)  # Model title
print(sar_model.name_x)
print(sar_model.name_y)

print(f"SAR Model AIC: {sar_model.aic}")

# Extract necessary values
loglik_sar = sar_model.logll
n = y.shape[0]
k = X_constant.shape[1] + 1  # +1 for the spatial lag coefficient (rho)

bic_sar = k * np.log(n) - 2 * loglik_sar
print(f"SAR Model BIC (manually computed): {bic_sar}")

print(f"SAR Model Log-Likelihood: {sar_model.logll}")
print("-" * 50)

print("\n--- Running Spatial Error Model (SEM) ---")
sem_model = spreg.ML_Error(
    y.values,
    X_constant.values,
    w=your_weights_matrix_26_regions,
    name_x=X_constant.columns.tolist(),
    name_y='Poverty_Level'
)

# Coefficients and Variance-Covariance
betas = sem_model.betas.flatten()
vcov = sem_model.vm
std_errs = np.sqrt(np.diag(vcov))

# z-stats and p-values
z_stats = betas / std_errs
p_values = 2 * (1 - norm.cdf(np.abs(z_stats)))

# Names of coefficients (lambda is the spatial error coefficient)
coeff_names = ["lambda"] + sem_model.name_x  # lambda first, then x
print("Coefficients:")
for var, coef, std_err, z, p in zip(coeff_names, betas, std_errs, z_stats, p_values):
    print(f"{var:<25} Coef: {coef:>10.4f} | StdErr: {std_err:>8.4f} | z-Stat: {z:>8.4f} (p={p:.4f})")

# Log-Likelihood
loglik_sem = sem_model.logll
print(f"\nSEM Model Log-Likelihood: {loglik_sem:.4f}")

# AIC is available directly
print(f"SEM Model AIC: {sem_model.aic:.4f}")

# Manually compute BIC
n = sem_model.n
k = sem_model.k + 1  # includes lambda
bic_sem = k * np.log(n) - 2 * loglik_sem
print(f"SEM Model BIC (manually computed): {bic_sem:.4f}")
print("-" * 50)

print("\n--- Running Spatial Durbin Model (SDM) ---")
# ML_Lag explicitly runs an SDM
sdm_model = ML_Lag(
    y.values,
    X.values,  # no constant added
    w=your_weights_matrix_26_regions,
    slx_lags=1,
    name_y='Poverty_Level',
    name_x=X_cols,  # matches X (no constant)
    spat_diag=True
)

# --- Custom summary print for SDM model (ML_Lag with slx_lags=1) ---


print("\n--- Spatial Durbin Model (SDM) ---")
print(f"Model Title: {sdm_model.title}")
print(f"Dependent Variable: {sdm_model.name_y}")
print(f"Independent Variables (X): {sdm_model.name_x}")
print(f"Number of Observations: {sdm_model.n}")
print(f"Number of Estimated Coefficients (excluding rho): {sdm_model.k}")

# Extract coefficients (rho + intercept + X + WX)
betas = sdm_model.betas.flatten()
vcov = sdm_model.vm  # variance-covariance matrix (k+1 x k+1)
std_errs = np.sqrt(np.diag(vcov))

# Compute z-stats and p-values
z_stats = betas / std_errs
p_values = 2 * (1 - norm.cdf(np.abs(z_stats)))

# Coefficients, standard errors, and z-stats
print("\nCoefficients:")
for var, coef, std_err, z, p in zip(["rho"] + sdm_model.name_x, betas, std_errs, z_stats, p_values):
    print(f"{var:<25} Coef: {coef:>10.4f} | StdErr: {std_err:>8.4f} | z-Stat: {z:>8.4f} (p={p:.4f})")

# Spatial lag coefficient (rho)
print(f"\nSpatial Lag Coefficient (rho): {sdm_model.betas.flatten()[0]:.4f}")

# Log-likelihood
loglik_sdm = sdm_model.logll
print(f"\nSDM Model Log-Likelihood: {loglik_sdm:.4f}")

# AIC is available directly
print(f"SDM Model AIC: {sdm_model.aic:.4f}")

# BIC: manually compute
n = sdm_model.n
k = sdm_model.k + 1 + len(X_cols)  # Intercept + X + WX + rho
bic_sdm = k * np.log(n) - 2 * loglik_sdm
print(f"SDM Model BIC (manually computed): {bic_sdm:.4f}")
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
lr_sdm_vs_sar = 2 * (sdm_model.logll - sar_model.logll)
df_sdm_vs_sar = len(X_cols)  # Number of additional parameters in WX_theta
# You'd typically use a chi-squared distribution to get the p-value
from scipy.stats import chi2

p_value_sdm_vs_sar = 1 - chi2.cdf(lr_sdm_vs_sar, df_sdm_vs_sar)
print(
    f"LR Test (SDM vs. SAR): Statistic = {lr_sdm_vs_sar:.4f}, DF = {df_sdm_vs_sar}, p-value = {p_value_sdm_vs_sar:.4f}")

# LR Test: SDM vs. SEM (Testing if WX_theta terms and rho (lagged Y) are jointly zero,
# OR more commonly just WX_theta terms are zero and error model parameters are equivalent.)
# This comparison is a bit more nuanced. A common test for SDM vs SEM in PySAL is the
# `LR_SAR_diag` test within spreg if you ran an `OLS_lag_error` or similar.
# For simplicity, if `spreg.diagnostics` doesn't provide a direct method for `ML_Durbin` vs `ML_Error`
# that's explicitly testing for the spatially lagged X terms,
# you can use the same logic as SDM vs SAR, recognizing that the "restricted" model is SEM.
# The degrees of freedom would again be `len(X_cols)`.
lr_sdm_vs_sem = 2 * (sdm_model.logll - sem_model.logll)
df_sdm_vs_sem = len(X_cols)  # Assuming this is the difference in parameters due to WX_theta
p_value_sdm_vs_sem = 1 - chi2.cdf(lr_sdm_vs_sem, df_sdm_vs_sem)
print(
    f"LR Test (SDM vs. SEM): Statistic = {lr_sdm_vs_sem:.4f}, DF = {df_sdm_vs_sem}, p-value = {p_value_sdm_vs_sem:.4f}")

print("-" * 50)
