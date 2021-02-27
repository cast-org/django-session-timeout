.. start-no-pypi

.. image:: https://dev.azure.com/lab-digital-opensource/django-session-timeout/_apis/build/status/labd.django-session-timeout?branchName=master
    :target: https://dev.azure.com/lab-digital-opensource/django-session-timeout/_build/latest?definitionId=2&branchName=master

.. image:: http://codecov.io/github/LabD/django-session-timeout/coverage.svg?branch=master
    :target: http://codecov.io/github/LabD/django-session-timeout?branch=master

.. image:: https://img.shields.io/pypi/v/django-session-timeout.svg
    :target: https://pypi.python.org/pypi/django-session-timeout/

.. image:: https://readthedocs.org/projects/django-session-timeout/badge/?version=stable
    :target: https://django-session-timeout.readthedocs.io/en/stable/?badge=stable
    :alt: Documentation Status

.. image:: https://img.shields.io/github/stars/labd/django-session-timeout.svg?style=social&logo=github
    :target: https://github.com/Labd/django-session-timeout/stargazers

.. end-no-pypi

======================
django-session-timeout
======================

Add timestamp to sessions to expire them after a given period of inactivity.

Installation
============

.. code-block:: shell

   pip install django-session-timeout


Usage
=====

Update your settings to add the SessionTimeoutMiddleware:

.. code-block:: python

    MIDDLEWARE_CLASSES = [
        # ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django_session_timeout.middleware.SessionTimeoutMiddleware',
        # ...
    ]

To enable the 'expiresessions' admin command, also add this to INSTALLED_APPS:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_session_timeout.apps.SessionTimeoutConfig',
        # ...
    ]


``SESSION_EXPIRE_AT_BROWSER_CLOSE`` should be set to True, so that sessions are closed when the user closes their browser.

Also add ``SESSION_EXPIRE_SECONDS`` to define when sessions should expire after going idle:


.. code-block:: python

    SESSION_EXPIRE_SECONDS = 3600  # 1 hour


By default, the session will expire X seconds after the start of the session.
To expire the session X seconds after the `last activity`, use the following setting:

.. code-block:: python

    SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True


By default, `last activity` will be updated on every request.
You can avoid some overhead, at the cost of some precision in expiry time, by only updating it if some time has passed
since the last update.  To so so, set a grace period as with this setting:

.. code-block:: python

    SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 60 # update at most once per minute

If you want to implement a friendly warning to users before their
session is forcibly timed out, you can define limits for when
such a warning should show up, and when the user should be logged
out if they do not respond to it.  Add these variables to your settings:

.. code-block:: python

    SESSION_IDLE_SECONDS = 600     # Show warning after 10 minutes
    SESSION_TIMEOUT_SECONDS = 1200 # After 10 more minutes, user will be logged off

This middleware does not implement the warning, but does
provide a couple of useful endpoints that you might need:
a "status" view that returns information abot the current session,
without itself being counted as activity that should reset the
idle time; and a "keepalive" URL that marks the session as active again.
