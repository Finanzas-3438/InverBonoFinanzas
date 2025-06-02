from django.shortcuts import render

def create_bond_view(request):
    return render(request, 'create-bond.html')
