"""
Domain logic for pricing calculations.
"""
from typing import Iterator, NamedTuple, Tuple
from functools import lru_cache
from constants import ANNUAL_MONTHS, EFFECTIVE_TAX_RATE


class InterestStep(NamedTuple):
    """Represents one step in the interest calculation."""
    month: int
    outstanding_balance: float
    monthly_interest: float
    cumulative_interest: float


def calculate_sale_price(
    sale_type: str,
    profit_application: str,
    purchase_price: float,
    tax_rate: float,
    profit_rate: float,
    interest_rate: float,
) -> Tuple[float, float]:
    """Calculate sale price and net profit after taxes.
    
    Args:
        sale_type: "Anual" or "Mensal"
        profit_application: "Aplicado na compra" or "Aplicado na venda"
        purchase_price: Base product value
        tax_rate: Effective tax rate (decimal, e.g., 0.1743)
        profit_rate: Desired margin (decimal, e.g., 0.20)
        interest_rate: Capital cost (decimal, e.g., 0.12 for 12%)
    
    Returns:
        Tuple of (sale_price, net_profit)
    
    Raises:
        ValueError: If inputs are invalid or calculations are impossible
    """
    # Input validation
    if purchase_price <= 0:
        raise ValueError("purchase_price must be > 0")
    if not (0 <= tax_rate < 1):
        raise ValueError("tax_rate must be in range [0, 1)")
    if not (0 <= profit_rate < 1):
        raise ValueError("profit_rate must be in range [0, 1)")
    if interest_rate < 0:
        raise ValueError("interest_rate must be >= 0")

    net_denominator = 1 - tax_rate
    if net_denominator <= 0:
        raise ValueError("tax_rate makes calculation impossible (>= 100%)")

    net_multiplier = 1 / net_denominator

    if sale_type == "Anual":
        if profit_application == "Aplicado na compra":
            sale_price = purchase_price * net_multiplier + (purchase_price * profit_rate * net_multiplier)
            net_profit = sale_price - (sale_price * tax_rate) - purchase_price
        elif profit_application == "Aplicado na venda":
            sale_denominator = 1 - profit_rate - tax_rate
            if sale_denominator <= 0:
                raise ValueError("profit_rate + tax_rate makes calculation impossible (>= 100%)")
            sale_price = purchase_price / sale_denominator
            net_profit = sale_price - (sale_price * tax_rate) - purchase_price
        else:
            raise ValueError(f"Invalid profit_application: {profit_application}")

    elif sale_type == "Mensal":
        if profit_application == "Aplicado na compra":
            annual_sale_price = (
                purchase_price * net_multiplier +
                (purchase_price * profit_rate * net_multiplier) +
                (purchase_price * interest_rate * net_multiplier)
            )
            sale_price = annual_sale_price / ANNUAL_MONTHS
            net_profit = annual_sale_price - (annual_sale_price * tax_rate) - (purchase_price * interest_rate) - purchase_price
        elif profit_application == "Aplicado na venda":
            sale_denominator = 1 - profit_rate - tax_rate
            if sale_denominator <= 0:
                raise ValueError("profit_rate + tax_rate makes calculation impossible (>= 100%)")
            annual_sale_price = (purchase_price / sale_denominator) + ((purchase_price * interest_rate) * net_multiplier)
            sale_price = annual_sale_price / ANNUAL_MONTHS
            net_profit = annual_sale_price - (annual_sale_price * tax_rate) - (purchase_price * interest_rate) - purchase_price
        else:
            raise ValueError(f"Invalid profit_application: {profit_application}")
    else:
        raise ValueError(f"Invalid sale_type: {sale_type}")

    return sale_price, net_profit


def iterate_interest_costs(
    purchase_price: float,
    selic_rate: float,
    total_months: int,
) -> Iterator[InterestStep]:
    """Generate month-by-month interest costs and accumulated returns.
    
    Args:
        purchase_price: Total amount to be financed
        selic_rate: Annual SELIC rate (decimal)
        total_months: Number of months to simulate
    
    Yields:
        InterestStep for each month
    """
    if purchase_price <= 0:
        raise ValueError("purchase_price must be > 0")
    if total_months < 1:
        raise ValueError("total_months must be >= 1")
    if selic_rate < 0:
        raise ValueError("selic_rate must be >= 0")

    monthly_selic = (1 + selic_rate) ** (1/12) - 1
    outstanding_balance = purchase_price
    monthly_payment = purchase_price / total_months
    cumulative_interest = 0.0

    for month in range(1, total_months + 1):
        monthly_interest = outstanding_balance * monthly_selic
        cumulative_interest += monthly_interest

        yield InterestStep(
            month=month,
            outstanding_balance=outstanding_balance,
            monthly_interest=monthly_interest,
            cumulative_interest=cumulative_interest
        )

        outstanding_balance = outstanding_balance - monthly_payment


@lru_cache(maxsize=128)
def minimum_acceptable_interest(
    purchase_price: float,
    selic_rate: float,
    total_months: int,
) -> float:
    """Calculate minimum acceptable interest rate (%) to cover capital cost.
    
    Args:
        purchase_price: Total amount to be financed
        selic_rate: Annual SELIC rate (decimal)
        total_months: Number of months to simulate
    
    Returns:
        Minimum interest rate as percentage
    """
    last_cumulative = 0.0
    for step in iterate_interest_costs(purchase_price, selic_rate, total_months):
        last_cumulative = step.cumulative_interest
    return (last_cumulative / purchase_price) * 100
