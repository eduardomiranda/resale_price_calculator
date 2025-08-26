# Constants for the resale price calculator application

# Time periods
ANNUAL_MONTHS = 12

# Tax rate (17.43% total effective rate)
EFFECTIVE_TAX_RATE = 0.1743

# UI options
OPTIONS_LUCRO = ("Aplicado na compra", "Aplicado na venda")
OPTIONS_VENDA = ("Anual", "Mensal")

# Default values
DEFAULT_PURCHASE_PRICE = 100.0
DEFAULT_SELIC_RATE = 15.0
DEFAULT_PROFIT_RATE = 20.0
DEFAULT_INTEREST_RATE = 12.0
DEFAULT_SELLER_MARGIN = 10.0

# UI steps
SELIC_STEP = 0.25
PROFIT_STEP = 0.5
INTEREST_STEP = 0.25
MARGIN_STEP = 0.25

# Sensitivity analysis defaults
DEFAULT_PROFIT_DELTA = 3
DEFAULT_INTEREST_DELTA = 3

# Visualization
HEATMAP_CMAP = "rocket_r"
HEATMAP_ANNOT_KWS = {
    'fontsize': 8,
    'color': "white",
    'alpha': 0.6,
    'verticalalignment': 'center',
}
