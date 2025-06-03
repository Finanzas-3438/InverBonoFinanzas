from django.shortcuts import render, redirect
from .models import Bond
from decimal import Decimal, InvalidOperation

def create_bond_view(request):
    if request.method == 'POST':
        def parse_decimal(val):
            try:
                return Decimal(val) if val not in (None, '', ' ') else None
            except (InvalidOperation, TypeError):
                return None

        bond_data = {
            'name': request.POST.get('bond_name', 'Bono #1'),
            'nominal_value': parse_decimal(request.POST.get('nominal_value')),
            'commercial_value': parse_decimal(request.POST.get('commercial_value')),
            'issue_date': request.POST.get('issue_date'),
            'years_number': parse_decimal(request.POST.get('years_number')),
            'coupon_frequency': request.POST.get('coupon_frequency'),
            'interest_rate_type': request.POST.get('interest_rate_type'),
            'capitalization': request.POST.get('capitalization'),
            'interest_rate': parse_decimal(request.POST.get('interest_rate')),
            'annual_discount_rate': parse_decimal(request.POST.get('annual_discount_rate')),
            'income_tax': parse_decimal(request.POST.get('income_tax')),
            'premium_percentage': parse_decimal(request.POST.get('premium_percentage')),
            'structuring_percentage': parse_decimal(request.POST.get('structuring_percentage')),
            'placement_percentage': parse_decimal(request.POST.get('placement_percentage')),
            'float_percentage': parse_decimal(request.POST.get('float_percentage')),
            'cavali_percentage': parse_decimal(request.POST.get('cavali_percentage')),
        }
        bond_data = {k: v for k, v in bond_data.items() if v is not None or k in ['nominal_value', 'commercial_value', 'issue_date', 'years_number', 'coupon_frequency', 'interest_rate_type', 'capitalization', 'interest_rate', 'annual_discount_rate', 'income_tax', 'nombre']}
        try:
            Bond.objects.create(**bond_data)
            return redirect('dashboard')
        except Exception as e:
            return render(request, 'create-bond.html', {'error': str(e)})
    return render(request, 'create-bond.html')

def list_bonds_view(request):
    db_error = False
    try:
        bonds = list(Bond.objects.all().order_by('-issue_date'))
    except Exception:
        db_error = True
        from collections import namedtuple
        BondMock = namedtuple('Bond', ['name', 'nominal_value', 'commercial_value', 'interest_rate', 'issue_date', 'get_coupon_frequency_display'])
        import datetime
        bonds = [
            BondMock(
                name='Bono Demo 1',
                nominal_value=1000,
                commercial_value=950,
                interest_rate=5.5,
                issue_date=datetime.date(2024, 6, 1),
                get_coupon_frequency_display='Mensual',
            ),
            BondMock(
                name='Bono Demo 2',
                nominal_value=2000,
                commercial_value=1800,
                interest_rate=6.0,
                issue_date=datetime.date(2024, 5, 15),
                get_coupon_frequency_display='Trimestral',
            ),
        ]
    return render(request, 'list.html', {'bonds': bonds, 'db_error': db_error})
