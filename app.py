import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Carregar os dados do arquivo CSV
df = pd.read_csv("vendas.csv", sep=",", decimal=",")

# Converter a coluna "Data" para o formato datetime
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

# Ordenar o DataFrame pela coluna "Data"
df = df.sort_values("Data")

# Criar uma coluna com o mês e ano para facilitar a filtragem
df["MonthYear"] = df["Data"].dt.strftime('%m-%Y')

# Criar uma coluna com o número da semana do ano
df["Week"] = df["Data"].dt.week

# Obter os meses únicos presentes no DataFrame
months = df["MonthYear"].unique()

# Selecionar os meses inicial e final através de selectbox
start_month = st.sidebar.selectbox("Mês de início", months)
end_month = st.sidebar.selectbox("Mês de término", months)

# Extrair o ano e o mês de início e término
start_month, start_year = start_month.split("-")
end_month, end_year = end_month.split("-")

# Filtrar o DataFrame com base no intervalo de meses selecionado
df_filtered = df[(df['Data'].dt.month >= int(start_month)) & (df['Data'].dt.year >= int(start_year)) & 
                 (df['Data'].dt.month <= int(end_month)) & (df['Data'].dt.year <= int(end_year))]

# Filtrar por cidade
cities = st.sidebar.multiselect("Selecione as cidades", df_filtered["Cidade"].unique())
if cities:
    df_filtered = df_filtered[df_filtered["Cidade"].isin(cities)]

# Exibir o DataFrame filtrado
df_filtered

fig_services = df_filtered["Services"].value_counts().reset_index()
fig_services.columns = ["Serviço", "Total"]
fig_services_plot = px.bar(fig_services, x="Serviço", y="Total", title="Total de Serviços", text="Total")
fig_services_plot.update_traces(texttemplate='%{text}', textposition='outside')

fig_services_plot

# Agrupar os dados por "Services" e "Status" e contar as ocorrências
service_status_counts = df_filtered.groupby(["Services", "Status"]).size().unstack(fill_value=0)

service_status_counts['Total'] = service_status_counts.sum(axis=1)

# Calcular a porcentagem de cada valor em relação ao total da linha
percentage_columns = service_status_counts.drop(columns='Total').div(service_status_counts['Total'], axis=0) * 100

# Arredondar as porcentagens para duas casas decimais
percentage_columns = percentage_columns.round(2)

# Renomear as colunas de porcentagem para diferenciar
percentage_columns = percentage_columns.add_suffix(' (%)')

# Combinar as contagens e as porcentagens em um único DataFrame
result = pd.concat([service_status_counts, percentage_columns], axis=1)

# Exibir a tabela no Streamlit
st.write("### Totais de Serviços por Status")
st.dataframe(result)

# Contar as ocorrências de cada sexo
sex_counts = df_filtered['Sexo'].value_counts()

# Definir o mapeamento de cores
color_discrete_map = {'M': 'blue', 'F': 'red'}

# Criar um gráfico de pizza para a porcentagem de cada sexo
fig = px.pie(values=sex_counts.values, names=sex_counts.index, title='Distribuição por Sexo', 
             labels={'index': 'Sexo'}, color=sex_counts.index, 
             color_discrete_map=color_discrete_map)

# Exibir o gráfico no Streamlit
st.write("### Distribuição por Sexo")
st.plotly_chart(fig)

