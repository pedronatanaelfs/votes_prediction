# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Rust for pywinpty (fixing the pywinpty issue)
RUN apt-get update && apt-get install -y curl build-essential
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Expose port 8888 for Jupyter
EXPOSE 8888

# Run both Python scripts and start JupyterLab
CMD ["bash", "-c", "python main.py && python get_proposicao_types.py && jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''"]
