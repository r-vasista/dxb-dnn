from django.urls import path
from . import views

app_name = 'reels'

urlpatterns = [
    path('reels/', views.reels_list, name='reels-list'),
    path('reels/api/', views.reels_api, name='reels-api'),
]