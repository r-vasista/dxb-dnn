from rest_framework import serializers
from post_management.models import category, sub_category, NewsPost , VideoNews, AppUser
from journalist.models import Journalist
from Ad_management.models import ad

from django.contrib.auth.hashers import make_password


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = sub_category
        fields = [
            'id',
            'subcat_name',
            'subcat_slug',
            'subcat_tag',
            'order',
        ]


class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = category
        fields = [
            'id',
            'cat_name',
            'cat_slug',
            'order',
            'sub_categories',
        ]

    def get_sub_categories(self, obj):
        subcats = sub_category.objects.filter(
            sub_cat=obj,
            subcat_status='active'
        ).order_by('order')

        return SubCategorySerializer(subcats, many=True).data


class NewsListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    posted_by = serializers.CharField(source='get_posted_by', read_only=True)

    # 🔹 Existing (names)
    subcategory = serializers.CharField(
        source='post_cat.subcat_name',
        read_only=True
    )
    category = serializers.CharField(
        source='post_cat.sub_cat.cat_name',
        read_only=True
    )

    # 🔹 NEW (IDs – APK ke liye IMPORTANT)
    subcategory_id = serializers.IntegerField(
        source='post_cat.id',
        read_only=True
    )
    category_id = serializers.IntegerField(
        source='post_cat.sub_cat.id',
        read_only=True
    )

    class Meta:
        model = NewsPost
        fields = [
            'id',
            'post_title',
            'slug',
            'post_short_des',
            'image',
            'post_des',

            # 👇 NEW
            'subcategory_id',
            'subcategory',
            'category_id',
            'category',

            'posted_by',
            'post_date',
            'viewcounter',
            'BreakingNews',
            'trending',
        ]

    def get_image(self, obj):
        if obj.post_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.post_image.url)
        return None


class VideoListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    posted_by = serializers.CharField(source='get_posted_by', read_only=True)

    # 🔹 Existing (names)
    subcategory = serializers.CharField(
        source='News_Category.subcat_name',
        read_only=True
    )
    category = serializers.CharField(
        source='News_Category.sub_cat.cat_name',
        read_only=True
    )

    # 🔹 NEW (IDs – APK ke liye IMPORTANT)
    subcategory_id = serializers.IntegerField(
        source='News_Category.id',
        read_only=True
    )
    category_id = serializers.IntegerField(
        source='News_Category.sub_cat.id',
        read_only=True
    )

    class Meta:
        model = VideoNews
        fields = [
            'id',
            'video_type',
            'video_title',
            'video_short_des',
            'video_url',
            'video_des',
            'thumbnail',

            # 👇 NEW
            'subcategory_id',
            'subcategory',
            'category_id',
            'category',

            'posted_by',
            'video_date',
            'viewcounter',
            'BreakingNews',
            'trending',
        ]

    def get_thumbnail(self, obj):
        if obj.video_thumbnail:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.video_thumbnail.url)
        return None


class SearchNewsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategory_id = serializers.IntegerField(source='post_cat.id', read_only=True)
    category_id = serializers.IntegerField(source='post_cat.sub_cat.id', read_only=True)

    class Meta:
        model = NewsPost
        fields = [
            'id',
            'post_title',
            'image',
            'subcategory_id',
            'category_id',
            'post_date',
        ]

    def get_image(self, obj):
        if obj.post_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.post_image.url)
        return None


class SearchVideoSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    subcategory_id = serializers.IntegerField(source='News_Category.id', read_only=True)
    category_id = serializers.IntegerField(source='News_Category.sub_cat.id', read_only=True)

    class Meta:
        model = VideoNews
        fields = [
            'id',
            'video_title',
            'thumbnail',
            'subcategory_id',
            'category_id',
            'video_date',
        ]

    def get_thumbnail(self, obj):
        if obj.video_thumbnail:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.video_thumbnail.url)
        return None

class AppUserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'name', 'email', 'password', 'phone', 'city', 'country']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Password hashing
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class AppUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class AppUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['name', 'phone', 'city', 'country']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.save()
        return instance


class JournalistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journalist
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'registration_type']


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ad
        fields = ['id', 'ad_url', 'ad_type', 'ad_image']
