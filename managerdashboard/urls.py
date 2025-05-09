from django.urls import path
from . import views

app_name = 'managerdashboard'

urlpatterns = [
    path('dashboard/', views.dashboard, name='manager_dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/view/<int:employee_id>/', views.view_employee, name='view_employee'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('forms/', views.forms_list, name='forms_list'),
    path('forms/create/', views.create_form, name='create_form'),
    path('forms/save/', views.save_form, name='save_form'),
    path('forms/update/', views.update_form, name='update_form'),
    path('forms/<slug:slug>/publish/', views.publish_form, name='publish_form'),
    path('forms/edit/<slug:slug>/', views.edit_form, name='edit_form'),
    path('forms/duplicate/<slug:slug>/', views.duplicate_form, name='duplicate_form'),
    path('forms/delete/<slug:slug>/', views.delete_form, name='delete_form'),
    path('forms/export/<slug:slug>/', views.export_form_submissions, name='export_form_submissions'),
    path('forms/submissions/<slug:slug>/', views.form_submissions, name='form_submissions'),
    path('reports/', views.reports, name='reports'),
]