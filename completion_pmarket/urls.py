from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('market', views.market, name='market'),
    path('outcome', views.outcome, name='outcome'),
    path('order', views.order, name='order'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('position', views.position, name='position'),
    path('signup', views.signup, name='signup'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
]
