
# Chamber of Deputies Open Data Project

This project fetches all propositions data from the Brazilian Chamber of Deputies Open Data API and performs analysis in Jupyter notebooks. The environment for this project can be reproduced using **Docker** or **Conda**.

## Project Structure

- **main.py**: The main file that fetches data from the API and saves it in a CSV file.
- **all_propositions.csv**: The generated file containing all propositions data fetched from the API.
- **notebook.ipynb**: Jupyter notebook for analyzing the propositions data.
- **Dockerfile**: Docker setup for a reproducible environment.
- **requirements.txt**: Python package dependencies.
- **environment.yml**: Conda environment setup (alternative to Docker).

## How to Set Up the Environment

### Option 1: Using Docker

1. Install **Docker**: Follow the instructions at https://www.docker.com/get-started to install Docker.

2. Clone the repository.

3. Build the Docker image:

   ```bash
   docker build -t my-jupyter-env .
   ```

4. Run the Docker container:

   ```bash
   docker run -p 8888:8888 my-jupyter-env
   ```

5. Open Jupyter Notebook by navigating to `http://localhost:8888` in your browser.

### Option 2: Using Conda

1. Install **Anaconda** or **Miniconda**: Follow the instructions at https://docs.conda.io/en/latest/miniconda.html to install Conda.

2. Clone the repository.

3. Create the Conda environment from the `environment.yml` file:

   ```bash
   conda env create -f environment.yml
   ```

4. Activate the environment:

   ```bash
   conda activate dados_abertos
   ```

5. Launch Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

### Installing Requirements

If you're not using Docker or Conda and want to set up the environment manually, install the dependencies with:

```bash
pip install -r requirements.txt
```

## How to Run the Project

1. After setting up the environment (via Docker, Conda, or manually), you can run the Jupyter notebook and start analyzing the propositions data.

2. To fetch the data, simply run `main.py`:

   ```bash
   python main.py
   ```

This will fetch all propositions and save them to a CSV file (`all_propositions.csv`).

## About the API

The Chamber of Deputies Open Data API provides data on propositions, including information such as ID, number, summary, author, situation, and more. Check the [official documentation](https://dadosabertos.camara.leg.br/swagger/api.html) for more details.

## License

This project is licensed under the MIT License.
