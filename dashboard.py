import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout='wide')

data = pd.read_csv('./database.csv')
st.title('Bovespa Dashboard')

col1, col2, col3, col4 = st.columns(4)

with col1:
  selected_category = st.selectbox('Segmento', data['TIPO'].unique()[::-1])
  data = data[data['TIPO'] == selected_category]

with col2:
  selected_companies = st.multiselect('Empresa', data['DENOM_CIA'].unique(), placeholder="Selecione especificamente")

with col3:
  min_year = st.number_input('Ano inicial', min_value=data['DT_FIM_EXERC'].min(), max_value=data['DT_FIM_EXERC'].max(), value=2019)

with col4:
  max_year = st.number_input('Ano final', min_value=min_year, max_value=data['DT_FIM_EXERC'].max(), value=data['DT_FIM_EXERC'].max())

data = data[(data['DT_FIM_EXERC'] >= min_year) & (data['DT_FIM_EXERC'] <= max_year)]

if (selected_companies): data = data[data['DENOM_CIA'].isin(selected_companies)]


col1, col2 = st.columns(2, gap="large")
with col1:
  st.header('Somatório Receita Líquida')
  base = data.groupby('DENOM_CIA')['RECEITA LIQUIDA'].sum().reset_index()
  fig = px.bar(base, x='DENOM_CIA', y='RECEITA LIQUIDA')
  fig.update_xaxes(title_text='')
  fig.update_yaxes(title_text='')
  st.plotly_chart(fig, use_container_width=True)

with col2:
  st.header('Somatório Ativo & Passivo circulante')
  base = data.groupby('DENOM_CIA').agg({'PASSIVO CIRCULANTE': 'sum', 'ATIVO CIRCULANTE': 'sum'}).reset_index()
  fig = px.histogram(base, x='DENOM_CIA', y=['ATIVO CIRCULANTE', 'PASSIVO CIRCULANTE'], barmode='group')
  fig.update_xaxes(title_text='')
  fig.update_yaxes(title_text='')
  st.plotly_chart(fig, use_container_width=True)


if max_year != min_year:
  col1, col2 = st.columns(2, gap="large")
  with col1:
    st.header('Receita Líquida (timeline)')
    fig = px.line(
      data,
      x='DT_FIM_EXERC',
      y='RECEITA LIQUIDA',
      color='DENOM_CIA',
      labels={'DT_FIM_EXERC': '', 'RECEITA LIQUIDA': '', 'DENOM_CIA': 'Empresa'},
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

  with col2:
    st.header('Ativo - Passivo (timeline)')
    data['ATIVO - PASSIVO'] = data['ATIVO CIRCULANTE'] - data['PASSIVO CIRCULANTE']
    fig = px.line(
      data,
      x='DT_FIM_EXERC',
      y='ATIVO - PASSIVO',
      color='DENOM_CIA',
      labels={'DT_FIM_EXERC': '', 'ATIVO - PASSIVO': '', 'DENOM_CIA': 'Empresa'},
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)


st.header('Composição do passivo total')
companies = [f'{company.split(" ")[0]} {company.split(" ")[1]}' for company in data['DENOM_CIA'].unique()]
fig = make_subplots(rows=1, cols=len(companies), subplot_titles=companies, specs=[[{'type': 'pie'}] * len(companies)], print_grid=True)
for i, cia in enumerate(data['DENOM_CIA'].unique()):
  base = data[data['DENOM_CIA'] == cia]
  fig.add_trace(
    go.Pie(
      labels=['EXIGIVEL A LONGO PRAZO', 'PASSIVO CIRCULANTE'],
      values=[base['EXIGIVEL A LONGO PRAZO'].sum(), base['PASSIVO CIRCULANTE'].sum()],
    ),
    row=1,
    col=i + 1
  )
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)


st.header('Endividamento geral')
fig = px.line(
  data,
  x='DT_FIM_EXERC',
  y='ENDIVIDAMENTO GERAL',
  color='DENOM_CIA',
  labels={'DT_FIM_EXERC': '', 'ENDIVIDAMENTO GERAL': '', 'DENOM_CIA': 'Empresa'},
)
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, use_container_width=True)


st.header('Liquidez e Endividamento')
data['LIQUIDEZ CORRENTE'] = pd.to_numeric(data['LIQUIDEZ CORRENTE'].str.replace(',', ''))
data['LIQUIDEZ A SECO'] = pd.to_numeric(data['LIQUIDEZ A SECO'].str.replace(',', ''))
fig = px.histogram(data, x='DENOM_CIA', y=['LIQUIDEZ CORRENTE', 'LIQUIDEZ A SECO', 'EXIGIVEL / ATIVO (TOTAL)'], barmode='group')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')
st.plotly_chart(fig, use_container_width=True)

