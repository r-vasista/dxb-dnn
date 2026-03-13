from django.urls import path
from .views import (
    HeadlineNewsAPIView, TrendingNewsAPIView, BreakingNewsAPIView, UserNewsAPIView, EventsAPIView,
    LatestNewsAPIView, ProfilesAPIView, ReelsAPIView, CategoryListAPIView, CategoryNewsAPIView,
    ArticlesAPIView
)

urlpatterns = [
    path('news/headline/', HeadlineNewsAPIView.as_view()),
    path('news/trending/', TrendingNewsAPIView.as_view()),
    path('news/breaking/', BreakingNewsAPIView.as_view()),
    path('news/user/', UserNewsAPIView.as_view()),
    path('news/latest/', LatestNewsAPIView.as_view()),
    path('news/category/', CategoryNewsAPIView.as_view()), 
    path('news/articles/', ArticlesAPIView.as_view()), 

    path('events/', EventsAPIView.as_view()),
    path('profiles/', ProfilesAPIView.as_view()),
    path('videos/reels/', ReelsAPIView.as_view()), 
    path('categories/', CategoryListAPIView.as_view()), 
]