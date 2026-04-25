from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import VisitorLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def check_bot_status(user_agent):
    """
    Returns (is_bot, should_block)
    """
    if not user_agent:
        return False, False

    ua = user_agent.lower()

    # 1. SEO / Good Bots (Allow these)
    good_bots = [
        'googlebot', 'bingbot', 'yandexbot', 'duckduckbot', 
        'baiduspider', 'facebot', 'facebookexternalhit', 
        'twitterbot', 'linkedinbot', 'slackbot'
    ]

    # 2. Aggressive / Scraping / AI Bots (Block these)
    bad_bots = [
        # AI / LLM
        'gptbot', 'chatgpt-user', 'ccbot', 'anthropic', 'claude', 'cohere',
        # SEO Tools (Often heavy crawlers)
        'ahrefs', 'semrush', 'mj12bot', 'dotbot', 'screaming frog',
        # Generic & Scrapers
        'bot', 'crawl', 'spider', 'slurp', 'scrapy', 'mechanize',
        'headlesschrome', 'phantomjs', 'puppeteer', 'playwright',
        'python-requests', 'curl', 'wget', 'bytespider', 'petalbot'
    ]

    is_seo_bot = any(keyword in ua for keyword in good_bots)
    is_malicious_bot = any(keyword in ua for keyword in bad_bots)

    if is_seo_bot:
        return True, False  # It's a bot, but don't block
    elif is_malicious_bot:
        return True, True   # It's a bot, and block it
    
    return False, False

class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            path = request.path.lower()

            if request.method != "GET" or path.startswith(('/admin', '/adminview')) or '.' in path:
                return

            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Get the status from our new helper
            is_any_bot, should_block = check_bot_status(user_agent)

            VisitorLog.objects.create(
                ip_address=ip,
                user_agent=user_agent,
                path=path,
                method=request.method,
                is_bot=is_any_bot,
                is_blocked=should_block,
            )

            if should_block:
                return HttpResponseForbidden("Access denied.")

        except Exception as e:
            print("Tracking error:", e)