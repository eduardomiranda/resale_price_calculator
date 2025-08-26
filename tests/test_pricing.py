"""
Tests for pricing domain logic.
"""
import pytest
from domain.pricing import (
    calculate_sale_price,
    iterate_interest_costs,
    minimum_acceptable_interest,
    InterestStep,
)


class TestCalculateSalePrice:
    """Test cases for sale price calculation."""

    def test_annual_profit_on_purchase(self):
        """Test annual sale with profit applied on purchase."""
        sale_price, net_profit = calculate_sale_price(
            "Anual", "Aplicado na compra", 100.0, 0.1743, 0.20, 0.12
        )
        assert sale_price > 100.0
        assert net_profit > 0

    def test_annual_profit_on_sale(self):
        """Test annual sale with profit applied on sale."""
        sale_price, net_profit = calculate_sale_price(
            "Anual", "Aplicado na venda", 100.0, 0.1743, 0.20, 0.12
        )
        assert sale_price > 100.0
        assert net_profit > 0

    def test_monthly_profit_on_purchase(self):
        """Test monthly sale with profit applied on purchase."""
        sale_price, net_profit = calculate_sale_price(
            "Mensal", "Aplicado na compra", 100.0, 0.1743, 0.20, 0.12
        )
        assert sale_price > 0
        assert net_profit > 0

    def test_monthly_profit_on_sale(self):
        """Test monthly sale with profit applied on sale."""
        sale_price, net_profit = calculate_sale_price(
            "Mensal", "Aplicado na venda", 100.0, 0.1743, 0.20, 0.12
        )
        assert sale_price > 0
        assert net_profit > 0

    def test_zero_purchase_price_raises_error(self):
        """Test that zero purchase price raises ValueError."""
        with pytest.raises(ValueError, match="purchase_price must be > 0"):
            calculate_sale_price("Anual", "Aplicado na compra", 0.0, 0.1743, 0.20, 0.12)

    def test_negative_purchase_price_raises_error(self):
        """Test that negative purchase price raises ValueError."""
        with pytest.raises(ValueError, match="purchase_price must be > 0"):
            calculate_sale_price("Anual", "Aplicado na compra", -100.0, 0.1743, 0.20, 0.12)

    def test_invalid_tax_rate_raises_error(self):
        """Test that invalid tax rate raises ValueError."""
        with pytest.raises(ValueError, match="tax_rate must be in range"):
            calculate_sale_price("Anual", "Aplicado na compra", 100.0, 1.5, 0.20, 0.12)

    def test_invalid_profit_rate_raises_error(self):
        """Test that invalid profit rate raises ValueError."""
        with pytest.raises(ValueError, match="profit_rate must be in range"):
            calculate_sale_price("Anual", "Aplicado na compra", 100.0, 0.1743, 1.5, 0.12)

    def test_negative_interest_rate_raises_error(self):
        """Test that negative interest rate raises ValueError."""
        with pytest.raises(ValueError, match="interest_rate must be >= 0"):
            calculate_sale_price("Anual", "Aplicado na compra", 100.0, 0.1743, 0.20, -0.12)

    def test_tax_rate_100_percent_raises_error(self):
        """Test that 100% tax rate raises ValueError."""
        with pytest.raises(ValueError, match="tax_rate makes calculation impossible"):
            calculate_sale_price("Anual", "Aplicado na compra", 100.0, 1.0, 0.20, 0.12)

    def test_profit_plus_tax_100_percent_raises_error(self):
        """Test that profit + tax >= 100% raises ValueError for sale application."""
        with pytest.raises(ValueError, match="profit_rate \\+ tax_rate makes calculation impossible"):
            calculate_sale_price("Anual", "Aplicado na venda", 100.0, 0.1743, 0.85, 0.12)

    def test_invalid_sale_type_raises_error(self):
        """Test that invalid sale type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid sale_type"):
            calculate_sale_price("Invalid", "Aplicado na compra", 100.0, 0.1743, 0.20, 0.12)

    def test_invalid_profit_application_raises_error(self):
        """Test that invalid profit application raises ValueError."""
        with pytest.raises(ValueError, match="Invalid profit_application"):
            calculate_sale_price("Anual", "Invalid", 100.0, 0.1743, 0.20, 0.12)

    def test_monotonicity_profit_rate(self):
        """Test that increasing profit rate increases sale price."""
        price1, _ = calculate_sale_price("Anual", "Aplicado na compra", 100.0, 0.1743, 0.10, 0.12)
        price2, _ = calculate_sale_price("Anual", "Aplicado na compra", 100.0, 0.1743, 0.20, 0.12)
        assert price2 > price1

    def test_monotonicity_interest_rate(self):
        """Test that increasing interest rate increases monthly sale price."""
        price1, _ = calculate_sale_price("Mensal", "Aplicado na compra", 100.0, 0.1743, 0.20, 0.10)
        price2, _ = calculate_sale_price("Mensal", "Aplicado na compra", 100.0, 0.1743, 0.20, 0.12)
        assert price2 > price1


class TestIterateInterestCosts:
    """Test cases for interest cost iteration."""

    def test_basic_iteration(self):
        """Test basic interest cost iteration."""
        steps = list(iterate_interest_costs(1000.0, 0.15, 12))
        assert len(steps) == 12
        assert all(isinstance(step, InterestStep) for step in steps)

    def test_first_step_values(self):
        """Test first step has correct values."""
        steps = list(iterate_interest_costs(1000.0, 0.15, 12))
        first = steps[0]
        assert first.month == 1
        assert first.outstanding_balance == 1000.0
        assert first.monthly_interest > 0
        assert first.cumulative_interest == first.monthly_interest

    def test_last_step_values(self):
        """Test last step has correct values."""
        steps = list(iterate_interest_costs(1000.0, 12))
        last = steps[-1]
        assert last.month == 12
        assert last.outstanding_balance == 1000.0 / 12  # Last payment
        assert last.cumulative_interest > 0

    def test_zero_purchase_price_raises_error(self):
        """Test that zero purchase price raises ValueError."""
        with pytest.raises(ValueError, match="purchase_price must be > 0"):
            list(iterate_interest_costs(0.0, 0.15, 12))

    def test_negative_purchase_price_raises_error(self):
        """Test that negative purchase price raises ValueError."""
        with pytest.raises(ValueError, match="purchase_price must be > 0"):
            list(iterate_interest_costs(-1000.0, 0.15, 12))

    def test_zero_months_raises_error(self):
        """Test that zero months raises ValueError."""
        with pytest.raises(ValueError, match="total_months must be >= 1"):
            list(iterate_interest_costs(1000.0, 0.15, 0))

    def test_negative_months_raises_error(self):
        """Test that negative months raises ValueError."""
        with pytest.raises(ValueError, match="total_months must be >= 1"):
            list(iterate_interest_costs(1000.0, 0.15, -12))

    def test_negative_selic_raises_error(self):
        """Test that negative SELIC rate raises ValueError."""
        with pytest.raises(ValueError, match="selic_rate must be >= 0"):
            list(iterate_interest_costs(1000.0, -0.15, 12))

    def test_zero_selic_rate(self):
        """Test that zero SELIC rate works correctly."""
        steps = list(iterate_interest_costs(1000.0, 0.0, 12))
        assert all(step.monthly_interest == 0.0 for step in steps)
        assert all(step.cumulative_interest == 0.0 for step in steps)


class TestMinimumAcceptableInterest:
    """Test cases for minimum acceptable interest calculation."""

    def test_basic_calculation(self):
        """Test basic minimum interest calculation."""
        min_rate = minimum_acceptable_interest(1000.0, 0.15, 12)
        assert min_rate > 0
        assert isinstance(min_rate, float)

    def test_zero_selic_rate(self):
        """Test minimum interest with zero SELIC rate."""
        min_rate = minimum_acceptable_interest(1000.0, 0.0, 12)
        assert min_rate == 0.0

    def test_caching_works(self):
        """Test that caching works correctly."""
        # First call
        rate1 = minimum_acceptable_interest(1000.0, 0.15, 12)
        # Second call with same parameters
        rate2 = minimum_acceptable_interest(1000.0, 0.15, 12)
        assert rate1 == rate2

    def test_different_parameters_give_different_results(self):
        """Test that different parameters give different results."""
        rate1 = minimum_acceptable_interest(1000.0, 0.15, 12)
        rate2 = minimum_acceptable_interest(1000.0, 0.20, 12)
        assert rate1 != rate2
