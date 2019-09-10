import time

from django.conf import settings
from django.contrib.auth.views import redirect_to_login

from .shared import SESSION_TIMEOUT_KEY, SESSION_USER_KEY
from .signals import user_timed_out

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "session") or request.session.is_empty():
            return

        sess = request.session

        # Set user if there is one for this session and not already set
        user = getattr(request, 'user', None)
        if not sess.get(SESSION_USER_KEY, None):
            if (user and getattr(user, 'is_authenticated', True)):
                sess[SESSION_USER_KEY] = user.pk

        # Set session start time if not already set.
        init_time = request.session.setdefault(SESSION_TIMEOUT_KEY, time.time())

        expire_seconds = getattr(
            settings, "SESSION_EXPIRE_SECONDS", settings.SESSION_COOKIE_AGE
        )

        session_is_expired = time.time() - init_time > expire_seconds

        if session_is_expired:
            user_timed_out.send(sender=self.__class__, user=user, session=sess)
            request.session.flush()
            if hasattr(request, 'user'):
                from django.contrib.auth.models import AnonymousUser
                request.user = AnonymousUser()
            return redirect_to_login(next=request.path)

        expire_since_last_activity = getattr(
            settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY", False
        )
        grace_period = getattr(
            settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD", 1
        )

        if expire_since_last_activity and time.time() - init_time > grace_period:
            request.session[SESSION_TIMEOUT_KEY] = time.time()
