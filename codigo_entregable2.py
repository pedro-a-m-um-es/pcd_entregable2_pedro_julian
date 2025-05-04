import functools
import asyncio
from abc import ABCMeta, abstractmethod
from math import sqrt


class NotValidType(Exception):
    def __init__(self, mensaje="Error: El tipo proporcionado no es válido"):
        self.message = mensaje
        super().__init__(self.message)

# FUNCIÓN GENERAL


def generarRegistroCamion():

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


# OBSERVER
class Camion:
    def __init__(self):
        self.__servidores = []

    def altaSistema(self, sistema):
        if not isinstance(sistema, SistemaAbstracto):
            raise NotValidType("Sistema no válido")
        self.__servidores.append(sistema)


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


class ServidorLogistico(SistemaAbstracto, CadenaOperaciones):
    def __init__(self):
        self.__registros = []
        CadenaOperaciones.__init__(self)


# CHAIN OF RESPONSIBILITY
class Handler:
    def __init__(self, sucesor=None):
        self.sucesor = sucesor


class EstadisticoTempHum(Handler):
    def __init__(self, estrategia=None, sucesor=None):
        super().__init__(sucesor)
        self.__estrategia = estrategia

    def cambiarEstrategia(self, estrategia):
        self.__estrategia = estrategia


class ComprobacionUmbralTemp(Handler):


class ComprobacionVariacionAsync(Handler):

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
