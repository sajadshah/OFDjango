from django.urls import path
from . import views

urlpatterns = [
    path('', views.input_form_view, name='input_form'),
    path('get-intermediate-images', views.get_intermediate_images, name='get_intermediate_images'),
]