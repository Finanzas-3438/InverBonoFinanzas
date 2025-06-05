from decimal import Decimal

def get_coupon_payment(nominal_value, coupon_rate):
    return nominal_value * coupon_rate

def get_premium_amount(nominal_value, premium_percentage):
    if premium_percentage is None:
        return Decimal('0')
    return nominal_value * (premium_percentage / Decimal('100'))

def get_final_payment(nominal_value, coupon_rate, premium_percentage):
    coupon = get_coupon_payment(nominal_value, coupon_rate)
    premium = get_premium_amount(nominal_value, premium_percentage)
    return nominal_value + coupon + premium

def get_cash_flows(nominal_value, coupon_rate, periods, premium_percentage=None):
    coupon = get_coupon_payment(nominal_value, coupon_rate)
    cash_flows = [coupon] * (periods - 1)
    final_payment = get_final_payment(nominal_value, coupon_rate, premium_percentage)
    cash_flows.append(final_payment)
    return cash_flows

def periodic_to_annual_rate(effective_period_rate, period_days, use_365=False):
    """Convierte una tasa efectiva de periodo a anual (360 o 365 días)."""
    days_in_year = Decimal('365') if use_365 else Decimal('360')
    return (Decimal('1') + effective_period_rate) ** (days_in_year / Decimal(str(period_days))) - Decimal('1')

def get_issuer_flows(nominal_value, coupon_rate, periods, premium_percentage=None):
    """Flujos del emisor: cupón cada periodo, último periodo incluye nominal y prima."""
    coupon = get_coupon_payment(nominal_value, coupon_rate)
    flows = [coupon] * (periods - 1)
    final_payment = get_final_payment(nominal_value, coupon_rate, premium_percentage)
    flows.append(final_payment)
    return flows

def get_issuer_flows_with_shield(nominal_value, coupon_rate, periods, premium_percentage=None, income_tax=None):
    """Flujos del emisor con escudo fiscal: cupón menos escudo cada periodo, último periodo incluye nominal y prima (escudo solo sobre cupón)."""
    coupon = get_coupon_payment(nominal_value, coupon_rate)
    shield = coupon * (income_tax / Decimal('100')) if income_tax else Decimal('0')
    flows = [(coupon - shield)] * (periods - 1)
    premium = get_premium_amount(nominal_value, premium_percentage)
    final_payment = nominal_value + premium + (coupon - shield)
    flows.append(final_payment)
    return flows

def get_bondholder_flows(nominal_value, coupon_rate, periods, premium_percentage=None):
    """Flujos del bonista: cupón cada periodo, último periodo incluye nominal y prima."""
    coupon = get_coupon_payment(nominal_value, coupon_rate)
    flows = [coupon] * (periods - 1)
    premium = get_premium_amount(nominal_value, premium_percentage)
    final_payment = nominal_value + premium + coupon
    flows.append(final_payment)
    return flows