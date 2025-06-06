from django.urls import path
from . import views

app_name = 'bonds'

urlpatterns = [
    path('create-bond/', views.create_bond_view, name='create_bond'),
    path('list/', views.list_bonds_view, name='list_bonds'),
    path('<int:pk>/', views.bond_detail, name='detail'),
    path('delete/<int:pk>/', views.delete_bond_view, name='delete_bond'),
]
