import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

#VARIABLE CON LA URL DE LA API
BASE_URL = "http://127.0.0.1:8002"





#Métodos para consumir la API
def mostrar_respuesta(respuesta):
    print(f"Código de estado : {respuesta.status}")
    contenido = respuesta.read().decode("utf-8")
    #Intentar mostrar la respuesta
    try:
        datos = json.loads(contenido)
        print("Respuesta JSON:")
        print(json.dumps(datos, indent=4, ensure_ascii=False))
    except:
        print("Respuesta:")
        print(contenido)
    print("*******************************")

#Utilizar método get
def obtenerMuebles():
    print("Lista de Alumnos 😊")
    try:
        with urlopen(f"{BASE_URL}/muebles") as respuesta:
            mostrar_respuesta(respuesta)
    except URLError as e:
        print(f"❌ Error al cargar el servidor {e}")
        

#ACCIONES QUE REALIZA EL CLIENTE
obtenerMuebles()


