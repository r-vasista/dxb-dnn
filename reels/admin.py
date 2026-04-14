from django.contrib import admin
from .models import Reel


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'category')
    search_fields = ('title', 'category')
    ordering = ('order', '-created_at')