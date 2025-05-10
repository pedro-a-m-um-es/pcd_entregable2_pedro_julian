import time
import datetime
import random
import functools
import asyncio
from abc import ABCMeta, abstractmethod
from math import sqrt
from itertools import combinations


# EXCEPCIONES PERSONALIZADAS
class NotValidType(Exception):
    def __init__(self, mensaje="Error: El tipo proporcionado no es válido"):
        self.message = mensaje
        super().__init__(self.message)

# FUNCIÓN GENERAL


def generarRegistroCamion():
    timestamp = int(time.time())
    temperatura = round(random.uniform(-10, 40), 1)
    humedad = round(random.uniform(30, 90), 1)
    longitud = round(random.uniform(-10.0, 10.0), 6)
    latitud = round(random.uniform(35.0, 45.0), 6)
    return (timestamp, temperatura, longitud, latitud, humedad)


def convertirCoordenadasOLC(longitud, latitud):
    return f"OLC-{round(latitud, 3)}-{round(longitud, 3)}"


# SINGLETON
class GestorLogistico:
    _instancia = None

    @classmethod
    def obtenerGestor(cls):
        if not cls._instancia:
            cls._instancia = cls()
        return cls._instancia

    def __crearCamion(self):
        return Camion()

    def iniciarMonitorizacion(self, duracion=None):
        if duracion and not isinstance(duracion, int):
            raise NotValidType("La duración debe ser un entero")

        camion = self.__crearCamion()
        camion.altaSistema(ServidorLogistico())

        if not duracion:
            while True:
                self.__iteracion(camion)
                time.sleep(5)
        else:
            fin = time.time() + duracion
            while fin > time.time():
                self.__iteracion(camion)
                time.sleep(5)

    def __iteracion(self, camion):
        camion.enviarRegistro()
        print("\n")


# OBSERVER
class Camion:
    def __init__(self):
        self.__servidores = []

    def altaSistema(self, sistema):
        if not isinstance(sistema, SistemaAbstracto):
            raise NotValidType("Sistema no válido")
        self.__servidores.append(sistema)

    def enviarRegistro(self):
        registro = generarRegistroCamion()
        for sistema in self.__servidores:
            sistema.actualizar(registro)


class SistemaAbstracto(metaclass=ABCMeta):
    @abstractmethod
    def actualizar(self, registro):
        pass


# SISTEMA Y CADENA DE OPERACIONES
class CadenaOperaciones:
    def __init__(self):
        self.__ultimo = ComprobacionVariacionAsync()
        self.__umbral = ComprobacionUmbralTemp(self.__ultimo)
        self.__estadistico = EstadisticoTempHum(sucesor=self.__umbral)

    def __filtrarUltimos60s(self, registros):
        if len(registros) > 12:
            return registros[-12:]
        return registros

    def start(self, registros):
        recientes = self.__filtrarUltimos60s(registros)
        self.__estadistico.cambiarEstrategia(
            random.choice([MediaDesv(), MaxMin(), Cuantiles()]))
        self.__estadistico.manejar_operacion(recientes)


class ServidorLogistico(SistemaAbstracto, CadenaOperaciones):
    def __init__(self):
        self.__registros = []
        CadenaOperaciones.__init__(self)

    def actualizar(self, registro):
        timestamp, temp, lon, lat, hum = registro
        fechaYhora = datetime.datetime.fromtimestamp(
            timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(
            f"[{fechaYhora}] Temp: {temp} ºC, Hum: {hum} %, Loc: {convertirCoordenadasOLC(lon, lat)}")
        self.__registros.append(registro)
        self.start(self.__registros)


# CHAIN OF RESPONSIBILITY
class Handler:
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    def manejar_operacion(self, registros):
        pass

    def extraerTH(self, registros):
        temps = [r[1] for r in registros]
        hums = [r[4] for r in registros]
        return temps, hums

    def cambiarSucesor(self, registros):
        if self.sucesor:
            self.sucesor.manejar_operacion(registros)


class EstadisticoTempHum(Handler):
    def __init__(self, estrategia=None, sucesor=None):
        super().__init__(sucesor)
        self.__estrategia = estrategia

    def cambiarEstrategia(self, estrategia):
        self.__estrategia = estrategia

    def manejar_operacion(self, registros):
        temps, hums = self.extraerTH(registros)
        self.__estrategia.calcular(temps, hums)
        self.cambiarSucesor(registros)


class ComprobacionUmbralTemp(Handler):
    UMBRAL = 35

    def manejar_operacion(self, registros):
        temps, _ = self.extraerTH(registros)
        if temps[-1] > ComprobacionUmbralTemp.UMBRAL:
            print(
                f"! Alerta: Temperatura actual {temps[-1]} ºC supera el umbral de {self.UMBRAL} ºC")
        self.cambiarSucesor(registros)


class ComprobacionVariacionAsync(Handler):

    def manejar_operacion(self, registros):
        asyncio.run(self.__verificar_async(registros))
        self.cambiarSucesor(registros)

    async def __verificar_async(self, registros):
        if len(registros) > 6:
            registros = registros[-6:]
        temps, hums = self.extraerTH(registros)
        await asyncio.gather(
            self.__verificar_variacion(temps, "temperatura"),
            self.__verificar_variacion(hums, "humedad")
        )

    async def __verificar_variacion(self, lista, tipo):
        if not lista or len(lista) < 2:
            return
        variacion = abs(lista[-1] - lista[0])
        if variacion > 2:
            print(
                f"! Alerta: {tipo.capitalize()} ha variado {variacion:.2f} unidades en los últimos 30s")


# STRATEGY
class Estrategia(metaclass=ABCMeta):
    @abstractmethod
    def calcular(self, temperaturas, humedades):
        pass


class MediaDesv(Estrategia):
    def calcular(self, temperaturas, humedades):
        for tipo, datos in [("Temperatura", temperaturas), ("Humedad", humedades)]:
            media = functools.reduce(lambda a, b: a + b, datos) / len(datos)
            desv = sqrt(
                sum(map(lambda x: (x - media) ** 2, datos)) / len(datos))
            print(f"{tipo}: Media = {round(media, 2)}, Desv = {round(desv, 2)}")


class MaxMin(Estrategia):
    def calcular(self, temperaturas, humedades):
        for tipo, datos in [("Temperatura", temperaturas), ("Humedad", humedades)]:
            print(f"{tipo}: Max = {max(datos)}, Min = {min(datos)}")


class Cuantiles(Estrategia):
    def calcular(self, temperaturas, humedades):
        for tipo, datos in [("Temperatura", temperaturas), ("Humedad", humedades)]:
            datos = sorted(datos)
            q1 = datos[int(0.25 * (len(datos) - 1))]
            q2 = datos[int(0.50 * (len(datos) - 1))]
            q3 = datos[int(0.75 * (len(datos) - 1))]
            print(f"{tipo}: Q1 = {q1}, Q2 = {q2}, Q3 = {q3}")


# EJECUCIÓN DEL CÓDIGO
if __name__ == "__main__":
    try:
        sistema = GestorLogistico.obtenerGestor()
        sistema.iniciarMonitorizacion(duracion=60)
    except Exception as e:
        print(f"Error: {e}")
