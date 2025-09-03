#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script analyzes proposition texts using Doc2Vec and clustering algorithms.
It processes text from the 'proposicao_ementa' column in voting proposition CSV files
and assigns each proposition to a cluster based on its textual content.
Output: content_cluster.csv with proposition IDs and their assigned clusters.
"""

import os
import pandas as pd
import numpy as np
import glob
import re
import nltk
from nltk.corpus import stopwords
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from tqdm import tqdm
import logging
import argparse

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                   level=logging.INFO)
logger = logging.getLogger(__name__)

def download_nltk_resources():
    """Download required NLTK resources if not already downloaded."""
    logger.info("Downloading required NLTK resources...")
    nltk.download('punkt')
    nltk.download('stopwords')

def load_proposition_data(years_range, data_path="../../data/voting/proposition"):
    """
    Load proposition data from CSV files for the specified years.
    
    Parameters:
    -----------
    years_range : list or tuple
        Range of years to process, e.g., (2003, 2024)
    data_path : str
        Path to the directory containing proposition data files
        
    Returns:
    --------
    pandas.DataFrame
        Combined DataFrame containing proposition data
    """
    start_year, end_year = years_range
    all_data = []
    
    for year in range(start_year, end_year + 1):
        file_path = os.path.join(data_path, f"votacoesProposicoes-{year}.csv")
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue
            
        logger.info(f"Reading data for year {year}...")
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
            # Keep only necessary columns
            if 'proposicao_id' in df.columns and 'proposicao_ementa' in df.columns:
                df_filtered = df[['proposicao_id', 'proposicao_ementa']].copy()
                # Remove duplicates by proposicao_id
                df_filtered.drop_duplicates(subset=['proposicao_id'], inplace=True)
                all_data.append(df_filtered)
            else:
                logger.warning(f"Required columns not found in file {file_path}")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
    
    if not all_data:
        raise ValueError("No data was loaded. Check file paths and formats.")
        
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.drop_duplicates(subset=['proposicao_id'], inplace=True)
    logger.info(f"Loaded {len(combined_df)} unique propositions")
    
    return combined_df

def preprocess_text(text):
    """
    Preprocess text by removing special characters, numbers, and stopwords.
    
    Parameters:
    -----------
    text : str
        The text to preprocess
        
    Returns:
    --------
    list
        List of preprocessed tokens
    """
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Replace non-alphanumeric with space
    text = re.sub(r'\d+', ' ', text)      # Remove numbers
    text = re.sub(r'\s+', ' ', text)      # Replace multiple spaces with single space
    text = text.strip()                   # Remove leading and trailing whitespace
    
    # Simple tokenization without language-specific features
    tokens = text.split()
    
    # Get Portuguese stopwords
    try:
        stop_words = set(stopwords.words('portuguese'))
    except:
        # Fallback to common Portuguese stopwords if NLTK's are not available
        logger.warning("NLTK Portuguese stopwords not available. Using manual fallback list.")
        stop_words = {
            "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até",
            "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois",
            "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "era",
            "eram", "éramos", "essa", "essas", "esse", "esses", "esta", "estas", "este",
            "estes", "eu", "foi", "fomos", "for", "foram", "forem", "fosse", "fossem",
            "fôssemos", "fui", "há", "isso", "isto", "já", "lhe", "lhes", "mais", "mas",
            "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "não", "nas",
            "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num", "numa",
            "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual",
            "quando", "que", "quem", "são", "se", "seja", "sejam", "sejamos", "sem", "ser",
            "será", "seremos", "seria", "seriam", "seríamos", "seu", "seus", "só", "somos",
            "sou", "sua", "suas", "também", "te", "tem", "tém", "temos", "tenha", "tenham",
            "tenhamos", "tenho", "terá", "terão", "terei", "teremos", "teria", "teriam",
            "teríamos", "teu", "teus", "teve", "tinha", "tinham", "tínhamos", "tive", "tivemos",
            "tiver", "tivera", "tiveram", "tiverem", "tivermos", "tu", "tua", "tuas", "um",
            "uma", "você", "vocês", "vos"
        }
    
    # Filter out short tokens and stopwords
    tokens = [t for t in tokens if len(t) > 2 and t not in stop_words]
    
    return tokens

def create_doc2vec_model(documents, vector_size=100, window=5, min_count=2, epochs=30):
    """
    Create and train a Doc2Vec model.
    
    Parameters:
    -----------
    documents : list
        List of TaggedDocument objects
    vector_size : int
        Size of the document vectors
    window : int
        Maximum distance between the current and predicted word
    min_count : int
        Minimum word frequency to include in vocabulary
    epochs : int
        Number of training epochs
        
    Returns:
    --------
    gensim.models.doc2vec.Doc2Vec
        Trained Doc2Vec model
    """
    logger.info(f"Training Doc2Vec model with {len(documents)} documents...")
    model = Doc2Vec(vector_size=vector_size, 
                   window=window, 
                   min_count=min_count, 
                   workers=4, 
                   epochs=epochs)
    
    # Build vocabulary
    model.build_vocab(documents)
    
    # Train model
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    
    logger.info("Doc2Vec model training completed")
    return model

def determine_optimal_clusters(vectors, max_clusters=20, min_clusters=2):
    """
    Determine the optimal number of clusters using silhouette scores.
    
    Parameters:
    -----------
    vectors : numpy.ndarray
        Document vectors
    max_clusters : int
        Maximum number of clusters to try
    min_clusters : int
        Minimum number of clusters to try
        
    Returns:
    --------
    int
        Optimal number of clusters
    """
    logger.info("Determining optimal number of clusters...")
    
    # Limit max clusters based on data size
    max_clusters = min(max_clusters, len(vectors) // 10)
    
    silhouette_scores = []
    cluster_range = range(min_clusters, max_clusters + 1)
    
    for n_clusters in tqdm(cluster_range):
        # Skip if we have too few samples
        if n_clusters >= len(vectors):
            continue
            
        # Try K-means clustering
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(vectors)
            
            # Calculate silhouette score
            score = silhouette_score(vectors, cluster_labels)
            silhouette_scores.append((n_clusters, score))
            logger.debug(f"Clusters: {n_clusters}, Silhouette Score: {score:.4f}")
        except Exception as e:
            logger.warning(f"Error with {n_clusters} clusters: {str(e)}")
    
    if not silhouette_scores:
        logger.warning("Could not determine optimal clusters. Using default of 5.")
        return 5
    
    # Find cluster count with highest silhouette score
    optimal_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
    logger.info(f"Optimal number of clusters: {optimal_clusters}")
    
    return optimal_clusters

def perform_clustering(vectors, n_clusters=None, max_clusters=20):
    """
    Perform clustering on document vectors.
    
    Parameters:
    -----------
    vectors : numpy.ndarray
        Document vectors
    n_clusters : int or None
        Number of clusters (if None, determined automatically)
    max_clusters : int
        Maximum number of clusters to try for automatic determination
        
    Returns:
    --------
    dict
        Dictionary with clustering results (kmeans and hierarchical)
    """
    # Determine optimal number of clusters if not provided
    if n_clusters is None:
        n_clusters = determine_optimal_clusters(vectors, max_clusters)
    
    clustering_results = {}
    
    # K-means clustering
    logger.info(f"Performing K-means clustering with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(vectors)
    clustering_results['kmeans'] = kmeans_labels
    
    # Hierarchical clustering
    logger.info(f"Performing hierarchical clustering with {n_clusters} clusters...")
    hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
    hierarchical_labels = hierarchical.fit_predict(vectors)
    clustering_results['hierarchical'] = hierarchical_labels
    
    return clustering_results

def main(start_year=2003, end_year=2024, n_clusters=None, output_path=None, vector_size=100):
    """
    Main function to process propositions and generate clusters.
    
    Parameters:
    -----------
    start_year : int
        Start year for data processing
    end_year : int
        End year for data processing
    n_clusters : int or None
        Number of clusters (if None, determined automatically)
    output_path : str or None
        Path to save the output CSV file
    vector_size : int
        Size of document vectors
    """
    # Ensure NLTK resources are available
    download_nltk_resources()
    
    # Set output path if not provided
    if output_path is None:
        output_path = os.path.join("Output", "content_cluster.csv")
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load proposition data
    df = load_proposition_data((start_year, end_year))
    
    # Preprocess texts
    logger.info("Preprocessing proposition texts...")
    df['processed_text'] = df['proposicao_ementa'].apply(preprocess_text)
    
    # Filter out empty texts
    df = df[df['processed_text'].apply(lambda x: len(x) > 0)]
    logger.info(f"After preprocessing, {len(df)} propositions remain")
    
    # Create tagged documents for Doc2Vec
    tagged_data = [TaggedDocument(words=doc, tags=[str(idx)]) 
                  for idx, doc in enumerate(df['processed_text'])]
    
    # Create and train Doc2Vec model
    model = create_doc2vec_model(tagged_data, vector_size=vector_size)
    
    # Get document vectors
    doc_vectors = np.array([model.infer_vector(doc.words) for doc in tagged_data])
    
    # Perform clustering
    clustering_results = perform_clustering(doc_vectors, n_clusters)
    
    # Add cluster labels to DataFrame
    for method, labels in clustering_results.items():
        df[f'cluster_{method}'] = labels
    
    # Create output DataFrame
    result_df = df[['proposicao_id'] + [col for col in df.columns if col.startswith('cluster_')]].copy()
    
    # Save results
    logger.info(f"Saving clustering results to {output_path}...")
    result_df.to_csv(output_path, index=False)
    logger.info("Processing completed successfully")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Cluster proposition texts using Doc2Vec')
    parser.add_argument('--start-year', type=int, default=2003, help='Start year for data processing')
    parser.add_argument('--end-year', type=int, default=2024, help='End year for data processing')
    parser.add_argument('--n-clusters', type=int, default=None, help='Number of clusters')
    parser.add_argument('--output', type=str, default=None, help='Path to save the output CSV file')
    parser.add_argument('--vector-size', type=int, default=100, help='Size of document vectors')
    
    args = parser.parse_args()
    
    main(
        start_year=args.start_year,
        end_year=args.end_year,
        n_clusters=args.n_clusters,
        output_path=args.output,
        vector_size=args.vector_size
    )
