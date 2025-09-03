# Organização dos Notebooks

Este diretório contém notebooks organizados de acordo com o fluxo de trabalho da pesquisa sobre predição de votos no Congresso Brasileiro.

## Estrutura de Diretórios

### 01-Data_Acquisition
Notebooks dedicados à aquisição e coleta de dados brutos de diversas fontes.
- `DA_Author.ipynb` - Coleta de dados sobre autores de proposições
- `DA_propositions.ipynb` - Coleta de dados sobre proposições legislativas
- `DA_votings.ipynb` - Coleta de dados sobre votações
- `Data_Aquisition.ipynb` - Notebook principal de aquisição de dados

### 02-Data_Processing
Notebooks para processamento e limpeza dos dados brutos coletados.
- `data_processing.ipynb` - Processamento geral dos dados
- `votes_aggregation.ipynb` - Agregação de dados de votações

### 03-Feature_Engineering
Notebooks para criação e transformação de features para os modelos.
- `authors_popularity.ipynb` - Análise de popularidade de autores
- `FE_Author_Popularity.ipynb` - Engenharia de features baseada em popularidade de autores
- `FE_Building_Graphs.ipynb` - Construção de grafos para análise de rede
- `FE_Detecting_communities.ipynb` - Detecção de comunidades em grafos
- `FE_Prop_Cluster.ipynb` - Clusterização de proposições
- `FE_Text_Cluster.ipynb` - Clusterização baseada em textos

### 04-Modeling
Notebooks para construção, treinamento e avaliação de modelos preditivos.
- `baselines.ipynb` - Modelos baseline
- `modeling.ipynb` - Construção de modelos gerais
- `proposition_result_prediction.ipynb` - Predição de resultados de proposições
- `vote_prediction.ipynb` - Predição de votos
- `votes_prediction.ipynb` - Métodos adicionais para predição de votos

### 05-Visualization
Diretório para notebooks focados em visualização de dados e resultados.

### 06-Results_Analysis
Notebooks para análise de resultados dos experimentos.
- `data_analysis.ipynb` - Análise de dados e resultados

### 07-Article_Reproductions
Notebooks para reprodução de métodos de artigos relacionados.
- `2021_using_AI.ipynb` - Reprodução de artigo sobre uso de IA
- `2022_data_centric.ipynb` - Reprodução de abordagem centrada em dados
- `2022_PAR.ipynb` - Reprodução do método PAR

### 08-Network_Analysis
Notebooks especializados em análise de redes e comunidades.
- `community_vote_prediction.ipynb` - Predição de votos baseada em comunidades
- `network_features.ipynb` - Extração de features de rede
- `networks_01.ipynb` - Análise básica de redes

### 09-Text_Analysis
Notebooks para análise e processamento de textos.
- `Doc2Vec.ipynb` - Implementação do modelo Doc2Vec para textos legislativos
- `LLM_cluster.ipynb` - Clustering usando modelos de linguagem

### 10-Utilities
Scripts e notebooks utilitários para apoiar o fluxo de trabalho.
- `analyze_features.py` - Script para análise de features

### 11-CSV_Files
Diretório com arquivos CSV importantes para o projeto.
- `df_all_info.csv` - Dataset completo com todas informações
- `df_author_popularity.csv` - Dataset com métricas de popularidade de autores
- `df_clusters.csv` - Dataset com informações de clusters
- `votos_agg.csv` - Dataset com votos agregados

### Archived
Notebooks obsoletos ou não utilizados atualmente.
- `01-07-2025.ipynb` - Notebook arquivado

Este diretório também contém uma pasta `Original_Folders` que preserva a organização original dos notebooks antes da reestruturação, mantendo assim o histórico da organização anterior.