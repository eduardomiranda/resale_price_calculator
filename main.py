import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Aplicativo Streamlit para calcular preço de venda com base
# em impostos, margem de lucro, custo de capital e cenários de variação.

# from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, StAggridTheme



total_tributos = 0.1743

options_lucro = ["Aplicado na compra", "Aplicado na venda"]
options_venda = ["Anual", "Mensal"]


# ========================
# Funções de cálculo
# ========================


def calcular_preco_venda_lucro(tipo_venda, aplicacao_lucro, preco_compra, total_tributos, lucro_desejado, taxa_juros):
    """Calcula preço de venda e lucro líquido após tributos.

    Parâmetros
    - tipo_venda: "Anual" ou "Mensal".
    - aplicacao_lucro: onde a margem é aplicada (compra ou venda).
    - preco_compra: valor base do produto.
    - total_tributos: alíquota total efetiva (decimal, ex.: 0.1743).
    - lucro_desejado: margem desejada (decimal, ex.: 0.20).
    - taxa_juros: custo de capital (decimal, ex.: 0.12 para 12%).

    Retorna
    - preco_venda: preço sugerido pelo modelo escolhido.
    - lucro: lucro líquido após tributos, sem a margem do vendedor.
    """
    # Detalhes dos cálculos
    # https://docs.google.com/spreadsheets/d/17mPB-8cjxMgNHP7sDDBul8z19SXgAocRGvD4cZvqAUw/edit?usp=sharing

    if tipo_venda == options_venda[0]: # Anual
        if aplicacao_lucro == options_lucro[0]: # "Aplicado na compra"
            preco_venda = preco_compra / (1 - total_tributos) + (preco_compra * lucro_desejado / (1 - total_tributos) )
            # preco_compra / (1 - total_tributos) :: Faz o cálculo do valor de venda considerando apenas os impostos 
            # (preco_compra * lucro_desejado / (1 - total_tributos) ) :: Faz o custo adicional do valor final considerando impostos sobre o lucro desejado
            # nas duas partes do denominador a subtração (1 - total_tributos) se repete, uma vez que é calculado separadamente o valor do imposto sobre cada parte que compõe o custo final
            lucro = preco_venda - (preco_venda * total_tributos) - preco_compra

        elif aplicacao_lucro == options_lucro[1]: # "Aplicado na venda"
            preco_venda = preco_compra / (1 - lucro_desejado - total_tributos )
            lucro = preco_venda - (preco_venda * total_tributos) - preco_compra

    elif tipo_venda == options_venda[1]: # Mensal
        if aplicacao_lucro == options_lucro[0]: # "Aplicado na compra"
            preco_venda_anual = (preco_compra / ( 1 - total_tributos)) + ((preco_compra * lucro_desejado) / (1 - total_tributos)) + ((preco_compra * taxa_juros) / (1 - total_tributos))
            # (preco_compra / ( 1 - total_tributos)) :: Faz o cálculo do valor de venda considerando apenas os impostos 
            # ((preco_compra * lucro_desejado) / (1 - total_tributos)) :: Faz o custo adicional do valor final considerando impostos sobre o lucro desejado
            # ((preco_compra * taxa_juros) / (1 - total_tributos)) :: Faz o custo adicional do valor final considerando impostos sobre o o custo do capital sobre o preço de compra
            # nas três partes do denominador a subtração (1 - total_tributos) se repete, uma vez que é calculado separadamente o valor do imposto sobre cada parte que compõe o custo final
            preco_venda = preco_venda_anual / 12
            lucro = preco_venda_anual - (preco_venda_anual * total_tributos) - (preco_compra * taxa_juros) - preco_compra

        elif aplicacao_lucro == options_lucro[1]: # "Aplicado na venda"
            preco_venda_anual = preco_compra / ( 1 - lucro_desejado - total_tributos) + (preco_compra * taxa_juros) / (1 - total_tributos)
            preco_venda = preco_venda_anual / 12
            lucro = preco_venda_anual - (preco_venda_anual * total_tributos) - (preco_compra * taxa_juros) - preco_compra

    return preco_venda, lucro




def calculo_taxa_juros( preco_compra: float, selic: float, total_meses: int) -> float:
    """Gera mês a mês os juros sobre saldo devedor e rendimentos acumulados.

    O cálculo transforma SELIC anual em taxa mensal equivalente e
    simula amortização linear (parcela fixa = preco_compra / total_meses).

    Yield por mês: (i, saldo_devedor, juros_no_mes, rendimentos_acumulados)
    """

    selic_mensal = (1 + selic) ** (1/12) - 1

    saldo_devedor = preco_compra
    parcela = preco_compra / total_meses

    rendimentos_acumulados = 0.0

    for i in range(1, total_meses + 1):
        juros_sobre_saldo_devedor = saldo_devedor * selic_mensal
        rendimentos_acumulados += juros_sobre_saldo_devedor

        yield i, saldo_devedor, juros_sobre_saldo_devedor, rendimentos_acumulados

        saldo_devedor = saldo_devedor - parcela



def juros_minimo_aceitavel(preco_compra: float, selic: float, total_meses: int) -> float:
    """Retorna taxa mínima aceitável (%) para cobrir o custo do capital em 12 meses.

    Usa a simulação de juros para obter o rendimento acumulado e
    converte para percentual sobre o preço de compra.
    """

    rendimentos_acumulado = list(calculo_taxa_juros( preco_compra, selic, 12))[-1][3]
    return rendimentos_acumulado/preco_compra * 100




# ========================
# Interface com Streamlit
# ========================


# Configuração da página do Streamlit
st.set_page_config(page_title="Calculadora de Preço de Venda", layout="centered")


st.title("📊 Calculadora de Preço de Venda")

col_baa7, col_428a = st.columns(2)

with col_baa7:
    # Seleção de como a margem é aplicada no cálculo
    default = options_lucro[0]
    aplicacao_lucro = st.pills("Seleciona onde a margem de lucro será aplicada:", options=options_lucro, selection_mode="single", default=default)

with col_428a:
    # Seleção do horizonte da venda (anual x mensal)
    default = options_venda[0]
    tipo_venda = st.pills("Seleciona o modelo de venda:", options=options_venda, selection_mode="single", default=default)



# Inputs de parâmetros do modelo
preco_compra = st.number_input(
    "Valor da compra em R$ (reais):",
    min_value=0.0,
    value=100.0,
    format="%.2f"
)


col_901d, col_4f32, col_924e, col_1a64 = st.columns(4)

with col_901d:
    # SELIC anual; convertida para decimal
    selic = st.number_input(
        "Taxa Selic atual (%):",
        min_value=0.0,
        step=0.25,
        value=15.0,
        format="%.2f"
    ) / 100  # converter para decimal

with col_4f32:
    # Margem de lucro desejada; convertida para decimal
    lucro_desejado = st.number_input(
        "Lucro desejado (%):",
        min_value=0.0,
        step=0.5,
        value=20.0,
        format="%.2f"
    ) / 100  # converter para decimal


with col_924e:
    # Taxa de juros do capital (mínimo definido por custo do capital simulado)
    taxa_juros = st.number_input(
        "Taxa de juros (%):",
        min_value= juros_minimo_aceitavel( preco_compra, selic, 12),
        step=0.25,
        value=12.0,
        format="%.2f"
    ) / 100  # converter para decimal


with col_1a64:
    # Percentual destinado ao vendedor sobre o lucro
    margem_vendedor = st.number_input(
        "Margem do vendedor (%):",
        min_value=0.0,
        step=0.25,
        value=10.0,
        format="%.2f"
    ) / 100  # converter para decimal



# Cálculo principal (preço + lucro)
preco_venda, lucro = calcular_preco_venda_lucro(tipo_venda, aplicacao_lucro, preco_compra, total_tributos, lucro_desejado, taxa_juros)

st.success(f"💰 Preço de venda **{tipo_venda.lower()}** sugerido: R$ {preco_venda:,.2f}")
st.success(f"💰 Margem do vendedor ({margem_vendedor*100:,.2f}%): R$ {lucro * margem_vendedor:,.2f} ")

if st.checkbox("Calcular variações na taxas de juros e lucro desejado"):
    # Análise de sensibilidade: variações em lucro e juros

    col_29ba, col_98ae = st.columns(2)

    with col_29ba:
        delta_lucro = st.number_input("Total de variações na taxa de lucro:",min_value=1,step=1,value=3)

    with col_98ae:
        delta_juros = st.number_input("Total de variações na taxa de juros:",min_value=1,step=1,value=3)


    fig, ax = plt.subplots()

    annot_kws={'fontsize':8, 
               # 'fontstyle':'italic',  
               'color':"white",
               'alpha':0.6, 
               # 'rotation':"vertical",
               'verticalalignment':'center',
               # 'backgroundcolor':'w'
               }


    data = []
    if tipo_venda == options_venda[0]: # Anual
        # Sensibilidade apenas em lucro desejado

        columns = ['Lucro desejado (%)', 'Preço de venda (R$)']
        for lucro_desejado in range(int(lucro_desejado*100) - delta_lucro, int(lucro_desejado*100) + delta_lucro + 1 ):
            preco_venda, lucro = calcular_preco_venda_lucro(tipo_venda, aplicacao_lucro, preco_compra, total_tributos, lucro_desejado/100, taxa_juros)
            data.append(( f'{lucro_desejado}%', preco_venda))
    
        df = pd.DataFrame(data, columns=columns)
        df.set_index('Lucro desejado (%)', inplace=True)    

        sns.heatmap(df, annot = True, fmt='.2f', linewidths=1, cbar=False, annot_kws= annot_kws, cmap="rocket_r", ax=ax)
        st.pyplot(fig)


    elif tipo_venda == options_venda[1]: # Mensal
        # Sensibilidade bidimensional (lucro x juros)

        index = [lucro_desejado for lucro_desejado in np.arange( lucro_desejado * 100 - delta_lucro, lucro_desejado * 100 + delta_lucro + 1 )]
        columns = [taxa for taxa in np.arange( taxa_juros * 100 - delta_juros, taxa_juros * 100 + delta_juros + 1, 1)]

        data = {}

        for ld in index:
            for tj in columns:
                lucro_desejado = float(ld)
                taxa_juros = float(tj)

                preco_venda, lucro = calcular_preco_venda_lucro(tipo_venda, aplicacao_lucro, preco_compra, total_tributos, lucro_desejado/100, taxa_juros/100)
                
                if tj not in data.keys():
                    data[tj] = [] 

                data[tj].append(preco_venda)

        df = pd.DataFrame(data=data, index=index, columns=columns)

        sns.heatmap(df, annot = True, fmt='.2f', linewidths=1, cbar=False, annot_kws= annot_kws, cmap="rocket_r", ax=ax)
        ax.set_title('Preço de venda mensal com variações \nna taxas de juros e lucro desejado')
        ax.set_xlabel('Taxa de juros (%)')
        ax.set_ylabel('Lucro desejado (%)')

        # Destaque visual na célula central (cenário base)
        nrows, ncols = df.shape
        center_row = nrows // 2
        center_col = ncols // 2

        # Rectangle(x, y, largura, altura)
        rect = patches.Rectangle(
            (center_col, center_row), 1, 1,  # posição + tamanho
            fill=False, edgecolor="blue", linewidth=2
        )
        ax.add_patch(rect)
        
        st.pyplot(fig)



# with st.expander("ℹ️ Cálculo do custo do capital"):
if st.checkbox("Cálculo do custo do capital"):
    # Exibe tabela mês a mês com juros sobre saldo devedor e acumulados

    total_meses = 12  # horizonte anual
    gen = calculo_taxa_juros( preco_compra, selic, total_meses)

    columns = ['Mês', 'Valor financiado no mês', 'Juros sobre saldo devedor', 'Rendimentos acumulados']
    data = []
    for i in range(1, total_meses + 1):
        mes, saldo_devedor, juros_sobre_saldo_devedor, rendimentos_acumulados = next(gen)
        data.append( (mes, f'{saldo_devedor:,.2f}', f'{juros_sobre_saldo_devedor:,.2f}', f'{rendimentos_acumulados:,.2f}') )

    df = pd.DataFrame(data, columns=columns)
    df.set_index('Mês', inplace=True)

    st.dataframe(df)



# with st.expander("ℹ️ Detalhamento dos tributos"):
if st.checkbox("Detalhamento dos tributos"):
    st.markdown("""
    - **PIS** (cumulativo): 0,65% sobre o faturamento bruto.
    - **COFINS** (cumulativo): 3,00% sobre o faturamento bruto.
    - **IRPJ** (Lucro Presumido): 4,80%, sendo 15% sobre a base presumida ou (15% x 32% = 4,80%) sobre o faturamento bruto.
    - **Adicional de IRPJ**: 3,20%, sendo 10% sobre a base presumida ou (10% x 32% = 3,20%) sobre o faturamento bruto sobre o que exceder R$ 20.000/mês de base   
    - **CSLL**: 2,88% sobre a base presumida.
    - **ISS** (SP – software/serviço) 2,90% sobre o faturamento bruto.

    **Total: 17,43%**
    """)


