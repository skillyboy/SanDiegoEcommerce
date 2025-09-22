from django.apps import AppConfig


class AgroLinkerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agro_linker'
    verbose_name = 'Agro Linker'

    def ready(self):
        # Import signal handlers and other startup registration here so
        # they run exactly once when Django loads apps. This avoids
        # duplicate model registration warnings caused by import-time
        # side effects in modules that import models directly.
        try:
            # Import the signals module if it exists. Keep import local to
            # avoid top-level side-effects during app import.
            import agro_linker.signals  # noqa: F401
        except Exception:
            # Signals module is optional; swallow exceptions to avoid
            # breaking startup if the module is not present.
            pass
