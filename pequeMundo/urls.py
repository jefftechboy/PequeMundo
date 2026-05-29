"""
URL configuration for pequeMundo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from app.views import crear_preferencia_mp, pago_exitoso, pago_fallido, pago_pendiente, webhook_mp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('pago/iniciar/', crear_preferencia_mp, name='crear_preferencia_mp'),
    path('pago/exitoso/', pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/', pago_fallido, name='pago_fallido'),
    path('pago/pendiente/', pago_pendiente, name='pago_pendiente'),
    path('pago/webhook/', webhook_mp, name='webhook_mp'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
