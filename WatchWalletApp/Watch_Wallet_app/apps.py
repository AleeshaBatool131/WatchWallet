from django.apps import AppConfig


class WatchWalletAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Watch_Wallet_app'

    def ready(self):
        import Watch_Wallet_app.signals
