# Notebook Organization

This directory contains notebooks organized according to the workflow of the research on vote prediction in the Brazilian Congress.

## Directory Structure

### 01-Data_Acquisition
Notebooks dedicated to acquiring and collecting raw data from various sources.
- `DA_Author.ipynb` - Collection of data about proposition authors
- `DA_propositions.ipynb` - Collection of data about legislative propositions
- `DA_votings.ipynb` - Collection of data about votes
- `Data_Aquisition.ipynb` - Main data acquisition notebook

### 02-Data_Processing
Notebooks for processing and cleaning the collected raw data.
- `data_processing.ipynb` - General data processing
- `votes_aggregation.ipynb` - Aggregation of voting data

### 03-Feature_Engineering
Notebooks for creating and transforming features for the models.
- `authors_popularity.ipynb` - Analysis of authors' popularity
- `FE_Author_Popularity.ipynb` - Feature engineering based on authors' popularity
- `FE_Building_Graphs.ipynb` - Construction of graphs for network analysis
- `FE_Detecting_communities.ipynb` - Detection of communities in graphs
- `FE_Prop_Cluster.ipynb` - Clustering of propositions
- `FE_Text_Cluster.ipynb` - Text-based clustering

### 04-Modeling
Notebooks for building, training, and evaluating predictive models.
- `baselines.ipynb` - Baseline models
- `modeling.ipynb` - Building general models
- `proposition_result_prediction.ipynb` - Prediction of proposition results
- `vote_prediction.ipynb` - Vote prediction
- `votes_prediction.ipynb` - Additional methods for vote prediction

### 05-Visualization
Directory for notebooks focused on visualizing data and results.

### 06-Results_Analysis
Notebooks for analyzing the results of experiments.
- `data_analysis.ipynb` - Analysis of data and results

### 07-Article_Reproductions
Notebooks for reproducing methods from related articles.
- `2021_using_AI.ipynb` - Reproduction of article on AI use
- `2022_data_centric.ipynb` - Reproduction of data-centric approach
- `2022_PAR.ipynb` - Reproduction of PAR method

### 08-Network_Analysis
Notebooks specialized in network and community analysis.
- `community_vote_prediction.ipynb` - Community-based vote prediction
- `network_features.ipynb` - Network feature extraction
- `networks_01.ipynb` - Basic network analysis

### 09-Text_Analysis
Notebooks for text analysis and processing.
- `Doc2Vec.ipynb` - Implementation of Doc2Vec model for legislative texts
- `LLM_cluster.ipynb` - Clustering using language models

### 10-Utilities
Scripts and utility notebooks to support the workflow.
- `analyze_features.py` - Script for feature analysis

### 11-CSV_Files
Directory with important CSV files for the project.
- `df_all_info.csv` - Complete dataset with all information
- `df_author_popularity.csv` - Dataset with author popularity metrics
- `df_clusters.csv` - Dataset with cluster information
- `votos_agg.csv` - Dataset with aggregated votes

### Archived
Obsolete or currently unused notebooks.
- `01-07-2025.ipynb` - Archived notebook

This directory also contains an `Original_Folders` folder that preserves the original organization of notebooks before restructuring, thus maintaining the history of the previous organization.