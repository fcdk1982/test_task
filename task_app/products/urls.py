from django.urls import path

from .views import UserLoginView, StatsView, ProductCreateView, IncreaseView

app_name = 'products'
urlpatterns = [
    path('', UserLoginView.as_view(), name='login_url'),
    path('create/', ProductCreateView.as_view(), name='create_url'),
    path('stats/<int:pk>/', StatsView.as_view(), name='stats_url'),
    path('increase/<int:pk>/', IncreaseView.as_view(), name='increase_url'),
]
