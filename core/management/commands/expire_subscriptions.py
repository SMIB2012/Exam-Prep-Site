"""
Management command to expire old subscriptions
"""
from django.core.management.base import BaseCommand
from core.utils.payment_check import auto_expire_subscriptions


class Command(BaseCommand):
    help = 'Expire old subscriptions automatically'

    def handle(self, *args, **options):
        expired_count = auto_expire_subscriptions()
        
        if expired_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully expired {expired_count} subscriptions')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No subscriptions needed to be expired')
            )
