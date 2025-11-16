from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import SellerProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create seller profiles for users with role "seller" or "both" who do not have one'

    def handle(self, *args, **options):
        # Find users with seller/both role but no seller profile
        users_without_profile = User.objects.filter(
            role__in=['seller', 'both']
        ).exclude(
            seller_profile__isnull=False
        )
        
        created_count = 0
        for user in users_without_profile:
            try:
                SellerProfile.objects.create(
                    user=user,
                    brand_name='',
                    biography='',
                    business_phone='',
                    website='',
                    social_media_links={}
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created seller profile for user: {user.username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create seller profile for {user.username}: {str(e)}')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} seller profile(s)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No missing seller profiles found')
            )
