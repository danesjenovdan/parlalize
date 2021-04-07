from django.apps import AppConfig
class UtilsConfig(AppConfig):
    name = 'utils'
    verbose_name = "Utils"
    def ready(self):
        from .recache import getAllStaticData, getSessionsList
        print("recache on ready")
        # getAllStaticData(None)
        #getSessionsList(None)