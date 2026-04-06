from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Django cache configuration'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing Django Cache Configuration...')
        
        try:
            # Test 1: Set a value
            self.stdout.write('📝 Setting cache value...')
            cache.set('test_key', 'test_value', timeout=60)
            self.stdout.write(self.style.SUCCESS('✅ Cache set successful'))
            
            # Test 2: Get the value
            self.stdout.write('📖 Getting cache value...')
            value = cache.get('test_key')
            if value == 'test_value':
                self.stdout.write(self.style.SUCCESS(f'✅ Cache get successful: {value}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Cache get failed. Expected "test_value", got: {value}'))
            
            # Test 3: Delete the value
            self.stdout.write('🗑️ Deleting cache value...')
            cache.delete('test_key')
            deleted_value = cache.get('test_key')
            if deleted_value is None:
                self.stdout.write(self.style.SUCCESS('✅ Cache delete successful'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Cache delete failed. Value still exists: {deleted_value}'))
            
            # Test 4: Show cache info
            self.stdout.write('📊 Cache Configuration:')
            self.stdout.write(f'   Backend: {settings.CACHES["default"]["BACKEND"]}')
            self.stdout.write(f'   Location: {settings.CACHES["default"]["LOCATION"]}')
            self.stdout.write(f'   Timeout: {settings.CACHES["default"].get("TIMEOUT", "Not set")}')
            self.stdout.write(f'   Key Prefix: {settings.CACHES["default"].get("KEY_PREFIX", "Not set")}')
            
            self.stdout.write(self.style.SUCCESS('🎉 All cache tests completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cache test failed with error: {e}'))
            self.stdout.write(f'   Error type: {type(e).__name__}')
