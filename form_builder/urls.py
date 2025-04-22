from django.urls import path
from . import views

app_name = 'form_builder'

urlpatterns = [
    path('<slug:slug>/', views.view_form, name='view_form'),
    path('<slug:slug>/submit/', views.submit_form, name='submit_form'),
    path('preview/', views.preview_form, name='preview_form'),

    # API endpoints for dynamic data
    path('api/user-location/', views.get_user_location_data, name='user_location_data'),
    path('api/states/', views.fetch_states, name='fetch_states'),
    path('api/states/<str:state_id>/districts/', views.fetch_districts, name='fetch_districts'),
    path('api/states/<str:state_id>/districts/<str:district_id>/blocks/', views.fetch_blocks, name='fetch_blocks'),
    path('api/states/<str:state_id>/districts/<str:district_id>/blocks/<str:block_id>/villages/', views.fetch_villages, name='fetch_villages'),
    path('api/states/<str:state_code>/blocks/<str:block_id>/shgs/', views.fetch_shgs, name='fetch_shgs'),
    path('api/states/<str:state_code>/blocks/<str:block_id>/vos/', views.fetch_vos, name='fetch_vos'),
    path('api/states/<str:state_code>/blocks/<str:block_id>/clfs/', views.fetch_clfs, name='fetch_clfs'),

    # API endpoints that use the user's location data
    path('api/villages/', views.fetch_villages, name='fetch_villages_user_location'),
    path('api/shgs/', views.fetch_shgs, name='fetch_shgs_user_location'),
    path('api/vos/', views.fetch_vos, name='fetch_vos_user_location'),
    path('api/clfs/', views.fetch_clfs, name='fetch_clfs_user_location'),
]