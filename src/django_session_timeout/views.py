from django.http import HttpResponse

from .shared import expire_sessions

def expire(request):
    expire_sessions()
    return HttpResponse("OK", content_type="text/plain")
