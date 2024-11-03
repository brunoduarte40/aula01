import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Configurações do Streamlit
st.title("Projeção Acumulada de Erros Abertos e Fechados por Semana")

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

# Calcular média de erros abertos e fechados por semana
df_filtered['week'] = df_filtered['issue_creation_date'].dt.to_period('W')
erros_abertos_por_semana = df_filtered[df_filtered['status'] == 'OPEN'].groupby('week').size().reindex(pd.period_range(df_filtered['week'].min(), df_filtered['week'].max(), freq='W'), fill_value=0)
erros_fechados_por_semana = df_filtered[df_filtered['status'] == 'CLOSED'].groupby('week').size().reindex(pd.period_range(df_filtered['week'].min(), df_filtered['week'].max(), freq='W'), fill_value=0)
media_abertos_por_semana = erros_abertos_por_semana.mean()
media_fechados_por_semana = erros_fechados_por_semana.mean()

# Parâmetros da simulação de Monte Carlo
num_simulacoes = st.slider("Número de Simulações", min_value=100, max_value=5000, value=1000, step=100)
num_semanas = st.slider("Projeção para Semanas Futuras", min_value=1, max_value=52, value=12)

# Simulação de Monte Carlo para novos erros abertos e fechados
simulacoes_abertos = []
simulacoes_fechados = []
for _ in range(num_simulacoes):
    simulacao_abertos = np.random.poisson(media_abertos_por_semana, num_semanas)
    simulacao_fechados = np.random.poisson(media_fechados_por_semana, num_semanas)
    simulacoes_abertos.append(simulacao_abertos)
    simulacoes_fechados.append(simulacao_fechados)

# Médias das simulações para projeções
media_simulacoes_abertos = np.mean(simulacoes_abertos, axis=0)
media_simulacoes_fechados = np.mean(simulacoes_fechados, axis=0)

# Cálculo do valor acumulado para as issues abertas e fechadas
acumulado_abertos = np.cumsum(media_simulacoes_abertos) + issues_abertas
acumulado_fechados = np.cumsum(media_simulacoes_fechados) + issues_fechadas

# Exibir cards atualizados com valores totais estimados
total_issues_abertas_acumulado = acumulado_abertos[-1]
total_issues_fechadas_acumulado = acumulado_fechados[-1]
st.metric("Total Acumulado Estimado de Issues Abertas", int(total_issues_abertas_acumulado))
st.metric("Total Acumulado Estimado de Issues Fechadas", int(total_issues_fechadas_acumulado))

# Gráfico da projeção acumulada de novos erros e erros fechados
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_semanas + 1), acumulado_abertos, marker='o', color="blue", label="Erros Abertos (Acumulado)")
plt.plot(range(1, num_semanas + 1), acumulado_fechados, marker='o', color="red", label="Erros Fechados (Acumulado)")
plt.title("Projeção Acumulada de Erros Abertos e Fechados por Semana")
plt.xlabel("Semanas Futuras")
plt.ylabel("Número Estimado de Erros (Acumulado)")
plt.legend()
plt.grid(True)

# Renderiza o gráfico no Streamlit
st.pyplot(plt)