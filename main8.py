import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Configurações do Streamlit
st.title("Projeção de Surgimento de Novos Erros por Semana")

# Carregar dados históricos de surgimento de erros
file_path = "C:\\Projeto Python\\pythonProjectSonarqube\\dados_consulta.xlsx"  # Caminho do arquivo
df = pd.read_excel(file_path, sheet_name="Resultado da consulta")

# Converter coluna de datas
df['issue_creation_date'] = pd.to_datetime(df['issue_creation_date'])

# Filtro para autor
unique_authors = df['author_login'].unique()
selected_authors = st.multiselect("Selecione os Autores", options=unique_authors, default=unique_authors.tolist())

# Filtrar DataFrame com base nos autores selecionados
df_filtered = df[df['author_login'].isin(selected_authors)]

# Cálculo de issues abertas e fechadas
issues_abertas = df_filtered[df_filtered['status'] == 'OPEN'].shape[0]
issues_fechadas = df_filtered[df_filtered['status'] == 'CLOSED'].shape[0]

# Exibir cards de total de issues abertas e fechadas
st.metric("Total de Issues Abertas", issues_abertas)
st.metric("Total de Issues Fechadas", issues_fechadas)

# Calcular média de erros por semana para cada projeto
df_filtered['week'] = df_filtered['issue_creation_date'].dt.to_period('W')
erros_por_semana = df_filtered.groupby(['Projects - Project UUID__kee', 'week']).size().unstack(fill_value=0)
media_erros_por_semana = erros_por_semana.mean(axis=1)

# Parâmetros da simulação de Monte Carlo
num_simulacoes = st.slider("Número de Simulações", min_value=100, max_value=5000, value=1000, step=100)
num_semanas = st.slider("Projeção para Semanas Futuras", min_value=1, max_value=52, value=12)

# Simulação de Monte Carlo
simulacoes_erros = []
for _ in range(num_simulacoes):
    sim_proj = []
    for media in media_erros_por_semana:
        # Gera projeção para cada projeto com base na média de erros por semana
        simulacao = np.random.poisson(media, num_semanas)
        sim_proj.append(simulacao)
    simulacoes_erros.append(np.array(sim_proj).sum(axis=0))

# Total de novos erros esperados
novos_erros_esperados = np.sum(np.mean(simulacoes_erros, axis=0))

# Atualizar contagem total de issues
total_issues_abertas = issues_abertas + novos_erros_esperados
total_issues_fechadas = issues_fechadas  # As fechadas permanecem inalteradas

# Exibir cards atualizados com novos erros esperados
st.metric("Total Estimado de Issues Abertas", int(total_issues_abertas))
st.metric("Total Estimado de Issues Fechadas", issues_fechadas)

# Gráfico da projeção de novos erros
media_simulacoes = np.mean(simulacoes_erros, axis=0)
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_semanas + 1), media_simulacoes, marker='o', color="blue")
plt.title("Projeção de Surgimento de Novos Erros por Semana")
plt.xlabel("Semanas Futuras")
plt.ylabel("Número Estimado de Novos Erros")
plt.grid(True)

# Renderiza o gráfico no Streamlit
st.pyplot(plt)
