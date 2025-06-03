from django.urls import path
from . import views

app_name = 'bonds'

urlpatterns = [
    path('create-bond/', views.create_bond_view, name='create_bond'),
    path('list/', views.list_bonds_view, name='list_bonds'),
]
