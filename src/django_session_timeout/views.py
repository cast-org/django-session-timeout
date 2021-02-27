import time

from django.http import HttpResponse, JsonResponse

from .shared import expire_sessions, get_session_timeout_setting, get_session_idle_setting, \
    SESSION_TIMEOUT_KEY


def status(request):
    """
    Return information on the status of the current session, without updating it.

    If there is no session with timing information, returns {"status": "EXPIRED"}.

    Otherwise current idle time is returned, and a status value depending on how this
    compares to the limits configured into your application, something like this:
    {"status": "ACTIVE", "idleTime": 63, "idleLimit": 600, "timeoutLimit": 1500}

    ACTIVE status means there has been recent activity.

    IDLE means that the session has been idle for long enough that an "are-you-there" message
    should be shown to the user.  Settings variable: SESSION_IDLE_SECONDS.

    TIMEOUT means that the user should be logged out by the client. Settings variable: SESSION_TIMEOUT_SECONDS.

    The middleware treats this URL specially, so that accessing it will not reset the idle time,
    unless query arg "keepalive" is true.
    """
    init_time = request.session.get(SESSION_TIMEOUT_KEY, None)
    if not init_time:
        return JsonResponse({
            'status': 'EXPIRED',
        })
    seconds_since_last_activity = time.time() - init_time
    idle_limit = get_session_idle_setting()
    timeout_limit = get_session_timeout_setting()
    if init_time:
        if timeout_limit and seconds_since_last_activity > timeout_limit:
            status = 'TIMEOUT'
        elif seconds_since_last_activity > idle_limit:
            status = 'IDLE'
        else:
            status = 'ACTIVE'
    else:
        status = 'NEW'
    return JsonResponse({
        'status': status,
        'idleTime': int(seconds_since_last_activity),
        'idleLimit': idle_limit,
        'timeoutLimit': timeout_limit,
    })


def keepalive(request):
    """
    Refresh session and return its status.

    This is the same as the status view, but does not get special treatment,
    so the session will be marked as not idle by the middleware.
    Can be used as a simple way to keep the session alive.
    """
    return status(request)


def expire(request):
    """
    Remove all sessions from the session store that are beyond their expiry time.
    """
    expire_sessions()
    return HttpResponse("OK", content_type="text/plain")
