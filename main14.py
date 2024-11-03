import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.title("Projeção de Erros por Semana")

# 2. Carregar dados históricos de erros
file_path = "dados_consulta.xlsx"
df = pd.read_excel(file_path, sheet_name="Resultado da consulta")

# 3. Converter coluna de datas para o tipo datetime
df['issue_creation_date'] = pd.to_datetime(df['issue_creation_date'])

# 4. Filtra dados por autor
unique_authors = df['author_login'].unique()
# Seleção autores específicos para análise
selected_authors = st.multiselect("Selecione os Autores", options=unique_authors, default=unique_authors.tolist())
# Filtra o DataFrame para conter apenas as issues dos autores selecionados
df_filtered = df[df['author_login'].isin(selected_authors)]

# 5. Contagem de issues abertas e fechadas com base nos autores selecionados
# Issues abertas (status "OPEN") e fechadas (status "CLOSED")
issues_abertas = df_filtered[df_filtered['status'] == 'OPEN'].shape[0]
issues_fechadas = df_filtered[df_filtered['status'] == 'CLOSED'].shape[0]

# Exibe o total de issues abertas e fechadas em cards
st.metric("Total de Issues Abertas", issues_abertas)
st.metric("Total de Issues Fechadas", issues_fechadas)

# 6. Calcula a média semanal de issues abertas e fechadas
# Converte a data de criação da issue para um período semanal
df_filtered['week'] = df_filtered['issue_creation_date'].dt.to_period('W')
# Conta o número de issues abertas por semana e preenche semanas sem issues com zero
erros_abertos_por_semana = df_filtered[df_filtered['status'] == 'OPEN'].groupby('week').size().reindex(pd.period_range(df_filtered['week'].min(), df_filtered['week'].max(), freq='W'), fill_value=0)
# Conta o número de issues fechadas por semana e preenche semanas sem issues com zero
erros_fechados_por_semana = df_filtered[df_filtered['status'] == 'CLOSED'].groupby('week').size().reindex(pd.period_range(df_filtered['week'].min(), df_filtered['week'].max(), freq='W'), fill_value=0)
# Calcula a média de issues abertas e fechadas por semana
media_abertos_por_semana = erros_abertos_por_semana.mean()
media_fechados_por_semana = erros_fechados_por_semana.mean()

# 7. Configuração de parâmetros para Simulação de Monte Carlo
# Controle deslizante para definir o número de simulações e de semanas futuras
num_simulacoes = st.slider("Número de Simulações", min_value=100, max_value=5000, value=1000, step=100)
num_semanas = st.slider("Projeção para Semanas Futuras", min_value=1, max_value=52, value=12)

# 8. Simulação de Monte Carlo para projeção de novos erros abertos e fechados
# Listas para armazenar os resultados das simulações
simulacoes_abertos = []
simulacoes_fechados = []
for _ in range(num_simulacoes):
    # Gera uma simulação aleatória baseada na média de issues abertas e fechadas por semana
    simulacao_abertos = np.random.poisson(media_abertos_por_semana, num_semanas)
    simulacao_fechados = np.random.poisson(media_fechados_por_semana, num_semanas)
    simulacoes_abertos.append(simulacao_abertos)
    simulacoes_fechados.append(simulacao_fechados)

# 9. Cálculo da média das simulações para cada semana projetada
# Calcula a média dos resultados de todas as simulações para cada semana futura
media_simulacoes_abertos = np.mean(simulacoes_abertos, axis=0)
media_simulacoes_fechados = np.mean(simulacoes_fechados, axis=0)

# 10. Cálculo do valor total estimado de issues abertas e fechadas
# Soma o valor atual de issues abertas e fechadas com as projeções para obter o total estimado
total_est_issues_abertas = issues_abertas + np.sum(media_simulacoes_abertos)
total_est_issues_fechadas = issues_fechadas + np.sum(media_simulacoes_fechados)

# Exibe os novos totais estimados de issues abertas e fechadas em cards no Streamlit
st.metric("Total Estimado de Issues Abertas", int(total_est_issues_abertas))
st.metric("Total Estimado de Issues Fechadas", int(total_est_issues_fechadas))

# 11. Gráfico acumulado da projeção de novos erros abertos e fechados
# Cria uma figura usando Plotly para exibir o crescimento acumulado das issues abertas e fechadas
fig_acumulado = go.Figure()
fig_acumulado.add_trace(go.Scatter(
    x=list(range(1, num_semanas + 1)),
    y=np.cumsum(media_simulacoes_abertos) + issues_abertas,
    mode='lines+markers',
    name="Erros Abertos (Acumulado)",
    line=dict(color="blue")
))
fig_acumulado.add_trace(go.Scatter(
    x=list(range(1, num_semanas + 1)),
    y=np.cumsum(media_simulacoes_fechados) + issues_fechadas,
    mode='lines+markers',
    name="Erros Fechados (Acumulado)",
    line=dict(color="red")
))
fig_acumulado.update_layout(
    title="Projeção Acumulada de Erros Abertos e Fechados por Semana",
    xaxis_title="Semanas Futuras",
    yaxis_title="Número Estimado de Erros (Acumulado)",
    legend_title="Status"
)

# Renderiza o gráfico acumulado no Streamlit
st.plotly_chart(fig_acumulado)

# 12. Gráfico da projeção semanal de novas issues abertas
# Cria uma figura para exibir a projeção semanal de novas issues abertas
fig_abertas_semanal = go.Figure()
fig_abertas_semanal.add_trace(go.Scatter(
    x=list(range(1, num_semanas + 1)),
    y=media_simulacoes_abertos,
    mode='lines+markers',
    name="Novas Issues Abertas",
    line=dict(color="blue")
))
fig_abertas_semanal.update_layout(
    title="Projeção de Novas Issues Abertas por Semana",
    xaxis_title="Semanas Futuras",
    yaxis_title="Número Estimado de Novas Issues Abertas"
)

# Renderiza o gráfico de novas issues abertas no Streamlit
st.plotly_chart(fig_abertas_semanal)

# 13. Gráfico da projeção semanal de issues fechadas
fig_fechadas_semanal = go.Figure()
fig_fechadas_semanal.add_trace(go.Scatter(
    x=list(range(1, num_semanas + 1)),
    y=media_simulacoes_fechados,
    mode='lines+markers',
    name="Issues Fechadas",
    line=dict(color="red")
))
fig_fechadas_semanal.update_layout(
    title="Projeção de Issues Fechadas por Semana",
    xaxis_title="Semanas Futuras",
    yaxis_title="Número Estimado de Issues Fechadas"
)

# Renderiza o gráfico de issues fechadas no Streamlit
st.plotly_chart(fig_fechadas_semanal)
