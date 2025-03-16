import requests
import csv

# URL to fetch proposition data
url = 'https://dadosabertos.camara.leg.br/api/v2/proposicoes'

# Loop through the years from 2003 to 2024
for year in range(2003, 2025):
    # Parameters for pagination and filtering for the current year
    params = {
        'itens': 100,  # Request 100 items per page
        'pagina': 1,   # Start from the first page
        'ano': year,   # Filter for propositions from the current year
        'dataInicio': f'{year}-01-01',  # Start date for the proposition processing
        'dataFim': f'{year}-12-31'      # End date for the proposition processing
    }

    # List to store all propositions for the current year
    all_propositions = []

    # Flag to track if there are more pages of data
    more_data = True

    while more_data:
        # Making the GET request
        response = requests.get(url, params=params)

        # Checking the request status
        if response.status_code == 200:
            # Converting the response to JSON
            data = response.json()

            # Adding the fetched data to the list of all propositions
            all_propositions.extend(data['dados'])

            # Check if there's more data (if we have a next page)
            if data['dados']:
                params['pagina'] += 1  # Move to the next page
            else:
                more_data = False  # No more data, stop the loop

            print(f"Fetched {len(data['dados'])} propositions from page {params['pagina'] - 1} for year {year}")
        else:
            print(f"Error fetching data: {response.status_code} for year {year}")
            more_data = False  # Stop in case of an error

    # Defining the CSV file name for the current year
    csv_filename = f'all_propositions_{year}.csv'

    # Writing data to CSV
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header row (the column names)
        header = ['id', 'numero', 'ano', 'ementa', 'siglaTipo']
        writer.writerow(header)

        # Write each proposition data row by row
        for proposition in all_propositions:
            row = [
                proposition.get('id', ''),
                proposition.get('numero', ''),
                proposition.get('ano', ''),
                proposition.get('ementa', ''),
                proposition.get('siglaTipo', '')  # Join list of themes into a string
            ]
            writer.writerow(row)

    print(f"All propositions from {year} saved in '{csv_filename}' with a total of {len(all_propositions)} propositions.")
