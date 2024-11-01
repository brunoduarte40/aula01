import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Carregar dados históricos de surgimento de erros
file_path = "C:\\Projeto Python\\pythonProjectSonarqube\\dados_consulta.xlsx"  # Caminho do arquivo
df = pd.read_excel(file_path, sheet_name="Resultado da consulta")

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

# Gráfico da projeção de novos erros
media_simulacoes = np.mean(simulacoes_erros, axis=0)
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_semanas + 1), media_simulacoes, marker='o', color="blue")
plt.title("Projeção de Surgimento de Novos Erros por Semana")
plt.xlabel("Semanas Futuras")
plt.ylabel("Número Estimado de Novos Erros")
plt.grid(True)
st.pyplot(plt)
