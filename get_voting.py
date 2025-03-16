import pandas as pd
import requests
import os
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Create folder for voting data
voting_folder = 'data/voting'
os.makedirs(voting_folder, exist_ok=True)

# Function to fetch voting data for a specific year with retries
def get_votacoes_for_year(year, page=1, retries=10, timeout=60):
    url = f"https://dadosabertos.camara.leg.br/api/v2/votacoes"
    
    # Define the start and end date for the year
    data_inicio = f"{year}-01-01"
    data_fim = f"{year}-12-31"
    
    params = {
        'dataInicio': data_inicio,
        'dataFim': data_fim,
        'pagina': page,
        'itens': 100  # Max limit per request (recommended by the API)
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)  # Set timeout for requests
            if response.status_code == 200:
                return response.json()  # Return the JSON response
            elif response.status_code == 504:
                logger.warning(f"Gateway Timeout error for year {year}, page {page}. Retrying...")
                time.sleep(5 * (attempt + 1))  # Exponential backoff
            elif response.status_code == 503:
                logger.warning(f"Service Unavailable (503) for year {year}, page {page}. Retrying...")
                time.sleep(10 * (attempt + 1))  # Longer delay for 503 errors
            else:
                logger.warning(f"Failed to fetch data for year {year}, page {page} - Status code: {response.status_code}")
                break
        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out for year {year}, page {page}. Retrying...")
            time.sleep(5 * (attempt + 1))  # Exponential backoff for timeouts
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for year {year}, page {page}: {e}")
            break
    return None

# Function to handle pagination and gather all votes for a given year
def get_all_votacoes_for_year(year):
    all_votacoes = []
    page = 1
    while True:
        logger.info(f"Fetching data for year {year}, page {page}...")
        data = get_votacoes_for_year(year, page)
        if data and 'dados' in data:
            votacoes = data['dados']
            all_votacoes.extend(votacoes)
            if len(votacoes) < 100:  # If fewer than 100 items, we've reached the last page
                break
            page += 1
        else:
            logger.error(f"Failed to fetch data for year {year}, page {page}. Ending fetch.")
            break
        time.sleep(20)  # Increase delay to 10 seconds between requests to avoid rate limits
    return all_votacoes

# Process each year from 2013 to 2024
for year in (2015, ):
    logger.info(f"Processing year {year}...")
    
    # Fetch all voting data for the current year
    votacoes = get_all_votacoes_for_year(year)
    
    if votacoes:
        # Convert the list of voting data into a DataFrame
        logger.info(f"Converting voting data for year {year} into DataFrame...")
        votacoes_df = pd.DataFrame(votacoes)
        
        # Save the DataFrame to a CSV file for the current year
        output_file = os.path.join(voting_folder, f'votacoes_{year}.csv')
        votacoes_df.to_csv(output_file, index=False)
        logger.info(f"Voting data for year {year} has been saved to: {output_file}")
    else:
        logger.warning(f"No voting data found for year {year}. Skipping.")

logger.info("Processing completed for all years.")
