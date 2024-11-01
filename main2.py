import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Carregar dados históricos de surgimento de erros
file_path = "dadosUteis.csv"  # Caminho do arquivo

# Tente ler como CSV, caso contrário use Excel com engine específico
try:
    df = pd.read_csv(file_path)
except ValueError:
    df = pd.read_excel(file_path, sheet_name="Resultado da consulta", engine="openpyxl")

# Converter coluna de datas
df['issue_creation_date'] = pd.to_datetime(df['issue_creation_date'])

# Calcular média de erros por semana para cada projeto
df['week'] = df['issue_creation_date'].dt.to_period('W')
erros_por_semana = df.groupby(['Projects - Project UUID__kee', 'week']).size().unstack(fill_value=0)
media_erros_por_semana = erros_por_semana.mean(axis=1)

# Parâmetros da simulação de Monte Carlo
num_simulacoes = 1000
num_semanas = 12  # Projeção para as próximas 12 semanas
simulacoes_erros = []

# Simulação de Monte Carlo
for _ in range(num_simulacoes):
    sim_proj = []
    for media in media_erros_por_semana:
        # Gera projeção para cada projeto com base na média de erros por semana
        simulacao = np.random.poisson(media, num_semanas)
        sim_proj.append(simulacao)
    simulacoes_erros.append(np.array(sim_proj).sum(axis=0))

# Calcula a média das simulações para as 12 semanas e garante que seja um array de 12 valores
media_simulacoes = np.mean(simulacoes_erros, axis=0)
media_simulacoes = np.squeeze(media_simulacoes)  # Garante que seja um array 1D de 12 valores

# Verificar o formato de media_simulacoes
st.write("Formato de media_simulacoes:", media_simulacoes.shape)

# Gráfico da projeção de novos erros
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_semanas + 1), media_simulacoes, marker='o', color="blue")
plt.title("Projeção de Surgimento de Novos Erros por Semana")
plt.xlabel("Semanas Futuras")
plt.ylabel("Número Estimado de Novos Erros")
plt.grid(True)

# Exibir o gráfico no Streamlit
st.pyplot(plt)
