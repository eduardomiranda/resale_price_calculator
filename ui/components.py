"""
UI components for the resale price calculator.
"""
import streamlit as st
import pandas as pd
import numpy as np
import math
from typing import Tuple

from constants import (
    DEFAULT_PURCHASE_PRICE, DEFAULT_SELIC_RATE, DEFAULT_PROFIT_RATE,
    DEFAULT_INTEREST_RATE, DEFAULT_SELLER_MARGIN,
    SELIC_STEP, PROFIT_STEP, INTEREST_STEP, MARGIN_STEP,
    DEFAULT_PROFIT_DELTA, DEFAULT_INTEREST_DELTA,
    OPTIONS_LUCRO, OPTIONS_VENDA
)
from domain.pricing import calculate_sale_price, minimum_acceptable_interest, iterate_interest_costs


def render_inputs(is_admin: bool) -> Tuple[str, str, float, float, float, float, float]:
    """Render all input widgets and return their values.
    
    Returns:
        Tuple of (profit_application, sale_type, purchase_price, selic_rate, 
                 profit_rate, interest_rate, seller_margin)
    """
    st.title("📊 Calculadora de Preço de Venda")
    # Streamlit emoji shortcodes
    # https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
    st.badge(" Calculadora utilizada para o cenário de **compra local** e **venda local**!", icon="🚨", color="red")


    if is_admin:
        # Selection columns
        col_profit, col_sale = st.columns(2)
        with col_profit:
                profit_application = st.pills(
                "Seleciona onde a margem de venda será aplicada:",
                options=OPTIONS_LUCRO,
                selection_mode="single",
                default=OPTIONS_LUCRO[1]
            )

        with col_sale:
                sale_type = st.pills(
                "Seleciona o modelo de venda:",
                options=OPTIONS_VENDA,
                selection_mode="single",
                default=OPTIONS_VENDA[0]
            )
    else: 
        profit_application = OPTIONS_LUCRO[1]

        sale_type = st.pills(
            "Seleciona o modelo de venda:",
            options=OPTIONS_VENDA,
            selection_mode="single",
            default=OPTIONS_VENDA[0]
        )


    # Purchase price input
    purchase_price = st.number_input(
        "Custo de compra em reais (R$):",
        min_value=0.0,
        value=DEFAULT_PURCHASE_PRICE,
        format="%.2f"
    )

    # Parameter inputs
    # col_selic, col_profit_rate, col_interest, col_margin = st.columns(4)
    col_selic, col_profit_rate, col_margin = st.columns(3)

    with col_selic:
        selic_rate = st.number_input(
            "Taxa Selic atual (%):",
            min_value=0.0,
            step=SELIC_STEP,
            value=DEFAULT_SELIC_RATE,
            format="%.2f"
        ) / 100  # Convert to decimal

    with col_profit_rate:
        profit_rate = st.number_input(
            "Margem de venda (%):",
            min_value=0.0,
            step=PROFIT_STEP,
            value=DEFAULT_PROFIT_RATE,
            format="%.2f"
        ) / 100  # Convert to decimal

    # with col_interest:
    #     min_interest_pct = minimum_acceptable_interest(purchase_price, selic_rate, 12)
    #     default_interest_pct = max(DEFAULT_INTEREST_RATE, min_interest_pct)
    #     interest_rate = st.number_input(
    #         "Taxa de juros (%):",
    #         min_value=min_interest_pct,
    #         step=INTEREST_STEP,
    #         value=default_interest_pct,
    #         format="%.2f"
    #     ) / 100  # Convert to decimal

    with col_margin:
        seller_margin = st.number_input(
            "Margem de comissão (%):",
            min_value=0.0,
            step=MARGIN_STEP,
            value=DEFAULT_SELLER_MARGIN,
            format="%.2f"
        ) / 100  # Convert to decimal

    min_interest_pct = minimum_acceptable_interest(purchase_price, selic_rate, 12)
    interest_rate = math.ceil(min_interest_pct)/100

    return profit_application, sale_type, purchase_price, selic_rate, profit_rate, interest_rate, seller_margin


def render_sensitivity_analysis(
    sale_type: str,
    profit_application: str,
    purchase_price: float,
    tax_rate: float,
    profit_rate: float,
    interest_rate: float,
) -> None:
    """Render sensitivity analysis heatmap."""
    with st.expander("Calcular variações na margem de venda"):
        profit_delta = st.number_input(
            "Total de variações na margem de venda?",
            min_value=1,
            step=1,
            value=DEFAULT_PROFIT_DELTA
        )

        render_annual_sensitivity(
            profit_application, purchase_price, tax_rate, profit_rate, 
            interest_rate, profit_delta
        )


def render_annual_sensitivity(
    profit_application: str,
    purchase_price: float,
    tax_rate: float,
    profit_rate: float,
    interest_rate: float,
    profit_delta: int,
) -> None:
    """Render annual sensitivity heatmap (profit rate only)."""
    import matplotlib.pyplot as plt
    import seaborn as sns
    from constants import HEATMAP_CMAP, HEATMAP_ANNOT_KWS

    fig, ax = plt.subplots()

    base_profit_pct = int(profit_rate * 100)
    data = []
    
    for candidate_profit_pct in range(base_profit_pct - profit_delta, base_profit_pct + profit_delta + 1):
        try:
            sale_price, _, _ = calculate_sale_price(
                "Anual", profit_application, purchase_price, tax_rate,
                candidate_profit_pct / 100, interest_rate
            )
            data.append((f'{candidate_profit_pct}%', sale_price))
        except ValueError:
            # Skip invalid combinations
            continue

    if data:
        df = pd.DataFrame(data, columns=['Margem de venda (%)', 'Preço de venda (R$)'])
        df.set_index('Margem de venda (%)', inplace=True)

        sns.heatmap(
            df, annot=True, fmt='.2f', linewidths=1, cbar=False,
            annot_kws=HEATMAP_ANNOT_KWS, cmap=HEATMAP_CMAP, ax=ax
        )
        st.pyplot(fig)


# def render_monthly_sensitivity(
#     profit_application: str,
#     purchase_price: float,
#     tax_rate: float,
#     profit_rate: float,
#     interest_rate: float,
#     profit_delta: int,
#     interest_delta: int,
# ) -> None:
#     """Render monthly sensitivity heatmap (profit rate x interest rate)."""
#     import matplotlib.pyplot as plt
#     import matplotlib.patches as patches
#     import seaborn as sns
#     from constants import HEATMAP_CMAP, HEATMAP_ANNOT_KWS

#     fig, ax = plt.subplots()

#     base_profit_pct = profit_rate * 100
#     base_interest_pct = interest_rate * 100
    
#     profit_range = np.arange(base_profit_pct - profit_delta, base_profit_pct + profit_delta + 1)
#     interest_range = np.arange(base_interest_pct - interest_delta, base_interest_pct + interest_delta + 1, 1)

#     data = {}
#     for profit_pct in profit_range:
#         for interest_pct in interest_range:
#             try:
#                 candidate_profit = float(profit_pct) / 100
#                 candidate_interest = float(interest_pct) / 100

#                 sale_price, _ = calculate_sale_price(
#                     "Mensal", profit_application, purchase_price, tax_rate,
#                     candidate_profit, candidate_interest
#                 )

#                 if interest_pct not in data:
#                     data[interest_pct] = []
#                 data[interest_pct].append(sale_price)
#             except ValueError:
#                 # Skip invalid combinations
#                 if interest_pct not in data:
#                     data[interest_pct] = []
#                 data[interest_pct].append(np.nan)

#     if data:
#         df = pd.DataFrame(data=data, index=profit_range, columns=interest_range)

#         sns.heatmap(
#             df, annot=True, fmt='.2f', linewidths=1, cbar=False,
#             annot_kws=HEATMAP_ANNOT_KWS, cmap=HEATMAP_CMAP, ax=ax
#         )
        
#         ax.set_title('Preço de venda mensal com variações \nna taxas de juros e lucro desejado')
#         ax.set_xlabel('Taxa de juros (%)')
#         ax.set_ylabel('Lucro desejado (%)')

#         # Highlight center cell
#         nrows, ncols = df.shape
#         center_row = nrows // 2
#         center_col = ncols // 2

#         rect = patches.Rectangle(
#             (center_col, center_row), 1, 1,
#             fill=False, edgecolor="blue", linewidth=2
#         )
#         ax.add_patch(rect)

#         st.pyplot(fig)


def render_capital_cost_table(
    purchase_price: float,
    selic_rate: float,
    total_months: int = 12,
) -> None:
    """Render capital cost calculation table."""
    with st.expander("Cálculo do custo do capital"):

        columns = ['Mês', 'Valor financiado no mês', 'Juros sobre saldo devedor', 'Rendimentos acumulados']
        data = []

        rendimento_acumulado = 0.0
        
        for step in iterate_interest_costs(purchase_price, selic_rate, total_months):
            data.append((
                step.month,
                f'{step.outstanding_balance:,.2f}',
                f'{step.monthly_interest:,.2f}',
                f'{step.cumulative_interest:,.2f}'
            ))
            rendimento_acumulado = step.cumulative_interest

        df = pd.DataFrame(data, columns=columns)
        df.set_index('Mês', inplace=True)
        
        custo_capital = rendimento_acumulado / purchase_price * 100
        st.markdown(f'O custo do capital no período de {total_months} meses foi de **{custo_capital:,.5f}%**')

        st.dataframe(df)


def render_tax_details() -> None:
    """Render tax breakdown information."""
    with st.expander("Detalhamento dos tributos"):
        st.markdown("""
        **PIS** (cumulativo): 0,65% sobre o faturamento bruto.
        \n\n**COFINS** (cumulativo): 3,00% sobre o faturamento bruto.
        \n\n**IRPJ** (Lucro Presumido): 4,80%, sendo 15% sobre a base presumida ou (15% x 32% = 4,80%) sobre o faturamento bruto.
        \n\n**Adicional de IRPJ**: 3,20%, sendo 10% sobre a base presumida ou (10% x 32% = 3,20%) sobre o faturamento bruto sobre o que exceder R$ 20.000/mês de base   
        \n\n**CSLL**: 2,88% sobre a base presumida.
        \n\n**ISS** (SP – software/serviço) 2,90% sobre o faturamento bruto.
        \n\n
        \n\n**Total: 17,43%**
        """)


def render_sales_price_calculations_details(sale_price_txt) -> None:

    with st.expander("Detalhar cálculos do preço de vendas"):
        st.markdown(sale_price_txt)