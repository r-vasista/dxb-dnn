from django.db import transaction
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
    
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .utils import (
    success_response, error_response
)
from .pagination import PaginationMixin
from .serializers import (
    NewsPostSerializer, JournalistListSerializer, VideoNewsSerializer, CategoryListSerializer, 
    SubCategorySerializer
)
from post_management.models import (
    NewsPost, Journalist, VideoNews, category
)

class HeadlineNewsAPIView(PaginationMixin, APIView):
    """
    Get Headline News

    GET /api/news/headlines/

    Returns:
        - Active headline news
        - schedule_date < now
        - status = active
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            current_datetime = timezone.now()

            queryset = NewsPost.objects.filter(
                schedule_date__lt=current_datetime,
                Head_Lines=True,
                status='active'
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related("tags").order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Headline news retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch headline news"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
      
class TrendingNewsAPIView(PaginationMixin, APIView):
    """
    Get Trending News

    GET /api/news/trending/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            current_datetime = timezone.now()

            queryset = NewsPost.objects.filter(
                schedule_date__lt=current_datetime,
                trending=True,
                status='active'
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related("tags").order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Trending news retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch trending news"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class BreakingNewsAPIView(PaginationMixin, APIView):
    """
    Get Breaking News

    GET /api/news/breaking/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            queryset = NewsPost.objects.filter(
                BreakingNews=True,
                status='active'
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related("tags").order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Breaking news retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch breaking news"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
      
      
class UserNewsAPIView(PaginationMixin, APIView):
    """
    Get User News (Posts created by journalists)

    GET /api/news/user/

    Returns:
        - schedule_date < now
        - journalist is not null
        - status = active
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            current_datetime = timezone.now()

            queryset = NewsPost.objects.filter(
                schedule_date__lt=current_datetime,
                journalist_id__isnull=False,
                status='active'
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related(
                "tags"
            ).order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="User news retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch user news"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class EventsAPIView(PaginationMixin, APIView):
    """
    Get Events

    GET /api/news/events/
        → Default: Latest scheduled events

    GET /api/news/events/?type=upcoming
    GET /api/news/events/?type=past
    GET /api/news/events/?type=ongoing
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            event_type = request.query_params.get("type")
            current_datetime = timezone.now()

            base_queryset = NewsPost.objects.filter(
                Event=True,
                status='active'
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related("tags")

            # 🔹 Default → events (same as home view)
            if not event_type:
                queryset = base_queryset.filter(
                    schedule_date__lt=current_datetime
                ).order_by('-id')

            elif event_type == "upcoming":
                queryset = base_queryset.filter(
                    Event_date__gt=current_datetime
                ).order_by('Event_date')

            elif event_type == "past":
                queryset = base_queryset.filter(
                    Eventend_date__lt=current_datetime
                ).order_by('-Eventend_date')

            elif event_type == "ongoing":
                queryset = base_queryset.filter(
                    Event_date__lte=current_datetime,
                    Eventend_date__gte=current_datetime
                ).order_by('Eventend_date')

            else:
                return Response(
                    error_response("Invalid type. Use upcoming, past or ongoing."),
                    status=status.HTTP_400_BAD_REQUEST
                )

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            message = (
                f"{event_type.capitalize()} events retrieved successfully"
                if event_type else
                "Events retrieved successfully"
            )

            return self.get_paginated_response(
                serializer.data,
                message=message
            )

        except Exception:
            return Response(
                error_response("Failed to fetch events"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            
            

class LatestNewsAPIView(PaginationMixin, APIView):
    """
    Get Latest News

    GET /api/news/latest/

    Conditions:
        - schedule_date < now
        - is_active = 1
        - status = active
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            current_datetime = timezone.now()

            queryset = NewsPost.objects.filter(
                schedule_date__lt=current_datetime,
                is_active=1,
                status='active'
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related(
                "tags"
            ).order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Latest news retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch latest news"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class ProfilesAPIView(PaginationMixin, APIView):
    """
    Get Active Profiles (Non-journalist registration type)

    GET /api/profiles/
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            queryset = Journalist.objects.filter(
                status='active'
            ).exclude(
                registration_type='journalist'
            ).order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = JournalistListSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Profiles retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch profiles"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReelsAPIView(PaginationMixin, APIView):
    """
    Get Reels

    GET /api/videos/reels/

    Conditions:
        - is_active = active
        - video_type = reel
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            queryset = VideoNews.objects.filter(
                is_active='active',
                video_type='reel'
            ).order_by('-id')

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = VideoNewsSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Reels retrieved successfully"
            )

        except Exception as e:
            return Response(
                error_response(str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryListAPIView(PaginationMixin, APIView):
    """
    Get Categories List

    GET /api/categories/
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            queryset = category.objects.filter(
                cat_status='active'
            ).prefetch_related("sub_category_set").order_by("order")

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = CategoryListSerializer(
                paginated_queryset,
                many=True
            )

            return self.get_paginated_response(
                serializer.data,
                message="Categories retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch categories"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryNewsAPIView(PaginationMixin, APIView):
    """
    Get News Posts By Category

    GET /api/news/category/?category_id=1
    GET /api/news/category/?category_slug=politics
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            category_id = request.query_params.get("category_id")
            category_slug = request.query_params.get("category_slug")

            if not category_id and not category_slug:
                return Response(
                    error_response("category_id or category_slug is required"),
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch Category
            if category_id:
                category_obj = category.objects.filter(
                    id=category_id,
                    cat_status='active'
                ).first()
            else:
                category_obj = category.objects.filter(
                    cat_slug=category_slug,
                    cat_status='active'
                ).first()

            if not category_obj:
                return Response(
                    error_response("Category not found"),
                    status=status.HTTP_404_NOT_FOUND
                )

            current_datetime = timezone.now()

            subcategories = category_obj.sub_category_set.filter(
                subcat_status='active'
            )

            queryset = NewsPost.objects.filter(
                post_cat__in=subcategories,
                is_active=1,
                status='active',
                schedule_date__lte=current_datetime
            ).select_related(
                "post_cat",
                "journalist",
                "author"
            ).prefetch_related(
                "tags"
            ).order_by("-schedule_date")

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message=f"News posts for {category_obj.cat_name} retrieved successfully"
            )

        except Exception:
            return Response(
                error_response("Failed to fetch category news"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ArticlesAPIView(PaginationMixin, APIView):
    """
    Get Articles

    GET /api/news/articles/

    Returns:
        - status = active
        - schedule_date < now
        - articles = 1
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            current_datetime = timezone.now()

            queryset = NewsPost.objects.select_related(
                "journalist",
                "post_cat",
                "post_cat__sub_cat"
            ).prefetch_related(
                "tags"
            ).filter(
                status="active",
                schedule_date__lt=current_datetime,
                articles=True
            ).order_by("-id")

            paginated_queryset = self.paginate_queryset(queryset, request)

            serializer = NewsPostSerializer(
                paginated_queryset,
                many=True,
                context={"request": request}
            )

            return self.get_paginated_response(
                serializer.data,
                message="Articles retrieved successfully"
            )

        except Exception as e:
            return Response(
                error_response(str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
