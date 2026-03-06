
# Climate Poverty Spatial Analysis

This project contains scripts, processed datasets, and documentation used to reproduce the spatial econometric analysis examining the interaction between climate variability, infrastructure access, and regional poverty dynamics in Tanzania.

The repository supports transparency and reproducibility for the associated research manuscript currently under peer review.

## Repository Structure

scripts/
Python scripts implementing spatial econometric models.

data/
Processed datasets used in regression analysis.

shapefiles/
Administrative boundary data used for spatial analysis.

supplementary/
Supplementary methodological documentation.

## Models Implemented

- Spatial Autoregressive Model (SAR)
- Geographically Weighted Regression (GWR)
- Spatial Durbin Model (SDM)

## Reproducibility

All scripts and processed datasets necessary to reproduce the spatial econometric analysis are included.

Raw household survey microdata cannot be shared due to confidentiality agreements, but aggregated datasets used in regression models are provided.

## Software Environment

The analysis was conducted using:

- Python
- GeoPandas
- PySAL
- MGWR
- NumPy
- Statsmodels
climate_poverty_analysis
│
├ README.md
│
├ data
│   ├ poverty_dataset_processed.csv
│   ├ infrastructure_dataset.csv
│   └ climate_dataset.csv
│
├ scripts
│   ├ 1_spatial_distribution_of_poverty_incidence.py
│   ├ 2_spatial_distribution_of_literacy_rate_coefficient.py
│   ├ 3_local_r2_map_explaining_income_levels.py
│   ├ 4_spatial_dependence_of_income_levels.py
│   └ complete_code_raw.py
│
├ shapefiles
│   ├ tanzania_regions.shp
│   ├ tanzania_regions.shx
│   ├ tanzania_regions.dbf
│   └ tanzania_regions.prj
│
└ supplementary
    └ Supplementary_Methods_Spatial_Econometric_Analysis.pdf
  requirements.txt
  numpy
pandas
geopandas
pysal
libpysal
matplotlib
scikit-learn
