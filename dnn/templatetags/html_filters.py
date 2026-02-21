from django import template
from html import unescape

register = template.Library()

@register.filter
def unescape_html(value):
    """Decode HTML entities in a string (e.g., &amp;ndash; to –)"""
    if value:
        return unescape(str(value))
    return value or ""

