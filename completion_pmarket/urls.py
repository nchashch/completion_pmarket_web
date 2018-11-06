from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('outcomes', views.market, name='outcomes'),
]

