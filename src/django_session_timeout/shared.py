import logging
import time
from enum import IntEnum
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from .signals import user_timed_out

logger = logging.getLogger(__name__)

# Shared constants

SESSION_TIMEOUT_KEY = "_session_init_timestamp_"

SESSION_USER_KEY = "_session_user_"


class SessionStatus(IntEnum):
    """
    Constants for indicating where a session is with respect to expiring due to inactivity.

    NEW indicates a session where no activity has yet been recorded.
    ACTIVE is a session where there has been recent activity.
    IDLE means that the session has been idle for long enough that an "are-you-there" message should be shown to the user.
    OVERDUE means that the user should be gracefully logged out at the next opportunity.
    EXPIRED means that the session should be forcefully removed.

    Relevant settings variables: SESSION_IDLE_SECONDS, SESSION_OVERDUE_SECONDS, SESSION_EXPIRE_SECONDS.
    If these are not set sessions will not go through the intermediate stages and will just be reported
    as ACTIVE or EXPIRED.
    """
    NEW = 0
    ACTIVE = 1
    IDLE = 2
    OVERDUE = 3
    EXPIRED = 4


def expire_sessions():
    engine = import_module(settings.SESSION_ENGINE)
    sesses = engine.SessionStore.get_model_class().objects.all()
    for sess in sesses:
        if (is_expired(sess)):
            userId = sess.get_decoded().get(SESSION_USER_KEY, None)
            user = User.objects.get(id=userId) if userId else None
            user_timed_out.send(sender=user.__class__, user=user, session=sess.get_decoded())
            logger.info("Removing expired session for %s: %s", user, sess)
            sess.delete()
        else:
            logger.debug("Not removing active for %s: %s", sess.get_decoded().get(SESSION_USER_KEY, None), sess)


def session_status(sess):
    """Return the current SessionStatus of the session based on whether there is recent activity."""
    if is_expired(sess):
        return SessionStatus.EXPIRED
    init_time = sess.get_decoded().get(SESSION_TIMEOUT_KEY, None)
    if not init_time:
        return SessionStatus.NEW
    seconds_since_last_activity = time.time() - init_time
    overdue_limit = get_session_overdue_setting()
    if overdue_limit and seconds_since_last_activity > overdue_limit:
        return SessionStatus.OVERDUE
    idle_limit = get_session_idle_setting()
    if seconds_since_last_activity > idle_limit:
        return SessionStatus.IDLE
    return SessionStatus.ACTIVE


def is_expired(sess):
    "Return True if session is past its expiry time"
    init_time = sess.get_decoded().get(SESSION_TIMEOUT_KEY, None)
    if init_time:
        expire_seconds = get_session_expire_setting()
        return time.time() - init_time > expire_seconds
    else:
        # Custom attribute is not set, go by standard Django expiry rules
        return sess.expire_date < timezone.now()


def get_session_expire_setting():
    return getattr(settings, "SESSION_EXPIRE_SECONDS", settings.SESSION_COOKIE_AGE)


def get_session_idle_setting():
    return getattr(settings, "SESSION_IDLE_SECONDS", None)


def get_session_overdue_setting():
    return getattr(settings, "SESSION_OVERDUE_SECONDS", None)
