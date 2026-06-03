import unittest
import xml.etree.ElementTree as ET

from src.daypo import _normalizar_url, _numero_imagen, _prefijo_imagen


class TestDaypoImagenes(unittest.TestCase):
    def test_prefijo_carpeta_como_daypo_js(self):
        self.assertEqual(_prefijo_imagen("1188924"), "118")
        self.assertEqual(_prefijo_imagen("123456"), "12")
        self.assertEqual(_prefijo_imagen("99999"), "9")

    def test_normalizar_url_daypo_net(self):
        self.assertEqual(
            _normalizar_url("https://www.daypo.net/examen-uro-5.html"),
            "https://www.daypo.com/examen-uro-5.html",
        )

    def test_numero_imagen_desde_texto(self):
        nodo = ET.fromstring('<b p="1" w="270" h="129">0</b>')
        self.assertEqual(_numero_imagen(nodo), "0")

    def test_numero_imagen_ignora_youtube(self):
        nodo = ET.fromstring('<b y="abc123">0</b>')
        self.assertIsNone(_numero_imagen(nodo))


if __name__ == "__main__":
    unittest.main()
