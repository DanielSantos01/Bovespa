import streamlit as st
import pandas as pd
import plotly.express as px
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title='Financial Dashboard', page_icon='https://icons.iconarchive.com/icons/custom-icon-design/flatastic-9/512/Line-chart-icon.png', layout = 'wide', initial_sidebar_state='collapsed')

@st.cache_data
def get_data():
  data = pd.read_csv('./database.csv').sort_values(by='DT_FIM_EXERC')
  data['LIQUIDEZ CORRENTE'] = pd.to_numeric(data['LIQUIDEZ CORRENTE'].str.replace(',', '.'))
  data['LIQUIDEZ A SECO'] = pd.to_numeric(data['LIQUIDEZ A SECO'].str.replace(',', '.'))
  data['EXIGIVEL / ATIVO (TOTAL)'] = pd.to_numeric(data['EXIGIVEL / ATIVO (TOTAL)'].str.replace(',', '.'))
  return data

get_metrics = lambda : ['LIQUIDEZ', 'ENDIVIDAMENTO', 'COBERTURA', 'LUCRATIVIDADE', 'ESTRUTURAIS', 'RETORNO', 'ATIVIDADE', 'INSIGHTS']
data = get_data()

visualization_keys = {
  'heatmap': 'Mapa de Calor',
  'lines': 'Linhas'
}

alternative_visualizations = {
  'LIQUIDEZ': {
    'ATIVO CIRCULANTE': [visualization_keys['heatmap'], visualization_keys['lines']],
    'PASSIVO CIRCULANTE': [visualization_keys['heatmap'], visualization_keys['lines']],
  }
}

runtime_vars = {}

def find_closed_intervals(years):
  if len(years) == 0:
    return []

  closed_intervals = []
  start_year = years[0]
  end_year = years[0]

  for year in years[1:]:
    if year == end_year + 1:
      end_year = year
    else:
      if start_year == end_year:
        closed_intervals.append(str(start_year))
      else:
        closed_intervals.append(f"{start_year}-{end_year}")
      start_year = end_year = year

  if start_year == end_year:
    closed_intervals.append(str(start_year))
  else:
    closed_intervals.append(f"{start_year}-{end_year}")

  return closed_intervals

## SIDEBAR-----------------------------------------------------------------------------------------------------------------------------------
st.sidebar.title('Financial Dashboard')
st.sidebar.header('Filtros')
selected_category = st.sidebar.selectbox('Segmento', data['TIPO'].unique(), index=2)
data = data[data['TIPO'] == selected_category]
selected_metric = st.sidebar.selectbox('Demonstrativos', get_metrics())
min_year = st.sidebar.number_input('Ano inicial', min_value=data['DT_FIM_EXERC'].min(), max_value=data['DT_FIM_EXERC'].max())
max_year = st.sidebar.number_input('Ano final', min_value=min_year, max_value=data['DT_FIM_EXERC'].max(), value=data['DT_FIM_EXERC'].max())
selected_companies = st.sidebar.multiselect('Empresa', data['DENOM_CIA'].unique(), placeholder="Selecione")

if alternative_visualizations.get(selected_metric):
  st.sidebar.header('Visualizações alternativas')
  for key in dict.keys(alternative_visualizations[selected_metric]):
    runtime_vars[f'VISUALIZATION {key}'] = st.sidebar.selectbox(key, alternative_visualizations[selected_metric][key])
##------------------------------------------------------------------------------------------------------------------------------------------

st.title(f'Indicadores de {selected_metric.lower().capitalize()}')

## APPLYING FILTERS--------------------------------------------------------------------------------------------------------------------------
data = data[(data['DT_FIM_EXERC'] >= min_year) & (data['DT_FIM_EXERC'] <= max_year)]
if (selected_companies): data = data[data['DENOM_CIA'].isin(selected_companies)]
##------------------------------------------------------------------------------------------------------------------------------------------

diff = max_year - min_year + 1

def plot_column(title, x='DENOM_CIA', y='DENOM_CIA', base=None, barmode=None):
  if base is None: base = data
  fig = px.bar(
    base,
    x=x,
    y=y,
    title=title,
    barmode=barmode
  )
  fig.update_xaxes(dtick=1, title_text='')
  fig.update_yaxes(title_text='')
  st.plotly_chart(fig, use_container_width=True)

def plot_line(title, base=None, x='DT_FIM_EXERC', y='LUCRO LIQUIDO', color='DENOM_CIA'):
  if base is None: base = data
  if diff == 1:
    plot_column(title, y=y, base=base)
  else:
    fig = px.line(
      base,
      x=x,
      y=y,
      color=color,
      title=title,
    )
    fig.update_xaxes(dtick=1, title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)

def plot_heatmap(title, base=None, y=None):
  if base is None or diff == 1: base = data
  if diff == 1:
    plot_column(title, y=y, base=base)
  else:
    fig = px.imshow(
      base,
      labels={'color': 'valor', 'DENOM_CIA': 'Empresa'},
      x=base.columns.get_level_values(1),
      y=base.index,
      title=title,
    )
    fig.update_xaxes(dtick=1, title_text='')
    fig.update_yaxes(title_text='')
    st.plotly_chart(fig, use_container_width=True)

def plot_histogram(title, x='DENOM_CIA', y='DENOM_CIA', base=None, barmode=None):
  if base is None: base = data
  fig = px.histogram(
    base,
    x=x,
    y=y,
    title=title,
    barmode=barmode
  )
  fig.update_xaxes(dtick=1, title_text='')
  fig.update_yaxes(title_text='')
  st.plotly_chart(fig, use_container_width=True)


# Tab de LIQUIDEZ
if selected_metric == 'LIQUIDEZ':
  col1, col2 = st.columns(2, gap='large')
  with col1:
    if runtime_vars['VISUALIZATION ATIVO CIRCULANTE'] == visualization_keys['lines']:
      plot_line('Ativo Circulante', y='ATIVO CIRCULANTE')
    else:
      base = data.pivot(index='DENOM_CIA', columns='DT_FIM_EXERC', values=['ATIVO CIRCULANTE'])
      plot_heatmap('Ativo Circulante', y='ATIVO CIRCULANTE', base=base)
  with col2:
    if runtime_vars['VISUALIZATION PASSIVO CIRCULANTE'] == visualization_keys['lines']:
      plot_line('Passivo Circulante', y='PASSIVO CIRCULANTE')
    else:
      base = data.pivot(index='DENOM_CIA', columns='DT_FIM_EXERC', values=['PASSIVO CIRCULANTE'])
      plot_heatmap('Passivo Circulante',  y='PASSIVO CIRCULANTE', base=base)

  plot_line('Capital Circulante Líquido', y='CAPITAL CIRCULANTE LIQUIDO')

  if diff == 1:
    base = (data.groupby('DENOM_CIA')['LIQUIDEZ CORRENTE'].sum()).reset_index()
    plot_column('Liquidez Corrente', y='LIQUIDEZ CORRENTE', base=base)
  else:
    plot_line('Liquidez Corrente', y='LIQUIDEZ CORRENTE')

  st.header('Relação Capital Circulante & Liquidez Corrente (normalized)')
  companies = data['DENOM_CIA'].unique()
  get_rows = lambda : math.ceil(len(companies)/2) if len(companies) > 1 else 1
  fig = make_subplots(
    rows=get_rows(),
    cols=2,
    shared_xaxes=True,
    subplot_titles=companies,
    vertical_spacing=(1/(get_rows() - 1)) * 0.4 if get_rows() > 1 else 0.4
  )
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


# Tab de ENDIVIDAMENTO
if selected_metric == 'ENDIVIDAMENTO':
  plot_line('Endividamento geral', y='ENDIVIDAMENTO GERAL')

  col1, col2 = st.columns(2, gap="large")
  with col1: plot_line('Exigível a Longo Prazo', y='EXIGIVEL A LONGO PRAZO')
  with col2: plot_line('Patrimônio Líquido', y='PATRIMONIO LIQUIDO')
  plot_line('Exigível Total / Ativo Total', y='EXIGIVEL / ATIVO (TOTAL)' )
  plot_line('Capitais de longo prazo', y='CAPITAIS DE LONGO PRAZO')




# Tab de COBERTURA
if selected_metric == 'COBERTURA':  
  plot_line('Cobertura de juros', y='COBERTURA DE JUROS')
  plot_line('Cobertura de juros (Caixa operações)', y='COBERTURA DE JUROS (CAIXA OPERAÇÕES)', )




# Tab de LUCRATIVIDADE
if selected_metric == 'LUCRATIVIDADE':
  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line('Margem Líquida', y='MG_LIQ')
    plot_line('Receita Líquida', y='RECEITA LIQUIDA', )
  with col2:
    plot_line('Margem Operacional', y='MG_OP')
    plot_line('Liquidez a seco', y='LIQUIDEZ A SECO')




# Tab de ESTRUTURAIS
if selected_metric == 'ESTRUTURAIS':
  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line('Custo da mercadoria vendida', y='CUSTO DA MERCADORIA VENDIDA %')
  with col2:
    plot_line('Despesas operacionais %', y='DESPESAS OPERACIONAIS %', )
  
  plot_line('Juros', y='JUROS')
  plot_line('Giro', y='GIRO')



# Tab de RETORNO
if selected_metric == 'RETORNO':
  uninvestment_companies = data[data['ROI'].isna()]['DENOM_CIA'].unique()
  year_intervals = []
  comps = []
  relation = {}

  for company in uninvestment_companies:
    base = data[data['DENOM_CIA'] == company][data['ROI'].isna()]
    intervals = find_closed_intervals(base['DT_FIM_EXERC'].unique())
    comps.extend([company] * len(intervals))
    year_intervals.extend(intervals)

  col1, col2 = st.columns(2, gap="large")
  with col1:
    plot_line('Retorno Sobre os Ativos', y='ROA')
  with col2:
    plot_line('Retorno Sobre o Patrimônio', y='ROE')

  plot_line('Retorno Sobre o Investimento', y='ROI')

  fig = go.Figure(
    data=[go.Table(header=dict(values=['Empresa', 'Período'], fill_color='rgb(0, 104, 201)', line_color='darkslategray'),
    cells=dict(values=[comps, year_intervals], fill_color='rgb(120, 120, 120)'))
  ])
  fig.update_layout(title="Empresas que não investiram em algum período")
  st.plotly_chart(fig, use_container_width=True)



# Tab de ATIVIDADE
if selected_metric == 'ATIVIDADE':
  plot_line('Giro', y='GIRO')
  plot_line('Giro dos valores a receber', y='GIRO DE VALORES A RECEBER')
  plot_line('Giro dos valores a pagar', y='GIRO DE DUPLICATAS A PAGAR')



# Tab de INSIGHTS
if selected_metric == 'INSIGHTS':
  col1, col2 = st.columns(2, gap="large")
  with col1:
    base = (data.groupby('DENOM_CIA')['RECEITA LIQUIDA'].sum()/diff).reset_index()
    plot_column('Receita Líquida (mean)', y='RECEITA LIQUIDA', base=base)
  with col2:
    base = data.groupby('DENOM_CIA').agg({'PASSIVO CIRCULANTE': 'sum', 'ATIVO CIRCULANTE': 'sum'}).reset_index()
    base['ATIVO CIRCULANTE'] = base['ATIVO CIRCULANTE']/diff
    base['PASSIVO CIRCULANTE'] = base['PASSIVO CIRCULANTE']/diff
    plot_histogram('Ativo e Passivo Circulante (mean)', y=['ATIVO CIRCULANTE', 'PASSIVO CIRCULANTE'], barmode='group', base=base)

  plot_histogram('Liquidez e Endividamento', y=['LIQUIDEZ CORRENTE', 'LIQUIDEZ A SECO', 'EXIGIVEL / ATIVO (TOTAL)'], barmode='group')

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
