import pandas as pd
import requests
import os
import logging
import time
import concurrent.futures
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Define a function to get authors' names from the API
def get_authors_from_api(proposition_id):
    start_time = time.time()  # Log start time of the API call
    url = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{proposition_id}/autores"
    
    try:
        # Make a GET request to the API
        response = requests.get(url)
        end_time = time.time()  # Log end time of the API call
        
        # Log the time taken for the API call
        logger.info(f"API call took {end_time - start_time:.2f} seconds for proposition {proposition_id}")
        
        if response.status_code == 200:
            # Parse the XML response
            soup = BeautifulSoup(response.content, 'xml')
            
            # Find all authors in the XML
            authors = soup.find_all('autor')
            
            # Extract names of the authors
            author_names = [author.find('nome').text for author in authors]
            return author_names
        else:
            logger.warning(f"Failed to fetch data for proposition {proposition_id} - Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching data for proposition {proposition_id}: {e}")
        return None

# Path to the data folder for authors
authors_folder = 'data/authors'
os.makedirs(authors_folder, exist_ok=True)

# Function to handle API calls for a batch of propositions
def process_batch(proposition_ids):
    batch_results = []
    for proposition_id in proposition_ids:
        logger.debug(f"Processing proposition ID: {proposition_id}")
        authors = get_authors_from_api(proposition_id)
        if authors:
            # Append the proposition ID and authors to the results
            for author in authors:
                batch_results.append({
                    'Proposition ID': proposition_id,
                    'Author Name': author
                })
    return batch_results

# Process the propositions year by year
for year in range(2003, 2025):
    logger.info(f"Processing year {year}...")
    
    # Path to the CSV file for the current year
    file_path = f'data/propositions/all_propositions_{year}.csv'
    
    if os.path.exists(file_path):
        logger.info(f"Reading file: {file_path}")
        
        # Read the CSV file (only necessary columns to optimize memory usage)
        df = pd.read_csv(file_path, usecols=['id'], dtype={'id': 'int32'}, low_memory=False)
        logger.info(f"Loaded {len(df)} rows for year {year}.")
        
        # Create a list to store authors' data for the current year
        all_authors_data = []
        
        # Process the CSV file in chunks for better performance
        chunk_size = 1000  # Adjust this value based on your needs
        logger.info(f"Processing propositions in chunks for year {year}...")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_propositions = {}
            for start in range(0, len(df), chunk_size):
                chunk = df.iloc[start:start + chunk_size]
                future = executor.submit(process_batch, chunk['id'])
                future_to_propositions[future] = chunk['id']
            
            for future in concurrent.futures.as_completed(future_to_propositions):
                batch_results = future.result()
                all_authors_data.extend(batch_results)

        # Convert the list of authors data into a DataFrame
        logger.info(f"Converting data to DataFrame for year {year}...")
        authors_df = pd.DataFrame(all_authors_data)
        
        # Save the DataFrame to a CSV file for the current year
        output_file = os.path.join(authors_folder, f'authors_per_proposition_{year}.csv')
        authors_df.to_csv(output_file, index=False)
        
        logger.info(f"Authors data for year {year} has been saved to: {output_file}")
    else:
        logger.warning(f"File for year {year} does not exist: {file_path}")

logger.info("Processing completed for all years.")
