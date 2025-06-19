# filepath: c:\Users\Augusto\Desktop\UPC\Septimo-Ciclo\Finanzas\InverBonoFinanzas\InverBono\bonds\calculations.py
from decimal import Decimal
from typing import Optional

from .bond_flows import (
    get_coupon_payment,
    get_final_payment,
    get_issuer_flows,
    get_issuer_flows_with_shield,
    get_bondholder_flows,
    get_cash_flows,
    periodic_to_annual_rate,
)

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

def get_cok(annual_discount_rate, coupon_frequency=None):
    """
    Returns the COK: (1 + annual_discount_rate) ** (coupon_frequency_days/360) - 1
    All rates should be in decimal (e.g., 0.12 for 12%).
    If coupon_frequency is None, defaults to 180 días (semestral, para compatibilidad).
    """
    if annual_discount_rate is None:
        return None
    if coupon_frequency is not None:
        days = get_coupon_frequency_days(coupon_frequency)
        if days is None:
            days = 180
    else:
        days = 180
    return (Decimal('1') + annual_discount_rate) ** (Decimal(str(days))/Decimal('360')) - Decimal('1')

def get_issuer_initial_cost(commercial_value, structuring=None, structuring_type='emisor', placement=None, placement_type='emisor', floatation=None, float_type='emisor', cavali=None, cavali_type='emisor'):
    """
    Returns the initial cost for the issuer based on cost types.
    Percentages should be in percent (e.g., 0.45 for 0.45%) and will be divided by 100.
    """
    total_percentage = Decimal('0')
    if structuring_type in ['emisor', 'ambos'] and structuring is not None:
        total_percentage += structuring / Decimal('100')
    if placement_type in ['emisor', 'ambos'] and placement is not None:
        total_percentage += placement / Decimal('100')
    if float_type in ['emisor', 'ambos'] and floatation is not None:
        total_percentage += floatation / Decimal('100')
    if cavali_type in ['emisor', 'ambos'] and cavali is not None:
        total_percentage += cavali / Decimal('100')
    if commercial_value is not None:
        return total_percentage * commercial_value
    return None

def get_bondholder_initial_cost(commercial_value, structuring=None, structuring_type='emisor', placement=None, placement_type='emisor', floatation=None, float_type='emisor', cavali=None, cavali_type='emisor'):
    """
    Returns the initial cost for the bondholder based on cost types.
    Percentages should be in percent (e.g., 0.45 for 0.45%) and will be divided by 100.
    """
    total_percentage = Decimal('0')
    if structuring_type in ['bonista', 'ambos'] and structuring is not None:
        total_percentage += structuring / Decimal('100')
    if placement_type in ['bonista', 'ambos'] and placement is not None:
        total_percentage += placement / Decimal('100')
    if float_type in ['bonista', 'ambos'] and floatation is not None:
        total_percentage += floatation / Decimal('100')
    if cavali_type in ['bonista', 'ambos'] and cavali is not None:
        total_percentage += cavali / Decimal('100')
    if commercial_value is not None:
        return total_percentage * commercial_value
    return None

def get_current_price(discount_rate, nominal_value, coupon_rate, periods, premium_percentage=None):
    """Calculate the current price of a bond."""
    periods = int(periods)
    cash_flows = get_cash_flows(nominal_value, coupon_rate, periods, premium_percentage)
    npv = sum(cf / (Decimal('1') + discount_rate) ** (i + 1) for i, cf in enumerate(cash_flows))
    return npv

def get_profit_or_loss(initial_flow, discount_rate, nominal_value, coupon_rate, periods, premium_percentage=None):
    """Calculate profit or loss from bond investment."""
    price = get_current_price(discount_rate, nominal_value, coupon_rate, periods, premium_percentage)
    return initial_flow + price

def get_duration(discount_rate, nominal_value, coupon_rate, periods, coupon_frequency, premium_percentage=None):
    """Calculates the Macaulay Duration of a bond in years."""
    periods_per_year = get_periods_per_year(coupon_frequency)
    if periods_per_year is None or periods_per_year == Decimal('0'):
        return None
    cash_flows = get_cash_flows(nominal_value, coupon_rate, periods, premium_percentage)
    bond_price = get_current_price(discount_rate, nominal_value, coupon_rate, periods, premium_percentage=premium_percentage)
    if bond_price is None or bond_price == Decimal('0') or discount_rate is None:
        return None
    
    weighted_pv_sum = Decimal('0')
    one_plus_dr = Decimal('1') + discount_rate
    for i, cf in enumerate(cash_flows):
        t = Decimal(i + 1)
        weighted_pv_sum += t * cf / (one_plus_dr ** t)
        
    duration_periods = weighted_pv_sum / bond_price
    duration_years = duration_periods / periods_per_year
    return duration_years

def get_convexity(discount_rate, nominal_value, coupon_rate, periods, coupon_frequency, premium_percentage=None):
    """
    Calculates the Convexity of a bond.
    """
    periods_per_year = get_periods_per_year(coupon_frequency)
    if periods_per_year is None or periods_per_year == Decimal('0'):
        return None
    
    cash_flows = get_cash_flows(nominal_value, coupon_rate, periods, premium_percentage)
    bond_price = get_current_price(discount_rate, nominal_value, coupon_rate, periods, premium_percentage=premium_percentage)
    if bond_price is None or bond_price == Decimal('0') or discount_rate is None:
        return None

    convexity_numerator = Decimal('0')
    one_plus_dr = Decimal('1') + discount_rate
    for i, cf in enumerate(cash_flows):
        t = Decimal(i + 1)
        convexity_numerator += cf * t * (t + 1) / (one_plus_dr ** t)
        
    convexity_periods = convexity_numerator / (bond_price * (one_plus_dr ** 2))
    convexity_years = convexity_periods / (periods_per_year ** 2)
    return convexity_years

def get_modified_duration(duration_years, discount_rate):
    """Calculates the Modified Duration of a bond in years."""
    if duration_years is None or discount_rate is None:
        return None
    one_plus_dr = Decimal('1') + discount_rate
    if one_plus_dr == Decimal('0'):
        return None
    return duration_years / one_plus_dr

def get_total_value(duration_years, convexity_years):
    """Calculates the sum of duration and convexity in years."""
    if duration_years is None or convexity_years is None:
        return None
    return duration_years + convexity_years

def tcea_issuer(initial_flow, nominal_value, coupon_rate, periods, coupon_frequency, premium_percentage=None, use_365=False):
    """Calcula la TCEA del emisor usando los flujos generados por get_issuer_flows de bond_flows."""
    from .bond_flows import get_issuer_flows
    issuer_flows = get_issuer_flows(nominal_value, coupon_rate, periods, premium_percentage)
    from decimal import Decimal, getcontext
    getcontext().prec = 12
    tol = Decimal('0.0000001')
    max_iter = 100
    low = Decimal('0.00001')
    high = Decimal('1')
    for _ in range(max_iter):
        mid = (low + high) / 2
        if mid == 0:
            low = tol
            continue
        npv = sum(cf / ((1 + mid) ** (i + 1)) for i, cf in enumerate(issuer_flows))
        if abs(npv + initial_flow) < tol:
            break
        elif npv > -initial_flow:
            low = mid
        else:
            high = mid
    else:
        mid = (low + high) / 2
    period_days = get_coupon_frequency_days(coupon_frequency)
    return periodic_to_annual_rate(mid, period_days, use_365=use_365)

def tcea_issuer_with_shield(initial_flow, nominal_value, coupon_rate, periods, coupon_frequency, premium_percentage=None, income_tax=None, use_365=False):
    """Calcula la TCEA del emisor con escudo fiscal usando los flujos generados por get_issuer_flows_with_shield de bond_flows."""
    from .bond_flows import get_issuer_flows_with_shield
    issuer_flows_with_shield = get_issuer_flows_with_shield(nominal_value, coupon_rate, periods, premium_percentage, income_tax)
    from decimal import Decimal, getcontext
    getcontext().prec = 12
    tol = Decimal('0.0000001')
    max_iter = 100
    low = Decimal('0.00001')
    high = Decimal('1')
    for _ in range(max_iter):
        mid = (low + high) / 2
        if mid == 0:
            low = tol
            continue
        npv = sum(cf / ((1 + mid) ** (i + 1)) for i, cf in enumerate(issuer_flows_with_shield))
        if abs(npv + initial_flow) < tol:
            break
        elif npv > -initial_flow:
            low = mid
        else:
            high = mid
    else:
        mid = (low + high) / 2
    period_days = get_coupon_frequency_days(coupon_frequency)
    return periodic_to_annual_rate(mid, period_days, use_365=use_365)

def trea_bondholder(initial_flow, nominal_value, coupon_rate, periods, coupon_frequency, premium_percentage=None, use_365=False):
    """Calcula la TREA del bonista usando los flujos generados por get_bondholder_flows de bond_flows."""
    from .bond_flows import get_bondholder_flows
    bondholder_flows = get_bondholder_flows(nominal_value, coupon_rate, periods, premium_percentage)
    from decimal import Decimal, getcontext
    getcontext().prec = 12
    tol = Decimal('0.0000001')
    max_iter = 100
    low = Decimal('0.00001')
    high = Decimal('1')
    for _ in range(max_iter):
        mid = (low + high) / 2
        if mid == 0:
            low = tol
            continue
        npv = sum(cf / ((1 + mid) ** (i + 1)) for i, cf in enumerate(bondholder_flows))
        if abs(npv + initial_flow) < tol: # initial_flow is negative
            break
        elif npv > -initial_flow:
            low = mid
        else:
            high = mid
    else:
        mid = (low + high) / 2
    period_days = get_coupon_frequency_days(coupon_frequency)
    return periodic_to_annual_rate(mid, period_days, use_365=use_365)

class BondOutcome:
    def __init__(self, bond):
        from . import calculations
        from .bond_flows import get_final_payment
        # Datos base
        self.bond = bond
        self.coupon_frequency_days = calculations.get_coupon_frequency_days(bond.coupon_frequency)
        self.capitalization_days = calculations.get_capitalization_days(bond.capitalization)
        self.periods_per_year = calculations.get_periods_per_year(bond.coupon_frequency)
        self.total_periods = calculations.get_total_periods(bond.years_number, bond.coupon_frequency)
        self.effective_annual_rate = calculations.get_effective_rate(
            bond.interest_rate / Decimal('100'), bond.interest_rate_type, self.capitalization_days)
        self.effective_coupon_rate = calculations.get_effective_rate_by_coupon_frequency(
            self.effective_annual_rate, bond.coupon_frequency)
        self.cok = calculations.get_cok(bond.annual_discount_rate / Decimal('100'), bond.coupon_frequency)
        
        self.issuer_initial_cost = calculations.get_issuer_initial_cost(
            bond.commercial_value,
            structuring=(bond.structuring_percentage or 0),
            structuring_type=bond.structuring_type,
            placement=(bond.placement_percentage or 0),
            placement_type=bond.placement_type,
            floatation=(bond.float_percentage or 0),
            float_type=bond.float_type,
            cavali=(bond.cavali_percentage or 0),
            cavali_type=bond.cavali_type,
        )
        self.bondholder_initial_cost = calculations.get_bondholder_initial_cost(
            bond.commercial_value,
            structuring=(bond.structuring_percentage or 0),
            structuring_type=bond.structuring_type,
            placement=(bond.placement_percentage or 0),
            placement_type=bond.placement_type,
            floatation=(bond.float_percentage or 0),
            float_type=bond.float_type,
            cavali=(bond.cavali_percentage or 0),
            cavali_type=bond.cavali_type,
        )

        # Precio actual y utilidad
        self.precio_actual = calculations.get_current_price(
            self.cok,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            premium_percentage=(bond.premium_percentage or 0)
        )
        self.utilidad = calculations.get_profit_or_loss(
            -bond.commercial_value - self.bondholder_initial_cost,
            self.cok,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            premium_percentage=(bond.premium_percentage or 0)
        )
        # Ratios de decisión
        self.duracion = calculations.get_duration(
            self.cok,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0)
        )
        self.convexidad = calculations.get_convexity(
            self.cok,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0)
        )
        self.total = calculations.get_total_value(self.duracion, self.convexidad)
        self.duracion_modificada = calculations.get_modified_duration(self.duracion, self.cok)

        # Indicadores de rentabilidad
        initial_flow_issuer = -bond.commercial_value + self.issuer_initial_cost
        self.tcea_emisor = calculations.tcea_issuer(
            initial_flow_issuer,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0),
            use_365=False
        )
        self.tcea_emisor_365 = calculations.tcea_issuer(
            initial_flow_issuer,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0),
            use_365=True
        )
        self.tcea_emisor_escudo = calculations.tcea_issuer_with_shield(
            initial_flow_issuer,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0),
            income_tax=(bond.income_tax or 0),
            use_365=False
        )
        self.tcea_emisor_escudo_365 = calculations.tcea_issuer_with_shield(
            initial_flow_issuer,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0),
            income_tax=(bond.income_tax or 0),
            use_365=True
        )
        self.trea_bonista = calculations.trea_bondholder(
            -bond.commercial_value - self.bondholder_initial_cost,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0),
            use_365=False
        )
        self.trea_bonista_365 = calculations.trea_bondholder(
            -bond.commercial_value - self.bondholder_initial_cost,
            bond.nominal_value,
            self.effective_coupon_rate,
            int(self.total_periods),
            bond.coupon_frequency,
            premium_percentage=(bond.premium_percentage or 0),
            use_365=True
        )