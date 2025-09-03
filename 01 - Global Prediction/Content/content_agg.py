import pandas as pd
import os

print("Loading vote sessions data...")
# Load vote sessions data
vote_sessions_df = pd.read_csv("01 - Global Prediction/data/vote_sessions_full.csv")

# Keep only relevant columns
columns_to_keep = [
    "id",
    "ultimaAberturaVotacao_descricao",
    "ultimaApresentacaoProposicao_descricao"
]
vote_sessions_df = vote_sessions_df[columns_to_keep]
print(f"Vote sessions loaded: {len(vote_sessions_df)} rows.")

# Define the range of years to process
years = range(2003, 2025)

# List to store DataFrames for each year
dfs = []

# Base path for the proposition files
base_path = "data/voting/proposition"

print("Loading proposition files by year...")
for year in years:
    file_path = os.path.join(base_path, f"votacoesProposicoes-{year}.csv")
    if os.path.exists(file_path):
        print(f"  Loading: {file_path}")
        df = pd.read_csv(file_path, sep=";", encoding="utf-8")
        df["year"] = year  # Optionally add year column
        dfs.append(df)
    else:
        print(f"  File not found: {file_path}")

# Concatenate all DataFrames into a single DataFrame
if dfs:
    proposicoes_df = pd.concat(dfs, ignore_index=True)
    print(f"Total propositions loaded: {len(proposicoes_df)}")
else:
    print("No proposition files were loaded.")
    proposicoes_df = pd.DataFrame(columns=["idVotacao", "proposicao_ementa"])

# Keep only the columns 'idVotacao' and 'proposicao_ementa'
print("Reducing proposition columns to 'idVotacao' and 'proposicao_ementa'...")
proposicoes_reduced_df = proposicoes_df[["idVotacao", "proposicao_ementa"]].copy()

# Merge vote_sessions_df with proposicoes_reduced_df using 'id' and 'idVotacao'
print("Merging vote sessions with proposition texts...")
merged_df = vote_sessions_df.merge(
    proposicoes_reduced_df,
    left_on="id",
    right_on="idVotacao",
    how="left"
)

# Remove the 'idVotacao' column after merge
merged_df = merged_df.drop(columns=["idVotacao"])

# Function to join text from the three columns, ignoring NaN values
def join_content(row):
    texts = []
    for col in ["ultimaAberturaVotacao_descricao", "ultimaApresentacaoProposicao_descricao", "proposicao_ementa"]:
        val = row.get(col)
        if pd.notnull(val):
            texts.append(str(val))
    return " ".join(texts)

# Create the 'content' column by joining the relevant text columns
print("Creating 'content' column by joining text fields...")
merged_df["content"] = merged_df.apply(join_content, axis=1)

# Keep only the 'id' and 'content' columns
final_df = merged_df[["id", "content"]]

# Remove duplicate ids, keeping the first occurrence
final_df = final_df.drop_duplicates(subset=["id"], keep="first")

# Save the resulting DataFrame to CSV in the same folder as this script
output_path = os.path.join(os.path.dirname(__file__), "prop_content.csv")
print(f"Saving final dataset to {output_path} ...")
final_df.to_csv(output_path, index=False, encoding="utf-8")
print("Done.")