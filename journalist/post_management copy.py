from .models import Journalist, Language, Equipment, CountryCode, Country, Region, City, Qualification
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
import random
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from post_management.models import category,sub_category,NewsPost,VideoNews
from cities_light.models import Country, Region, City
from phonenumbers import parse, is_valid_number, NumberParseException
from .models import CountryCode 
from django.db.models import Exists, OuterRef
from django.contrib import messages
from datetime import date, datetime
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password

import logging
logger = logging.getLogger(__name__)



#news post
def Journalist_News_Post(request):
    journalist_id = request.session.get('journalist_id')
    
    if not journalist_id:
        messages.error(request, "You must be signed in as a journalist to post.")
        return redirect('sign-in')

    try:
        journalist = Journalist.objects.get(id=journalist_id)
    except Journalist.DoesNotExist:
        messages.error(request, "Invalid journalist account.")
        return redirect('sign-in')
    
    if request.method == "POST":  
        postcat = request.POST.get('post_cat')
        post_title = request.POST.get('post_title')
        post_short_des = request.POST.get('post_short_des')
        post_des = request.POST.get('post_des')
        post_image = request.FILES.get("post_image")
        post_tag = request.POST.get('post_tag')
        newsch = request.POST.get('scheduled_datetime')
        status = "inactive"
        
        newsdata = NewsPost(
            post_cat_id=postcat,
            post_title=post_title,
            post_short_des=post_short_des,
            post_des=post_des,
            post_image=post_image,
            post_tag=post_tag,
            schedule_date=newsch,
            status=status,
            journalist=journalist 
        )
        newsdata.save()
        messages.success(request, 'Your news has been successfully submitted! It will be reviewed by our trusted team before publication.')
        return redirect('news-post')
    else:
        blogdata=NewsPost.objects.filter(is_active=1,status='active').order_by('-id') [:20]
        mainnews=NewsPost.objects.filter(status='active').order_by('order')[:4]
        articales=NewsPost.objects.filter(articles=1,status='active').order_by('-id') [:3]
        vidarticales=VideoNews.objects.filter(articles=1,is_active='active',video_type='video').order_by('order')[:2]
        headline=NewsPost.objects.filter(Head_Lines=1,status='active').order_by('-id') [:14]
        trending=NewsPost.objects.filter(trending=1,status='active').order_by('-id') [:3]
        brknews=NewsPost.objects.filter(BreakingNews=1,status='active').order_by('-id') [:8]
        podcast=VideoNews.objects.filter(is_active='active').order_by('-id') [:1]
        Category=category.objects.filter(cat_status='active').order_by('order') [:11]
        Categories=category.objects.filter(cat_status='active').order_by('order') [:11]
        slider=NewsPost.objects.filter().order_by('-id')[:5]
        latestnews=NewsPost.objects.all().order_by('-id')[:5]
        data={
            'BlogData':blogdata,
            'mainnews':mainnews,
            'Slider':slider,
            'Blogcat':Category,
            'latnews':latestnews,
            'Articale':articales,
            'vidart':vidarticales,
            'headline':headline,
            'trendpost':trending,
            'bnews':brknews,
            'vidnews':podcast,
            'categories':Categories,
            'journalist': journalist,
            }
    return render(request, 'inn/Journalist_news_post.html', data)
            

def Journalist_Manage_Post(request):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        messages.error(request, "You must be signed in as a journalist to manage post.")
        return redirect('sign-in')

    try:
        journalist = Journalist.objects.get(id=journalist_id)
    except Journalist.DoesNotExist:
        messages.error(request, "Invalid journalist account.")
        return redirect('sign-in')

    blogdata = NewsPost.objects.filter(journalist=journalist, is_active=1).order_by('-id')[:20]
    mainnews = NewsPost.objects.filter(journalist=journalist, status='active').order_by('order')[:4]
    articales = NewsPost.objects.filter(journalist=journalist, articles=1, status='active').order_by('-id')[:3]
    headline = NewsPost.objects.filter(journalist=journalist, Head_Lines=1, status='active').order_by('-id')[:14]
    trending = NewsPost.objects.filter(journalist=journalist, trending=1, status='active').order_by('-id')[:3]
    brknews = NewsPost.objects.filter(journalist=journalist, BreakingNews=1, status='active').order_by('-id')[:8]
    slider = NewsPost.objects.filter(journalist=journalist).order_by('-id')[:5]
    latestnews = NewsPost.objects.filter(journalist=journalist).order_by('-id')[:5]
    vidarticales = VideoNews.objects.filter(articles=1, is_active='active', video_type='video').order_by('order')[:2]
    podcast = VideoNews.objects.filter(is_active='active').order_by('-id')[:1]
    Category = category.objects.filter(cat_status='active').order_by('order')[:11]
    Categories = category.objects.filter(cat_status='active').order_by('order')[:11]

    data = {
        'BlogData': blogdata,
        'mainnews': mainnews,
        'Slider': slider,
        'Blogcat': Category,
        'latnews': latestnews,
        'Articale': articales,
        'vidart': vidarticales,
        'headline': headline,
        'trendpost': trending,
        'bnews': brknews,
        'vidnews': podcast,
        'categories': Categories,
        'journalist': journalist,
    }

    return render(request, 'inn/Journalist_manage_post.html', data)


def Journalist_Edit_News_Post(request, post_id):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        return redirect('sign-in')

    try:
        journalist = Journalist.objects.get(id=journalist_id)
    except Journalist.DoesNotExist:
        return redirect('sign-in')

    try:
        blogdata = NewsPost.objects.get(id=post_id, journalist=journalist, status="inactive")
    except NewsPost.DoesNotExist:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('manage-post')

    Category = category.objects.filter(cat_status='active').order_by('order')[:11]
    Categories = category.objects.filter(cat_status='active').order_by('order')[:11]
    trending = NewsPost.objects.filter(journalist=journalist, trending=1, status='active').order_by('-id')[:3]
    articales = NewsPost.objects.filter(journalist=journalist, articles=1, status='active').order_by('-id')[:3]

    data = {
        'ed': blogdata,
        'categories': Categories,
        'Blogcat': Category,
        'trendpost': trending,
        'Articale': articales,
        'journalist': journalist,
    }
    return render(request, 'inn/Journalist_edit_news_Post.html', data)


def JournalistUpdatePost(request):
    if request.method == "POST":
        journalist_id = request.session.get('journalist_id')
        if not journalist_id:
            messages.error(request, "You must be signed in as a journalist to update a post.")
            return redirect('sign-in')

        try:
            journalist = Journalist.objects.get(id=journalist_id)
        except Journalist.DoesNotExist:
            messages.error(request, "Invalid journalist account.")
            return redirect('sign-in')

        post_id = request.POST.get('post_id')

        post = get_object_or_404(NewsPost, id=post_id, journalist=journalist)

        postcat = request.POST.get('post_cat')
        post_title = request.POST.get('post_title')
        post_short_des = request.POST.get('post_short_des')
        post_des = request.POST.get('post_des')
        post_tag = request.POST.get('post_tag')
        newsch = request.POST.get('scheduled_datetime')

        if 'post_image' in request.FILES:
            post.post_image = request.FILES['post_image']


        post.post_cat_id = postcat
        post.post_title = post_title
        post.post_short_des = post_short_des
        post.post_des = post_des
        post.post_tag = post_tag
        post.schedule_date = newsch
        post.status = "inactive" 

        post.save()

        return redirect('manage-post')

    messages.error(request, 'Invalid request method.')
    return redirect('manage-post')





#video post 
def Journalist_video_Post(request):
    journalist_id = request.session.get('journalist_id')

    if not journalist_id:
        messages.error(request, "You must be signed in as a journalist to post.")
        return redirect('sign-in')

    try:
        journalist = Journalist.objects.get(id=journalist_id)
    except Journalist.DoesNotExist:
        messages.error(request, "Invalid journalist account.")
        return redirect('sign-in')
    
    if request.method == "POST":  
        postcat = request.POST.get('post_cat')
        video_type = request.POST.get('video_type')
        video_title = request.POST.get('video_title')
        video_short_des = request.POST.get('video_short_des')
        video_des = request.POST.get('video_des')
        video_url = request.POST.get('video_url')
        video_thumbnail = request.FILES.get('video_thumbnail')
        video_tag = request.POST.get('video_tag')
        newsch = request.POST.get('scheduled_datetime')
        status = "inactive"
        
        VideoNewsdata = VideoNews(
            News_Category_id=postcat,
            video_type=video_type,
            video_title=video_title,
            video_short_des=video_short_des,
            video_des=video_des,
            video_url=video_url,
            video_thumbnail=video_thumbnail,
            video_tag=video_tag,
            schedule_date=newsch,
            is_active=status,
            journalist=journalist 
        )
        VideoNewsdata.save()
        messages.success(request, 'Your news has been successfully submitted! It will be reviewed by our trusted team before publication.')
        return redirect('news-post')
    else:

        Category=category.objects.filter(cat_status='active').order_by('order') [:11]
        Categories=category.objects.filter(cat_status='active').order_by('order') [:11]
        data={
            'Blogcat':Category,
            'categories':Categories,
            'journalist': journalist,
            }
    return render(request, 'inn/Journalist_video_post.html', data)



def Journalist_Manage_Video_Post(request):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        messages.error(request, "You must be signed in as a journalist to manage post.")
        return redirect('sign-in')

    try:
        journalist = Journalist.objects.get(id=journalist_id)
    except Journalist.DoesNotExist:
        messages.error(request, "Invalid journalist account.")
        return redirect('sign-in')

    headline = VideoNews.objects.filter(journalist=journalist, Head_Lines=1, is_active='active',).order_by('-id')[:14]
    articales = VideoNews.objects.filter(journalist=journalist, articles=1, is_active='active',).order_by('-id')[:3]
    trending = VideoNews.objects.filter(journalist=journalist, trending=1, is_active='active',).order_by('-id')[:3]
    brknews = VideoNews.objects.filter(journalist=journalist, BreakingNews=1, is_active='active',).order_by('-id')[:8]
    vidarticales = VideoNews.objects.filter(articles=1, is_active='active', video_type='video').order_by('order')[:2]

    video_podcast = VideoNews.objects.filter(journalist=journalist, video_type='video').order_by('-id')
    reels_podcast = VideoNews.objects.filter(journalist=journalist, video_type='reel').order_by('-id')
    BlogData = VideoNews.objects.filter(journalist=journalist).order_by('-id')
    
    Category = category.objects.filter(cat_status='active').order_by('order')[:11]
    Categories = category.objects.filter(cat_status='active').order_by('order')[:11]

    data = {
        'video_podcast': video_podcast,
        'reels_podcast': reels_podcast,
        'Blogcat': Category,
        'Articale': articales,
        'vidart': vidarticales,
        'headline': headline,
        'trendpost': trending,
        'bnews': brknews,
        'categories': Categories,
        'journalist': journalist,
        'BlogData': BlogData,
    }

    return render(request, 'inn/Journalist_manage_video_post.html', data)


def Journalist_Edit_Video_Post(request, post_id):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        return redirect('sign-in')

    try:
        journalist = Journalist.objects.get(id=journalist_id)
    except Journalist.DoesNotExist:
        return redirect('sign-in')

    
    try:
        videopost = VideoNews.objects.get(id=post_id, journalist=journalist, is_active = "inactive")
    except VideoNews.DoesNotExist:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('manage-video-post')

    Category = category.objects.filter(cat_status='active').order_by('order')[:11]
    Categories = category.objects.filter(cat_status='active').order_by('order')[:11]

    data = {
        'ed': videopost,
        'categories': Categories,
        'Blogcat': Category,
        'journalist': journalist,
    }
    return render(request, 'inn/Journalist_edit_video_Post.html', data)


def JournalistUpdateVideoPost(request):
    if request.method == "POST":
        journalist_id = request.session.get('journalist_id')
        if not journalist_id:
            messages.error(request, "You must be signed in as a journalist to update a post.")
            return redirect('sign-in')

        try:
            journalist = Journalist.objects.get(id=journalist_id)
        except Journalist.DoesNotExist:
            messages.error(request, "Invalid journalist account.")
            return redirect('sign-in')

        post_id = request.POST.get('post_id')

        post = get_object_or_404(VideoNews, id=post_id, journalist=journalist)

        postcat = request.POST.get('post_cat')
        video_type = request.POST.get('video_type')
        post_title = request.POST.get('post_title')
        post_short_des = request.POST.get('post_short_des')
        post_des = request.POST.get('post_des')
        post_tag = request.POST.get('post_tag')
        newsch = request.POST.get('scheduled_datetime')

        if 'post_image' in request.FILES:
            post.video_thumbnail = request.FILES['post_image']


        post.News_Category_id = postcat
        post.video_type = video_type
        post.video_title = post_title
        post.video_short_des = post_short_des
        post.video_des = post_des
        post.video_tag = post_tag   
        post.schedule_date = newsch
        post.is_active = "inactive"

        post.save()

        return redirect('manage-video-post')

    messages.error(request, 'Invalid request method.')
    return redirect('manage-video-post')


def profiledxb(request, journalist_id):
    current_datetime = datetime.now()
    journalist = get_object_or_404(Journalist, id=journalist_id)
    journalist_articales = NewsPost.objects.filter(journalist=journalist, articles=1, status='active').order_by('-id')[:6]
    galleries = journalist.galleries.filter(status='active').order_by('-post_at')[:8]
    Category = category.objects.filter(cat_status='active').order_by('order')[:12]

    journalist_blogdata = NewsPost.objects.filter(journalist=journalist, status='active').order_by('-id')[:6]
    profiles = Journalist.objects.filter(status='active').order_by('-id')[:4]

    blogdata=NewsPost.objects.filter(schedule_date__lt=current_datetime,is_active=1,status='active').order_by('-id') [:10]
    mainnews=NewsPost.objects.filter(schedule_date__lt=current_datetime,is_active=1,status='active').order_by('-id') [:2]
    articales=NewsPost.objects.filter(schedule_date__lt=current_datetime,articles=1,status='active').order_by('-id') [:3]
    headline=NewsPost.objects.filter(schedule_date__lt=current_datetime,Head_Lines=1,status='active').order_by('-id')[:4]
    trending=NewsPost.objects.filter(schedule_date__lt=current_datetime,trending=1,status='active').order_by('-id') [:7]
    brknews=NewsPost.objects.filter(schedule_date__lt=current_datetime,BreakingNews=1,status='active').order_by('-id') [:8]
    podcast=VideoNews.objects.filter(is_active='active').order_by('-id') [:1]
    vidarticales=VideoNews.objects.filter(articles=1,is_active='active',video_type='video').order_by('order')[:2]


    context = {
        'journalist_blogdata':journalist_blogdata,
        'mainnews':mainnews,
        'Blogcat':Category,
        'journalist_articales':journalist_articales,
        'vidart':vidarticales,
        'headline':headline,
        'trendpost':trending,
        'bnews':brknews,
        'vidnews':podcast,
        'journalist': journalist,
        'BlogData': blogdata,
        'Articale': articales,
        'galleries': galleries,
        'profile': profiles,
    }

    return render(request, "inn/profile.html", context)






import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from .models import Gallery, Journalist
from django.contrib import messages
from django.utils.timezone import now

import base64
from django.core.files.base import ContentFile
from django.utils.timezone import now
import base64
from django.core.files.base import ContentFile
from .models import Gallery, Journalist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Gallery, Journalist

def GalleryPost(request):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        return redirect('sign-in')

    journalist = get_object_or_404(Journalist, id=journalist_id)

    if request.method == "POST":
        images_data = request.POST.getlist('images[]')
        current_count = journalist.galleries.filter(status='active').count()
        post_limit = journalist.gallery_post_limit
        slots_left = post_limit - current_count

        for img_data in images_data:
            if not img_data.strip():
                continue
            if slots_left <= 0:
                break
            try:
                format, imgstr = img_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(base64.b64decode(imgstr), name=f'gallery_{journalist.id}_{current_count+1}.{ext}')
                Gallery.objects.create(journalist=journalist, image=image_file, status='active')
                slots_left -= 1
                current_count += 1
            except Exception as e:
                messages.error(request, f"Failed to save one image: {e}")
                continue

        messages.success(request, "Gallery updated successfully.")
        return redirect('gallery_post')

    gallery_post_limit = journalist.gallery_post_limit
    active_gallery_count = journalist.galleries.filter(status='active').count()
    active_galleries = journalist.galleries.filter(status='active')
    remaining_slots = range(gallery_post_limit - active_gallery_count)

    return render(request, "inn/Journalist_gallery_post.html", {
        "journalist": journalist,
        "remaining_slots": remaining_slots,
        'active_galleries': active_galleries,
    })

from django.http import JsonResponse
from .models import Gallery

def delete_gallery_image(request, pk):
    if request.method == 'POST':
        journalist_id = request.session.get('journalist_id')
        if not journalist_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            gallery = Gallery.objects.get(pk=pk, journalist_id=journalist_id)
            gallery.status = 'inactive'
            gallery.save()
            return JsonResponse({'success': True})
        except Gallery.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)



