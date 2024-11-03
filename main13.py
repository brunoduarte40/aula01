import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Configurações do Streamlit
st.title("Projeção de Erros por Semana")

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

# Média simulação de projeções semanais
media_simulacoes_abertos = np.mean(simulacoes_abertos, axis=0)
media_simulacoes_fechados = np.mean(simulacoes_fechados, axis=0)

# Cálculo do valor total estimado de issues abertas e fechadas
total_est_issues_abertas = issues_abertas + np.sum(media_simulacoes_abertos)
total_est_issues_fechadas = issues_fechadas + np.sum(media_simulacoes_fechados)

# Exibir cards atualizados com novos totais estimados
st.metric("Total Estimado de Issues Abertas", int(total_est_issues_abertas))
st.metric("Total Estimado de Issues Fechadas", int(total_est_issues_fechadas))

# Gráfico inicial da projeção acumulada de novos erros e erros fechados usando Plotly
fig_acumulado = go.Figure()
fig_acumulado.add_trace(go.Scatter(x=list(range(1, num_semanas + 1)), y=np.cumsum(media_simulacoes_abertos) + issues_abertas, mode='lines+markers', name="Erros Abertos (Acumulado)", line=dict(color="blue")))
fig_acumulado.add_trace(go.Scatter(x=list(range(1, num_semanas + 1)), y=np.cumsum(media_simulacoes_fechados) + issues_fechadas, mode='lines+markers', name="Erros Fechados (Acumulado)", line=dict(color="red")))
fig_acumulado.update_layout(title="Projeção Acumulada de Erros Abertos e Fechados por Semana", xaxis_title="Semanas Futuras", yaxis_title="Número Estimado de Erros (Acumulado)", legend_title="Status")

# Renderiza o gráfico acumulado no Streamlit
st.plotly_chart(fig_acumulado)

# Gráfico da projeção de novas issues abertas por semana
fig_abertas_semanal = go.Figure()
fig_abertas_semanal.add_trace(go.Scatter(x=list(range(1, num_semanas + 1)), y=media_simulacoes_abertos, mode='lines+markers', name="Novas Issues Abertas", line=dict(color="blue")))
fig_abertas_semanal.update_layout(title="Projeção de Novas Issues Abertas por Semana", xaxis_title="Semanas Futuras", yaxis_title="Número Estimado de Novas Issues Abertas")

# Renderiza o gráfico de novas issues abertas no Streamlit
st.plotly_chart(fig_abertas_semanal)

# Gráfico da projeção de issues fechadas por semana
fig_fechadas_semanal = go.Figure()
fig_fechadas_semanal.add_trace(go.Scatter(x=list(range(1, num_semanas + 1)), y=media_simulacoes_fechados, mode='lines+markers', name="Issues Fechadas", line=dict(color="red")))
fig_fechadas_semanal.update_layout(title="Projeção de Issues Fechadas por Semana", xaxis_title="Semanas Futuras", yaxis_title="Número Estimado de Issues Fechadas")

# Renderiza o gráfico de issues fechadas no Streamlit
st.plotly_chart(fig_fechadas_semanal)
