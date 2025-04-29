from django.urls import path
from . import views

app_name = 'employeedashboard'

urlpatterns = [
    path('', views.dashboard, name='employee_dashboard'),
    path('forms/', views.my_forms, name='my_forms'),
    path('forms/<slug:slug>/', views.view_form, name='view_form'),
    path('submissions/', views.my_submissions, name='my_submissions'),
    path('profile/', views.profile, name='profile'),
    path('reports/', views.reports, name='reports'),
    path('reports/form/<slug:slug>/', views.form_reports, name='form_reports'),
]