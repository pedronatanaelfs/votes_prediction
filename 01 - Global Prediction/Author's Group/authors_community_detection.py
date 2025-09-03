import pandas as pd
import os
import pickle
import leidenalg as la
import igraph as ig
import networkx as nx
import numpy as np
from collections import defaultdict
from pathlib import Path
import random
import matplotlib.pyplot as plt
import seaborn as sns
import re

# 1 - Load the dataset
print("Loading voting dataset...")
df_votes = pd.read_csv('01 - Global Prediction/data/vote_sessions_full.csv')
print(f"Original dataset shape: {df_votes.shape}")


# 2 - Load the community graphs
print("\nLoading community graphs...")
graphs_with_communities_dir = "data/graphs_with_communities"
print(f"Graphs directory: {graphs_with_communities_dir}")

# 3 - Check if the graphs directory exists
if not os.path.exists(graphs_with_communities_dir):
    print(f"Error: Directory {graphs_with_communities_dir} not found")
else:
    # 4 - List and load graph files
    graph_files = [f for f in os.listdir(graphs_with_communities_dir) if f.endswith('.gpickle')]
    print(f"Found {len(graph_files)} graph files")

    # 5 - Load all graphs
    community_graphs = {}
    for file in graph_files:
        file_path = os.path.join(graphs_with_communities_dir, file)
        try:
            graph_name = os.path.splitext(file)[0].replace('_with_communities', '')
            with open(file_path, 'rb') as f:
                community_graphs[graph_name] = pickle.load(f)
            print(f"Loaded graph: {graph_name}")
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    # 6 - Extract community data from graphs with detailed node ID inspection
    print("\nExtracting community data with detailed node ID inspection...")
    community_data = []
    
    # 7 - Debug counters
    int_nodes = 0
    float_nodes = 0
    str_nodes = 0
    other_nodes = 0
    
    for graph_name, graph in community_graphs.items():
        # 8 - Extract legislature number
        match = re.search(r'(\d+)', graph_name)
        if not match:
            print(f"Warning: Could not extract legislature number from {graph_name}")
            continue
            
        legislature_num = int(match.group(1))
        
        # 9 - Debug: Print node type information for this graph
        node_types = {}
        for node in list(graph.nodes())[:20]:  # Sample first 20 nodes
            node_type = type(node).__name__
            if node_type not in node_types:
                node_types[node_type] = []
            if len(node_types[node_type]) < 5:  # Store up to 5 examples per type
                node_types[node_type].append(str(node))
                
        print(f"\nGraph {graph_name} node types:")
        for node_type, examples in node_types.items():
            print(f"  - {node_type}: {examples}")
        
        # 10 - Get community assignments with type tracking
        for node, attrs in graph.nodes(data=True):
            if 'community' in attrs:
                # Track node types for debugging
                if isinstance(node, int):
                    int_nodes += 1
                elif isinstance(node, float):
                    float_nodes += 1
                elif isinstance(node, str):
                    str_nodes += 1
                else:
                    other_nodes += 1
                
                # Store as standardized string
                node_str = str(node)
                
                community_data.append({
                    'legislature': graph_name,
                    'legislature_num': legislature_num,
                    'deputy_id': node,  # Original node
                    'deputy_id_str': node_str,  # String representation
                    'community_id': attrs['community']
                })
    
    print(f"\nNode type statistics across all graphs:")
    print(f"Int nodes: {int_nodes}")
    print(f"Float nodes: {float_nodes}")
    print(f"String nodes: {str_nodes}")
    print(f"Other type nodes: {other_nodes}")
    
    # 11 - Create DataFrame with community data
    graph_community_df = pd.DataFrame(community_data)
    print(f"\nCreated community DataFrame with {len(graph_community_df)} entries")
    
    # 12 - Standardize voting dataset IDs
    print("\nStandardizing voting dataset IDs...")
    votes_copy = df_votes.copy()

    # Convert date string to datetime
    votes_copy['data'] = pd.to_datetime(votes_copy['data'])

    # Calculate date one year before the vote
    votes_copy['date_one_year_before'] = votes_copy['data'] - pd.DateOffset(years=1)

    # Keep the legislature column for reference
    votes_copy['legislatura'] = votes_copy['legislatura'].astype(int)
    
    # 13 - Convert voting dataset IDs to string for consistent matching
    votes_copy['deputy_id_str'] = votes_copy['idDeputadoAutor'].apply(
        lambda x: str(int(float(x))) if pd.notna(x) else None
    )
    
    # 14 - Sample conversion for demonstration
    sample_conversions = pd.DataFrame({
        'Original': votes_copy['idDeputadoAutor'].head(5),
        'Converted': votes_copy['deputy_id_str'].head(5)
    })
    print("Sample ID conversions:")
    print(sample_conversions)
    
    # 15 - Create lookup dictionaries using both legislature and year-based windows
    print("\nCreating lookup dictionaries...")

    # Load legislature data for date mappings
    try:
        legislature_data = pd.read_csv('data/extra/legislaturas.csv', delimiter=';')
        legislature_data['dataInicio'] = pd.to_datetime(legislature_data['dataInicio'])
        legislature_data['dataFim'] = pd.to_datetime(legislature_data['dataFim'])
        legislature_data['idLegislatura'] = legislature_data['idLegislatura'].astype(int)
        print(f"Loaded legislature data: {len(legislature_data)} legislatures")
    except Exception as e:
        print(f"Error loading legislature data: {e}")
        legislature_data = pd.DataFrame(columns=['idLegislatura', 'dataInicio', 'dataFim'])

    # Create a mapping of dates to legislatures
    date_to_legislature = {}
    for _, row in legislature_data.iterrows():
        start_date = row['dataInicio']
        end_date = row['dataFim']
        leg_id = row['idLegislatura']
        
        # Create a mapping for each day in this legislature
        current_date = start_date
        while current_date <= end_date:
            date_to_legislature[current_date.strftime('%Y-%m-%d')] = leg_id
            current_date += pd.DateOffset(days=1)

    # Create legislature-based lookup (original method)
    community_lookup_by_legislature = {}
    for _, row in graph_community_df.iterrows():
        deputy_id_str = row['deputy_id_str']
        leg_num = row['legislature_num']
        community = row['community_id']
        community_lookup_by_legislature[(deputy_id_str, leg_num)] = community

    # Create date-based lookup
    community_lookup_by_date = {}
    for _, row in graph_community_df.iterrows():
        deputy_id_str = row['deputy_id_str']
        leg_num = row['legislature_num']
        community = row['community_id']
        
        # Find the date range for this legislature
        leg_data = legislature_data[legislature_data['idLegislatura'] == leg_num]
        if len(leg_data) > 0:
            start_date = leg_data.iloc[0]['dataInicio']
            end_date = leg_data.iloc[0]['dataFim']
            
            # Store community for each month in this legislature
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime('%Y-%m')
                community_lookup_by_date[(deputy_id_str, date_key)] = community
                current_date += pd.DateOffset(months=1)

    print(f"Created legislature-based lookup with {len(community_lookup_by_legislature)} entries")
    print(f"Created date-based lookup with {len(community_lookup_by_date)} entries")
    
    # 16 - Sample of lookup dictionary
    lookup_sample = list(community_lookup_by_legislature.items())[:5]
    print(f"Sample from lookup dictionary: {lookup_sample}")
    
    # 17 - Test specific author IDs with detailed output
    print("\nDetailed lookup tests:")
    test_ids = votes_copy['deputy_id_str'].dropna().sample(5).tolist()
    
    for test_id in test_ids:
        print(f"\nTesting deputy ID: {test_id}")
        # Try all legislatures
        for leg in sorted(graph_community_df['legislature_num'].unique()):
            lookup_key = (test_id, leg)
            result = community_lookup_by_legislature.get(lookup_key)
            print(f"  Legislature {leg}: {result}")
    
    # 18 - Create debug functions to check lookup by legislature and by date
    def get_community_by_legislature_debug(deputy_id_str, legislature_num):
        key = (deputy_id_str, legislature_num)
        result = community_lookup_by_legislature.get(key)
        if result is None:
            # Check for existence in any legislature
            keys_with_deputy = [k for k in community_lookup_by_legislature.keys() if k[0] == deputy_id_str]
            if keys_with_deputy:
                found_legs = [k[1] for k in keys_with_deputy]
                return f"Not found in leg {legislature_num}, but found in legs {found_legs}"
            else:
                return f"Not found in any legislature"
        return result

    def get_community_by_date_debug(deputy_id_str, date_str):
        # Extract year-month from the date
        try:
            date_key = pd.to_datetime(date_str).strftime('%Y-%m')
            key = (deputy_id_str, date_key)
            result = community_lookup_by_date.get(key)
            if result is None:
                # Check for existence in any date
                keys_with_deputy = [k for k in community_lookup_by_date.keys() if k[0] == deputy_id_str]
                if keys_with_deputy:
                    found_dates = [k[1] for k in keys_with_deputy]
                    return f"Not found for date {date_key}, but found in dates {found_dates[:5]}..."
                else:
                    return f"Not found for any date"
            return result
        except:
            return f"Invalid date format: {date_str}"
    
    # 19 - Apply the function with debugging
    print("\nAssigning previous communities with debug...")
    
    # 20 - Create a sample for detailed debugging
    sample_rows = votes_copy.sample(10)
    debug_results = []
    
    for _, row in sample_rows.iterrows():
        deputy_id_str = row['deputy_id_str']
        date_before = row['date_one_year_before']
        date_str = date_before.strftime('%Y-%m-%d') if not pd.isna(date_before) else None
        
        debug_result = {
            'deputy_id': row['idDeputadoAutor'],
            'deputy_id_str': deputy_id_str,
            'date': row['data'],
            'date_one_year_before': date_str,
            'lookup_result': get_community_by_date_debug(deputy_id_str, date_str) if date_str else None
        }
        debug_results.append(debug_result)
    
    debug_df = pd.DataFrame(debug_results)
    print("Debug lookup results:")
    print(debug_df)
    
    # 21 - Apply the function to all rows using the one-year window
    def get_community_one_year_before(row):
        deputy_id = row['deputy_id_str']
        if pd.isna(deputy_id):
            return None
        
        # Get the date one year before
        date_before = row['date_one_year_before']
        if pd.isna(date_before):
            return None
            
        date_key = date_before.strftime('%Y-%m')
        
        # Try to find the community using the date-based lookup
        key = (deputy_id, date_key)
        return community_lookup_by_date.get(key)

    # Apply the function to get the community from one year before
    votes_copy['author_prev_community'] = votes_copy.apply(get_community_one_year_before, axis=1)
    
    # 22 - Print summary statistics
    found_count = votes_copy['author_prev_community'].notna().sum()
    missing_count = votes_copy['author_prev_community'].isna().sum()
    
    print(f"\nCommunity assignment statistics:")
    print(f"Found community: {found_count} rows ({found_count/len(votes_copy)*100:.1f}%)")
    print(f"Missing community: {missing_count} rows ({missing_count/len(votes_copy)*100:.1f}%)")
    
    # 23 - For rows missing communities, print detailed analysis
    missing_analysis = votes_copy[votes_copy['author_prev_community'].isna()].groupby('legislatura').size()
    print("\nMissing community by legislature:")
    print(missing_analysis)
    
    # 24 - Sample of rows with assigned communities
    print("\nSample of rows with assigned communities:")
    community_sample = votes_copy[votes_copy['author_prev_community'].notna()].sample(5)
    print(community_sample[['idDeputadoAutor', 'deputy_id_str', 'data', 'date_one_year_before', 'author_prev_community']])
    
    # Clean up and save
    final_df = votes_copy.drop(columns=['deputy_id_str', 'date_one_year_before'])
    df_with_communities = final_df
    
    # Additional debugging for specific dates and authors
    print("\nDEBUG: Checking authors with missing communities one year before...")
    sample_date = pd.Timestamp('2015-02-01')  # Example date to check
    sample_date_one_year_before = sample_date - pd.DateOffset(years=1)
    
    deputies_missing = votes_copy[
        (votes_copy['data'] >= sample_date) & 
        (votes_copy['data'] < sample_date + pd.DateOffset(days=30)) &
        (votes_copy['author_prev_community'].isna())
    ]['deputy_id_str'].unique()
    
    if len(deputies_missing) > 0:
        print(f"Found {len(deputies_missing)} unique deputies with missing communities for date {sample_date}")
        
        # Check a sample of these deputies
        for deputy in deputies_missing[:5]:
            print(f"\nChecking deputy {deputy}:")
            
            # Check for available months for this deputy
            keys_with_deputy = [k for k in community_lookup_by_date.keys() if k[0] == deputy]
            if keys_with_deputy:
                date_keys = sorted([k[1] for k in keys_with_deputy])
                print(f"  Found data for months: {date_keys[:5]}...")
            else:
                print(f"  Not found in any date data")

    # 25 - Calculate community sizes for each legislature
    print("\nCalculating community sizes for each legislature...")
    community_sizes = {}

    for legislature_num in sorted(graph_community_df['legislature_num'].unique()):
        # Filter community data for this legislature
        leg_data = graph_community_df[graph_community_df['legislature_num'] == legislature_num]
        
        # Count deputies in each community
        community_counts = leg_data['community_id'].value_counts().to_dict()
        
        # Store in the dictionary
        community_sizes[legislature_num] = community_counts
        
        print(f"Legislature {legislature_num}: {community_counts}")

    # 26 - Add community size columns to the dataset
    print("\nAdding community size columns...")
    # Convert date string to datetime if needed
    if not pd.api.types.is_datetime64_dtype(df_with_communities['data']):
        df_with_communities['data'] = pd.to_datetime(df_with_communities['data'])

    # Calculate date one year before the vote
    df_with_communities['date_one_year_before'] = df_with_communities['data'] - pd.DateOffset(years=1)

    # Map dates to legislatures
    def get_legislature_for_date(date):
        if pd.isna(date):
            return None
        date_str = date.strftime('%Y-%m-%d')
        return date_to_legislature.get(date_str)

    # Get legislature for the date one year before
    df_with_communities['prev_legislature'] = df_with_communities['date_one_year_before'].apply(get_legislature_for_date)

    # 27 - Create a function to get community size
    def get_community_size(leg_num, comm_id):
        if leg_num not in community_sizes:
            return None
        return community_sizes[leg_num].get(comm_id, 0)

    # 28 - Add columns for community 0 and 1 sizes
    df_with_communities['prev_community_0_size'] = df_with_communities['prev_legislature'].apply(
        lambda leg: get_community_size(leg, 0)
    )

    df_with_communities['prev_community_1_size'] = df_with_communities['prev_legislature'].apply(
        lambda leg: get_community_size(leg, 1)
    )

    # For legislature 54, also add community 2 size (since it has 3 communities)
    if 2 in graph_community_df[graph_community_df['legislature_num'] == 54]['community_id'].unique():
        df_with_communities['prev_community_2_size'] = df_with_communities['prev_legislature'].apply(
            lambda leg: get_community_size(leg, 2) if leg == 54 else 0
        )

    # 29 - Clean up the final dataset
    final_df = df_with_communities.drop(columns=['prev_legislature', 'date_one_year_before'])

    # 30 - Show summary of added columns
    print("\nCommunity size columns summary:")
    print(f"prev_community_0_size: {final_df['prev_community_0_size'].notna().sum()} non-null values")
    print(f"prev_community_1_size: {final_df['prev_community_1_size'].notna().sum()} non-null values")
    if 'prev_community_2_size' in final_df.columns:
        print(f"prev_community_2_size: {final_df['prev_community_2_size'].notna().sum()} non-null values")

    # 31 - Create a simplified dataset with only the required columns
    print("\nCreating simplified dataset with only the required columns...")
    # Select only the necessary columns, using idDeputadoAutor as the id column
    required_columns = ['id','idDeputadoAutor', 'author_prev_community', 'prev_community_0_size', 'prev_community_1_size']
    if 'prev_community_2_size' in final_df.columns:
        required_columns.append('prev_community_2_size')

    # Create a copy and rename idDeputadoAutor to id
    simplified_df = final_df[required_columns].copy()

    # Save the simplified dataset
    simplified_df.to_csv('01 - Global Prediction/Author\'s Group/authors_community_dataset_one_year_window.csv', index=False)
    print(f"\nSaved simplified dataset to 'authors_community_dataset_one_year_window.csv' with shape {simplified_df.shape}")
    print(f"Columns in simplified dataset: {simplified_df.columns.tolist()}")

    # 32 - Show a sample of rows from the simplified dataset
    print("\nSample rows from simplified dataset:")
    sample_rows = simplified_df[simplified_df['author_prev_community'].notna()].sample(min(5, len(simplified_df)))
    print(sample_rows)