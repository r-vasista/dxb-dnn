from .models import Journalist, Language, Equipment, CountryCode, Country, Region, City, Qualification, Gallery
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
import random
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from post_management.models import category,sub_category,NewsPost,VideoNews,Tag
from cities_light.models import Country, Region, City
from phonenumbers import parse, is_valid_number, NumberParseException
from .models import CountryCode 
from django.db.models import Exists, OuterRef
from django.contrib import messages
from datetime import date, datetime
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
import base64
from django.core.files.base import ContentFile
import logging
logger = logging.getLogger(__name__)
from .models import Gallery
from django.db.models import Count
from django.http import HttpResponseForbidden


def tag_autocomplete(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        q = request.GET.get('term', '').lstrip('#')  # Remove # if typed
        tags = Tag.objects.filter(name__istartswith=q).annotate(
            post_count=Count('newspost')
        ).values('name', 'post_count')[:10]

        data = [{
            'id': tag["name"],
            'text': tag["name"],
            'count': tag["post_count"]
        } for tag in tags]

        return JsonResponse(data, safe=False)


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
        post_image = request.POST.get("post_image")
        if post_image:
            format, imgstr = post_image.split(';base64')
            ext = format.split('/')[-1]
            post_images = ContentFile(base64.b64decode(imgstr), name=f'cropped.{ext}')
        tags_input = request.POST.getlist('tags[]')
        newsch = request.POST.get('scheduled_datetime')
        status = "inactive"
        
        newsdata = NewsPost(
            post_cat_id=postcat,
            post_title=post_title,
            post_short_des=post_short_des,
            post_des=post_des,
            post_image=post_images,
            schedule_date=newsch,
            status=status,
            journalist=journalist 
        )
        newsdata.save()
        for tag_name in tags_input:
            tag_name = tag_name.strip()
            if tag_name.startswith('#'):
                tag_name = tag_name[1:]  # Remove the #
            if tag_name:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                newsdata.tags.add(tag_obj)


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
        Category=category.objects.filter(cat_status='active').order_by('order') [:12]
        Categories=category.objects.filter(cat_status='active').order_by('order') [:12]
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
        tags_input = request.POST.getlist('tags[]') 
        newsch = request.POST.get('scheduled_datetime')

        if request.POST.get('post_image'):
            image_data = request.POST.get('post_image')
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]
            post.post_image.save(f"post_{post.id}.{ext}", ContentFile(base64.b64decode(imgstr)), save=False)
        
        post.post_cat_id = postcat
        post.post_title = post_title
        post.post_short_des = post_short_des
        post.post_des = post_des
        post.tags.clear()
        for tag_name in tags_input:
            tag_name = tag_name.strip().lstrip('#')  # clean input
            if tag_name:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)
        post.schedule_date = newsch
        post.status = "inactive" 

        post.save()
        messages.success(request, 'Your news has been update successfully!')

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
        video_thumbnail = request.POST.get('video_thumbnail')
        if video_thumbnail:
            format, imgstr = video_thumbnail.split(';base64')
            ext = format.split('/')[-1]
            video_thumbnails = ContentFile(base64.b64decode(imgstr), name=f'cropped.{ext}')
        tags_input = request.POST.getlist('tags[]')
        newsch = request.POST.get('scheduled_datetime')
        status = "inactive"
        
        VideoNewsdata = VideoNews(
            News_Category_id=postcat,
            video_type=video_type,
            video_title=video_title,
            video_short_des=video_short_des,
            video_des=video_des,
            video_url=video_url,
            video_thumbnail=video_thumbnails,
            schedule_date=newsch,
            is_active=status,
            journalist=journalist 
        )
        VideoNewsdata.save()
        for tag_name in tags_input:
            tag_name = tag_name.strip()
            if tag_name.startswith('#'):
                tag_name = tag_name[1:]  # Remove the #
            if tag_name:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                VideoNewsdata.tags.add(tag_obj)
        messages.success(request, 'Your news has been successfully submitted! It will be reviewed by our trusted team before publication.')
        return redirect('news-post')
    else:

        Category=category.objects.filter(cat_status='active').order_by('order') [:12]
        Categories=category.objects.filter(cat_status='active').order_by('order') [:12]
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
        newsch = request.POST.get('scheduled_datetime')
        tags_input = request.POST.getlist('tags[]') 
        
        
        if request.POST.get('post_image'):
            image_data = request.POST.get('post_image')
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]
            post.video_thumbnail.save(f"post_{post.id}.{ext}", ContentFile(base64.b64decode(imgstr)), save=False)


        post.News_Category_id = postcat
        post.video_type = video_type
        post.video_title = post_title
        post.video_short_des = post_short_des
        post.video_des = post_des
        post.tags.clear()
        for tag_name in tags_input:
            tag_name = tag_name.strip().lstrip('#')  # clean input
            if tag_name:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)
        post.schedule_date = newsch
        post.is_active = "inactive"

        post.save()
        messages.success(request, 'Your news has been update successfully!')

        return redirect('manage-video-post')

    messages.error(request, 'Invalid request method.')
    return redirect('manage-video-post')


def GalleryPost(request):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        return redirect('sign-in')

    journalist = get_object_or_404(Journalist, id=journalist_id)

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        caption = request.POST.get('caption', '').strip()
        cropped_image_data = request.POST.get('cropped_image_data')

        # Check post limit
        current_count = journalist.galleries.filter(status='active').count()
        post_limit = journalist.gallery_post_limit
        if current_count >= post_limit:
            messages.error(request, f"You have reached your post limit of {post_limit}.")
            return redirect('gallery_post')

        if not cropped_image_data:
            messages.error(request, "Image is required.")
            return redirect('gallery_post')


        # Decode base64 image
        format, imgstr = cropped_image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'gallery_{journalist.id}_{current_count + 1}.{ext}')

        # Save the Gallery post
        Gallery.objects.create(
            journalist=journalist,
            title=title,
            caption=caption,
            image=image_file,
            status='active'
        )
        messages.success(request, "Post created successfully.")
        return redirect('gallery_post')

    # GET request
    gallery_post_limit = journalist.gallery_post_limit
    active_gallery_count = journalist.galleries.filter(status='active').count()
    active_galleries = journalist.galleries.filter(status='active')
    remaining_slots = range(gallery_post_limit - active_gallery_count)

    context = {
        "journalist": journalist,
        "remaining_slots": remaining_slots,
        "active_galleries": active_galleries,
    }

    return render(request, "inn/Journalist_gallery_post.html", context)


def delete_gallery_image(request, pk):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        return redirect('sign-in')  # Force login first

    try:
        gallery = Gallery.objects.get(pk=pk, journalist_id=journalist_id)
        gallery.status = 'inactive'
        gallery.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Gallery.DoesNotExist:
        return HttpResponseForbidden("You are not allowed to delete this image.")


def edit_gallery_image(request, pk):
    journalist_id = request.session.get('journalist_id')
    if not journalist_id:
        return redirect('sign-in')

    gallery = get_object_or_404(Gallery, pk=pk, journalist_id=journalist_id)

    if request.method == 'POST':
        gallery.title = request.POST.get('title', '').strip()
        gallery.caption = request.POST.get('caption', '').strip()
        gallery.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('dashboard') 


def AddArtist(request):
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
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        # Check for required fields
        if not first_name or not last_name or not email:
            messages.error(request, 'All fields are required.')
            return render(request, 'inn/add_artist.html', {'journalist': journalist})

        # Prevent self-invitation
        if email.lower() == journalist.email.lower():
            messages.error(request, 'You cannot invite your own email!')
            return render(request, 'inn/add_artist.html', {'journalist': journalist})

        # Check if artist already exists
        if Journalist.objects.filter(email=email).exists():
            messages.error(request, 'Artist already exists.')
            return render(request, 'inn/add_artist.html', {'journalist': journalist})

        # If all validations pass, send the invitation email
        subject = "Please Complete Your Registration"
        message = (
            f"Dear {first_name} {last_name},\n\n"
            f"You have been invited to register on DXB News Network by:\n"
            f"Organisation: {journalist.organisation_name}\n"
            f"Email: {journalist.email}\n"
            f"Phone: {journalist.phone_number}\n\n"
            f"Click the link below to complete your registration:\n"
            f"https://www.dxbnewsnetwork.com/auth/sign-up/\n\n"
            f"If you are already registered, you may ignore this email.\n\n"
            f"Warm regards,\nDXB News Network Security Team\n"
            f"📧 info@dxbnewsnetwork.com\n🌐 www.dxbnewsnetwork.com"
        )

        from_email = 'no-reply@dxbnewsnetwork.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        messages.success(request, 'The invitation link has been successfully sent!')

    return render(request, 'inn/add_artist.html', {'journalist': journalist})



