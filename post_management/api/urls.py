from django.urls import path
from .views import CategoryListAPI, GlobalSearchAPI, NewsListAPI, NewsDetailAPI , VideoListAPI, VideoDetailAPI, AppSignupAPI, AppLoginAPI, AppProfileUpdateAPI, HomePageAPI

urlpatterns = [
    path('homepage/', HomePageAPI.as_view(), name='api-home-page'),
    path('categories/', CategoryListAPI.as_view(), name='api-category-list'),
    path('news/', NewsListAPI.as_view(), name='api-news-list'),
    path(
        'news/<int:id>/',
        NewsDetailAPI.as_view(),
        name='api-news-detail'
    ),
    path('videos/', VideoListAPI.as_view(), name='api-video-list'),
    path('videos/<int:id>/', VideoDetailAPI.as_view(), name='api-video-detail'),
    path('search/', GlobalSearchAPI.as_view(), name='api-global-search'),
    path('auth/signup/', AppSignupAPI.as_view(), name='auth-signup'),
    path('auth/login/', AppLoginAPI.as_view(), name='auth-login'),
    path('auth/update-profile/', AppProfileUpdateAPI.as_view(), name='auth-update-profile'),

]
