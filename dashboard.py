import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout='wide')

def get_data():
  data = pd.read_csv('./database.csv').sort_values(by='DT_FIM_EXERC')
  data['LIQUIDEZ CORRENTE'] = pd.to_numeric(data['LIQUIDEZ CORRENTE'].str.replace(',', '.'))
  data['LIQUIDEZ A SECO'] = pd.to_numeric(data['LIQUIDEZ A SECO'].str.replace(',', '.'))
  return data

data = get_data()


metrics = ['LIQUIDEZ', 'ENDIVIDAMENTO', 'COBERTURA', 'LUCRATIVIDADE', 'RETORNO', 'ATIVIDADE', 'INSIGHTS']

## SIDEBAR-----------------------------------------------------------------------------------------------------------------------------------
st.sidebar.title('Bovespa Dashboard')
st.sidebar.header('Filtros')
selected_category = st.sidebar.selectbox('Segmento', data['TIPO'].unique())
data = data[data['TIPO'] == selected_category]
selected_metric = st.sidebar.selectbox('Demonstrativos', metrics)
min_year = st.sidebar.number_input('Ano inicial', min_value=data['DT_FIM_EXERC'].min(), max_value=data['DT_FIM_EXERC'].max())
max_year = st.sidebar.number_input('Ano final', min_value=min_year, max_value=data['DT_FIM_EXERC'].max(), value=data['DT_FIM_EXERC'].max())
selected_companies = st.sidebar.multiselect('Empresa', data['DENOM_CIA'].unique(), placeholder="Selecione especificamente")
##------------------------------------------------------------------------------------------------------------------------------------------

st.title(f'Indicadores de {selected_metric.lower().capitalize()}')

## APPLYING FILTERS--------------------------------------------------------------------------------------------------------------------------
data = data[(data['DT_FIM_EXERC'] >= min_year) & (data['DT_FIM_EXERC'] <= max_year)]
if (selected_companies): data = data[data['DENOM_CIA'].isin(selected_companies)]
##------------------------------------------------------------------------------------------------------------------------------------------

diff = max_year - min_year + 1

if selected_metric == 'LIQUIDEZ' and max_year != min_year:
  col1, col2 = st.columns(2, gap="large")
  with col1:
    st.header('Capital Circulante Líquido (mean)')
    base = (data.groupby('DENOM_CIA')['CAPITAL CIRCULANTE LIQUIDO'].sum()/diff).reset_index()
    fig = px.bar(base, x='DENOM_CIA', y='CAPITAL CIRCULANTE LIQUIDO')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)

  with col2:
    st.header('Capital Circulante Líquido (timeline)')
    print(data[data['DENOM_CIA'] == 'UNIDAS LOCAÇÕES E SERVIÇOS S.A.'][['CAPITAL CIRCULANTE LIQUIDO', 'DT_FIM_EXERC']])
    fig = px.line(
      data,
      x='DT_FIM_EXERC',
      y='CAPITAL CIRCULANTE LIQUIDO',
      color='DENOM_CIA',
      labels={'DT_FIM_EXERC': '', 'CAPITAL CIRCULANTE LIQUIDO': '', 'DENOM_CIA': 'Empresa'},
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)


  st.header('Liquidez Corrente')
  fig = px.line(
    data,
    x='DT_FIM_EXERC',
    y='LIQUIDEZ CORRENTE',
    color='DENOM_CIA',
    labels={'DT_FIM_EXERC': '', 'LIQUIDEZ CORRENTE': '', 'DENOM_CIA': 'Empresa'},
  )
  fig.update_xaxes(dtick=1)
  st.plotly_chart(fig, use_container_width=True)


  st.header('Liquidez a Seco')
  fig = px.line(
    data,
    x='DT_FIM_EXERC',
    y='LIQUIDEZ A SECO',
    color='DENOM_CIA',
    labels={'DT_FIM_EXERC': '', 'LIQUIDEZ A SECO': '', 'DENOM_CIA': 'Empresa'},
  )
  fig.update_xaxes(dtick=1)
  st.plotly_chart(fig, use_container_width=True)

  st.header('Comparação liquidez corrente e a seco (mean)')
  base = data.groupby('DENOM_CIA').agg({'LIQUIDEZ A SECO': 'sum', 'LIQUIDEZ CORRENTE': 'sum'}).reset_index()
  base['LIQUIDEZ A SECO'] = base['LIQUIDEZ A SECO']/diff
  base['LIQUIDEZ CORRENTE'] = base['LIQUIDEZ CORRENTE']/diff
  fig = px.histogram(base, x='DENOM_CIA', y=['LIQUIDEZ CORRENTE', 'LIQUIDEZ A SECO'], barmode='group')
  fig.update_xaxes(title_text='')
  fig.update_yaxes(title_text='')
  st.plotly_chart(fig, use_container_width=True)


if selected_metric == 'ENDIVIDAMENTO':
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


if selected_metric == 'INSIGHTS':
  ##------------------------------------------------------------------------------------------------------------------------------------------
  col1, col2 = st.columns(2, gap="large")
  with col1:
    st.header('Média Receita Líquida')
    base = (data.groupby('DENOM_CIA')['RECEITA LIQUIDA'].sum()/diff).reset_index()
    fig = px.bar(base, x='DENOM_CIA', y='RECEITA LIQUIDA')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)

  with col2:
    st.header('Média Ativo & Passivo circulante')
    base = data.groupby('DENOM_CIA').agg({'PASSIVO CIRCULANTE': 'sum', 'ATIVO CIRCULANTE': 'sum'}).reset_index()
    base['ATIVO CIRCULANTE'] = base['ATIVO CIRCULANTE']/diff
    base['PASSIVO CIRCULANTE'] = base['PASSIVO CIRCULANTE']/diff
    fig = px.histogram(base, x='DENOM_CIA', y=['ATIVO CIRCULANTE', 'PASSIVO CIRCULANTE'], barmode='group')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)
  ##------------------------------------------------------------------------------------------------------------------------------------------

  st.header('Ativo - Passivo')
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

  st.header('Liquidez e Endividamento')
  fig = px.histogram(data, x='DENOM_CIA', y=['LIQUIDEZ CORRENTE', 'LIQUIDEZ A SECO', 'EXIGIVEL / ATIVO (TOTAL)'], barmode='group')
  fig.update_xaxes(title_text='')
  fig.update_yaxes(title_text='')
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

