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
        self.assertEqual(result, self.bond.interest_rate / Decimal('100'))

    # tasa efectiva periodo
    def test_get_effective_rate_by_coupon_frequency(self):
        result = calculations.get_effective_rate_by_coupon_frequency(self.bond.interest_rate / Decimal('100'), self.bond.coupon_frequency)
        expected = (Decimal('1') + self.bond.interest_rate / Decimal('100')) ** (Decimal('180')/Decimal('360')) - Decimal('1')
        self.assertAlmostEqual(result, expected)

    # COK periodo 
    def test_get_cok(self):
        result = calculations.get_cok(self.bond.annual_discount_rate / Decimal('100'))
        expected = (Decimal('1') + self.bond.annual_discount_rate / Decimal('100')) ** (Decimal('180')/Decimal('360')) - Decimal('1')
        self.assertAlmostEqual(result, expected)

    # costes iniciales emisor
    def test_get_issuer_initial_cost(self):
        total_percentage = sum([
            self.bond.structuring_percentage,
            self.bond.placement_percentage,
            self.bond.float_percentage,
            self.bond.cavali_percentage
        ]) / Decimal('100')
        expected = total_percentage * self.bond.commercial_value
        result = calculations.get_issuer_initial_cost(
            self.bond.commercial_value,
            structuring=self.bond.structuring_percentage / Decimal('100'),
            placement=self.bond.placement_percentage / Decimal('100'),
            floatation=self.bond.float_percentage / Decimal('100'),
            cavali=self.bond.cavali_percentage / Decimal('100'),
        )
        self.assertAlmostEqual(result, expected)

    # coster iniciales bonista
    def test_get_bondholder_initial_cost(self):
        total_percentage = sum([
            self.bond.float_percentage,
            self.bond.cavali_percentage
        ]) / Decimal('100')
        expected = total_percentage * self.bond.commercial_value
        result = calculations.get_bondholder_initial_cost(
            self.bond.commercial_value,
            floatation=self.bond.float_percentage / Decimal('100'),
            cavali=self.bond.cavali_percentage / Decimal('100'),
        )
        self.assertAlmostEqual(result, expected)

