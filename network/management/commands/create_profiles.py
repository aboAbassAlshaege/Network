# network/management/commands/create_profiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from network.models import Profile

class Command(BaseCommand):
    help = "Create profiles for existing users who don't have one."

    def handle(self, *args, **kwargs):
        User = get_user_model()  # Get the custom user model

        # Loop through all users and create profiles if they don't have one
        for user in User.objects.all():
            if not hasattr(user, 'profile'):  # Check if the user has a related profile
                Profile.objects.create(user=user)  # Create a profile for the user
                self.stdout.write(self.style.SUCCESS(f'Profile created for user: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User {user.username} already has a profile'))
