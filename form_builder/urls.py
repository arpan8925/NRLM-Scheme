from django.urls import path
from . import views

app_name = 'form_builder'

urlpatterns = [
    path('<slug:slug>/', views.view_form, name='view_form'),
    path('<slug:slug>/submit/', views.submit_form, name='submit_form'),
    path('preview/', views.preview_form, name='preview_form'),
    # Add other form_builder URLs here
] 