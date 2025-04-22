from django.urls import path
from . import views

app_name = 'managerdashboard'

urlpatterns = [
    path('dashboard/', views.dashboard, name='manager_dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('forms/', views.forms_list, name='forms_list'),
    path('forms/create/', views.create_form, name='create_form'),
    path('forms/save/', views.save_form, name='save_form'),
    path('forms/update/', views.update_form, name='update_form'),
    path('forms/<slug:slug>/publish/', views.publish_form, name='publish_form'),
    path('forms/edit/<slug:slug>/', views.edit_form, name='edit_form'),
    path('forms/duplicate/<slug:slug>/', views.duplicate_form, name='duplicate_form'),
    path('forms/delete/<slug:slug>/', views.delete_form, name='delete_form'),
]