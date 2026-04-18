from django.db import models
from autoslug import AutoSlugField
from image_cropping import ImageCropField, ImageRatioField
from PIL import Image
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
#from embed_video.fields import EmbedVideoField
from journalist.models import Journalist
from autoslug import AutoSlugField

from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import os

class category(models.Model):
    cat_name=models.CharField(max_length=255,unique=True,null=True,default=None)
    cat_slug=AutoSlugField(populate_from='cat_name',unique=True,null=True,default=None)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    cat_status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    order=models.IntegerField(unique=True,null=True,default=None,verbose_name="Order")
    def __str__(self):
        return self.cat_name

class sub_category(models.Model):
    sub_cat=models.ForeignKey("category", verbose_name="Select Cetegory",null=True,default=None,on_delete=models.CASCADE)
    subcat_name=models.CharField(max_length=255,unique=True,null=True,default=None)
    subcat_slug=AutoSlugField(populate_from='subcat_name',unique=True,null=True,default=None)
    subcat_tag=models.TextField(null=True,default="#trending #latest", verbose_name="Cat tag")
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    subcat_status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    order=models.IntegerField(unique=True,null=True,default=None,verbose_name="Order")
    def __str__(self):
        return self.sub_cat.cat_name + " / " + self.subcat_name


class Tag(models.Model):
    name = models.CharField(max_length=500, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    create_date=models.DateTimeField(default=timezone.now)
    is_active=models.BooleanField(verbose_name="Status", null=True, default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('posts_by_tag', args=[self.slug])
      

class NewsPost(models.Model):
    post_cat=models.ForeignKey("sub_category", verbose_name="Select Cetegory",null=True,default=None,on_delete=models.CASCADE)
    post_title=models.CharField(max_length=150, verbose_name="News Head Line",null=True,default=None)
    meta_title=models.CharField(max_length=150, verbose_name="Meta Title(35 to 65 chr standard)",null=True,default=None)
    slug=AutoSlugField(max_length=200, populate_from='meta_title',unique=True,default=None,
    always_update=False,
    editable=True)
    post_short_des=models.CharField(max_length=160, verbose_name="Short Discretion",null=True,default=None)
    post_des=RichTextUploadingField(null=True,default='No News', verbose_name="Long Discretion")
    # post_image=models.FileField(upload_to="blog/", max_length=255,null=True,default=None)
    post_image = ImageCropField(upload_to='newsimage/%Y/%m/%d', max_length=255,null=True,default=None, verbose_name="News Image (1280X720px)")
    #image_crop = ImageRatioField('post_image', '430x360')
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.post_image:
            return

        try:
            original_path = self.post_image.path
            base, ext = os.path.splitext(original_path)

            # Skip if already WEBP
            if ext.lower() == ".webp":
                return

            # Convert to WEBP in memory
            with Image.open(original_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img.thumbnail((1280, 720))

                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=85)
                buffer.seek(0)

            # New file name
            webp_filename = os.path.basename(base) + ".webp"

            # Delete old file BEFORE saving new
            if os.path.exists(original_path):
                os.remove(original_path)

            # Save new WEBP file
            self.post_image.save(webp_filename, ContentFile(buffer.read()), save=False)

            # Update DB without recursion
            super().save(update_fields=["post_image"])

        except Exception as e:
            print("Image conversion error:", e)
    
    post_tag=models.TextField(null=True,default="#trending #latest", verbose_name="News tag")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
        
    is_active=models.BooleanField(verbose_name="Latest News", null=True, default=True)
    Head_Lines=models.BooleanField(verbose_name="Head Lines", null=True, default=False)
    articles=models.BooleanField(verbose_name="Articles", null=True, default=False)
    trending=models.BooleanField(verbose_name="Trending", null=True, default=False)
    BreakingNews=models.BooleanField(verbose_name="Breaking News", null=True, default=False)
    Event=models.BooleanField(verbose_name="Upcoming Event", null=True, default=False)
    
    Event_date=models.DateField(unique=False,null=False,default=timezone.now,verbose_name="Event Start Date")
    Eventend_date=models.DateField(unique=False,null=False,default=timezone.now,verbose_name="Event End Date")
    schedule_date=models.DateTimeField(unique=False,null=False,default=timezone.now,verbose_name="Schedule Date")
    post_date=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    viewcounter = models.IntegerField(unique=False,null=True,default=0,verbose_name="Views")
    post_status=models.IntegerField(verbose_name="Counter",null=True,default=100)
    order=models.IntegerField(unique=False,null=True,default=5,verbose_name="Order")
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    journalist = models.ForeignKey(Journalist, on_delete=models.CASCADE, null=True, blank=True, default=None)
    
    @property
    def thumbnail_url(self):
        """
        Returns thumbnail URL if exists (WEBP > JPG > JPEG > PNG),
        else returns original image URL.
        """

        if not self.post_image:
            return ""

        original_url = self.post_image.url
        original_path = self.post_image.path

        base_name, _ = os.path.splitext(os.path.basename(original_path))
        root_dir = os.path.dirname(original_path)
        thumb_dir = os.path.join(root_dir, "thumbnails")

        # Priority order: fastest → fallback
        thumbnail_extensions = [".webp", ".jpg", ".jpeg", ".png"]

        for ext in thumbnail_extensions:
            thumb_path = os.path.join(thumb_dir, f"{base_name}{ext}")
            if os.path.exists(thumb_path):
                return original_url.replace(
                    os.path.basename(original_url),
                    f"thumbnails/{base_name}{ext}"
                )

        # Fallback to original image
        return original_url
    
    @property
    def total_views(self):
        """
        Combines the base Counter (post_status) and actual Views (viewcounter).
        Handles cases where either might be None.
        """
        base_count = self.post_status if self.post_status else 0
        actual_views = self.viewcounter if self.viewcounter else 0
        return base_count + actual_views

    def get_posted_by(self):
        if self.journalist:
            return self.journalist.username
        elif self.author:
            return self.author.username
        return "Unknown"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.author and not self.journalist:
            raise ValidationError("A post must have either an author or a journalist.")
        if self.author and self.journalist:
            raise ValidationError("A post cannot have both an author and a journalist.")
    
    def __str__(self):
        return self.post_title
        
    def get_absolute_url(self):
         return reverse('newsdetails', args=[self.slug])


class VideoNews(models.Model):
    News_Category =models.ForeignKey("sub_category", verbose_name="Select Category",null=True,default=None,on_delete=models.CASCADE)
    VIDEO_CHOICES = (
        ('video', 'Video'),
        ('reel', 'Reel'),
    )
    video_type = models.CharField(max_length=8, choices=VIDEO_CHOICES, default='video', verbose_name="Video Type")
    video_title=models.CharField(max_length=150, verbose_name="Title (Lenth 60 Char)",null=True,default=None)
    slug=AutoSlugField(populate_from='video_title',unique=True,null=True,default=None)
    video_short_des=models.CharField(max_length=160, verbose_name="Meta/Short Des",null=True,default=None)
    video_des=RichTextUploadingField(null=True,default=None, verbose_name="Video Discretion")
    video_url=models.CharField(verbose_name="Youtube Video URL",max_length=255,default=True,null=True)
    video_thumbnail = ImageCropField(upload_to='thumbnail/', max_length=255,null=True,default='thumbnail/na.jpg',blank=True, verbose_name="Thumbnail (1280X720px)")
    video_tag=models.CharField(max_length=255,null=True,default=0)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    schedule_date=models.DateTimeField(unique=False,null=False,default=timezone.now,verbose_name="Schedule Date")
    video_date=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    viewcounter = models.IntegerField(unique=False,null=True,default=0,verbose_name="Views", editable=False)
    counter = models.IntegerField(unique=False,null=True,default=0,verbose_name="counter")
    order=models.IntegerField(unique=False,null=True,default=5,verbose_name="Order")
    Head_Lines=models.BooleanField(verbose_name="Head Lines", null=True, default=False)
    articles=models.BooleanField(verbose_name="Articles", null=True, default=False)
    trending=models.BooleanField(verbose_name="Trending", null=True, default=False)
    BreakingNews=models.BooleanField(verbose_name="Breaking News", null=True, default=False)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('rejected', 'Rejected'),
    )
    is_active = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    journalist = models.ForeignKey(Journalist, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def get_posted_by(self):
        if self.journalist:
            return self.journalist.username
        elif self.author:
            return self.author.username
        return "Unknown"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.author and not self.journalist:
            raise ValidationError("A post must have either an author or a journalist.")
        if self.author and self.journalist:
            raise ValidationError("A post cannot have both an author and a journalist.")
        
    def __str__(self):
        return self.video_title
    
    def get_absolute_url(self):
        return reverse('videonewsdetails', args=[self.slug])


class CMS(models.Model):
    pagename=models.CharField(max_length=150, verbose_name="News Head Line",null=True,default=None)
    Content=RichTextUploadingField(null=True,default='No News', verbose_name="Long Discretion")
    pageimage = ImageCropField(upload_to='cms/', max_length=255,null=True,default=None, verbose_name="Page Image (1280X220px)")
    #image_crop = ImageRatioField('post_image', '430x360')
    
    def save(self, *args, **kwargs):
        # Override the save method to resize the image before saving
        super(CMS, self).save(*args, **kwargs)
        # Open the image
        img = Image.open(self.pageimage.path)
        # Set the desired size for cropping (width, height)
        desired_size = (1280, 220)
        # Resize the image while maintaining the aspect ratio
        img.thumbnail(desired_size)
        # Save the resized image back to the original path
        img.save(self.pageimage.path)
    
    slug=AutoSlugField(max_length=200, populate_from='pagename',unique=True,null=True,default=None)
    post_date=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    viewcounter = models.IntegerField(unique=False,null=True,default=0,verbose_name="Views")
    post_status=models.IntegerField(verbose_name="Counter",null=True,default=100)
    order=models.IntegerField(unique=False,null=True,default=5,verbose_name="Order")
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1) 
    
    def __str__(self):
        return self.pagename
    def get_absolute_url(self):
         return reverse('cms', args=[self.slug])
     
class slider(models.Model):
    slidercat=models.ForeignKey("sub_category", verbose_name="Select Cetegory",null=True,default=None,on_delete=models.CASCADE)
    title=models.CharField(max_length=200, verbose_name="News Head Line",null=True,default=None)
    des=models.CharField(max_length=300, verbose_name="Short Discretion",null=True,default=None)
    sliderimage = ImageCropField(upload_to='blog/', max_length=255,null=True,default=None, verbose_name="Slider Image (1400X520px)")
    #image_crop = ImageRatioField('post_image', '430x360')
    
    def save(self, *args, **kwargs):
        # Override the save method to resize the image before saving
        super(slider, self).save(*args, **kwargs)
        # Open the image
        img = Image.open(self.sliderimage.path)
        # Set the desired size for cropping (width, height)
        desired_size = (1400, 520)
        # Resize the image while maintaining the aspect ratio
        img.thumbnail(desired_size)
        # Save the resized image back to the original path
        img.save(self.sliderimage.path)
    
    slug=AutoSlugField(max_length=200, populate_from='slidercat',unique=True,null=True,default=None)
    post_date=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order=models.IntegerField(unique=False,null=True,default=5,verbose_name="Order")
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1) 
    
    def __str__(self):
        return self.slidercat

class AppUser(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    email = models.EmailField(max_length=255, unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=255, verbose_name="Password")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Phone")
    
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



class NewsRedirect(models.Model):
    """
    Model to store redirects for deleted/moved news posts.
    This helps preserve SEO value by redirecting old URLs to similar content.
    """
    old_slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="The slug of the deleted/old news post"
    )
    redirect_slug = models.SlugField(
        max_length=255,
        db_index=True,
        help_text="The slug to redirect to (similar news post)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable this redirect"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about why this redirect was created"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.old_slug} → {self.redirect_slug}"

    def clean(self):
        """Validate that old_slug and redirect_slug are different"""
        if self.old_slug == self.redirect_slug:
            raise ValidationError("Old slug and redirect slug cannot be the same")


class VisitorLog(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)

    is_bot = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False) 

    entry_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path}"
