# Votes Prediction Project README

This project focuses on predicting Brazilian federal deputies' votes based on historical voting data, author characteristics, and bill proposals.

## Project Structure

See the notebook organization in [notebooks/README.md](notebooks/README.md)

## Environment Setup

To configure the development and execution environment for this project, follow the steps below:

### Prerequisites

- Anaconda or Miniconda installed
- Git (optional, for cloning the repository)

### Environment Installation

1. Clone the repository:
   ```bash
   git clone [REPOSITORY_URL]
   cd votes_prediction
   ```

2. Create an Anaconda virtual environment:
   ```bash
   # Create conda environment with Python 3.9
   conda create -n votes_prediction python=3.9
   
   # Activate conda environment (Windows/Linux/macOS)
   conda activate votes_prediction
   ```

3. Install dependencies:
   ```bash
   # Using pip within conda environment
   pip install -r requirements.txt
   
   # Alternatively, you can use conda to install packages
   # conda install --file requirements.txt
   ```

### Running Scripts

To execute Python scripts in the project:

```bash
# Example of running the data acquisition script
python "01 - Global Prediction/data/data_aquisition.py"

# Example of running the community detection script
python "01 - Global Prediction/Author's Group/authors_community_detection.py"
```

## Using Jupyter Notebooks

To work with Jupyter notebooks in the project:

1. With the conda environment activated, install JupyterLab (if not already installed):
   ```bash
   conda install jupyterlab
   ```

2. Register the conda environment as a Jupyter kernel:
   ```bash
   conda install ipykernel
   python -m ipykernel install --user --name=votes_prediction --display-name="Python (votes_prediction)"
   ```

3. Start JupyterLab:
   ```bash
   jupyter lab
   ```

4. When opening notebooks, select the `Python (votes_prediction)` kernel to ensure access to all installed dependencies.
