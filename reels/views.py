from django.shortcuts import render
from django.http import JsonResponse
from .models import Reel


def reels_list(request):
    """Standalone page showing all reels (optional)."""
    reels = Reel.objects.filter(is_active=True)
    return render(request, 'reels/reels_page.html', {'reels': reels})


def reels_api(request):
    """JSON endpoint — useful if you ever want to load reels via fetch/AJAX."""
    reels = Reel.objects.filter(is_active=True).values(
        'id', 'title', 'category', 'order'
    )
    return JsonResponse({'reels': list(reels)})


def get_active_reels():
    """
    Helper used by other views (e.g. home view) to inject reels
    into a shared context without a separate request.

    Usage in your home view:
        from reels.views import get_active_reels
        context['reels'] = get_active_reels()
    """
    return Reel.objects.filter(is_active=True)