from decimal import Decimal
from datetime import date
from django.test import TestCase
from bonds.models import Bond
from bonds import calculations

class BondCalculationsTest(TestCase):

    def setUp(self):
        self.bond = Bond.objects.create(
            name="Bono Excel Test",
            nominal_value=Decimal('1000'),
            commercial_value=Decimal('1050'),
            issue_date=date(2022, 5, 1),
            years_number=Decimal('3'),
            coupon_frequency='semestral',
            interest_rate_type='efectiva',
            capitalization='bimestral',
            interest_rate=Decimal('9'),  # %
            annual_discount_rate=Decimal('6'),  # %
            income_tax=Decimal('30'),  # %
            premium_percentage=Decimal('1'),  # %
            structuring_percentage=Decimal('0.450'),
            placement_percentage=Decimal('0.250'),
            float_percentage=Decimal('0.150'),
            cavali_percentage=Decimal('0.500'),
        )

    # frecuencia del cupon
    def test_get_coupon_frequency_days(self):
        self.assertEqual(calculations.get_coupon_frequency_days(self.bond.coupon_frequency), 180)

    # dias de capitalizacion
    def test_get_capitalization_days(self):
        self.assertEqual(calculations.get_capitalization_days(self.bond.capitalization), 60)

    # periodos por año
    def test_get_periods_per_year(self):
        self.assertEqual(calculations.get_periods_per_year(self.bond.coupon_frequency), Decimal('2'))

    # n total de periodos
    def test_get_total_periods(self):
        self.assertEqual(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency), Decimal('6'))

    # tasa efectiva anual 
    def test_get_effective_rate(self):
        result = calculations.get_effective_rate(self.bond.interest_rate / Decimal('100'), self.bond.interest_rate_type, calculations.get_capitalization_days(self.bond.capitalization))
        self.assertEqual(result, Decimal('0.09'))  # 9,0000%

    # tasa efectiva periodo
    def test_get_effective_rate_by_coupon_frequency(self):
        result = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / Decimal('100'), self.bond.coupon_frequency)
        self.assertAlmostEqual(result, Decimal('0.04403'), places=5)  # 4,403%

    # COK periodo 
    def test_get_cok(self):
        result = calculations.get_cok(self.bond.annual_discount_rate / Decimal('100'))
        self.assertAlmostEqual(result, Decimal('0.02956'), places=5)  # 2,956%

    # costes iniciales emisor
    def test_get_issuer_initial_cost(self):
        result = calculations.get_issuer_initial_cost(
            self.bond.commercial_value,
            structuring=self.bond.structuring_percentage / Decimal('100'),
            placement=self.bond.placement_percentage / Decimal('100'),
            floatation=self.bond.float_percentage / Decimal('100'),
            cavali=self.bond.cavali_percentage / Decimal('100'),
        )
        self.assertAlmostEqual(result, Decimal('14.18'), places=2)

    # costes iniciales bonista
    def test_get_bondholder_initial_cost(self):
        result = calculations.get_bondholder_initial_cost(
            self.bond.commercial_value,
            floatation=self.bond.float_percentage / Decimal('100'),
            cavali=self.bond.cavali_percentage / Decimal('100'),
        )
        self.assertAlmostEqual(result, Decimal('6.83'), places=2)

    # precio actual
    def test_get_current_price(self):
        """Test the calculation of bond current price using get_bond_current_price with setup data."""
        discount_rate = calculations.get_cok(self.bond.annual_discount_rate / 100)
        nominal_value = self.bond.nominal_value
        coupon_rate = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / 100, self.bond.coupon_frequency)
        periods = int(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency))

        coupon_payment = nominal_value * coupon_rate
        premium_amount = nominal_value * (self.bond.premium_percentage / 100)

        final_payment = nominal_value + premium_amount + coupon_payment
        
        result = calculations.get_current_price(
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            final_payment
        )
        self.assertAlmostEqual(result, Decimal('1086.88'), places=2)

    # utlidad / perdida
    def test_get_profit_or_loss(self):
        """Test the calculation of bond profit/loss using get_bond_profit_or_loss with setup data."""
        discount_rate = calculations.get_cok(self.bond.annual_discount_rate / 100)
        nominal_value = self.bond.nominal_value
        coupon_rate = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / 100, self.bond.coupon_frequency)
        periods = int(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency))
        
        initial_cost_bond = calculations.get_bondholder_initial_cost(
            self.bond.commercial_value,
            floatation=self.bond.float_percentage / 100,
            cavali=self.bond.cavali_percentage / 100,
        )
        
        initial_flow = - self.bond.commercial_value - initial_cost_bond

        coupon_payment = nominal_value * coupon_rate
        premium_amount = nominal_value * (self.bond.premium_percentage / 100)
        final_payment_with_premium = nominal_value + premium_amount + coupon_payment
        
        result = calculations.get_profit_or_loss(
            initial_flow,
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            final_payment=final_payment_with_premium
        )
        self.assertAlmostEqual(result, Decimal('30.06'), places=2)

    # duracion
    def test_get_duration(self):
        """Test Macaulay Duration calculation."""
        discount_rate = calculations.get_cok(self.bond.annual_discount_rate / 100)
        nominal_value = self.bond.nominal_value
        coupon_rate = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / 100, self.bond.coupon_frequency)
        periods = int(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency))
        result = calculations.get_duration(
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            self.bond.coupon_frequency,
            premium_percentage=self.bond.premium_percentage
        )
        self.assertAlmostEqual(result, Decimal('2.72'), places=2)

    # convexidad
    def test_get_convexity(self):
        """Test Convexity calculation."""
        discount_rate = calculations.get_cok(self.bond.annual_discount_rate / 100)
        nominal_value = self.bond.nominal_value
        coupon_rate = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / 100, self.bond.coupon_frequency)
        periods = int(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency))
        result = calculations.get_convexity(
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            self.bond.coupon_frequency,
            premium_percentage=self.bond.premium_percentage
        )
        self.assertAlmostEqual(result, Decimal('8.66'), places=2)

    # duracion modificada
    def test_get_modified_duration(self):
        """Test Modified Duration calculation."""
        discount_rate = calculations.get_cok(self.bond.annual_discount_rate / 100)
        nominal_value = self.bond.nominal_value
        coupon_rate = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / 100, self.bond.coupon_frequency)
        periods = int(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency))
        duration = calculations.get_duration(
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            self.bond.coupon_frequency,
            premium_percentage=self.bond.premium_percentage
        )
        result = calculations.get_modified_duration(duration, discount_rate)
        self.assertAlmostEqual(result, Decimal('2.64'), places=2)

    # curacion + convexidad
    def test_get_total_value(self):
        """Test Total (Duration + Convexity) calculation."""
        discount_rate = calculations.get_cok(self.bond.annual_discount_rate / 100)
        nominal_value = self.bond.nominal_value
        coupon_rate = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / 100, self.bond.coupon_frequency)
        periods = int(calculations.get_total_periods(self.bond.years_number, self.bond.coupon_frequency))
        duration = calculations.get_duration(
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            self.bond.coupon_frequency,
            premium_percentage=self.bond.premium_percentage
        )
        convexity = calculations.get_convexity(
            discount_rate,
            nominal_value,
            coupon_rate,
            periods,
            self.bond.coupon_frequency,
            premium_percentage=self.bond.premium_percentage
        )
        result = calculations.get_total_value(duration, convexity)
        self.assertAlmostEqual(result, Decimal('11.38'), places=2)

