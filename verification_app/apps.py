from django.apps import AppConfig


class VerificationAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'verification_app'

    def ready(self):
        import verification_app.signals