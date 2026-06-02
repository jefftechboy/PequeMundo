from django.apps import AppConfig
import os
import threading


api_iniciada = False


class AppConfigPrincipal(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        global api_iniciada

        if os.environ.get('RUN_MAIN') != 'true':
            return

        if api_iniciada:
            return

        api_iniciada = True

        def iniciar_api():
            from app.ServidorRest import ejecutar_servidor
            ejecutar_servidor()

        hilo = threading.Thread(
            target=iniciar_api,
            daemon=True
        )

        hilo.start()
