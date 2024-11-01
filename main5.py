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
df = df[df['author_login'].isin(selected_authors)]

# Calcular média de erros por semana para cada projeto
df['week'] = df['issue_creation_date'].dt.to_period('W')
erros_por_semana = df.groupby(['Projects - Project UUID__kee', 'week']).size().unstack(fill_value=0)
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
