from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

class Bond(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bonds', null=True, blank=True)
    name = models.CharField(max_length=100, default="Bono #1")
    nominal_value = models.DecimalField(max_digits=20, decimal_places=2)
    commercial_value = models.DecimalField(max_digits=20, decimal_places=2)
    issue_date = models.DateField()
    years_number = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
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
    premium_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    structuring_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    placement_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    float_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    cavali_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    
    structuring_type = models.CharField(max_length=10, choices=[('emisor', 'Emisor'), ('bonista', 'Bonista'), ('ambos', 'Ambos')], default='emisor')
    placement_type = models.CharField(max_length=10, choices=[('emisor', 'Emisor'), ('bonista', 'Bonista'), ('ambos', 'Ambos')], default='emisor')
    float_type = models.CharField(max_length=10, choices=[('emisor', 'Emisor'), ('bonista', 'Bonista'), ('ambos', 'Ambos')], default='emisor')
    cavali_type = models.CharField(max_length=10, choices=[('emisor', 'Emisor'), ('bonista', 'Bonista'), ('ambos', 'Ambos')], default='emisor')
    
    # tcea_emisor calculada
    tcea_emisor = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    # tcea_emisor_escudo calculada
    tcea_emisor_escudo = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    # trea_bonista calculada
    trea_bonista = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    # duracion calculada
    duracion = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    # convexidad calculada
    convexidad = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    # total (duracion+convexidad) calculada
    total = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    # duracion_modificada calculada
    duracion_modificada = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    # precio_actual calculada
    precio_actual = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # utilidad calculada
    utilidad = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # issuer_initial_cost calculada
    issuer_initial_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # bondholder_initial_cost calculada
    bondholder_initial_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # cok calculada
    cok = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    # effective_annual_rate calculada
    effective_annual_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    # effective_coupon_rate calculada
    effective_coupon_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    # capitalization_days calculada
    capitalization_days = models.IntegerField(null=True, blank=True)
    # total_periods calculada
    total_periods = models.IntegerField(null=True, blank=True)
    # coupon_frequency_days calculada
    coupon_frequency_days = models.IntegerField(null=True, blank=True)
    # periods_per_year calculada
    periods_per_year = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def clean(self):
        decimal_fields = [
            'nominal_value', 'commercial_value', 'years_number', 'interest_rate', 'annual_discount_rate', 'income_tax',
            'premium_percentage', 'structuring_percentage', 'placement_percentage', 'float_percentage', 'cavali_percentage',
            'tcea_emisor', 'tcea_emisor_escudo', 'trea_bonista', 'duracion', 'convexidad', 'total', 'duracion_modificada',
            'precio_actual', 'utilidad', 'issuer_initial_cost', 'bondholder_initial_cost', 'cok', 'effective_annual_rate',
            'effective_coupon_rate', 'periods_per_year'
        ]
        for field in decimal_fields:
            val = getattr(self, field, None)
            if val in (None, '', ' '):
                setattr(self, field, Decimal('0'))
            else:
                try:
                    setattr(self, field, Decimal(str(val)))
                except (InvalidOperation, TypeError, ValueError):
                    setattr(self, field, Decimal('0'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


