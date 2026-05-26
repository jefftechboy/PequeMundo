from django.contrib import admin
from .models import *

class BaseAdmin(admin.ModelAdmin):

    def get_list_display(self, request):

        return [field.name for field in self.model._meta.fields]
    
# Register your models here.
admin.site.register(estadoMueble,BaseAdmin)
admin.site.register(disponiblidadMueble,BaseAdmin)
admin.site.register(mueble,BaseAdmin)
admin.site.register(comuna,BaseAdmin)
admin.site.register(tipoCuenta,BaseAdmin)
admin.site.register(cuenta,BaseAdmin)
admin.site.register(tipoEnvio,BaseAdmin)
admin.site.register(envio,BaseAdmin)
admin.site.register(compra,BaseAdmin)
admin.site.register(detalleCompra,BaseAdmin)
admin.site.register(categoriaMueble,BaseAdmin)
admin.site.register(estadoProductoComprado,BaseAdmin)
