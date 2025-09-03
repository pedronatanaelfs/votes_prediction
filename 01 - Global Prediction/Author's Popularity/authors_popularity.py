import pandas as pd
import numpy as np
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Função para imprimir e registrar progresso com timestamp
def log_progress(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()  # Força a saída imediata para o console

# Verifica se os diretórios de saída existem
def ensure_output_directory(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        log_progress(f"Criado diretório: {directory}")

# Início da execução
start_time = time.time()
log_progress("Iniciando cálculo de popularidade de autores...")

try:
    # 1) Load the vote sessions data
    log_progress("Carregando dados de sessões de votação...")
    df_sessions = pd.read_csv("01 - Global Prediction/data/vote_sessions_full.csv")
    if df_sessions.empty:
        log_progress("Erro: Falha ao carregar dados das sessões de votação")
        sys.exit(1)
    else:
        log_progress(f"Dados de sessões carregados com sucesso: {len(df_sessions)} linhas")
        log_progress(f"Colunas disponíveis: {', '.join(df_sessions.columns)}")

    # Add a column for session importance/relevance (based on number of votes)
    log_progress("Calculando métricas de importância das sessões...")
    session_votes_count = df_sessions.groupby('id').size().reset_index(name='total_votes')
    log_progress(f"Contagem por sessão calculada: {len(session_votes_count)} sessões únicas")
    
    df_sessions = df_sessions.merge(session_votes_count, on='id', how='left')
    log_progress(f"Merge concluído. Shape após merge: {df_sessions.shape}")

    # 2) Drop duplicate sessions
    log_progress("Removendo sessões duplicadas...")
    df_sessions_unique = df_sessions.drop_duplicates(subset=['id'])
    log_progress(f"Número de sessões únicas: {len(df_sessions_unique)}")

    # Salva checkpoint intermediário
    df_sessions_unique.to_csv('01 - Global Prediction/Author\'s Popularity/checkpoint_sessions.csv', index=False)
    log_progress("Checkpoint de sessões salvo")

    # 3) Define the path pattern and years
    log_progress("Preparando para carregar dados de votos...")
    data_path = "data/voting/votes/votacoesVotos-{year}.csv"
    years = range(2003, 2025)

    # 4) Load and concatenate all datasets (using optimized approach)
    log_progress("Carregando dados de votos ano a ano...")
    dfs = []
    total_votes = 0
    
    # Verifica se arquivo de checkpoint existe para pular etapa de carregamento
    checkpoint_file = '01 - Global Prediction/Author\'s Popularity/checkpoint_votes.csv'
    if os.path.exists(checkpoint_file):
        log_progress(f"Carregando dados de votos do checkpoint...")
        df_votes = pd.read_csv(checkpoint_file)
        log_progress(f"Checkpoint de votos carregado: {len(df_votes)} votos")
    else:
        for year in years:
            try:
                year_path = data_path.format(year=year)
                if not os.path.exists(year_path):
                    log_progress(f"Arquivo não encontrado para o ano {year}: {year_path}")
                    continue
                    
                log_progress(f"Carregando dados do ano {year}...")
                df = pd.read_csv(year_path, delimiter=';', quotechar='"')
                dfs.append(df)
                total_votes += len(df)
                log_progress(f"Carregados {len(df)} votos para {year}. Total até agora: {total_votes}")
            except Exception as e:
                log_progress(f"Erro carregando dados para {year}: {e}")
                traceback.print_exc()

        log_progress(f"Concatenando {len(dfs)} dataframes de votos...")
        df_votes = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        log_progress(f"Total de votos carregados: {len(df_votes)}")
        
        # Salva checkpoint para evitar recarregar todos os dados
        if not df_votes.empty:
            log_progress("Salvando checkpoint de votos...")
            ensure_output_directory(checkpoint_file)
            df_votes.to_csv(checkpoint_file, index=False)
            log_progress("Checkpoint de votos salvo")

    # 5) Filter df_votes based on df_sessions
    if 'df_sessions' in locals() and 'id' in df_sessions_unique.columns and not df_votes.empty:
        log_progress("Filtrando votos e mesclando com dados de sessões...")
        log_progress(f"Antes do filtro: {len(df_votes)} linhas")
        
        session_ids = set(df_sessions_unique['id'])
        log_progress(f"Total de IDs de sessões para filtro: {len(session_ids)}")
        
        # Verifica amostra de IDs para debug
        sample_ids = list(session_ids)[:5] if len(session_ids) >= 5 else list(session_ids)
        log_progress(f"Amostra de IDs de sessão: {sample_ids}")
        
        # Verifica tipos de dados
        log_progress(f"Tipo de 'idVotacao' em df_votes: {df_votes['idVotacao'].dtype}")
        log_progress(f"Tipo de 'id' em df_sessions_unique: {df_sessions_unique['id'].dtype}")
        
        # Converte os tipos de dados se necessário
        if df_votes['idVotacao'].dtype != df_sessions_unique['id'].dtype:
            log_progress("Convertendo tipos de dados para garantir compatibilidade...")
            if df_sessions_unique['id'].dtype == 'int64':
                df_votes['idVotacao'] = pd.to_numeric(df_votes['idVotacao'], errors='coerce')
            else:
                df_sessions_unique['id'] = df_sessions_unique['id'].astype(str)
                df_votes['idVotacao'] = df_votes['idVotacao'].astype(str)
        
        # Filtra usando método mais eficiente
        df_votes_selected = df_votes[df_votes['idVotacao'].isin(session_ids)].copy()
        log_progress(f"Após filtro: {len(df_votes_selected)} linhas")
        
        # Verifica se o filtro funcionou
        if len(df_votes_selected) == 0:
            log_progress("ALERTA: Nenhuma linha após filtro. Verificando dados...")
            common_ids = set(df_votes['idVotacao'].unique()) & session_ids
            log_progress(f"IDs em comum: {len(common_ids)}")
            
            if len(common_ids) == 0:
                log_progress("Não há IDs em comum entre os conjuntos de dados. Verificando amostra de IDs de votos...")
                sample_vote_ids = list(df_votes['idVotacao'].unique())[:5]
                log_progress(f"Amostra de IDs de votação: {sample_vote_ids}")
                
                # Tentativa com tipos de dados diferentes
                log_progress("Tentando converter tipos de dados...")
                df_votes['idVotacao_str'] = df_votes['idVotacao'].astype(str)
                df_sessions_unique['id_str'] = df_sessions_unique['id'].astype(str)
                common_str_ids = set(df_votes['idVotacao_str'].unique()) & set(df_sessions_unique['id_str'].unique())
                log_progress(f"IDs em comum após conversão para string: {len(common_str_ids)}")
                
                if len(common_str_ids) > 0:
                    log_progress("Usando IDs convertidos para string...")
                    df_votes_selected = df_votes[df_votes['idVotacao_str'].isin(common_str_ids)].copy()
                    log_progress(f"Após filtro com strings: {len(df_votes_selected)} linhas")
                else:
                    log_progress("ERRO CRÍTICO: Não foi possível encontrar correspondências entre os datasets")
                    sys.exit(1)
        
        # Merge com informações de autor e relevância
        log_progress("Mesclando com coluna 'author' e métricas de relevância...")
        if len(df_votes_selected) > 0:
            merge_columns = ['id', 'author']
            if 'total_votes' in df_sessions_unique.columns:
                merge_columns.append('total_votes')
                
            df_votes_selected = df_votes_selected.merge(
                df_sessions_unique[merge_columns], 
                left_on='idVotacao', right_on='id', how='left'
            )
            log_progress(f"Após merge: {len(df_votes_selected)} linhas")
            
            if 'id' in df_votes_selected.columns:
                df_votes_selected.drop(columns=['id'], inplace=True)
                
        # Salva checkpoint intermediário dos votos filtrados
        checkpoint_filtered = '01 - Global Prediction/Author\'s Popularity/checkpoint_votes_filtered.csv'
        df_votes_selected.to_csv(checkpoint_filtered, index=False)
        log_progress("Checkpoint de votos filtrados salvo")

    # 6) Convert 'dataHoraVoto' to datetime
    log_progress("Convertendo 'dataHoraVoto' para datetime...")
    try:
        df_votes_selected['dataHoraVoto'] = pd.to_datetime(df_votes_selected['dataHoraVoto'], errors='coerce')
        # Remove linhas com datas inválidas
        invalid_dates = df_votes_selected['dataHoraVoto'].isna().sum()
        if invalid_dates > 0:
            log_progress(f"Removendo {invalid_dates} linhas com datas inválidas")
            df_votes_selected = df_votes_selected.dropna(subset=['dataHoraVoto'])
    except Exception as e:
        log_progress(f"Erro ao converter datas: {e}")
        traceback.print_exc()

    # 7) Sort votes by 'dataHoraVoto' for chronological processing
    log_progress("Ordenando votos por 'dataHoraVoto' para processamento cronológico...")
    df_votes_selected = df_votes_selected.sort_values(by='dataHoraVoto')

    # 8) Initialize parameters for improved popularity calculation
    log_progress("Definindo parâmetros para cálculo de popularidade...")
    TIME_WINDOW_DAYS = 365  # Rolling window of 1 year
    HALF_LIFE_DAYS = 90     # Half-life of 3 months for exponential decay
    MIN_VOTES_THRESHOLD = 5 # Minimum votes needed for reliable popularity
    DEFAULT_POPULARITY = 0.5 # Default popularity for new authors
    
    # Ajusta parâmetros para processamento mais rápido em caso de dataset muito grande
    if len(df_votes_selected) > 1000000:
        log_progress(f"Dataset muito grande ({len(df_votes_selected)} votos). Otimizando parâmetros...")
        PROCESS_CHUNK_SIZE = 10000  # Processa em chunks para evitar problemas de memória
    else:
        PROCESS_CHUNK_SIZE = len(df_votes_selected)

    # 9) Initialize data structures for efficient calculation
    log_progress("Inicializando estruturas de dados para cálculo eficiente...")
    popularity_records = []
    author_votes = defaultdict(list)

    # 10) Process votes in chronological order - Primeira passagem
    total_rows = len(df_votes_selected)
    log_progress(f"Processando {total_rows} votos para calcular popularidade dos autores...")

    # Primeiro passo: coletar dados de votos
    log_progress("Primeira passagem: coletando dados de votos...")
    
    # Normaliza importância da votação antecipadamente
    max_votes = df_sessions_unique['total_votes'].max() if 'total_votes' in df_sessions_unique.columns else 1
    log_progress(f"Valor máximo de votos para normalização: {max_votes}")
    
    # Processa em chunks para monitorar progresso
    chunk_size = 100000
    for chunk_start in range(0, total_rows, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total_rows)
        log_progress(f"Processando chunk {chunk_start}-{chunk_end} de {total_rows}...")
        
        chunk = df_votes_selected.iloc[chunk_start:chunk_end]
        
        for _, row in chunk.iterrows():
            author = row['author']
            vote = row['voto']
            vote_time = row['dataHoraVoto']
            session_id = row['idVotacao']
            
            # Evita erro se total_votes não estiver presente
            if 'total_votes' in row:
                vote_importance = row['total_votes'] / max_votes  # Normalized importance
            else:
                vote_importance = 1.0  # Default importance if missing
            
            is_yes = 1 if isinstance(vote, str) and vote.lower() == 'sim' else 0
            
            # Store the vote with its metadata
            author_votes[author].append({
                'time': vote_time,
                'is_yes': is_yes,
                'importance': vote_importance,
                'session_id': session_id
            })
            
        log_progress(f"Processados {chunk_end} / {total_rows} votos. Autores únicos: {len(author_votes)}")
        
    # Salva checkpoint de autor_votes para recuperação em caso de falha
    log_progress("Primeira passagem concluída. Salvando checkpoint...")
    
    # Converte para formato serializável
    author_votes_serializable = {}
    for author, votes in author_votes.items():
        author_votes_serializable[author] = [
            {
                'time': str(v['time']),
                'is_yes': v['is_yes'],
                'importance': float(v['importance']),
                'session_id': v['session_id']
            }
            for v in votes
        ]
    
    # Cria um DataFrame para salvar o checkpoint
    checkpoint_df = pd.DataFrame([
        {'author': author, 'votes': str(votes)}
        for author, votes in author_votes_serializable.items()
    ])
    
    checkpoint_df.to_csv('01 - Global Prediction/Author\'s Popularity/checkpoint_author_votes.csv', index=False)
    log_progress("Checkpoint da primeira passagem salvo")

    # Segunda passagem: calcular popularidade ponderada por tempo e importância
    log_progress("Segunda passagem: calculando métricas aprimoradas de popularidade...")
    
    # Métricas globais de progresso da segunda passagem
    second_pass_start = time.time()
    total_authors = len(author_votes)
    total_votes_all = sum(len(v) for v in author_votes.values()) if total_authors > 0 else 0
    processed_votes_all = 0
    progress_log_interval = max(10000, total_votes_all // 100) if total_votes_all > 0 else 10000  # ~100 logs
    log_progress(f"Total de autores: {total_authors}. Total de votos a processar na 2ª passagem: {total_votes_all}")
    
    # Processa autores em lotes para exibir progresso
    authors_processed = 0
    records_before_checkpoint = 100000  # Salva checkpoint a cada 100k registros
    records_since_last_checkpoint = 0
    
    for author, votes in author_votes.items():
        # Monitoramento de progresso
        authors_processed += 1
        if authors_processed % 100 == 0:
            elapsed = time.time() - start_time
            log_progress(f"Processando autor {authors_processed}/{total_authors} ({(authors_processed/total_authors)*100:.1f}%). Tempo decorrido: {elapsed:.1f}s")
        
        # Ordena votos por tempo para cada autor
        votes.sort(key=lambda x: x['time'])
        
        # Constantes e estruturas para atualização O(1) amortizada
        total_votes = len(votes)
        lambda_decay = np.log(2) / HALF_LIFE_DAYS
        A_weighted_sum = 0.0  # soma de w_j * exp(-lambda * (t_i - t_j))
        B_weighted_sum = 0.0  # soma de w_j * y_j * exp(-lambda * (t_i - t_j))
        window_deque = deque()  # mantém votos anteriores dentro da janela [TIME_WINDOW_DAYS]
        raw_total_votes = 0
        raw_yes_votes = 0
        recent_deque = deque()  # janela de 180 dias para volatilidade
        recent_count = 0
        recent_sum = 0.0
        recent_sumsq = 0.0

        for i in range(total_votes):
            current_vote = votes[i]
            current_time = current_vote['time']
            session_id = current_vote['session_id']

            # Atualiza acumuladores exponenciais com o voto imediatamente anterior
            if i > 0:
                prev_vote = votes[i - 1]
                dt_days = (current_time - prev_vote['time']).days
                if dt_days < 0:
                    dt_days = 0
                decay_factor = np.exp(-lambda_decay * dt_days)
                A_weighted_sum = decay_factor * (A_weighted_sum + prev_vote['importance'])
                B_weighted_sum = decay_factor * (B_weighted_sum + prev_vote['importance'] * prev_vote['is_yes'])

                # Adiciona o voto anterior às janelas de 365d e 180d
                window_deque.append((prev_vote['time'], prev_vote['is_yes'], prev_vote['importance']))
                raw_total_votes += 1
                raw_yes_votes += prev_vote['is_yes']

                recent_deque.append((prev_vote['time'], prev_vote['is_yes']))
                recent_count += 1
                recent_sum += prev_vote['is_yes']
                recent_sumsq += prev_vote['is_yes'] ** 2

            # Remove votos que saíram da janela de 365 dias (ajusta somas e acumuladores)
            while window_deque:
                age_days = (current_time - window_deque[0][0]).days
                if age_days <= TIME_WINDOW_DAYS:
                    break
                old_time, old_yes, old_importance = window_deque.popleft()
                raw_total_votes -= 1
                raw_yes_votes -= old_yes
                # Remove contribuição atual do item expirado dos acumuladores exponenciais
                contrib_decay = np.exp(-lambda_decay * age_days)
                A_weighted_sum -= old_importance * contrib_decay
                B_weighted_sum -= old_importance * old_yes * contrib_decay

            # Remove votos que saíram da janela de 180 dias (para volatilidade)
            while recent_deque:
                age_days_recent = (current_time - recent_deque[0][0]).days
                if age_days_recent <= 180:
                    break
                _, old_yes_recent = recent_deque.popleft()
                recent_count -= 1
                recent_sum -= old_yes_recent
                recent_sumsq -= old_yes_recent ** 2

            # Calcula várias métricas de popularidade
            weighted_total_votes = A_weighted_sum
            weighted_yes_votes = B_weighted_sum

            if weighted_total_votes > 0:
                weighted_popularity = weighted_yes_votes / weighted_total_votes
            else:
                weighted_popularity = DEFAULT_POPULARITY

            if raw_total_votes >= MIN_VOTES_THRESHOLD:
                raw_popularity = raw_yes_votes / raw_total_votes if raw_total_votes > 0 else DEFAULT_POPULARITY
            else:
                # Suavização Bayesiana para poucos votos
                prior_votes = MIN_VOTES_THRESHOLD - raw_total_votes
                raw_popularity = (raw_yes_votes + prior_votes * DEFAULT_POPULARITY) / (raw_total_votes + prior_votes) if (raw_total_votes + prior_votes) > 0 else DEFAULT_POPULARITY

            # Combina métricas (pesos podem ser ajustados)
            combined_popularity = 0.7 * weighted_popularity + 0.3 * raw_popularity

            # Volatilidade com estatística incremental na janela de 180 dias
            if recent_count >= 3:
                mean_recent = recent_sum / recent_count
                var_recent = max(0.0, (recent_sumsq / recent_count) - (mean_recent ** 2))
                volatility = float(np.sqrt(var_recent))
            else:
                volatility = 0.0

            # Armazena métricas
            popularity_records.append({
                'author': author,
                'popularity': combined_popularity,
                'weighted_popularity': weighted_popularity,
                'raw_popularity': raw_popularity,
                'volatility': volatility,
                'vote_count': raw_total_votes,
                'date': current_time.date(),
                'idVotacao': session_id
            })

            # Progresso global
            processed_votes_all += 1
            if total_votes_all > 0 and (processed_votes_all % progress_log_interval == 0 or processed_votes_all == total_votes_all):
                elapsed = time.time() - second_pass_start
                rate = processed_votes_all / elapsed if elapsed > 0 else 0
                remaining = total_votes_all - processed_votes_all
                eta_seconds = (remaining / rate) if rate > 0 else float('inf')
                pct = (processed_votes_all / total_votes_all) * 100
                log_progress(f"Segunda passagem: {processed_votes_all}/{total_votes_all} votos ({pct:.1f}%), ETA ~ {eta_seconds/60:.1f} min")

            # Checkpoint intermediário
            records_since_last_checkpoint += 1
            if records_since_last_checkpoint >= records_before_checkpoint:
                temp_df = pd.DataFrame(popularity_records)
                temp_checkpoint = '01 - Global Prediction/Author\'s Popularity/checkpoint_popularity_partial.csv'
                temp_df.to_csv(temp_checkpoint, index=False)
                log_progress(f"Checkpoint intermediário salvo: {len(popularity_records)} registros processados")
                records_since_last_checkpoint = 0

    # 11) Create DataFrame with computed popularity
    log_progress("Criando DataFrame com métricas de popularidade aprimoradas...")
    df_author_popularity = pd.DataFrame(popularity_records)
    log_progress(f"DataFrame criado com {len(df_author_popularity)} registros")
    
    # 12) Drop duplicate voting session IDs
    log_progress("Removendo IDs de sessão de votação duplicados...")
    df_author_popularity = df_author_popularity.drop_duplicates(subset=['idVotacao'])
    log_progress(f"DataFrame de popularidade final: {df_author_popularity.shape}")
    
    # 13) Save the DataFrame to a CSV file
    output_path = '01 - Global Prediction/Author\'s Popularity/author_popularity.csv'
    log_progress(f"Salvando métricas de popularidade em {output_path}...")
    ensure_output_directory(output_path)
    df_author_popularity.to_csv(output_path, index=False, encoding='utf-8')
    log_progress(f"Métricas de popularidade salvas com sucesso")
    
    elapsed_time = time.time() - start_time
    log_progress(f"Processamento completo em {elapsed_time:.2f} segundos ({elapsed_time/60:.2f} minutos)")
    
    log_progress("Resumo das melhorias:")
    log_progress("1. Implementado decaimento temporal com ponderação exponencial (meia-vida de 3 meses)")
    log_progress("2. Adicionada janela móvel de 1 ano para análise de votos recentes")
    log_progress("3. Incorporada importância do voto baseada na participação na sessão")
    log_progress("4. Adicionada suavização Bayesiana para autores com poucos votos")
    log_progress("5. Calculada volatilidade como métrica adicional")
    log_progress("6. Melhorada eficiência do código com algoritmo em duas passagens")
    log_progress("7. Adicionadas múltiplas métricas de popularidade para análise mais detalhada")
    log_progress("8. Implementados checkpoints para recuperação em caso de falha")
    log_progress("9. Adicionados diagnósticos extensivos e logs detalhados")
    
except Exception as e:
    log_progress(f"ERRO CRÍTICO: {str(e)}")
    traceback.print_exc()
    sys.exit(1)