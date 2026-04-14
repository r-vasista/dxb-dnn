from django.db import models


class Reel(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='reels/videos/', blank=True, null=True,
                                  help_text="Upload an MP4 video file")
    video_url = models.URLField(blank=True, null=True,
                                help_text="Or paste an external video URL (MP4 direct link)")
    thumbnail = models.ImageField(upload_to='reels/thumbnails/', blank=True, null=True,
                                  help_text="Optional thumbnail image shown before hover")
    category = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower number = shown first")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Reel'
        verbose_name_plural = 'Reels'

    def __str__(self):
        return self.title

    def get_video_src(self):
        """Return the best available video source."""
        if self.video_file:
            return self.video_file.url
        return self.video_url or ''