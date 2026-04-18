# middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import VisitorLog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def is_bot(user_agent):
    if not user_agent:
        return False

    bot_keywords = [
        # Generic
        'bot', 'crawl', 'spider', 'slurp',

        # Search engines
        'googlebot', 'bingbot', 'yandexbot', 'duckduckbot', 'baiduspider',

        # Social media crawlers
        'facebookexternalhit', 'facebot', 'twitterbot', 'linkedinbot', 'embedly',

        # SEO tools
        'ahrefs', 'semrush', 'mj12bot', 'dotbot', 'screaming frog',

        # Monitoring / uptime
        'uptimerobot', 'pingdom', 'statuscake',

        # Headless browsers / automation
        'headlesschrome', 'phantomjs', 'puppeteer', 'playwright',

        # HTTP clients / scripts
        'python-requests', 'curl', 'wget', 'httpclient', 'libwww',

        # Scrapers
        'scrapy', 'mechanize',

        # AI / LLM crawlers
        'gptbot', 'chatgpt-user', 'ccbot', 'anthropic', 'claude', 'cohere',

        # Misc aggressive crawlers
        'archive.org_bot', 'ia_archiver', 'petalbot', 'bytespider'
    ]

    ua = user_agent.lower()
    return any(keyword in ua for keyword in bot_keywords)


class VisitorTrackingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            path = request.path.lower()

            if request.method != "GET":
                return

            if path.startswith('/admin') or path.startswith('/adminview'):
                return

            if '.' in path:
                return

            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            bot_detected = is_bot(user_agent)

            VisitorLog.objects.create(
                ip_address=ip,
                user_agent=user_agent,
                path=path,
                method=request.method,
                is_bot=bot_detected,
                is_blocked=bot_detected,  # blocked if and only if it's a bot
            )

            if bot_detected:
                return HttpResponseForbidden("Access denied.")

        except Exception as e:
            print("Tracking error:", e)