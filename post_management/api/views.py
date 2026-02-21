from rest_framework.generics import ListAPIView , RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from post_management.models import category , NewsPost , VideoNews, AppUser
from journalist.models import Journalist
from Ad_management.models import ad
from .serializers import CategorySerializer , NewsListSerializer, SearchNewsSerializer, SearchVideoSerializer , VideoListSerializer, AppUserSignupSerializer, AppUserLoginSerializer, AppUserUpdateSerializer, JournalistSerializer, AdSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone



class SearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 50


class CategoryListAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return category.objects.filter(
            cat_status='active'
        ).order_by('order')

class NewsListAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewsListSerializer

     # 🔹 Pagination defined INSIDE view
    class Pagination(PageNumberPagination):
        page_size = 10                 # default records
        page_size_query_param = 'limit'
        max_page_size = 50

    pagination_class = Pagination

    def get_queryset(self):
        qs = NewsPost.objects.filter(
            status='active',
            is_active=True
        ).order_by('-post_date')

        # 🔹 Sub-category filter (MANDATORY when sent)
        subcat_id = self.request.GET.get('subcategory_id')
        if subcat_id:
            qs = qs.filter(post_cat_id=subcat_id)

        # 🔹 Status-based filters
        if self.request.GET.get('breaking') == '1':
            qs = qs.filter(BreakingNews=True)

        if self.request.GET.get('trending') == '1':
            qs = qs.filter(trending=True)

        if self.request.GET.get('headlines') == '1':
            qs = qs.filter(Head_Lines=True)

        if self.request.GET.get('articles') == '1':
            qs = qs.filter(articles=True)

        return qs


class NewsDetailAPI(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewsListSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return NewsPost.objects.filter(
            status='active',
            is_active=True
        )

class VideoListAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = VideoListSerializer

     # 🔹 Pagination defined INSIDE view
    class Pagination(PageNumberPagination):
        page_size = 10                 # default records
        page_size_query_param = 'limit'
        max_page_size = 50

    pagination_class = Pagination

    def get_queryset(self):
        qs = VideoNews.objects.filter(
            is_active='active'
        ).order_by('-video_date')

        # 🔹 Sub-category filter
        subcat_id = self.request.GET.get('subcategory_id')
        if subcat_id:
            qs = qs.filter(News_Category_id=subcat_id)

        # 🔹 Video type filter (video / reel)
        video_type = self.request.GET.get('video_type')
        if video_type in ['video', 'reel']:
            qs = qs.filter(video_type=video_type)

        # 🔹 Status filters
        if self.request.GET.get('breaking') == '1':
            qs = qs.filter(BreakingNews=True)

        if self.request.GET.get('trending') == '1':
            qs = qs.filter(trending=True)

        if self.request.GET.get('headlines') == '1':
            qs = qs.filter(Head_Lines=True)

        if self.request.GET.get('articles') == '1':
            qs = qs.filter(articles=True)

        return qs


class VideoDetailAPI(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = VideoListSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return VideoNews.objects.filter(is_active='active')
    

class GlobalSearchAPI(APIView):
    permission_classes = [AllowAny]
    pagination_class = SearchPagination

    def get(self, request):
        query = request.GET.get('q', '').strip()

        if not query:
            return Response({
                "count": 0,
                "results": []
            })

        # 🔹 NEWS SEARCH
        news_qs = NewsPost.objects.select_related(
            'post_cat',
            'post_cat__sub_cat'
        ).filter(
            Q(post_title__icontains=query) |
            Q(post_short_des__icontains=query) |
            Q(post_cat__subcat_name__icontains=query) |
            Q(post_cat__sub_cat__cat_name__icontains=query),
            status='active',
            is_active=True
        ).order_by('-post_date')

        # 🔹 VIDEO SEARCH
        video_qs = VideoNews.objects.select_related(
            'News_Category',
            'News_Category__sub_cat'
        ).filter(
            Q(video_title__icontains=query) |
            Q(video_short_des__icontains=query) |
            Q(News_Category__subcat_name__icontains=query) |
            Q(News_Category__sub_cat__cat_name__icontains=query),
            is_active='active'
        ).order_by('-video_date')

        # 🔹 Serialize
        news_data = SearchNewsSerializer(
            news_qs, many=True, context={'request': request}
        ).data

        video_data = SearchVideoSerializer(
            video_qs, many=True, context={'request': request}
        ).data

        # 🔹 Combine results
        combined = (
            [{"type": "news", **item} for item in news_data] +
            [{"type": "video", **item} for item in video_data]
        )

        # 🔹 Pagination manually
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(combined, request)
        return paginator.get_paginated_response(page)

class AppSignupAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = AppUserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens manually
            refresh = RefreshToken()
            refresh['user_id'] = user.id
            refresh['email'] = user.email
            
            return Response({
                "status": "success", 
                "message": "Account created successfully!", 
                "data": serializer.data,
                "tokens": {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AppLoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = AppUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = AppUser.objects.get(email=email)
            except AppUser.DoesNotExist:
                return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if check_password(password, user.password):
                # Generate JWT tokens manually
                refresh = RefreshToken()
                refresh['user_id'] = user.id
                refresh['email'] = user.email

                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "tokens": {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "phone": user.phone,
                        "city": user.city,
                        "country": user.country
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({"status": "error", "message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AppProfileUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        # Helper method for consistent error handling
        try:
            return AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return None

    def post(self, request):
        # We'll get user_id from the token (request.user comes from JWTAuthentication)
        # Note: SimpleJWT by default sets request.user to a Django User object.
        # Since we use a custom AppUser and manual token generation, 
        # request.user might be an internal SimpleJWT user object or a dict from the claim.
        # We should rely on the 'user_id' we put in the token claim.
        
        try:
            # When using manual token generation with SimpleJWT, request.user usually resolves
            # based on USER_ID_FIELD. Since AppUser is not the AUTH_USER_MODEL,
            # we need to be careful.
            # The safest way here since we manually forged tokens:
            token_user_id = request.auth.payload.get('user_id')
            user = self.get_object(token_user_id)
        except Exception:
            # Fallback/Debug
            return Response({"status": "error", "message": "Invalid auth token"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user:
             return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomePageAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        current_datetime = timezone.now()
        
        # 1. Slider (Latest 5)
        slider_qs = NewsPost.objects.filter(
            schedule_date__lte=current_datetime, 
            status='active', 
            is_active=True
        ).order_by('-id')[:5]
        
        # 2. Breaking News
        breaking_qs = NewsPost.objects.filter(
            BreakingNews=True, 
            status='active', 
            is_active=True
        ).order_by('-id')[:4]
        
        # 3. Headlines
        headlines_qs = NewsPost.objects.filter(
            Head_Lines=True, 
            status='active', 
            is_active=True
        ).order_by('-id')[:4]
        
        # 4. Trending
        trending_qs = NewsPost.objects.filter(
            trending=True, 
            status='active', 
            is_active=True
        ).order_by('-id')[:6]
        
        # 5. Latest News
        latest_qs = NewsPost.objects.filter(
            schedule_date__lte=current_datetime, 
            status='active', 
            is_active=True
        ).order_by('-id')[:10]
        
        # 6. Videos
        videos_qs = VideoNews.objects.filter(
            is_active='active', 
            video_type='video'
        ).order_by('order')[:4]
        
        # 7. Reels
        reels_qs = VideoNews.objects.filter(
            is_active='active', 
            video_type='reel'
        ).order_by('-id')[:16]
        
        # 10. Articles
        profiles_qs = Journalist.objects.filter(status='active').exclude(registration_type='journalist').order_by('-id')[:6]

        # 10. Articles
        articles_qs = NewsPost.objects.filter(
            schedule_date__lte=current_datetime,
            articles=True,
            status='active'
        ).order_by('-id')[:12]

        # 11. Ads (Fetching a few active ads)
        ads_qs = ad.objects.filter(is_active=True).order_by('-id')
        head_top_ad = ads_qs.filter(ads_cat__ads_cat_slug='topad')[:1]
        ad_top_left = ads_qs.filter(ads_cat__ads_cat_slug='topleft-600x80')[:4]
        ad_top_right = ads_qs.filter(ads_cat__ads_cat_slug='topright-600x80')[:4]

        # 12. Brand Partners
        from service.models import BrandPartner
        bp_qs = BrandPartner.objects.filter(is_active=1).order_by('-id')[:30]
        
        # 13. Events
        current_datetime = timezone.now()
        upcoming_events = NewsPost.objects.filter(Event=1, Event_date__gt=current_datetime, status='active').order_by('Event_date')[:10]
        ongoing_events = NewsPost.objects.filter(Event=1, Event_date__lte=current_datetime, Eventend_date__gte=current_datetime, status='active').order_by('Eventend_date')[:10]
        past_events = NewsPost.objects.filter(Event=1, Eventend_date__lt=current_datetime, status='active').order_by('-Eventend_date')[:10]

        # Serialization
        context = {'request': request}
        
        return Response({
            "status": "success",
            "data": {
                "header": {
                    "breaking_news": NewsListSerializer(breaking_qs, many=True, context=context).data, # News Ticker
                },
                "sections": [
                    {
                        "type": "top_ads",
                        "title": "Header Ads",
                        "data": {
                            "head_top": AdSerializer(head_top_ad, many=True, context=context).data,
                            "top_left": AdSerializer(ad_top_left, many=True, context=context).data,
                            "top_right": AdSerializer(ad_top_right, many=True, context=context).data,
                        }
                    },
                    {
                        "type": "video_news",
                        "title": "Video News",
                        "data": VideoListSerializer(videos_qs, many=True, context=context).data
                    },
                    {
                        "type": "headlines",
                        "title": "Latest Headlines",
                        "data": NewsListSerializer(headlines_qs, many=True, context=context).data
                    },
                    {
                        "type": "artdomain",
                        "title": "Artdomain Users",
                        "data": JournalistSerializer(profiles_qs, many=True, context=context).data
                    },
                    {
                        "type": "trending",
                        "title": "Discover What's Trending",
                        "data": NewsListSerializer(trending_qs, many=True, context=context).data
                    },
                    {
                        "type": "reels",
                        "title": "Must Watch Reels",
                        "data": VideoListSerializer(reels_qs, many=True, context=context).data
                    },
                    {
                        "type": "articles",
                        "title": "Top Articles",
                        "data": NewsListSerializer(articles_qs, many=True, context=context).data
                    },
                    {
                        "type": "events",
                        "title": "Events",
                        "data": {
                            "upcoming": NewsListSerializer(upcoming_events, many=True, context=context).data,
                            "ongoing": NewsListSerializer(ongoing_events, many=True, context=context).data,
                            "past": NewsListSerializer(past_events, many=True, context=context).data,
                        }
                    },
                    {
                        "type": "brand_partners",
                        "title": "Our Partners",
                        "data": [{"id": b.id, "name": "Partner", "image": request.build_absolute_uri(b.Logo.url) if b.Logo else None} for b in bp_qs]
                    }
                ]
            }
        }, status=status.HTTP_200_OK)
