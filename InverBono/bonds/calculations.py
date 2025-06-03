from decimal import Decimal

COUPON_FREQ_DAYS = {
    'diaria': 1,
    'semanal': 7,
    'quincenal': 15,
    'mensual': 30,
    'bimestral': 60,
    'trimestral': 90,
    'cuatrimestral': 120,
    'semestral': 180,
    'anual': 360,
}

def get_coupon_frequency_days(coupon_frequency):
    """Returns the coupon frequency in days."""
    return COUPON_FREQ_DAYS.get(coupon_frequency)

def get_capitalization_days(capitalization):
    """Returns the capitalization frequency in days."""
    return COUPON_FREQ_DAYS.get(capitalization)

def get_periods_per_year(coupon_frequency):
    """Returns the number of periods per year (360 / coupon_frequency_days)."""
    days = get_coupon_frequency_days(coupon_frequency)
    if days:
        return Decimal('360') / Decimal(str(days))
    return None

def get_total_periods(years_number, coupon_frequency):
    """Returns the total number of periods (years_number * periods_per_year)."""
    periods_per_year = get_periods_per_year(coupon_frequency)
    if years_number is not None and periods_per_year is not None:
        return Decimal(str(years_number)) * periods_per_year
    return None

def get_effective_rate(rate, rate_type, capitalization_days):
    """
    Returns the effective rate depending on the rate type.
    If 'efectiva', returns the rate as is.
    If 'nominal', applies the formula:
    (1 + rate / (360 / capitalization_days)) ** (360 / capitalization_days) - 1
    All rates should be in decimal (e.g., 0.12 for 12%).
    """
    if rate is None or capitalization_days is None:
        return None
    if rate_type == 'efectiva':
        return rate
    elif rate_type == 'nominal':
        base = Decimal('1') + (rate / (Decimal('360') / Decimal(str(capitalization_days))))
        exponent = Decimal('360') / Decimal(str(capitalization_days))
        return base ** exponent - Decimal('1')
    return None

def get_effective_rate_by_coupon_frequency(effective_annual_rate, coupon_frequency):
    """
    Returns the effective rate for the coupon period, given the effective annual rate and coupon frequency.
    Formula: (1 + effective_annual_rate) ** (coupon_frequency_days / 360) - 1
    All rates should be in decimal (e.g., 0.12 for 12%).
    """
    days = get_coupon_frequency_days(coupon_frequency)
    if effective_annual_rate is None or days is None:
        return None
    return (Decimal('1') + effective_annual_rate) ** (Decimal(str(days)) / Decimal('360')) - Decimal('1')

def get_cok(annual_discount_rate):
    """
    Returns the COK: (1 + annual_discount_rate) ** (180/360) - 1
    All rates should be in decimal (e.g., 0.12 for 12%).
    """
    if annual_discount_rate is None:
        return None
    return (Decimal('1') + annual_discount_rate) ** (Decimal('180')/Decimal('360')) - Decimal('1')

def get_issuer_initial_cost(commercial_value, structuring=None, placement=None, floatation=None, cavali=None):
    """
    Returns the initial cost for the issuer: sum of all optional costs (except premium) * commercial_value
    Percentages should be in decimal (e.g., 0.01 for 1%).
    """
    total_percentage = Decimal('0')
    for val in [structuring, placement, floatation, cavali]:
        if val is not None:
            total_percentage += val
    if commercial_value is not None:
        return total_percentage * commercial_value
    return None

def get_bondholder_initial_cost(commercial_value, floatation=None, cavali=None):
    """
    Returns the initial cost for the bondholder: only floatation and cavali * commercial_value
    Percentages should be in decimal (e.g., 0.01 for 1%).
    """
    total_percentage = Decimal('0')
    for val in [floatation, cavali]:
        if val is not None:
            total_percentage += val
    if commercial_value is not None:
        return total_percentage * commercial_value
    return None


# Ejemplo de uso:
# cupon = calcular_cupon_anual(bond.nominal_value, bond.interest_rate)
# total_gastos = calcular_valor_total_gastos(bond.premium_percentage, bond.structuring_percentage, ...)
