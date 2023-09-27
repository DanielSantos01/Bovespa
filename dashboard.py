import streamlit as st
import pandas as pd
import plotly.express as px
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout='wide')

def plot_line(column_name, title=None):
  st.header(title or column_name)
  fig = px.line(
    data,
    x='DT_FIM_EXERC',
    y=column_name,
    color='DENOM_CIA',
    labels={'DT_FIM_EXERC': '', column_name: '', 'DENOM_CIA': 'Empresa'},
  )
  fig.update_xaxes(dtick=1)
  st.plotly_chart(fig, use_container_width=True)

def get_data():
  data = pd.read_csv('./database.csv').sort_values(by='DT_FIM_EXERC')
  data['LIQUIDEZ CORRENTE'] = pd.to_numeric(data['LIQUIDEZ CORRENTE'].str.replace(',', '.'))
  data['LIQUIDEZ A SECO'] = pd.to_numeric(data['LIQUIDEZ A SECO'].str.replace(',', '.'))
  data['EXIGIVEL / ATIVO (TOTAL)'] = pd.to_numeric(data['EXIGIVEL / ATIVO (TOTAL)'].str.replace(',', '.'))
  return data

get_metrics = lambda : ['LIQUIDEZ', 'ENDIVIDAMENTO', 'COBERTURA', 'LUCRATIVIDADE', 'ESTRUTURAIS', 'RETORNO', 'ATIVIDADE', 'INSIGHTS']
data = get_data()

## SIDEBAR-----------------------------------------------------------------------------------------------------------------------------------
st.sidebar.title('Bovespa Dashboard')
st.sidebar.header('Filtros')
selected_category = st.sidebar.selectbox('Segmento', data['TIPO'].unique(), index=2)
data = data[data['TIPO'] == selected_category]
selected_metric = st.sidebar.selectbox('Demonstrativos', get_metrics())
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

if selected_metric == 'LIQUIDEZ':
  if diff == 1:
    st.header('Capital Circulante Líquido')
    base = (data.groupby('DENOM_CIA')['CAPITAL CIRCULANTE LIQUIDO'].sum()).reset_index()
    fig = px.bar(base, x='DENOM_CIA', y='CAPITAL CIRCULANTE LIQUIDO')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)
  else:
    st.header('Capital Circulante Líquido')
    fig = px.line(
      data,
      x='DT_FIM_EXERC',
      y='CAPITAL CIRCULANTE LIQUIDO',
      color='DENOM_CIA',
      labels={'DT_FIM_EXERC': '', 'CAPITAL CIRCULANTE LIQUIDO': '', 'DENOM_CIA': 'Empresa'},
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)


  if diff == 1:
    st.header('Liquidez corrente')
    base = (data.groupby('DENOM_CIA')['LIQUIDEZ CORRENTE'].sum()).reset_index()
    fig = px.bar(base, x='DENOM_CIA', y='LIQUIDEZ CORRENTE')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)
  else:
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


  st.header('Relação Capital Circulante & Liquidez Corrente (normalized)')
  companies = data['DENOM_CIA'].unique()
  fig = make_subplots(rows=math.ceil(len(companies)/2), cols=2, shared_xaxes=True, subplot_titles=companies, vertical_spacing=0.4)
  for i, company in enumerate(companies, start=1):
    base = data[data['DENOM_CIA'] == company]
    if i % 2 != 0: col = 1
    else: col = 2
    row = math.ceil(i/2)
    factor = data['CAPITAL CIRCULANTE LIQUIDO'].max()/100

    fig.add_trace(
      go.Bar(
        x=base['DT_FIM_EXERC'],
        y=base['CAPITAL CIRCULANTE LIQUIDO'],
        name='Capital Circulante',
        marker_color='blue',
      ),
      row=row, col=col,
    )

    fig.add_trace(
      go.Scatter(
        x=base['DT_FIM_EXERC'],
        y=base['LIQUIDEZ CORRENTE'] * factor,
        mode='lines',
        name='LIQUIDEZ CORRENTE',
        line=dict(color='red', width=2),
      ),
      row=row, col=col,
    )
  fig.update_layout(showlegend=False)
  st.plotly_chart(fig, use_container_width=True)

  plot_line('LIQUIDEZ A SECO')
  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line("ATIVO CIRCULANTE")
  with col2:
    plot_line("PASSIVO CIRCULANTE")


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

  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line("EXIGIVEL A LONGO PRAZO")
  with col2:
    plot_line("PATRIMONIO LIQUIDO")

  plot_line("EXIGIVEL / ATIVO (TOTAL)")
  plot_line("CAPITAIS DE LONGO PRAZO")


if selected_metric == 'INSIGHTS':
  ##------------------------------------------------------------------------------------------------------------------------------------------
  col1, col2 = st.columns(2, gap="large")
  with col1:
    st.header('Receita Líquida (mean)')
    base = (data.groupby('DENOM_CIA')['RECEITA LIQUIDA'].sum()/diff).reset_index()
    fig = px.bar(base, x='DENOM_CIA', y='RECEITA LIQUIDA')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)

  with col2:
    st.header('Ativo & Passivo circulante (mean)')
    base = data.groupby('DENOM_CIA').agg({'PASSIVO CIRCULANTE': 'sum', 'ATIVO CIRCULANTE': 'sum'}).reset_index()
    base['ATIVO CIRCULANTE'] = base['ATIVO CIRCULANTE']/diff
    base['PASSIVO CIRCULANTE'] = base['PASSIVO CIRCULANTE']/diff
    fig = px.histogram(base, x='DENOM_CIA', y=['ATIVO CIRCULANTE', 'PASSIVO CIRCULANTE'], barmode='group')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)
  ##------------------------------------------------------------------------------------------------------------------------------------------

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

# Tab de COBERTURA
if selected_metric == 'COBERTURA':  
  plot_line('COBERTURA DE JUROS')
  plot_line('COBERTURA DE JUROS (CAIXA OPERAÇÕES)')
  

# Tab de LUCRATIVIDADE
if selected_metric == 'LUCRATIVIDADE':

  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line('MG_LIQ', 'Margem Líquida')
    plot_line('RECEITA LIQUIDA')
  with col2:
    plot_line('MG_OP', 'Margem Operacional')
    plot_line('LIQUIDEZ A SECO')


# Tab de ESTRUTURAIS
if selected_metric == 'ESTRUTURAIS':
  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line('CUSTO DA MERCADORIA VENDIDA %')
  with col2:
    plot_line('DESPESAS OPERACIONAIS %')
  
  plot_line('JUROS')
  plot_line('GIRO')


# Tab de RETORNO
if selected_metric == 'RETORNO':
  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line('ROA')
  with col2:
    plot_line('ROE')

  plot_line('ROI')

# Tab de ATIVIDADE
if selected_metric == 'ATIVIDADE':
  plot_line('GIRO')
  plot_line('GIRO DE VALORES A RECEBER')
  plot_line('GIRO DE DUPLICATAS A PAGAR')
