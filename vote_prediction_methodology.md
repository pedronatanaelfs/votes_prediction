# Legislative Vote Prediction Methodology

This document describes the methodology used in the research project for predicting votes in the Brazilian Congress, addressing both the local perspective (individual votes) and the global perspective (proposition outcomes).

## Overview

The project analyzes legislative vote prediction from two complementary perspectives:

1. **Local Perspective**: Focuses on predicting the individual vote of each parliamentarian.
2. **Global Perspective**: Focuses on predicting the final outcome of a proposition (approval or rejection).

## Influencing Factors

### Local Perspective (Individual Vote)

In the local perspective analysis, a parliamentarian's vote is influenced by three main factors:

1. **Group Alignment**: Represents the influence of political communities and groups to which the parliamentarian belongs.
   - Implementation: Detection of well-defined communities of deputies through network analysis (da SILVA, 2024).
   - Technique: Community detection algorithms in voting graphs.

2. **Relationship with the Proposal's Author**: Analyzes how the relationship between the voter and the proposal's author affects the vote.
   - Implementation: Modeling directional relationships between authors and voters (KARIMI et al., 2019).
   - Technique: Weighted directed networks that capture historical patterns of support/rejection.

3. **Personal Assessment of the Proposal's Content**: Considers the parliamentarian's individual assessment of the proposition's text and theme.
   - Implementation: Proposition clusters derived from multiplex signed networks (ARINIK et al., 2020).
   - Technique: Grouping legislative texts with similar characteristics to identify voting patterns.

### Global Perspective (Proposition Outcome)

In the global perspective analysis, the final outcome of a proposition is influenced by:

1. **Content**: Analysis of the text, theme, and nature of the proposition.
   - Implementation: Natural language processing and classification of legislative texts.
   - Technique: Text embedding models and thematic classification.

2. **Author's Group**: Considers the influence of the political group to which the author belongs.
   - Implementation: Analysis of political communities and coalitions.
   - Technique: Same community detection techniques applied to authors.

3. **Author's Individual Popularity**: Evaluates the author's success history in previous propositions.
   - Implementation: Popularity metrics based on past approvals and co-authorship.
   - Technique: Statistical analysis of voting history and centrality metrics in networks.

## Methodological Workflow

The project follows a workflow structured in three main stages:

### 1. Data Acquisition
- Collection of data from the Brazilian government's open data platform
- Organization and structuring of data for analysis
- Data preprocessing and cleaning

### 2. Application of Methodologies
- Detection of communities of authors and voters
- Calculation of popularity metrics and relationships between voters
- Creation of proposition clusters based on content and voting patterns

### 3. Predictive Modeling
- Construction of global and local prediction tables:
  - **Global Table**: Prop ID, Cluster, Author's Popularity, Author's Community, Approval
  - **Local Table**: Voter ID, Community, Relationship with Author, Relationship with Proposal, Vote
- Division of the dataset into training, testing, and validation sets
- Training and validation of machine learning algorithms

## Integration of Perspectives

The methodological differential of this project lies in the integration of local and global perspectives, allowing:

1. Multilevel analysis of the legislative process
2. Capture of individual and collective dynamics
3. Greater robustness in predicting voting outcomes

This holistic approach allows not only to predict outcomes but also to understand the underlying mechanisms of Brazilian legislative behavior, offering valuable insights into the political decision-making process.