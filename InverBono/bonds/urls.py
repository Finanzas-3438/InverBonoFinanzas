from django.urls import path
from . import views

app_name = 'bonds'

urlpatterns = [
    path('create-bond/', views.create_bond_view, name='create_bond'),
    path('list/', views.list_bonds_view, name='list_bonds'),
    path('editor/', views.bond_editor, name='editor_bonds'),
    path('calculate_bond/', views.calculate_bond_view, name='calculate_bond'),
    path('<int:pk>/', views.bond_detail, name='detail'),
    path('delete/<int:pk>/', views.delete_bond_view, name='delete_bond'),
    path('download/<int:bond_id>/', views.download_bond_excel, name='download_bond_excel'),
]
