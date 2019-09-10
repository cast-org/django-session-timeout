import time
import logging
from importlib import import_module
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...signals import user_timed_out
from django.utils import timezone
from django.conf import settings
from ...shared import SESSION_TIMEOUT_KEY, SESSION_USER_KEY

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = (
        "Can be run as a cronjob or directly to clean out expired sessions "
        "(only with the database backend at the moment)."
    )

    def handle(self, **options):
        expire_seconds = getattr(settings, "SESSION_EXPIRE_SECONDS", settings.SESSION_COOKIE_AGE)
        engine = import_module(settings.SESSION_ENGINE)
        sesses = engine.SessionStore.get_model_class().objects.all()
        for sess in sesses:
            if (self.is_expired(sess)):
                userId = sess.get_decoded().get(SESSION_USER_KEY, None)
                user = User.objects.get(id=userId) if userId else None
                user_timed_out.send(sender=self.__class__, user=user, session=sess.get_decoded())
                logger.info("Removing expired session for %s: %s", user, sess)
                # sess.delete()
            else:
                logger.debug("Not removing user %s session %s", sess.get_decoded().get(SESSION_USER_KEY, None), sess)


    def is_expired(self, sess):
        "Return True if session is past its expiry time"
        init_time = sess.get_decoded().get(SESSION_TIMEOUT_KEY, None)
        if (init_time):
            expire_seconds = getattr(settings, "SESSION_EXPIRE_SECONDS", settings.SESSION_COOKIE_AGE)
            return  (time.time() - init_time > expire_seconds)
        else:
            # Custom attribute is not set, go by standard Django expiry rules
            return (sess.expire_date < timezone.now())
