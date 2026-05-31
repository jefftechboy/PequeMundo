import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE_URL = "http://127.0.0.1:8001"


def mostrar_respuesta(respuesta):
    print(f"Código de estado: {respuesta.status}")
    contenido = respuesta.read().decode("utf-8")

    try:
        datos = json.loads(contenido)
        print("Respuesta JSON:")
        print(json.dumps(datos, indent=4, ensure_ascii=False))
    except:
        print("Respuesta:")
        print(contenido)

    print("-" * 50)


def listar_muebles():
    print("LISTAR MUEBLES")
    try:
        with urlopen(f"{BASE_URL}/muebles") as respuesta:
            mostrar_respuesta(respuesta)
    except URLError as e:
        print(f"Error al cargar el servidor: {e}")


def obtener_mueble(mueble_id):
    print(f"OBTENER MUEBLE ID {mueble_id}")
    try:
        with urlopen(f"{BASE_URL}/muebles/{mueble_id}") as respuesta:
            mostrar_respuesta(respuesta)
    except HTTPError as e:
        print(f"Error HTTP: {e.code}")
        print(e.read().decode("utf-8"))
    except URLError as e:
        print(f"Error al cargar el servidor: {e}")


def crear_mueble(nombre, descripcion, precio, cantidad, estado, disponiblidad, categoria_mueble):
    print("CREAR MUEBLE")

    datos = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "cantidad": cantidad,
        "estado": estado,
        "disponiblidad": disponiblidad,
        "categoria_mueble": categoria_mueble
    }

    cuerpo = json.dumps(datos).encode("utf-8")

    solicitud = Request(
        url=f"{BASE_URL}/muebles",
        data=cuerpo,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

    try:
        with urlopen(solicitud) as respuesta:
            mostrar_respuesta(respuesta)
    except HTTPError as e:
        print(f"Error HTTP: {e.code}")
        print(e.read().decode("utf-8"))
    except URLError as e:
        print(f"Error al cargar el servidor: {e}")


def actualizar_mueble(mueble_id, nombre, descripcion, precio, cantidad, estado, disponiblidad, categoria_mueble):
    print(f"ACTUALIZAR MUEBLE {mueble_id}")

    datos = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "cantidad": cantidad,
        "estado": estado,
        "disponiblidad": disponiblidad,
        "categoria_mueble": categoria_mueble
    }

    cuerpo = json.dumps(datos).encode("utf-8")

    solicitud = Request(
        url=f"{BASE_URL}/muebles/{mueble_id}",
        data=cuerpo,
        method="PUT",
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

    try:
        with urlopen(solicitud) as respuesta:
            mostrar_respuesta(respuesta)
    except HTTPError as e:
        print(f"Error HTTP: {e.code}")
        print(e.read().decode("utf-8"))
    except URLError as e:
        print(f"Error al cargar el servidor: {e}")


def eliminar_mueble(mueble_id):
    print(f"ELIMINAR MUEBLE {mueble_id}")

    solicitud = Request(
        url=f"{BASE_URL}/muebles/{mueble_id}",
        method="DELETE"
    )

    try:
        with urlopen(solicitud) as respuesta:
            mostrar_respuesta(respuesta)
    except HTTPError as e:
        print(f"Error HTTP: {e.code}")
        print(e.read().decode("utf-8"))
    except URLError as e:
        print(f"Error al cargar el servidor: {e}")


listar_muebles()
obtener_mueble(1)
crear_mueble("Mesa Auxiliar", "Mesa pequeña de apoyo", 45990, 7, 1, 1, 2)
actualizar_mueble(1, "Sofá Premium", "Sofá de 3 cuerpos premium", 349990, 4, 1, 1, 1)
eliminar_mueble(2)