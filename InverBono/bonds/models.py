from django.db import models

class Bond(models.Model):
    name = models.CharField(max_length=100, default="Bono #1")
    nominal_value = models.DecimalField(max_digits=20, decimal_places=2)
    commercial_value = models.DecimalField(max_digits=20, decimal_places=2)
    issue_date = models.DateField()
    years_number = models.DecimalField(max_digits=2, decimal_places=2)
    coupon_frequency = models.CharField(max_length=20, choices=[
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('cuatrimestral', 'Cuatrimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ])
    interest_rate_type = models.CharField(max_length=10, choices=[
        ('efectiva', 'Efectiva'),
        ('nominal', 'Nominal'),
    ])
    capitalization = models.CharField(max_length=20, choices=[
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('cuatrimestral', 'Cuatrimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    annual_discount_rate = models.DecimalField(max_digits=5, decimal_places=2)
    income_tax = models.DecimalField(max_digits=5, decimal_places=2)
    premium_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    structuring_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    placement_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    float_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cavali_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
