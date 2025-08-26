"""
Main Streamlit application for resale price calculator.
"""
import streamlit as st

from constants import EFFECTIVE_TAX_RATE
from domain.pricing import calculate_sale_price
from ui.components import (
    render_inputs, render_sensitivity_analysis, 
    render_capital_cost_table, render_tax_details
)


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(page_title="Calculadora de Preço de Venda", layout="centered")

    # Render inputs and get values
    (
        profit_application, sale_type, purchase_price, selic_rate,
        profit_rate, interest_rate, seller_margin
    ) = render_inputs()

    # Main calculation
    try:
        sale_price, net_profit = calculate_sale_price(
            sale_type, profit_application, purchase_price, EFFECTIVE_TAX_RATE,
            profit_rate, interest_rate
        )

        # Display results
        st.success(f"💰 Preço de venda **{sale_type.lower()}** sugerido: R$ {sale_price:,.2f}")
        st.success(f"💰 Margem do vendedor ({seller_margin*100:,.2f}%): R$ {net_profit * seller_margin:,.2f}")

    except ValueError as e:
        st.error(f"Erro no cálculo: {e}")
        return

    # Additional features
    render_sensitivity_analysis(
        sale_type, profit_application, purchase_price, EFFECTIVE_TAX_RATE,
        profit_rate, interest_rate
    )

    render_capital_cost_table(purchase_price, selic_rate)

    render_tax_details()


if __name__ == "__main__":
    main()


