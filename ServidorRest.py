# Importar librerías
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import sys
import os
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pequeMundo.settings")
django.setup()

from app.models import mueble


def buscar_mueble_por_id(mueble_id):
    try:
        return mueble.objects.get(id=mueble_id)
    except mueble.DoesNotExist:
        return None


def serializar_mueble(obj):
    return {
        "id": obj.id,
        "nombre": obj.nombre,
        "descripcion": obj.descripcion,
        "foto": obj.foto.url if obj.foto else None,
        "precio": obj.precio,
        "cantidad": obj.cantidad,
        "estado": obj.estado_id,
        "disponiblidad": obj.disponiblidad_id,
        "categoria_mueble": obj.categoria_mueble_id
    }


class ApiMuebles(BaseHTTPRequestHandler):
    def enviar_respuesta(self, codigo, datos):
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        respuesta = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.wfile.write(respuesta)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def leer_json(self):
        longitud = int(self.headers.get("Content-Length", 0))
        if longitud == 0:
            return None

        cuerpo = self.rfile.read(longitud).decode("utf-8")
        try:
            return json.loads(cuerpo)
        except json.JSONDecodeError:
            return None

    def obtener_id_desde_ruta(self):
        partes = self.path.strip("/").split("/")
        if len(partes) == 2 and partes[0] == "muebles":
            try:
                return int(partes[1])
            except ValueError:
                return None
        return None

    def do_GET(self):
        ruta = urlparse(self.path).path

        if ruta == "/muebles":
            lista_muebles = [serializar_mueble(item) for item in mueble.objects.all()]
            self.enviar_respuesta(200, lista_muebles)
            return

        mueble_id = self.obtener_id_desde_ruta()
        if mueble_id is not None:
            obj = buscar_mueble_por_id(mueble_id)
            if obj:
                self.enviar_respuesta(200, serializar_mueble(obj))
            else:
                self.enviar_respuesta(404, {"error": "Mueble no encontrado"})
            return

        self.enviar_respuesta(404, {"error": "Ruta no encontrada"})

    def do_POST(self):
        ruta = urlparse(self.path).path

        if ruta != "/muebles":
            self.enviar_respuesta(404, {"error": "Ruta no encontrada"})
            return

        datos = self.leer_json()
        if not datos:
            self.enviar_respuesta(400, {"error": "JSON no válido"})
            return

        if not datos.get("nombre") or not datos.get("descripcion") or datos.get("precio") is None:
            self.enviar_respuesta(400, {"error": "Faltan campos obligatorios"})
            return

        try:
            nuevo_mueble = mueble.objects.create(
                nombre=datos.get("nombre"),
                descripcion=datos.get("descripcion"),
                precio=datos.get("precio"),
                cantidad=datos.get("cantidad", 0),
                estado_id=datos.get("estado"),
                disponiblidad_id=datos.get("disponiblidad"),
                categoria_mueble_id=datos.get("categoria_mueble")
            )
            self.enviar_respuesta(201, serializar_mueble(nuevo_mueble))
        except Exception as e:
            self.enviar_respuesta(400, {"error": str(e)})

    def do_PUT(self):
        mueble_id = self.obtener_id_desde_ruta()

        if mueble_id is None:
            self.enviar_respuesta(404, {"error": "Ruta no válida"})
            return

        obj = buscar_mueble_por_id(mueble_id)
        if not obj:
            self.enviar_respuesta(404, {"error": "Mueble no encontrado"})
            return

        datos = self.leer_json()
        if not datos:
            self.enviar_respuesta(400, {"error": "JSON no válido"})
            return

        try:
            obj.nombre = datos.get("nombre", obj.nombre)
            obj.descripcion = datos.get("descripcion", obj.descripcion)
            obj.precio = datos.get("precio", obj.precio)
            obj.cantidad = datos.get("cantidad", obj.cantidad)

            if datos.get("estado") is not None:
                obj.estado_id = datos.get("estado")
            if datos.get("disponiblidad") is not None:
                obj.disponiblidad_id = datos.get("disponiblidad")
            if datos.get("categoria_mueble") is not None:
                obj.categoria_mueble_id = datos.get("categoria_mueble")

            obj.save()
            self.enviar_respuesta(200, serializar_mueble(obj))
        except Exception as e:
            self.enviar_respuesta(400, {"error": str(e)})

    def do_DELETE(self):
        mueble_id = self.obtener_id_desde_ruta()

        if mueble_id is None:
            self.enviar_respuesta(404, {"error": "Ruta no válida"})
            return

        obj = buscar_mueble_por_id(mueble_id)
        if not obj:
            self.enviar_respuesta(404, {"error": "Mueble no encontrado"})
            return

        obj.delete()
        self.enviar_respuesta(200, {"mensaje": "Mueble eliminado"})


def ejecutar_servidor():
    host = "127.0.0.1"
    puerto = 8001
    servidor = HTTPServer((host, puerto), ApiMuebles)

    print(f"API REST funciona en http://{host}:{puerto}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        servidor.server_close()


ejecutar_servidor()