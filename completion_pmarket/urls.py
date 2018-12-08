from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('market', views.market, name='market'),
    path('outcome', views.outcome, name='outcome'),
    path('order', views.order, name='order'),
    path('portfolio', views.portfolio, name='portfolio')
]
