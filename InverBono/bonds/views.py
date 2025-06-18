from django.shortcuts import render, redirect, get_object_or_404
from .models import Bond
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from .calculations import BondOutcome
from django.core.exceptions import ValidationError

def bond_detail(request, pk):
    bond = get_object_or_404(Bond, pk=pk)
    return render(request, 'bonds/detail.html', {'bond': bond})

def truncate_decimal(value, max_digits, decimal_places):
    if value is None:
        return None
    try:
        d = Decimal(value)
    except Exception:
        return None
    # Truncar a la cantidad de decimales permitidos
    quantize_str = '1.' + ('0' * decimal_places)
    d = d.quantize(Decimal(quantize_str), rounding=ROUND_DOWN)
    # Limitar la cantidad de dígitos totales
    sign, digits, exp = d.as_tuple()
    digits = list(digits)
    if len(digits) > max_digits:
        # Quitar dígitos de la parte entera si es necesario
        extra = len(digits) - max_digits
        digits = digits[extra:]
        d = Decimal((sign, tuple(digits), exp))
    return d

def create_bond_view(request):
    error_message = None
    if request.method == 'POST':
        def parse_decimal(val, default=0):
            try:
                if val in (None, '', ' '):
                    return Decimal(default)
                return Decimal(val)
            except (InvalidOperation, TypeError, ValueError):
                return Decimal(default)

        bond_data = {
            'name': request.POST.get('name', 'Bono #1'),
            'nominal_value': parse_decimal(request.POST.get('nominal_value'), 0),
            'commercial_value': parse_decimal(request.POST.get('commercial_value'), 0),
            'issue_date': request.POST.get('issue_date'),
            'years_number': parse_decimal(request.POST.get('years_number'), 0),
            'coupon_frequency': request.POST.get('coupon_frequency'),
            'interest_rate_type': request.POST.get('interest_rate_type'),
            'capitalization': request.POST.get('capitalization'),
            'interest_rate': parse_decimal(request.POST.get('interest_rate'), 0),
            'annual_discount_rate': parse_decimal(request.POST.get('annual_discount_rate'), 0),
            'income_tax': parse_decimal(request.POST.get('income_tax'), 0),
            'premium_percentage': parse_decimal(request.POST.get('premium_percentage'), 0),
            'structuring_percentage': parse_decimal(request.POST.get('structuring_percentage'), 0),
            'placement_percentage': parse_decimal(request.POST.get('placement_percentage'), 0),
            'float_percentage': parse_decimal(request.POST.get('float_percentage'), 0),
            'cavali_percentage': parse_decimal(request.POST.get('cavali_percentage'), 0),
            'structuring_type': request.POST.get('structuring_type'),
            'placement_type': request.POST.get('placement_type'),
            'float_type': request.POST.get('float_type'),
            'cavali_type': request.POST.get('cavali_type'),
        }

        try:
            bond_instance = Bond(**bond_data)
            # calculating
            outcome = BondOutcome(bond_instance)
            def to_decimal(val):
                if val is None:
                    return None
                try:
                    return Decimal(val)
                except Exception:
                    return Decimal('0')
            # Truncar los campos calculados según el modelo
            bond_instance.tcea_emisor = truncate_decimal(outcome.tcea_emisor, 10, 5)
            bond_instance.tcea_emisor_escudo = truncate_decimal(outcome.tcea_emisor_escudo, 10, 5)
            bond_instance.trea_bonista = truncate_decimal(outcome.trea_bonista, 10, 5)
            bond_instance.duracion = truncate_decimal(outcome.duracion, 10, 4)
            bond_instance.convexidad = truncate_decimal(outcome.convexidad, 10, 4)
            bond_instance.total = truncate_decimal(outcome.total, 10, 4)
            bond_instance.duracion_modificada = truncate_decimal(outcome.duracion_modificada, 10, 4)
            bond_instance.precio_actual = truncate_decimal(outcome.precio_actual, 20, 2)
            bond_instance.utilidad = truncate_decimal(outcome.utilidad, 20, 2)
            bond_instance.issuer_initial_cost = truncate_decimal(outcome.issuer_initial_cost, 20, 2)
            bond_instance.bondholder_initial_cost = truncate_decimal(outcome.bondholder_initial_cost, 20, 2)
            bond_instance.cok = truncate_decimal(outcome.cok, 10, 5)
            bond_instance.effective_annual_rate = truncate_decimal(outcome.effective_annual_rate, 10, 5)
            bond_instance.effective_coupon_rate = truncate_decimal(outcome.effective_coupon_rate, 10, 5)
            bond_instance.capitalization_days = outcome.capitalization_days
            bond_instance.total_periods = int(outcome.total_periods) if outcome.total_periods is not None else 0
            bond_instance.coupon_frequency_days = outcome.coupon_frequency_days
            bond_instance.periods_per_year = to_decimal(outcome.periods_per_year)
            
            # save
            bond_instance.save()
            return redirect('bonds:detail', pk=bond_instance.pk)
        except ValidationError as e:
            error_message = f'Error de validación: {e}'
        except Exception as e:
            error_message = f'Ocurrió un error inesperado al registrar el bono: {e}'
    return render(request, 'create-bond.html', {'error_message': error_message})

def list_bonds_view(request):
    try:
        bonds = list(Bond.objects.all().order_by('-issue_date'))
        db_error = False
    except Exception:
        bonds = []
        db_error = True
    return render(request, 'list.html', {'bonds': bonds, 'db_error': db_error})

def delete_bond_view(request, pk):
    bond = get_object_or_404(Bond, pk=pk)
    if request.method == 'POST':
        bond.delete()
    return redirect('bonds:list_bonds')

