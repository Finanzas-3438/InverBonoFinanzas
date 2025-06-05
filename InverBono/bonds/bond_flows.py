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
