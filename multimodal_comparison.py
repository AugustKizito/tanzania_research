import geopandas as gpd
import libpysal as lp
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, chi2  # Ensure chi2 is imported for LR tests
from spreg import ML_Lag, ML_Error
import warnings
from mgwr.sel_bw import Sel_BW
from mgwr.gwr import GWR

#from estimation_of_ols_sar_sem_and_sdm import lr_sdm_vs_sem

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
data_dict = {
    'RegionName': regions,
    'Poverty_Level': poverty_incidence,
    'Total Health Facilities': total_health_facilities,
    'Total Access to Water %': total_access_to_water,
    'Total Access to Electricity': total_access_to_electricity
}
df_from_arrays = pd.DataFrame(data_dict)

# --- Load Shapefile and Merge Data ---
regions_path = "tanzania_regions/kIZITO.shp"
try:
    gdf = gpd.read_file(regions_path)
    df_from_arrays['RegionName_Clean'] = df_from_arrays['RegionName'].str.strip().str.title()
    gdf['ADM1_EN_Clean'] = gdf['ADM1_EN'].str.strip().str.title()
    df_from_arrays['RegionName_Clean'] = df_from_arrays['RegionName_Clean'].replace({'Mororgoro': 'Morogoro'})
    merged_gdf = gdf.merge(df_from_arrays, left_on='ADM1_EN_Clean', right_on='RegionName_Clean', how='left')

    if merged_gdf['Poverty_Level'].isna().any():
        print("WARNING: Some regions did not merge successfully and have NaN for Poverty_Level.")
        print("Unmerged regions (based on shapefile names):",
              merged_gdf[merged_gdf['Poverty_Level'].isna()]['ADM1_EN'].tolist())
    else:
        print("All regions successfully merged with data from arrays.")

except FileNotFoundError:
    print(f"Error: Shapefile not found at {regions_path}. Please ensure the path is correct.")
    merged_gdf = df_from_arrays.copy()
    merged_gdf['geometry'] = None
    print("Proceeding with non-spatial analysis due to missing shapefile.")

# --- 2. Define Dependent and Independent Variables from merged_gdf ---
y = merged_gdf['Poverty_Level']

X_cols = [
    'Total Health Facilities',
    'Total Access to Water %',
    'Total Access to Electricity',
]
X = merged_gdf[X_cols]

X_constant = sm.add_constant(X)

# --- 3. Create Spatial Weights Matrix for 26 Regions ---
if 'geometry' in merged_gdf.columns and merged_gdf['geometry'].iloc[0] is not None:
    your_weights_matrix_26_regions = lp.weights.Queen.from_dataframe(merged_gdf, use_index=False)
    your_weights_matrix_26_regions.transform = 'R'
    print(f"\nSpatial weights matrix created for {len(your_weights_matrix_26_regions.id_order)} regions.")
else:
    your_weights_matrix_26_regions = None
    print("\nSkipping spatial weights matrix creation as geometry data is not available.")

# --- 4. Run Each Model and Print Summaries ---

print("\n" + "=" * 70)
print("--- Running OLS Model (Non-Spatial) ---")
print("=" * 70)
ols_model = sm.OLS(y, X_constant).fit()
print(ols_model.summary())
print("=" * 70 + "\n")

if your_weights_matrix_26_regions:
    print("\n" + "=" * 70)
    print("--- Running Spatial Autoregressive (SAR) Model ---")
    print("=" * 70)
    sar_model = ML_Lag(y.values, X_constant.values, w=your_weights_matrix_26_regions,
                       name_y='Poverty_Level', name_x=X_constant.columns.tolist())

    print(f"Model Title: {sar_model.title}")
    print(f"Dependent Variable: {sar_model.name_y}")
    print(f"Independent Variables (X): {sar_model.name_x}")
    print(f"Number of Observations: {sar_model.n}")

    # Extract coefficients (rho + intercept + X)
    betas_sar = sar_model.betas.flatten()
    vcov_sar = sar_model.vm
    std_errs_sar = np.sqrt(np.diag(vcov_sar))

    # Compute z-stats and p-values
    z_stats_sar = betas_sar / std_errs_sar
    p_values_sar = 2 * (1 - norm.cdf(np.abs(z_stats_sar)))

    # Coefficients, standard errors, and z-stats
    print("\nCoefficients:")
    # The order of betas from ML_Lag is usually [rho, intercept, X_vars...]
    sar_coeff_names = ["rho"] + sar_model.name_x
    print(f"{'Variable':<25} {'Coef':>10} {'StdErr':>10} {'z-Stat':>10} {'p-value':>10}")
    print("-" * 70)
    for var, coef, std_err, z, p in zip(sar_coeff_names, betas_sar, std_errs_sar, z_stats_sar, p_values_sar):
        print(f"{var:<25} {coef:>10.4f} {std_err:>10.4f} {z:>10.4f} {p:>10.4f}")

    print(f"\nSAR Model Log-Likelihood: {sar_model.logll:.4f}")
    print(f"SAR Model AIC: {sar_model.aic:.4f}")

    # BIC: manually compute
    n_sar = sar_model.n
    k_sar = sar_model.k  # k includes all estimated parameters: rho, intercept, X_vars
    bic_sar = k_sar * np.log(n_sar) - 2 * sar_model.logll
    print(f"SAR Model BIC (manually computed): {bic_sar:.4f}")
    print("=" * 70 + "\n")

    print("\n" + "=" * 70)
    print("--- Running Spatial Error Model (SEM) ---")
    print("=" * 70)
    sem_model = ML_Error(
        y.values,
        X_constant.values,
        w=your_weights_matrix_26_regions,
        name_x=X_constant.columns.tolist(),
        name_y='Poverty_Level'
    )

    print(f"Model Title: {sem_model.title}")
    print(f"Dependent Variable: {sem_model.name_y}")
    print(f"Independent Variables (X): {sem_model.name_x}")
    print(f"Number of Observations: {sem_model.n}")

    # Coefficients and Variance-Covariance
    betas_sem = sem_model.betas.flatten()
    vcov_sem = sem_model.vm
    std_errs_sem = np.sqrt(np.diag(vcov_sem))

    # z-stats and p-values
    z_stats_sem = betas_sem / std_errs_sem
    p_values_sem = 2 * (1 - norm.cdf(np.abs(z_stats_sem)))

    # Names of coefficients (lambda is the spatial error coefficient, then X_constant variables)
    # The order of betas from ML_Error is usually [lambda, intercept, X_vars...]
    sem_coeff_names = ["lambda"] + sem_model.name_x
    print("\nCoefficients:")
    print(f"{'Variable':<25} {'Coef':>10} {'StdErr':>10} {'z-Stat':>10} {'p-value':>10}")
    print("-" * 70)
    for var, coef, std_err, z, p in zip(sem_coeff_names, betas_sem, std_errs_sem, z_stats_sem, p_values_sem):
        print(f"{var:<25} {coef:>10.4f} {std_err:>10.4f} {z:>10.4f} {p:>10.4f}")

    # Log-Likelihood
    print(f"\nSEM Model Log-Likelihood: {sem_model.logll:.4f}")

    # AIC is available directly
    print(f"SEM Model AIC: {sem_model.aic:.4f}")

    # Manually compute BIC
    n_sem = sem_model.n
    k_sem = sem_model.k  # k includes all estimated parameters: lambda, intercept, X_vars
    bic_sem = k_sem * np.log(n_sem) - 2 * sem_model.logll
    print(f"SEM Model BIC (manually computed): {bic_sem:.4f}")
    print("=" * 70 + "\n")

    print("\n" + "=" * 70)
    print("--- Running Spatial Durbin Model (SDM) ---")
    print("=" * 70)
    # ML_Lag with slx_lags=1 is the correct way to run SDM in spreg v1.8.1
    sdm_model = ML_Lag(
        y.values,
        X.values,  # no constant added
        w=your_weights_matrix_26_regions,
        slx_lags=1,
        name_y='Poverty_Level',
        name_x=X_cols,  # matches X (no constant)
        spat_diag=True
    )

    print(f"Model Title: {sdm_model.title}")
    print(f"Dependent Variable: {sdm_model.name_y}")
    print(f"Independent Variables (X): {sdm_model.name_x}")
    print(f"Number of Observations: {sdm_model.n}")

    # Extract coefficients (rho + intercept + X + WX)
    betas_sdm = sdm_model.betas.flatten()
    vcov_sdm = sdm_model.vm
    std_errs_sdm = np.sqrt(np.diag(vcov_sdm))

    # Compute z-stats and p-values
    z_stats_sdm = betas_sdm / std_errs_sdm
    p_values_sdm = 2 * (1 - norm.cdf(np.abs(z_stats_sdm)))

    # Coefficient names: rho, intercept, X_cols, W_X_cols
    sdm_coeff_names = ["rho", "CONSTANT"] + X_cols + [f"W_{col}" for col in X_cols]

    print("\nCoefficients:")
    print(f"{'Variable':<25} {'Coef':>10} {'StdErr':>10} {'z-Stat':>10} {'p-value':>10}")
    print("-" * 70)
    # Ensure all names match the length of betas
    if len(sdm_coeff_names) != len(betas_sdm):
        # Fallback for names if there's a mismatch (e.g., if constant handling varies)
        print("Warning: Mismatch between expected coefficient names and actual betas length. Using generic names.")
        sdm_coeff_names = [f"Beta_{i}" for i in range(len(betas_sdm))]

    for var, coef, std_err, z, p in zip(sdm_coeff_names, betas_sdm, std_errs_sdm, z_stats_sdm, p_values_sdm):
        print(f"{var:<25} {coef:>10.4f} {std_err:>10.4f} {z:>10.4f} {p:>10.4f}")

    # Log-likelihood
    print(f"\nSDM Model Log-Likelihood: {sdm_model.logll:.4f}")

    # AIC is available directly
    print(f"SDM Model AIC: {sdm_model.aic:.4f}")

    # BIC: manually compute
    n_sdm = sdm_model.n
    k_sdm = sdm_model.k  # k includes all estimated parameters: rho, intercept, X_vars, WX_vars
    bic_sdm = k_sdm * np.log(n_sdm) - 2 * sdm_model.logll
    print(f"SDM Model BIC (manually computed): {bic_sdm:.4f}")
    print("=" * 70 + "\n")

    print("\n" + "=" * 70)
    print("--- Spatial Durbin Model (SDM) - Manual Impact Decomposition ---")
    print("=" * 70)

    # --- MANUAL SDM Impact Calculation ---
    n = sdm_model.n
    rho = sdm_model.betas[0][0]
    b_d = sdm_model.betas[2:2 + len(X_cols)]  # Direct effects
    b_i = sdm_model.betas[2 + len(X_cols):]  # Indirect effects

    W = your_weights_matrix_26_regions.full()[0]
    I = np.eye(n)
    P = np.linalg.inv(I - rho * W)

    direct_impacts = []
    indirect_impacts = []
    total_impacts = []

    for i in range(len(X_cols)):
        bd = b_d[i][0]
        bi = b_i[i][0]

        S = P @ (bd * np.eye(n) + bi * W)
        direct = np.trace(S) / n
        indirect = (np.sum(S) - np.trace(S)) / n
        total = direct + indirect

        direct_impacts.append(direct)
        indirect_impacts.append(indirect)
        total_impacts.append(total)

    # Display
    print(f"{'Variable':<30} {'Direct':>10} {'Indirect':>10} {'Total':>10}")
    print("-" * 70)
    for var, d, ind, tot in zip(X_cols, direct_impacts, indirect_impacts, total_impacts):
        print(f"{var:<30} {d:>10.4f} {ind:>10.4f} {tot:>10.4f}")
    print("=" * 70 + "\n")

    # --- 5. Likelihood Ratio Test Results ---
    print("\n" + "=" * 70)
    print("--- Likelihood Ratio (LR) Test Results ---")
    print("=" * 70)

    # LR Test: SDM vs. SAR (Testing if WX_theta terms are jointly zero)
    # In spreg, ML_Durbin (SDM) is the unrestricted model, ML_Lag (SAR) is the restricted model
    lr_sdm_vs_sar = 2 * (sdm_model.logll - sar_model.logll)
    df_sdm_vs_sar = len(X_cols)  # Number of WX terms
    p_value_sdm_vs_sar = 1 - chi2.cdf(lr_sdm_vs_sar, df_sdm_vs_sar)
    print(
        f"LR Test (SDM vs. SAR): Statistic = {lr_sdm_vs_sar:.4f}, DF = {df_sdm_vs_sar}, p-value = {p_value_sdm_vs_sar:.4f}")

    # LR Test: SDM vs. SEM (Testing if WX_theta terms and rho are jointly zero)
    # Assumes SEM does not include lagged X or lagged Y (rho)
    lr_sdm_vs_sem = 2 * (sdm_model.logll - sem_model.logll)
    df_sdm_vs_sem = len(X_cols)  # Number of WX terms again assumed
    p_value_sdm_vs_sem = 1 - chi2.cdf(lr_sdm_vs_sem, df_sdm_vs_sem)
    print(
        f"LR Test (SDM vs. SEM): Statistic = {lr_sdm_vs_sem:.4f}, DF = {df_sdm_vs_sem}, p-value = {p_value_sdm_vs_sem:.4f}")

    print("=" * 70 + "\n")


else:
    print("\nSpatial models (SAR, SEM, SDM) skipped due to missing shapefile/weights matrix.")


if your_weights_matrix_26_regions:
    print("\n" + "=" * 70)
    print("--- Running Geographically Weighted Regression (GWR) ---")
    print("=" * 70)

    # Convert geometry to list of tuples for coords
    if merged_gdf.geometry.crs and merged_gdf.geometry.crs.is_geographic:
        print("Warning: GWR is best run on projected CRS, but using geographic for now.")
    # Convert geometry to list of tuples for coords
    coords = [tuple((geom.centroid.x, geom.centroid.y)) for geom in merged_gdf.geometry]

    y_gwr = y.values.reshape(-1, 1)
    X_gwr = sm.add_constant(X).values

    # Use fixed bandwidth (distance-based kernel)
    selector = Sel_BW(coords, y_gwr, X_gwr, fixed=True)  # <<< FIXED bandwidth
    bw = selector.search()

    print(f"Optimal fixed bandwidth: {bw:.4f}")

    # Fit the GWR model
    gwr_model = GWR(coords, y_gwr, X_gwr, bw=bw, fixed=True)
    gwr_results = gwr_model.fit()
    print(gwr_results.summary())

    # Local coefficients summary
    local_coefs = gwr_results.params
    gwr_variable_names = ['Intercept'] + X.columns.tolist()

    print("\nSummary of GWR Local Coefficients:")
    print("{:<25} {:<10} {:<10} {:<10}".format("Variable", "Mean", "Min", "Max"))
    print("-" * 60)
    for i, col_name in enumerate(gwr_variable_names):
        mean_val = np.mean(local_coefs[:, i])
        min_val = np.min(local_coefs[:, i])
        max_val = np.max(local_coefs[:, i])
        print(f"{col_name:<25} {mean_val:<10.4f} {min_val:<10.4f} {max_val:<10.4f}")
    print("-" * 60)
    print("=" * 70 + "\n")
else:
    print("\nGWR model skipped due to missing shapefile/weights matrix.")
