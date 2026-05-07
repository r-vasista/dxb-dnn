from django.urls import path
from portal.views import NewsPostCreateView, PortalUserCheckAPIView, TagListAPIView, NewsViewsAPIView

urlpatterns = [
    path('create-news/', NewsPostCreateView.as_view()),
    path('check-username/', PortalUserCheckAPIView.as_view()),
    path('tags/', TagListAPIView.as_view()),
    path('news/<str:slug>/views/', NewsViewsAPIView.as_view())
    
]
