from django.apps import AppConfig
from django.core.cache import cache


class LicenseApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "license_api"

    def ready(self):
        self.clear_cache_on_start()

    def clear_cache_on_start(self):
        try:
            cache.delete('start_date_time')
        except Exception as e:
            print(f"⚠️ Ошибка при очистке кэша: {e}")
