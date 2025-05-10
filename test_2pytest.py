import pytest
from codigo_entregable2 import *
# PYTEST


def test_generar_registro():
    registro = generarRegistroCamion()
    assert isinstance(registro, tuple) and len(registro) == 5


def test_convertir_coord():
    olc = convertirCoordenadasOLC(-3.7038, 40.4168)
    assert olc.startswith("OLC-")


def test_estrategia_media():
    estrategia = MediaDesv()
    estrategia.calcular([20, 22, 21], [50, 52, 51])


def test_estrategia_maxmin():
    estrategia = MaxMin()
    estrategia.calcular([18, 25, 20], [60, 70, 65])


def test_estrategia_cuantiles():
    estrategia = Cuantiles()
    estrategia.calcular([15, 16, 17, 18], [40, 42, 43, 44])


def test_servidor_logistico():
    servidor = ServidorLogistico()
    registro = generarRegistroCamion()
    servidor.actualizar(registro)
    assert len(servidor._ServidorLogistico__registros) == 1
    assert isinstance(servidor._ServidorLogistico__registros[0], tuple)
    assert len(servidor._ServidorLogistico__registros[0]) == 5


def test_estadistico_temp_hum():
    estadistico = EstadisticoTempHum()
    registros = [(1, 20, 0, 0, 50)]
    estrategia = MediaDesv()
    estadistico.cambiarEstrategia(estrategia)
    estadistico.manejar_operacion(registros)
    assert estadistico._EstadisticoTempHum__estrategia == estrategia


def test_extraerTH():
    handler = Handler()
    registros = [(1, 20, 0, 0, 50), (2, 22, 0, 0, 55)]
    temps, hums = handler.extraerTH(registros)
    assert temps == [20, 22]
    assert hums == [50, 55]
