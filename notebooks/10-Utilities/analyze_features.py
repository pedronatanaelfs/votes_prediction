import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

print("Loading and preprocessing data...")
# Load data
df = pd.read_csv('votacoes_com_llm_pop.csv')

# Keep only necessary columns
columns_to_keep = [
    'data',
    'tema',
    'orientacao_GOV',
    'author_prev_community',
    'prev_community_0_size',
    'prev_community_1_size',
    'prev_community_2_size',
    'classified_llm',
    'authors_pop',
    'aprovacao'
]

df = df[columns_to_keep]

# Convert columns to int
cols_to_int = [
    'author_prev_community',
    'prev_community_0_size',
    'prev_community_1_size',
    'prev_community_2_size',
    'aprovacao'
]

df = df.dropna(subset=cols_to_int)
for col in cols_to_int:
    df[col] = df[col].astype('int64')

# Convert date
df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')

# Create authors_major_comm feature
def is_major_comm(row):
    if row['author_prev_community'] == 0 and row['prev_community_0_size'] > row['prev_community_1_size']:
        return 1
    elif row['author_prev_community'] == 1 and row['prev_community_1_size'] > row['prev_community_0_size']:
        return 1
    else:
        return 0

df['authors_major_comm'] = df.apply(is_major_comm, axis=1)

# Keep only necessary columns
columns_to_keep = [
    'data',
    'tema',
    'classified_llm',
    'authors_pop', 
    "authors_major_comm",
    'orientacao_GOV',
    'aprovacao'
]

df = df[columns_to_keep]

# Drop rows with NaN values
df = df.dropna()

print(f"Dataset shape after preprocessing: {df.shape}")

# Sort by date and split into train/val/test
df_sorted = df.sort_values('data')
n = len(df_sorted)
train_end = int(0.7 * n)
val_end = int(0.85 * n)

df_train = df_sorted.iloc[:train_end]
df_val = df_sorted.iloc[train_end:val_end]
df_test = df_sorted.iloc[val_end:]

# Define features and target
feature_cols = [col for col in df.columns if col not in ['aprovacao', 'data']]
X_train = df_train[feature_cols]
y_train = df_train['aprovacao']
X_val = df_val[feature_cols]
y_val = df_val['aprovacao']
X_test = df_test[feature_cols]
y_test = df_test['aprovacao']

# Define numerical and categorical columns
numerical_cols = ['authors_pop']
categorical_cols = [col for col in feature_cols if col not in numerical_cols]

print(f"Feature columns: {feature_cols}")
print(f"Numerical columns: {numerical_cols}")
print(f"Categorical columns: {categorical_cols}")

# MODEL WITH ALL FEATURES
print("\n--- Training model with all features ---")

# Define preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
    ]
)

# Define best parameters (from original notebook)
best_params = {
    'classifier__n_estimators': 300,
    'classifier__learning_rate': 0.003,
    'classifier__max_depth': 3
}

# Create pipeline
xgb_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(
        eval_metric='logloss',
        n_estimators=best_params['classifier__n_estimators'],
        learning_rate=best_params['classifier__learning_rate'],
        max_depth=best_params['classifier__max_depth']
    ))
])

# Train model
xgb_pipeline.fit(X_train, y_train)

# Evaluate on test set
y_test_pred = xgb_pipeline.predict(X_test)
y_test_proba = xgb_pipeline.predict_proba(X_test)[:, 1]

# Calculate metrics
test_accuracy = accuracy_score(y_test, y_test_pred)
test_f1 = f1_score(y_test, y_test_pred)
test_auc = roc_auc_score(y_test, y_test_proba)
test_report = classification_report(y_test, y_test_pred, output_dict=True)
test_recall = test_report['1']['recall']

print("Model with all features - Test metrics:")
print(f"Accuracy: {test_accuracy:.4f}")
print(f"F1 Score: {test_f1:.4f}")
print(f"ROC AUC: {test_auc:.4f}")
print(f"Recall: {test_recall:.4f}")

# MODEL WITHOUT HIGHLIGHTED FEATURES
print("\n--- Training model without highlighted features ---")

# Create feature list without highlighted features
feature_cols_without_highlighted = [col for col in feature_cols if col not in ['authors_pop', 'authors_major_comm']]
print(f"Features without highlighted: {feature_cols_without_highlighted}")

# Create datasets
X_train_reduced = df_train[feature_cols_without_highlighted]
X_val_reduced = df_val[feature_cols_without_highlighted]
X_test_reduced = df_test[feature_cols_without_highlighted]

# Define preprocessor for reduced features
preprocessor_reduced = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), feature_cols_without_highlighted)
    ]
)

# Create pipeline
xgb_pipeline_reduced = Pipeline([
    ('preprocessor', preprocessor_reduced),
    ('classifier', XGBClassifier(
        eval_metric='logloss',
        n_estimators=best_params['classifier__n_estimators'],
        learning_rate=best_params['classifier__learning_rate'],
        max_depth=best_params['classifier__max_depth']
    ))
])

# Train model
xgb_pipeline_reduced.fit(X_train_reduced, y_train)

# Evaluate on test set
y_test_pred_reduced = xgb_pipeline_reduced.predict(X_test_reduced)
y_test_proba_reduced = xgb_pipeline_reduced.predict_proba(X_test_reduced)[:, 1]

# Calculate metrics
test_accuracy_reduced = accuracy_score(y_test, y_test_pred_reduced)
test_f1_reduced = f1_score(y_test, y_test_pred_reduced)
test_auc_reduced = roc_auc_score(y_test, y_test_proba_reduced)
test_report_reduced = classification_report(y_test, y_test_pred_reduced, output_dict=True)
test_recall_reduced = test_report_reduced['1']['recall']

print("Model without highlighted features - Test metrics:")
print(f"Accuracy: {test_accuracy_reduced:.4f}")
print(f"F1 Score: {test_f1_reduced:.4f}")
print(f"ROC AUC: {test_auc_reduced:.4f}")
print(f"Recall: {test_recall_reduced:.4f}")

# COMPARISON
print("\n--- Comparison ---")
print("Metric\t\tWith Features\tWithout Features\tDifference")
print(f"Accuracy:\t{test_accuracy:.4f}\t\t{test_accuracy_reduced:.4f}\t\t{test_accuracy - test_accuracy_reduced:.4f}")
print(f"F1 Score:\t{test_f1:.4f}\t\t{test_f1_reduced:.4f}\t\t{test_f1 - test_f1_reduced:.4f}")
print(f"ROC AUC:\t{test_auc:.4f}\t\t{test_auc_reduced:.4f}\t\t{test_auc - test_auc_reduced:.4f}")
print(f"Recall:\t\t{test_recall:.4f}\t\t{test_recall_reduced:.4f}\t\t{test_recall - test_recall_reduced:.4f}") 