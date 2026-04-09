print("signals.py loaded")
from allauth.account.signals import user_logged_in, user_signed_up
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(user_signed_up)
def google_login_first_time(request, user, **kwargs):
    """
    Triggered when a user signs up via social login.
    Ensures a Profile exists and sets a session flag if role is not set.
    """
    print("user_signed_up triggered for:", user.email)
    profile, created = Profile.objects.get_or_create(user=user)

    if not profile.role:
        request.session['ask_role'] = True
        print("ask_role set in session")


@receiver(user_logged_in)
def check_role_after_login(request, user, **kwargs):
    print("user_logged_in triggered for:", user.email)
    if not getattr(user.profile, 'role', None):
        request.session['ask_role'] = True
        print("ask_role set in session (login)")
