from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Django cache with persistent data'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing Django Cache with Persistent Data...')
        
        try:
            # Set a persistent value
            self.stdout.write('📝 Setting persistent cache value...')
            cache.set('persistent_test', 'cache_working_123', timeout=300)
            self.stdout.write(self.style.SUCCESS('✅ Persistent cache set'))
            
            # Verify it exists
            value = cache.get('persistent_test')
            if value == 'cache_working_123':
                self.stdout.write(self.style.SUCCESS(f'✅ Cache verified: {value}'))
                self.stdout.write(self.style.SUCCESS('🔑 Check Redis for key: dress_shop:persistent_test'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Cache verification failed: {value}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cache test failed: {e}'))
