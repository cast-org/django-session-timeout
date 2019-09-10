from django.dispatch import Signal

user_timed_out = Signal(providing_args=['session', 'user'])
