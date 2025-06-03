from django.shortcuts import render, redirect
from .models import Bond

def create_bond_view(request):
    if request.method == 'POST':
        bond_data = {
            'nominal_value': request.POST.get('nominal_value'),
            'commercial_value': request.POST.get('commercial_value'),
            'issue_date': request.POST.get('issue_date'),
            'years_number': request.POST.get('years_number'),
            'coupon_frequency': request.POST.get('coupon_frequency'),
            'interest_rate_type': request.POST.get('interest_rate_type'),
            'capitalization': request.POST.get('capitalization'),
            'interest_rate': request.POST.get('interest_rate'),
            'annual_discount_rate': request.POST.get('annual_discount_rate'),
            'income_tax': request.POST.get('income_tax'),
            'premium_percentage': request.POST.get('premium_percentage'),
            'structuring_percentage': request.POST.get('structuring_percentage'),
            'placement_percentage': request.POST.get('placement_percentage'),
            'float_percentage': request.POST.get('float_percentage'),
            'cavali_percentage': request.POST.get('cavali_percentage'),
        }

        Bond.objects.create(**bond_data)

        # return redirect('success_page')

    return render(request, 'create-bond.html')
