# Metodologia para Previsão de Votos Legislativos

Este documento descreve a metodologia utilizada no projeto de pesquisa para predição de votos no Congresso Brasileiro, abordando tanto a perspectiva local (votos individuais) quanto a perspectiva global (resultado das proposições).

## Visão Geral

O projeto analisa a previsão de votos legislativos a partir de duas perspectivas complementares:

1. **Perspectiva Local**: Foca na previsão do voto individual de cada parlamentar.
2. **Perspectiva Global**: Foca na previsão do resultado final de uma proposição (aprovação ou rejeição).

## Fatores de Influência

### Perspectiva Local (Voto Individual)

Na análise da perspectiva local, o voto de um parlamentar é influenciado por três fatores principais:

1. **Alinhamento de Grupo**: Representa a influência das comunidades e grupos políticos aos quais o parlamentar pertence.
   - Implementação: Detecção de comunidades bem definidas de deputados através de análise de redes (da SILVA, 2024).
   - Técnica: Algoritmos de detecção de comunidades em grafos de votação.

2. **Relacionamento com o Autor da Proposta**: Analisa como a relação entre o votante e o autor da proposta afeta o voto.
   - Implementação: Modelagem de relações direcionais entre autores e votantes (KARIMI et al., 2019).
   - Técnica: Redes direcionadas ponderadas que capturam padrões históricos de apoio/rejeição.

3. **Avaliação Pessoal do Conteúdo da Proposta**: Considera a avaliação individual do parlamentar sobre o texto e tema da proposição.
   - Implementação: Clusters de proposições derivados de redes assinadas múltiplas (ARINIK et al., 2020).
   - Técnica: Agrupamento de textos legislativos com características semelhantes para identificar padrões de votação.

### Perspectiva Global (Resultado da Proposição)

Na análise da perspectiva global, o resultado final de uma proposição é influenciado por:

1. **Conteúdo**: Análise do texto, tema e natureza da proposição.
   - Implementação: Processamento de linguagem natural e classificação de textos legislativos.
   - Técnica: Modelos de embeddings textuais e classificação temática.

2. **Grupo do Autor**: Considera a influência do grupo político ao qual o autor pertence.
   - Implementação: Análise de comunidades e coalizões políticas.
   - Técnica: Mesmas técnicas de detecção de comunidades aplicadas aos autores.

3. **Popularidade Individual do Autor**: Avalia o histórico de sucesso do autor em proposições anteriores.
   - Implementação: Métricas de popularidade baseadas em aprovações passadas e coautoria.
   - Técnica: Análise estatística de histórico de votações e métricas de centralidade em redes.

## Fluxo de Trabalho Metodológico

O projeto segue um fluxo de trabalho estruturado em três etapas principais:

### 1. Aquisição de Dados
- Coleta de dados da plataforma de dados abertos do governo brasileiro
- Organização e estruturação dos dados para análise
- Pré-processamento e limpeza dos dados

### 2. Aplicação de Metodologias
- Detecção de comunidades de autores e votantes
- Cálculo de métricas de popularidade e relacionamento entre votantes
- Criação de clusters de proposições baseados em conteúdo e padrões de votação

### 3. Modelagem Preditiva
- Construção de tabelas de previsão global e local:
  - **Tabela Global**: Prop ID, Cluster, Popularidade do Autor, Comunidade do Autor, Aprovação
  - **Tabela Local**: Votante ID, Comunidade, Relação com Autor, Relação com Proposta, Voto
- Divisão do dataset em conjuntos de treinamento, teste e validação
- Treinamento e validação de algoritmos de aprendizado de máquina

## Integração das Perspectivas

O diferencial metodológico deste projeto está na integração das perspectivas local e global, permitindo:

1. Análise multinível do processo legislativo
2. Captura de dinâmicas individuais e coletivas
3. Maior robustez na previsão de resultados de votações

Esta abordagem holística permite não apenas prever resultados, mas também compreender os mecanismos subjacentes ao comportamento legislativo brasileiro, oferecendo insights valiosos sobre o processo de tomada de decisão política.