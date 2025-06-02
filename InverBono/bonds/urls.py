from django.urls import path
from . import views

app_name = 'bonds'

urlpatterns = [
    path('create-bond/', views.create_bond_view, name='create_bond'),
]
