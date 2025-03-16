import requests
import csv

# URL to fetch proposition types
url = 'https://dadosabertos.camara.leg.br/api/v2/referencias/proposicoes/siglaTipo'

# Making the GET request
response = requests.get(url)

# Checking the request status
if response.status_code == 200:
    # Converting the response to JSON
    data = response.json()

    # Defining the CSV file name
    csv_filename = 'proposition_types.csv'

    # Opening the CSV file for writing
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Writing the header of the table with translated column names
        writer.writerow(['Code', 'Abbreviation', 'Name', 'Description'])

        # Writing the proposition types to the table
        for type_info in data['dados']:
            writer.writerow([type_info['cod'], type_info['sigla'], type_info['nome'], type_info['descricao']])

    print(f"CSV file '{csv_filename}' created successfully!")

else:
    print(f"Error fetching data: {response.status_code}")
