import os
import requests
import pandas as pd
import json
from tqdm import tqdm  # For progress bar

# Base URL for the API endpoint
BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/votacoes/"

# Paths
data_folder = "data/voting"
output_folder = "data/voting_details"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# List to store failed requests for retrying later
failed_requests = []

# Function to fetch voting details
def fetch_voting_details(voting_id):
    url = f"{BASE_URL}{voting_id}"
    try:
        response = requests.get(url, timeout=10)  # Add a timeout to avoid hanging
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.SSLError as e:
        print(f"SSL Error for voting ID {voting_id}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed for voting ID {voting_id}: {e}")
        return None

# Iterate over each year from 2003 to 2024
for year in range(2011, 2025):
    file_name = f"votacoes_{year}.csv"
    file_path = os.path.join(data_folder, file_name)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_name} does not exist. Skipping...")
        continue
    
    # Load the dataset
    df = pd.read_csv(file_path)
    
    # Prepare a list to store all voting details
    voting_details = []
    
    # Iterate over each row in the dataset
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc=f"Processing {year}"):
        voting_id = row['id']
        details = fetch_voting_details(voting_id)
        
        if details:
            voting_details.append(details)
        else:
            failed_requests.append((year, voting_id))  # Log failed requests
    
    # Save the collected details to a JSON file
    output_file = os.path.join(output_folder, f"voting_details_{year}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(voting_details, f, ensure_ascii=False, indent=4)
    
    print(f"Saved voting details for {year} to {output_file}")

# Retry failed requests at the end
if failed_requests:
    print("\nRetrying failed requests...")
    retry_success = []
    
    for year, voting_id in tqdm(failed_requests, desc="Retrying failed requests"):
        details = fetch_voting_details(voting_id)
        
        if details:
            retry_success.append((year, voting_id, details))
    
    # Append retried details to their respective year files
    for year, voting_id, details in retry_success:
        output_file = os.path.join(output_folder, f"voting_details_{year}.json")
        
        # Load existing data
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        # Append the retried details
        existing_data.append(details)
        
        # Save the updated data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully retried and saved voting ID {voting_id} for year {year}.")
    
    # Log remaining failed requests
    remaining_failures = set(failed_requests) - set((year, voting_id) for year, voting_id, _ in retry_success)
    if remaining_failures:
        print("\nThe following requests could not be processed after retrying:")
        for year, voting_id in remaining_failures:
            print(f"Year: {year}, Voting ID: {voting_id}")

print("All data has been processed and saved.")