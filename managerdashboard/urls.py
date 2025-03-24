from django.urls import path
from . import views

app_name = 'managerdashboard'

urlpatterns = [
    path('', views.dashboard, name='manager_dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
] 