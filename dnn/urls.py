from django.urls import path, include
from django.contrib import admin
from dnn import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.views.generic.base import RedirectView

#sitmap start
from django.contrib.sitemaps.views import sitemap
from dnn.sitemaps import custom_sitemap_index, sitemap_news, sitemap_images, sitemap_images_by_month, sitemap_videos, sitemap_videos_by_month, sitemap_article, sitemap_article_by_month, sitemap_archive, sitemap_archive_by_month, sitemap_tags, sitemap_tag_detail, sitemap_static, sitemap_categories, sitemap_category_detail
from webstories.sitemaps import WebStorySitemap
#sitmap end

admin.site.site_header="DNN Admin"
admin.site.site_title="DNN Admin"
admin.site.index_title="Dasboard"

sitemaps = {
    'webstories': WebStorySitemap,
}

urlpatterns = [
    # Explicit redirect for favicon.ico requests (fixes 500 error)
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),

    path('', views.home, name="home"),
    path('webstories/', include('webstories.urls')),
    path('auth/', include('journalist.urls')),
    path('topic/<slug:slug>', views.posts_by_tag, name='posts_by_tag'),
    path('tags/<slug:slug>', views.posts_by_tag, name='posts_by_tag_legacy'),
    path('artdomain/<str:username>/', views.profiledxb, name='journalist_profile'),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('thanks', views.thanks, name="thanks"),
    path('error', views.ErrorPage, name="error"),
    path('contact-us', views.Contactus, name="contact-us"),
    path('sitemap-page', views.SiteMap, name="sitemap-page"),
    path('advertise-with-us', views.advertise, name="advertise-with-us"),
    path('upcoming-events', views.UcEvents, name="upcoming-events"),
    path('news-pdf', views.GetNewsPdf, name="news-pdf"),
    path('career', views.Career, name="career"),
    path('UserSubscriber', views.SubscribeView, name="UserSubscriber"),
    path('Reg-Form', views.Reg_Form, name="Reg-Form"),
    path('search', views.find_post_by_title, name="search"),
    path('adsinquiry', views.Adsinquiry, name='adsinquiry'),
    path('voices-of-uae', views.voicesofuae, name='voices-of-uae'),
    path('cms<slug:slug>/', views.cms_detail, name='cms'),
    path('setting', views.Settings, name='setting'),
    path('reels/', include('reels.urls', namespace='reels')),
    
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path(
        "ads.txt",
        TemplateView.as_view(template_name="ads.txt", content_type="text/plain"),
    ),
    
    
    #sitmap start
    path('sitemap', custom_sitemap_index, name='sitemap'),
    path('sitemap/news', sitemap_news, name='sitemap-news'),
    path('sitemap/images', sitemap_images, name='sitemap-images'),
    path('sitemap/images/<int:year>/<int:month>/', sitemap_images_by_month, name='sitemap-images-by-month'),
    path('sitemap/videos', sitemap_videos, name='sitemap-video'),
    path('sitemap/videos/<int:year>/<int:month>/', sitemap_videos_by_month, name='sitemap-videos-by-month'),
    path('sitemap/articles', sitemap_article, name='sitemap-articles'),
    path('sitemap/articles/<int:year>/<int:month>/', sitemap_article_by_month, name='sitemap-articles-by-month'),
    path('sitemap/archive', sitemap_archive, name='sitemap-archive'),
    path('sitemap/archive/<int:year>/<int:month>/', sitemap_archive_by_month, name='sitemap-archive-by-month'),
    path('sitemap/tags', sitemap_tags, name='sitemap-tags'),
    path('sitemap/tags/<slug:slug>', sitemap_tag_detail, name='sitemap-tag-detail'),
    path('sitemap/static', sitemap_static, name='sitemap-static'),
    path('sitemap/categories', sitemap_categories, name='sitemap-categories'),
    path('sitemap/categories/<slug:slug>', sitemap_category_detail, name='sitemap-category-detail'),
    
    path('sitemap-webstories.xml', sitemap, 
         {'sitemaps': sitemaps}, 
         name='django.contrib.sitemaps.views.sitemap'),
    #for recon
    path('dxbnewsnetwork/api/', include('portal.urls')),

   #for apk
   path('api/', include('post_management.api.urls')),
   path('api-v2/', include('api.urls')),


    #sitmap end
    #admin-user-pannel-path
    path('user-dashboard', views.Userdashboard, name="user-dashboard"),
    path('managepost', views.ManagePost, name="managepost"),
    path('guest-news-post', views.Guestpost, name="guest-news-post"),
    path('registration', views.Userregistration, name="registration"),
    path('registeration', views.Registeration, name="registeration"),
    path('login', views.Userlogin, name="login"),
    path('logout', views.Logout, name="logout"),
    path('edit-news-post/<int:post_id>', views.EditNewsPost, name="edit-news-post"),
    path('update-post', views.UpdateNewsPost, name="update-post"),
    
    #dynemic-path---
    path('<slug>', views.newsdetails, name="newsdetails"),
    path('all-news/<slug>', views.AllNews, name="all-news"),
    path('all-reels-news/<slug>', views.AllReelsNews, name="all-reels-news"),
    path('all-video-news/<slug>', views.AllvideoNews, name="all-video-news"),
    path('video/<slug>', views.videonewsdetails, name="videonewsdetails"),
    path('<str:catlink>/<slug>', views.catdetails, name="catdetails"),
    path('events/<slug>', views.eventdetails, name="eventdetails"),
    #dynemic-path-end
    
    #path('logincheck', views.Logincheck, name="logincheck"),
    #admin-----link---end------

    #path('video/<slug>', views.videocategory, name="videocategory"),
    # path('<data>', views.pagename),
    
    path('adminview/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls'))
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
