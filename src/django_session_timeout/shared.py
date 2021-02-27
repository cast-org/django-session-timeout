import logging
import time
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from .signals import user_timed_out

logger = logging.getLogger(__name__)

# Shared constants

SESSION_TIMEOUT_KEY = "_session_init_timestamp_"

SESSION_USER_KEY = "_session_user_"


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


def is_expired(sess):
    """Return True if session is past its expiry time.

    This is for encoded, out-of-view session objects."""
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


def get_session_timeout_setting():
    return getattr(settings, "SESSION_TIMEOUT_SECONDS", None)
