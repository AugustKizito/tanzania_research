# Tanzania Research Project

This project analyzes the spatial distribution of various socioeconomic factors in Tanzania using geospatial data and Python. The repository contains scripts and data needed to visualize and analyze this information.

## Getting Started

These instructions will guide you through setting up a virtual environment in PyCharm and running the project.
### 3.1 Context and Data Sources

The research was conducted in Tanzania, the largest country in East Africa, covering an area of approximately 945,087 square kilometers. Tanzania is situated on the eastern coast of Africa and shares borders with eight neighboring countries. The country has a diverse economy and significant spatial disparities in poverty distribution. The study area encompasses seven regions: Dar es Salaam, Mwanza, Arusha, Mbeya, Singida, Pwani, and Kigoma. These regions were selected to represent different zones in Tanzania, each with distinct geographical features and socio-economic characteristics.

Insert Location Map Here (Map Title: "Study Area Location Map")

This map highlights the specific regions included in the study, providing a visual context for the analysis of spatial patterns and socio-economic factors influencing poverty in Tanzania.
### 3.1 Context and Data Sources

The research was conducted in Tanzania, the largest country in East Africa, covering an area of approximately 945,087 square kilometers. Tanzania is situated on the eastern coast of Africa and shares borders with eight neighboring countries. The country has a diverse economy and significant spatial disparities in poverty distribution. The study area encompasses seven regions: Dar es Salaam, Mwanza, Arusha, Mbeya, Singida, Pwani, and Kigoma. These regions were selected to represent different zones in Tanzania, each with distinct geographical features and socio-economic characteristics.

Insert Location Map Here (Map Title: "Study Area Location Map")

This map highlights the specific regions included in the study, providing a visual context for the analysis of spatial patterns and socio-economic factors influencing poverty in Tanzania.


### Prerequisites

- [PyCharm](https://www.jetbrains.com/pycharm/download/)
- [Python 3.x](https://www.python.org/downloads/)

### Installation

#### Step 1: Clone the Repository

First, you need to clone the repository to your local machine. Open a terminal and run the following command:

```bash
git clone https://github.com/AugustKizito/tanzania_research.git
```

#### Step 2: Open the Project in PyCharm
Open PyCharm.

Click on `File -> Open...`.

Navigate to the location where you cloned the repository and select the `tanzania_research` directory.

Click `OK`.

#### Step 3: Set Up a Virtual Environment
Open the terminal within PyCharm or use an external terminal.

Navigate to the project directory if you are not already there:

```bash
cd path_to_your_project/tanzania_research
```

Create a virtual environment named env:

```bash
python -m venv env
Activate the virtual environment:
```
Windows:

```bash
.\env\Scripts\activate
MacOS/Linux:
```

```bash
source env/bin/activate
```
Install the required packages:

```bash
pip install -r requirements.txt
```
#### Step 4: Configure PyCharm to Use the Virtual Environment
Go to `File -> Settings` (or `PyCharm -> Preferences` on macOS).

Navigate to `Project: tanzania_research -> Python Interpreter`.

Click the gear icon and select `Add...`.

Choose `Existing environment` and navigate to the location of the `env` folder you created.

Select the Python interpreter located in the `env` directory.

- **Windows:** `env\Scripts\python.exe`
- **MacOS/Linux:** `env/bin/python`

Click `OK` and apply the changes.

#### Step 5: Running the Project
Ensure that the virtual environment is activated.

In the terminal, navigate to the project directory.

Run the scripts you are interested in. For example:

```bash
python draw_spatial_distribution.py


```bash
python draw_spatial_distribution.py
```
Additional Notes
Ensure that all necessary data files (such as shapefiles) are located in the appropriate directories as expected by the scripts.
If you encounter any issues with missing packages, you can manually install them using pip install <package-name>.