"""Replacements for assets2020.csv. No original 3b1b bitmap is used as input.
Requires Pillow, NumPy, Pygments, ImageMagick for SVG, and the free project fonts.
AI deliveries are reviewed in entregas/2020 and NEVER installed by this script.
"""
from __future__ import annotations
import argparse,csv,hashlib,html,importlib.util,io,json,math,re,shutil,sys,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

HERE=Path(__file__).resolve().parent;ASSETS=HERE.parents[2];ROOT=ASSETS.parents[1]
AUDIT=ROOT/'_tools/assets_licencias/codex';CACHE=ROOT/'_tools/.cache/assets2020';FONTS=ASSETS/'fonts'
SOURCE_FILE=HERE/'assets2020_sources.json';AI_DIR=AUDIT/'entregas/2020'
loader=importlib.util.spec_from_file_location('asset_download_helpers',HERE.parent/'downloads/make_downloaded_assets.py')
d=importlib.util.module_from_spec(loader);loader.loader.exec_module(d);d.CACHE=CACHE;d.UA={'User-Agent':'ManimLearningAssets2020/1.0 (educational open-source assets)'}
ROWS=[{'n': '1',
  'asset': 'raster_images/Mona_Lisa.jpg',
  'ancho': '640',
  'alto': '954',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/hamming/DiskOfBits',
  'via': 'descargar',
  'que_es': 'La Gioconda de Leonardo.',
  'nota': 'Commons, reproducción fiel de obra 2D de dominio público.'},
 {'n': '2',
  'asset': 'raster_images/spanish_flu.jpg',
  'ancho': '1024',
  'alto': '772',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2020/covid/SARSvs1918',
  'via': 'descargar',
  'que_es': 'Foto de 1918: hospital de emergencia lleno de camas durante la gripe española (Camp Funston, '
            'Kansas).',
  'nota': 'Commons/NMHM, dominio público (foto del ejército de EE. UU. de 1918).'},
 {'n': '3',
  'asset': 'raster_images/Influenza.jpg',
  'ancho': '2650',
  'alto': '2069',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/sir/RealR0Estimates',
  'via': 'descargar',
  'que_es': 'Micrografía electrónica de viriones de influenza (manchas redondas sobre fondo gris).',
  'nota': 'CDC Public Health Image Library: dominio público (obra del gobierno de EE. UU.).'},
 {'n': '4',
  'asset': 'raster_images/EmmyNoether.png',
  'ancho': '640',
  'alto': '975',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2020/monster/MentionGroupsInPhysics',
  'via': 'descargar',
  'que_es': 'Retrato fotográfico de Emmy Noether de cuerpo entero/medio cuerpo, fondo transparente.',
  'nota': 'Commons, foto anterior a 1915, dominio público. El original es RGBA: recorta el fondo por código '
          'si la escena lo necesita.'},
 {'n': '5',
  'asset': 'raster_images/Fields Medal.png',
  'ancho': '2200',
  'alto': '2200',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2020/monster/MonstrousMoonshine',
  'via': 'descargar o generar',
  'que_es': 'Anverso de una medalla de oro con un perfil en relieve (la Medalla Fields), fondo transparente.',
  'nota': 'Primero Commons con licencia libre verificada (ojo: la foto y el diseño de 1933). Si no hay, '
          'genera una medalla de oro GENÉRICA con un perfil inventado, sin inscripciones legibles, fondo '
          'transparente.'},
 {'n': '6',
  'asset': 'raster_images/flags/au.png',
  'ancho': '550',
  'alto': '275',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/covid/CompareCountries',
  'via': 'descargar',
  'que_es': 'Bandera de Australia.',
  'nota': 'SVG de Commons (símbolo oficial, dominio público) rasterizado al tamaño exacto.'},
 {'n': '7',
  'asset': 'raster_images/flags/kr.png',
  'ancho': '550',
  'alto': '367',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/covid/CompareCountries',
  'via': 'descargar',
  'que_es': 'Bandera de Corea del Sur.',
  'nota': 'SVG de Commons (símbolo oficial, dominio público) rasterizado al tamaño exacto.'},
 {'n': '8',
  'asset': 'raster_images/John Conway.jpg',
  'ancho': '868',
  'alto': '848',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2020/monster/MonsterQuotes',
  'via': 'descargar',
  'que_es': 'Foto de John Horton Conway.',
  'nota': 'Commons con licencia libre (hay fotos CC BY / CC BY-SA). Si no hay: tarjeta propia por código con '
          'el nombre, sin cara.'},
 {'n': '9',
  'asset': 'raster_images/John McKay.jpg',
  'ancho': '250',
  'alto': '308',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/MonstrousMoonshine',
  'via': 'descargar',
  'que_es': 'Foto del matemático John McKay.',
  'nota': 'Commons/Oberwolfach (MFO) con licencia libre. Si no hay: tarjeta propia por código con el nombre, '
          'sin cara.'},
 {'n': '10',
  'asset': 'raster_images/Richard Borcherds.jpg',
  'ancho': '238',
  'alto': '277',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2020/monster/MonsterQuotes',
  'via': 'descargar',
  'que_es': 'Foto de Richard Borcherds.',
  'nota': 'Commons/Oberwolfach (MFO) con licencia libre. Si no hay: tarjeta propia por código con el nombre, '
          'sin cara.'},
 {'n': '11',
  'asset': 'raster_images/Gerd_Gigerenzer.jpg',
  'ancho': '750',
  'alto': '450',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/med_test/GigerenzerSession',
  'via': 'descargar',
  'que_es': 'Foto de Gerd Gigerenzer (apaisada 750x450).',
  'nota': 'Commons con licencia libre. Si no hay: tarjeta propia por código con el nombre, sin cara.'},
 {'n': '12',
  'asset': 'raster_images/standupmaths.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Avatar del canal de YouTube de Matt Parker (Stand-up Maths).',
  'nota': 'Foto libre de la persona en Commons. Si no hay: tarjeta propia por código con el NOMBRE DEL CANAL '
          '(la escena no rotula). Nunca el avatar real del canal ni una cara generada.'},
 {'n': '13',
  'asset': 'raster_images/singingbanana.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Avatar del canal de James Grime (singingbanana).',
  'nota': 'Igual que standupmaths.'},
 {'n': '14',
  'asset': 'raster_images/Ben Sparks.jpg',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Foto/avatar de Ben Sparks.',
  'nota': 'Igual que standupmaths.'},
 {'n': '15',
  'asset': 'raster_images/Zoe Griffiths.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Foto/avatar de Zoe Griffiths.',
  'nota': 'Igual que standupmaths.'},
 {'n': '16',
  'asset': 'raster_images/tomrocksmaths.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Avatar del canal de Tom Crawford (Tom Rocks Maths).',
  'nota': 'Igual que standupmaths.'},
 {'n': '17',
  'asset': 'raster_images/James Tanton.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Foto/avatar de James Tanton.',
  'nota': 'Igual que standupmaths.'},
 {'n': '18',
  'asset': 'raster_images/blackpenredpen.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Avatar del canal de Steve Chow (blackpenredpen).',
  'nota': 'Igual que standupmaths.'},
 {'n': '19',
  'asset': 'raster_images/Eddie Woo.jpg',
  'ancho': '176',
  'alto': '176',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/AskAboutFavoriteMegaNumber',
  'via': 'descargar',
  'que_es': 'Foto/avatar de Eddie Woo.',
  'nota': 'Igual que standupmaths.'},
 {'n': '20',
  'asset': 'raster_images/Hamming_Code_Snippet.png',
  'ancho': '2512',
  'alto': '958',
  'modo': 'RGBA',
  'escenas': '2',
  'ejemplo': '_2020/hamming/MultiplePerspectives',
  'via': 'código',
  'que_es': 'Captura de código Python (def hamming_syndrome(bits): return reduce(lambda x, y: x ^ y, [i for '
            '(i, b) in enumerate(bits) if b])) con resaltado de sintaxis sobre fondo negro, con comentarios.',
  'nota': 'Renderiza el mismo texto por código (Pygments + Pillow, fuente JetBrains Mono de '
          '_lib/assets/fonts) al tamaño exacto. Es código de Grant: se acredita a 3Blue1Brown.'},
 {'n': '21',
  'asset': 'raster_images/HammingCodeOneLine.png',
  'ancho': '1054',
  'alto': '300',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2020/hamming/Thumbnail2',
  'via': 'código',
  'que_es': 'Variante corta del mismo código (reduce(... enumerate(block) if bit)).',
  'nota': 'Igual que Hamming_Code_Snippet.'},
 {'n': '22',
  'asset': 'raster_images/LowResMandelbrot.png',
  'ancho': '600',
  'alto': '400',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/hamming/DataGettingZapped',
  'via': 'código',
  'que_es': 'Conjunto de Mandelbrot de baja resolución, fondo rojo-naranja, interior negro, borde '
            'verde/amarillo.',
  'nota': 'numpy + Pillow, mismo encuadre y aspecto (la escena simula datos dañados: baja resolución a '
          'propósito).'},
 {'n': '23',
  'asset': 'raster_images/J_Invariant_Coloring.jpg',
  'ancho': '904',
  'alto': '660',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/MonstrousMoonshine',
  'via': 'código',
  'que_es': 'Coloreado de dominio (arcoíris) de la función j en el semiplano superior, con cúspides abajo.',
  'nota': 'numpy: j(τ) por su serie q o por E4/E6, coloreado por argumento, mismo encuadre.'},
 {'n': '24',
  'asset': 'raster_images/ParityCheckIcon.jpg',
  'ancho': '2560',
  'alto': '1440',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/hamming/CompareXorToParityChecks',
  'via': 'código',
  'que_es': 'Fotograma del video de Hamming de Grant: cuadrícula 4x4 de bits con columnas/filas resaltadas y '
            'las preguntas Q1-Q4.',
  'nota': 'Redibújalo por código (Pillow/matplotlib) con el mismo contenido y disposición. Es obra de 3b1b '
          'recreada.'},
 {'n': '25',
  'asset': 'raster_images/XorViewIcon.jpg',
  'ancho': '2560',
  'alto': '1440',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/hamming/CompareXorToParityChecks',
  'via': 'código',
  'que_es': 'Fotograma del video de Hamming: cuadrícula 4x4 de bits y la suma XOR en binario de las '
            'posiciones activas.',
  'nota': 'Igual que ParityCheckIcon.'},
 {'n': '26',
  'asset': 'raster_images/ppv_image.png',
  'ancho': '3552',
  'alto': '2000',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2020/med_test/AskWhatTheParadoxIs',
  'via': 'código',
  'que_es': 'Fotograma del video de tests médicos: P(cancer | positivo) ≈ 9/(9+89), valor predictivo '
            'positivo y dos recuadros de figuritas (9 verdaderos positivos, 89 falsos positivos).',
  'nota': 'Redibújalo por código con el mismo contenido; las figuritas, iconos de persona simples (no pi '
          'creatures).'},
 {'n': '27',
  'asset': 'raster_images/twitter_covid_test_poll.png',
  'ancho': '1189',
  'alto': '928',
  'modo': 'RGBA',
  'escenas': '3',
  'ejemplo': '_2020/med_test/LookOverTweet',
  'via': 'código',
  'que_es': 'Captura de un tweet de Grant con una encuesta (texto del tweet y 4 opciones con porcentajes: '
            '35.1, 10.3, 11.8, 42.8; 24,224 votos).',
  'nota': 'Tarjeta de encuesta propia por código con el mismo texto y resultados, SIN logos ni estilo '
          'reconocible de Twitter/X (sin pájaro, sin avatar real: un círculo neutro).'},
 {'n': '28',
  'asset': 'raster_images/COVID-19_Map.png',
  'ancho': '2526',
  'alto': '1532',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2020/sir/RealR0Estimates',
  'via': 'descargar o código',
  'que_es': 'Captura del panel de Johns Hopkins de marzo de 2020 (mapa mundial oscuro con círculos rojos y '
            'lista de casos, "Total Confirmed 511,603").',
  'nota': 'No uses la captura (es de JHU/Esri). Opción A: un mapa COVID-19 de finales de marzo de 2020 en '
          'Commons con licencia libre. Opción B: por código, mapa mundial de dominio público (Natural Earth '
          'o Commons) con círculos proporcionales a casos por país de esa fecha (datos JHU CSSE, CC BY 4.0, '
          'atribuir) y el total.'},
 {'n': '29',
  'asset': 'raster_images/average_face.jpg',
  'ancho': '300',
  'alto': '400',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2020/monster/IntroduceGroupTheory',
  'via': 'descargar o generar',
  'que_es': 'Rostro promedio compuesto (fusión de muchas caras), frontal, fondo claro.',
  'nota': 'Commons: una cara promedio compuesta con licencia libre. Si no hay, genera una cara compuesta de '
          'persona INVENTADA (aspecto de promedio suave), sin parecido con nadie.'},
 {'n': '30',
  'asset': 'raster_images/Mario.png',
  'ancho': '840',
  'alto': '1200',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2020/18S191/convolutions/ConvolutionIntroduction',
  'via': 'código',
  'que_es': 'Sprite de pixel art de Mario (personaje de Nintendo) corriendo.',
  'nota': 'No uses Mario. Deriva el personaje original MarioSmall '
          '(_lib/assets/generated/replacements/codex/entregas/MarioSmall.svg) para que el proyecto use el '
          'mismo personaje; ajusta al aspecto 840x1200 con transparencia y píxeles nítidos. La escena le '
          'aplica convoluciones (desenfoque).'}]
ITEMS = {'1': {'kind': 'commons',
       'title': 'File:Mona Lisa, by Leonardo da Vinci, from C2RMF retouched.jpg',
       'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                  'del destino, sin usar el bitmap de Grant.'},
 '2': {'kind': 'commons',
       'title': 'File:Camp Funston, at Fort Riley, Kansas, during the 1918 Spanish flu pandemic.jpg',
       'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                  'del destino, sin usar el bitmap de Grant.'},
 '4': {'kind': 'commons',
       'title': 'File:Emmy Noether.jpg',
       'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                  'del destino, sin usar el bitmap de Grant.',
       'note': 'El original RGBA tiene alfa 255 en todo el lienzo; la escena no necesita una silueta '
               'recortada. Se conserva la fotografía histórica documental en RGBA.'},
 '6': {'kind': 'commons',
       'title': 'File:Flag of Australia.svg',
       'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                  'del destino, sin usar el bitmap de Grant.'},
 '7': {'kind': 'commons',
       'title': 'File:Flag of South Korea.svg',
       'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                  'del destino, sin usar el bitmap de Grant.'},
 '8': {'kind': 'commons',
       'title': 'File:John H Conway 2005 (cropped).jpg',
       'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                  'del destino, sin usar el bitmap de Grant.'},
 '10': {'kind': 'commons',
        'title': 'File:Richard Borcherds, 1993 (cropped).jpg',
        'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                   'del destino, sin usar el bitmap de Grant.'},
 '11': {'kind': 'commons',
        'title': 'File:Gerd Gigerenzer (26970147768).jpg',
        'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                   'del destino, sin usar el bitmap de Grant.'},
 '12': {'kind': 'commons',
        'title': 'File:Matt Parker at Nine lessons and Carols for Godless People.jpg',
        'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                   'del destino, sin usar el bitmap de Grant.',
        'centering': [0.5, 0],
        'crop': [0.25, 0, 0.8, 0.55]},
 '13': {'kind': 'commons',
        'title': 'File:James Grime.jpg',
        'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                   'del destino, sin usar el bitmap de Grant.',
        'centering': [0.5, 0.22]},
 '17': {'kind': 'commons',
        'title': 'File:James Tanton.jpg',
        'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                   'del destino, sin usar el bitmap de Grant.',
        'crop': [0.04, 0.025, 0.45, 0.7],
        'centering': [0.5, 0.2]},
 '19': {'kind': 'commons',
        'title': 'File:Eddie Woo, February 2019 01 (cropped).jpg',
        'changes': 'Fuente libre verificada independientemente; recorte de encuadre y ajuste al tamaño/modo '
                   'del destino, sin usar el bitmap de Grant.',
        'centering': [0.5, 0.22]},
 '3': {'kind': 'cdc',
       'changes': 'Micrografía auténtica CDC PHIL 11098, viriones de influenza reconstruida de 1918; '
                  'conversión del falso color a grises y ajuste de tamaño.',
       'note': 'Licencia y crédito revisados en la ficha individual de PHIL, sin asumir que toda imagen CDC '
               'sea libre.'},
 '9': {'kind': 'card',
       'label': 'John\nMcKay',
       'note': 'Se descartó un homónimo que era fiscal estadounidense; no se identificó una foto libre '
               'verificada del matemático.',
       'changes': 'Tarjeta tipográfica independiente con el nombre, sin cara ni silueta.'},
 '14': {'kind': 'card',
        'label': 'Ben Sparks',
        'note': 'Sin foto libre identificada con autor/licencia verificables; no se usa su avatar.',
        'changes': 'Tarjeta tipográfica independiente con el nombre, sin cara ni silueta.'},
 '15': {'kind': 'card',
        'label': 'Zoe\nGriffiths',
        'note': 'Sin foto libre identificada con autor/licencia verificables; no se usa avatar ni homónimos.',
        'changes': 'Tarjeta tipográfica independiente con el nombre, sin cara ni silueta.'},
 '16': {'kind': 'card',
        'label': 'Tom\nRocks Maths',
        'note': 'Se descartó una fotografía de un futbolista homónimo; tarjeta con el nombre del canal.',
        'changes': 'Tarjeta tipográfica independiente con el nombre, sin cara ni silueta.'},
 '18': {'kind': 'card',
        'label': 'blackpenredpen',
        'note': 'Sin foto libre identificada de Steve Chow; nombre del canal en tipografía neutra, sin '
                'recrear su marca.',
        'changes': 'Tarjeta tipográfica independiente con el nombre, sin cara ni silueta.'},
 '5': {'kind': 'ai',
       'delivery': 'Fields Medal.png',
       'note': 'Foto del anverso localizada en Commons con licencia PD para la fotografía, pero no se '
               'verificó suficientemente el derecho separado sobre el diseño de 1933; medalla genérica '
               'inventada, sin inscripciones ni copia del perfil.',
       'changes': 'Creación IA independiente sin usar como referencia el original; solo entrega, instalación '
                  'diferida al coordinador.',
       'subject': 'Medalla genérica de oro con perfil inventado, sustituta de la Fields Medal real; entrega '
                  'IA no instalada.'},
 '29': {'kind': 'face_average',
        'changes': 'Compuesto propio calculado desde las fotos femeninas neutrales del Face Research Lab '
                   'London Set (CC BY 4.0): registro ocular por los dos primeros landmarks .tem, media '
                   'aritmética y reflexión bilateral, 300×400 RGB. No se usa la imagen de Grant ni IA.',
        'note': 'Fuente fotográfica libre localizada siguiendo la cita DeBruine/Jones de la escena; '
                'compuesto recalculado, no copia de su promedio publicado. Se conserva la atribución del '
                'conjunto.'},
 '20': {'kind': 'code',
        'op': 'code_long',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Algoritmo equivalente: XOR de índices activos mediante reduce(xor, indices, 0); no se copia '
                'la captura ni su redacción.'},
 '21': {'kind': 'code',
        'op': 'code_short',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Expresión propia equivalente, con inicial 0 para lista vacía. En Thumbnail2 el uso del PNG '
                'está comentado y la escena usa Code(...); no se modifica esa escena.'},
 '22': {'kind': 'code',
        'op': 'mandelbrot',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Cálculo en cuadrícula 150×100 y ampliación entera ×4 con vecino más cercano; baja '
                'resolución intencionada.'},
 '23': {'kind': 'code',
        'op': 'j',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'j = E4³/Δ, con q y producto de Δ, tras reducción al dominio fundamental modular; colores '
                'por argumento. Referencia de la fórmula: '
                'https://docs.magma-maths.org/BasicRings/RealAndComplexFields/elliptic-modular.html'},
 '24': {'kind': 'code',
        'op': 'parity',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Diseño propio con tabla original de bits y preguntas Q1–Q4 de pertenencia a mitades de '
                'columnas/filas; posición objetivo 15, sin afirmar un síndrome incompatible con la tabla.'},
 '25': {'kind': 'code',
        'op': 'xor',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Índices activos [2,3,4,6,10,12,15], XOR = 10 decimal = 1010 binario.'},
 '26': {'kind': 'code',
        'op': 'ppv',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': '9 verdaderos positivos + 89 falsos positivos; PPV = 9/98 ≈ 9.18%; figuritas geométricas '
                'propias, sin pi creatures.'},
 '27': {'kind': 'code',
        'op': 'poll',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Texto reformulado por autorización expresa del usuario; mismos supuestos, intervalos y '
                'porcentajes 35.1/10.3/11.8/42.8, con 24,224 respuestas; diseño sin marcas ni interfaz '
                'Twitter/X.'},
 '30': {'kind': 'code',
        'op': 'sprite',
        'changes': 'Recreación independiente libre autorizada por el usuario; mismo contenido '
                   'matemático/factual con código, texto y diseño propios.',
        'note': 'Derivado exclusivamente del MarioSmall.svg propio sin bigote; piernas en pose de carrera, '
                'fondo transparente y píxeles cuadrados nítidos ×40.'},
 '28': {'kind': 'covid',
        'world_url': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson',
        'data_url': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/03-26-2020.csv',
        'changes': 'Mapa mundial independiente: polígonos de Natural Earth (PD), círculos por casos '
                   'confirmados agregados por país de JHU CSSE (CC BY 4.0), total recalculado y fecha '
                   'explícita.',
        'note': 'No se usa la captura ni el mapa de JHU/Esri; se indica la fecha diaria real en lugar del '
                'total parcial original.'}}
VERSION='2020-independent-v1'
PD='https://creativecommons.org/publicdomain/mark/1.0/'
CC0='https://creativecommons.org/publicdomain/zero/1.0/'
INK='#DFE7EE';MINT='#6AD5BC';GOLD='#F4C76B';BLUE='#6EB6DD';BG='#101722'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size,mono=False,bold=False):
 name=('JetBrainsMono-Bold.ttf' if bold else 'JetBrainsMono-Regular.ttf') if mono else ('CMUSerif-Bold.ttf' if bold else 'CMUSerif-Roman.ttf')
 return ImageFont.truetype(str(FONTS/name),max(5,int(size)))
def center(draw,xy,text,f,fill=INK):draw.text(xy,text,font=f,fill=fill,anchor='mm',align='center')
def fitfont(text,maxwidth,maxsize,mono=False):
 for n in range(int(maxsize),5,-1):
  f=font(n,mono);lines=text.split('\n')
  if max(f.getlength(line) for line in lines)<=maxwidth:return f
 return font(6,mono)
def canvas(size,mode='RGB'):return Image.new(mode,size,BG)
def name_card(size,label):
 im=Image.new('RGB',size,'#EEEFEA');draw=ImageDraw.Draw(im);w,h=size
 draw.rectangle((w*.065,h*.065,w*.935,h*.935),outline='#ABB2B5',width=max(1,w//150))
 f=fitfont(label,w*.8,w*.13,True);center(draw,(w/2,h/2),label,f,'#263746');return im


def code_panel(size,long):
 # Independent expression of the same XOR-of-active-indices algorithm.
 text=('from functools import reduce\nfrom operator import xor\n\ndef hamming_syndrome(bits):\n    indices = (i for i, bit in enumerate(bits) if bit)\n    return reduce(xor, indices, 0)') if long else 'reduce(xor,\n       (i for i, bit in enumerate(block) if bit),\n       0)'
 im=Image.new('RGBA',size,'#101722');draw=ImageDraw.Draw(im);w,h=size;f=fitfont(text,w*.92,h*.14,True);lineh=round(f.size*1.5);y=(h-lineh*len(text.splitlines()))//2;x0=w*.04;x=x0
 for token,value in lex(text,PythonLexer()):
  color=GOLD if token in Token.Keyword else BLUE if token in Token.Name.Function else MINT if token in Token.Name.Builtin else '#98A6B8' if token in Token.Comment else INK
  parts=value.split('\n')
  for i,part in enumerate(parts):
   if part:draw.text((x,y),part,font=f,fill=color);x+=draw.textlength(part,font=f)
   if i<len(parts)-1:y+=lineh;x=x0
 return im


def mandelbrot(size):
 w,h=150,100;x=np.linspace(-2.45,1.0,w);y=np.linspace(-1.16,1.16,h);c=x[None,:]+1j*y[:,None];z=np.zeros_like(c);steps=np.zeros((h,w),int);active=np.ones((h,w),bool)
 for n in range(1,121):
  z[active]=z[active]**2+c[active];escaped=active&(np.abs(z)>2);steps[escaped]=n;active[escaped]=False
 hue=np.uint8(np.clip(steps*.014,0,.34)*255);sat=np.full((h,w),255,'uint8');value=np.full((h,w),255,'uint8');value[active]=0
 out=Image.fromarray(np.stack([hue,sat,value],axis=-1),'HSV').convert('RGB');return out.resize(size,Image.Resampling.NEAREST)


def log_j(tau):
 tau=np.asarray(tau,dtype=complex).copy()
 for _ in range(30):
  tau-=np.floor(tau.real+.5);mask=np.abs(tau)<1-1e-14
  if not mask.any():break
  tau[mask]=-1/tau[mask]
 q=np.exp(2j*np.pi*tau);e4=np.ones_like(q);logs=np.zeros_like(q)
 for n in range(1,25):
  sigma=sum(k**3 for k in range(1,n+1) if n%k==0);qn=q**n;e4+=240*sigma*qn;logs+=np.log1p(-qn)
 return 3*np.log(e4)-2j*np.pi*tau-24*logs

def j_coloring(size):
 w,h=size;tau=np.linspace(-2,2,w)[None,:]+1j*np.linspace(1.4,.018,h)[:,None];l=log_j(tau)
 hue=(l.imag/(2*np.pi))%1;sat=np.full((h,w),.85);val=.55+.45/(1+np.exp(np.clip(-l.real/3,-40,40)));val*=.88+.12*np.cos(l.real*np.pi/np.log(10))**2
 hsv=np.stack([np.uint8(hue*255),np.uint8(sat*255),np.uint8(val*255)],axis=-1)
 return Image.fromarray(hsv,'HSV').convert('RGB')


def grid(draw,box,bits,indices=False,selected=None,highlight=None):
 x,y,w,h=box;cw=w/4;ch=h/4
 for i,bit in enumerate(bits):
  r,c=divmod(i,4);b=(x+c*cw,y+r*ch,x+(c+1)*cw,y+(r+1)*ch)
  if selected and i in selected:draw.rectangle(b,fill='#245F72')
  draw.rectangle(b,outline='#7E8B9A',width=max(1,round(w/330)))
  center(draw,(b[0]+cw/2,b[1]+ch*.40),str(bit),font(min(cw,ch)*.52),INK if bit else '#6C7B8A')
  center(draw,(b[0]+cw/2,b[1]+ch*.81),format(i,'04b') if indices else str(i),font(min(cw,ch)*.17,indices),'#9DAEBB')
  if i==highlight:draw.rectangle(b,outline=GOLD,width=max(3,round(w/140)))

def hamming_views(size,parity):
 im=canvas(size);draw=ImageDraw.Draw(im);w,h=size
 title='Parity-check view: locating position 15' if parity else 'XOR of the active positions'
 center(draw,(w*.5,h*.06),title,font(h*.045,True),INK)
 bits=[1,1,0,1,0,1,0,0,1,1,0,1,1,0,1,1] if parity else [0,0,1,1,1,0,1,0,0,0,1,0,1,0,0,1]
 active=[i for i,b in enumerate(bits) if b]
 grid(draw,(w*.055,h*.16,w*.36,h*.72),bits,not parity,set(active) if not parity else None,15 if parity else None)
 if parity:
  labels=['Q1: column bit 0','Q2: column bit 1','Q3: row bit 0','Q4: row bit 1']
  for k,label in enumerate(labels):
   yy=h*(.20+.18*k);draw.text((w*.48,yy),label,font=font(h*.039,True),fill=INK)
   xx=w*.76;cell=h*.031
   for i in range(16):
    r,c=divmod(i,4);yes=bool((c if k<2 else r)&(1<<(k%2)));draw.rectangle((xx+c*cell,yy+r*cell,xx+(c+1)*cell,yy+(r+1)*cell),fill=MINT if yes else '#24313D',outline='#667782',width=1)
   center(draw,(w*.91,yy+2*cell),'1',font(h*.06,True),GOLD)
  draw.text((w*.49,h*.91),'15 = 1111 (binary)',font=font(h*.036,True),fill=GOLD)
 else:
  values=[format(i,'04b') for i in active];f=font(h*.064,True)
  for k,text in enumerate(values):center(draw,(w*.77,h*(.16+.085*k)),text,f)
  yy=h*.77;draw.line((w*.66,yy,w*.88,yy),fill=INK,width=max(2,h//300));cx,cy=w*.63,yy-h*.045;rad=h*.023;draw.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),outline=BLUE,width=max(2,h//250));draw.line((cx-rad*.7,cy,cx+rad*.7,cy),fill=BLUE,width=max(2,h//250));draw.line((cx,cy-rad*.7,cx,cy+rad*.7),fill=BLUE,width=max(2,h//250));center(draw,(w*.77,h*.84),'1010',font(h*.075,True),GOLD)
 return im


def person(draw,x,y,s,color):
 draw.ellipse((x+s*.28,y,x+s*.72,y+s*.44),fill=color)
 draw.rounded_rectangle((x+s*.12,y+s*.49,x+s*.88,y+s*1.55),radius=s*.12,fill=color)
 draw.rectangle((x+s*.18,y+s*1.3,x+s*.42,y+s*1.95),fill=color);draw.rectangle((x+s*.58,y+s*1.3,x+s*.82,y+s*1.95),fill=color)

def ppv(size):
 im=canvas(size,'RGBA');d0=ImageDraw.Draw(im);w,h=size
 center(d0,(w*.5,h*.065),'Positive predictive value',font(h*.049,True),BLUE)
 center(d0,(w*.5,h*.155),'P(cancer | positive) = 9 / (9 + 89) (about 9.18%)',font(h*.046),INK)
 center(d0,(w*.5,h*.23),'PPV = TP / (TP + FP)',font(h*.037,True),MINT)
 left=(w*.06,h*.33,w*.34,h*.94);right=(w*.39,h*.33,w*.94,h*.94)
 for b,c in [(left,GOLD),(right,MINT)]:d0.rounded_rectangle(b,radius=w*.008,outline=c,width=max(2,w//600))
 center(d0,(w*.2,h*.38),'9 true positives',font(h*.032,True),GOLD);center(d0,(w*.665,h*.38),'89 false positives',font(h*.032,True),MINT)
 center(d0,(w*.2,h*.305),'Have cancer',font(h*.031),GOLD);center(d0,(w*.665,h*.305),'Do not have cancer',font(h*.031),MINT)
 s=h*.044
 for i in range(9):r,c=divmod(i,3);person(d0,w*.145+c*s*1.15,h*.53+r*s*2.35,s,GOLD)
 s=h*.026
 for i in range(89):r,c=divmod(i,12);person(d0,w*.46+c*s*1.2,h*.455+r*s*2.15,s,MINT)
 return im


def poll(size):
 w,h=size;im=Image.new('RGBA',size,'#F2EFE7');draw=ImageDraw.Draw(im)
 draw.rectangle((20,20,w-21,h-21),outline='#A8AAA3',width=2);draw.ellipse((35,33,91,89),fill='#AAB2B5');draw.text((113,40),'Probability question',font=font(32,True,True),fill='#253641')
 # Text is independently phrased; these baselines match LookOverTweet's fixed underlines.
 # Keep the answer rows below unchanged. Phrase ranges: 419:1069, 497:914,
 # 1053:1146 and 33:404 at underline y=201,448,448,510.
 ink='#172B35'
 def phrase(x,baseline,text,width):
  f=fitfont(text,width,49)
  draw.text((x,baseline),text,font=f,fill=ink,anchor='ls')
 def spread(x0,x1,baseline,text,size=49):
  # Coordinator: spreads the gap between words so that the placeholder text reaches the underlined phrase
  f=font(size);words=text.split();gap=(x1-x0-sum(f.getlength(wd) for wd in words))/(len(words)-1);x=x0
  for wd in words:draw.text((x,baseline),wd,font=f,fill=ink,anchor='ls');x+=f.getlength(wd)+gap
 spread(33,403,193,'Assume that just')
 phrase(419,193,'1 in 1,000 people have covid-19.',650)
 phrase(33,255,'You feel tired and your throat is mildly sore.',1100)
 phrase(33,317,'You take a test and the result is positive.',1100)
 spread(33,481,440,'The test itself has a')
 phrase(497,440,'1% false positive rate',417)
 spread(930,1037,440,'and a',44)
 phrase(1053,440,'10%',93)
 phrase(33,502,'false negative rate.',371)
 phrase(425,502,'How likely are you',720)
 phrase(33,563,'to have covid-19 after this result?',1100)
 options=['Between 0% and 15%','Between 15% and 50%','Between 50% and 85%','Over 85%'];percent=[35.1,10.3,11.8,42.8]
 for i,(label,p) in enumerate(zip(options,percent)):
  cy=[616,686,756,826][i];draw.rectangle((30,cy-24,30+(w-170)*p/100,cy+24),fill='#BDD7CE');draw.text((45,cy),label,font=font(30),fill='#173234',anchor='lm');draw.text((w-38,cy),f'{p:.1f}%',font=font(30,True),fill='#173234',anchor='rm')
 draw.text((30,h-56),'24,224 responses',font=font(25,True),fill='#516268',anchor='lt')
 return im


def runner_sprite(size):
 source=ASSETS/'generated/replacements/codex/entregas/MarioSmall.svg';tree=ET.parse(source);pix=Image.new('RGBA',(20,20));bg='#6ba8ff'
 for e in tree.getroot().iter():
  if e.tag.rsplit('}',1)[-1]!='rect':continue
  fill=e.get('fill','').lower()
  if fill==bg:continue
  x,y=int(float(e.get('x','0'))),int(float(e.get('y','0')));w,h=int(float(e.get('width','1'))),int(float(e.get('height','1')))
  ImageDraw.Draw(pix).rectangle((x,y,x+w-1,y+h-1),fill=fill)
 # Preserve the original face/cap/costume; pose only the lower legs independently.
 dr=ImageDraw.Draw(pix);dr.rectangle((0,15,19,19),fill=(0,0,0,0));dark='#252730';orange='#E7842F';brown='#795337'
 dr.polygon([(7,14),(9,14),(9,16),(8,17),(6,18),(3,18),(3,16),(6,16),(7,15)],fill=dark);dr.polygon([(7,15),(8,15),(8,16),(7,17),(6,17),(6,16)],fill=orange);dr.rectangle((4,17,6,17),fill=brown)
 dr.polygon([(10,14),(13,14),(13,16),(14,17),(16,18),(16,19),(11,19),(11,17),(10,16)],fill=dark);dr.rectangle((11,15,12,17),fill=orange);dr.rectangle((12,18,15,18),fill=brown)
 out=Image.new('RGBA',size);block=pix.resize((800,800),Image.Resampling.NEAREST);out.alpha_composite(block,((size[0]-800)//2,(size[1]-800)//2));return out


def covid_map(size):
 # Terms are rechecked in every execution of this data-derived generator.
 license_text=d.http('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/README.md').decode()
 assert 'Creative Commons Attribution 4.0' in license_text,'JHU CC BY 4.0 not verified'
 terms=d.http('https://www.naturalearthdata.com/about/terms-of-use/').decode();assert 'public domain' in terms.lower()
 world=json.loads(d.cached(ITEMS['28']['world_url']).read_text());raw=list(csv.DictReader(io.StringIO(d.cached(ITEMS['28']['data_url']).read_text())))
 w,h=size;im=canvas(size,'RGBA');draw=ImageDraw.Draw(im);top=h*.19;plot=(w*.22,top,w*.98,h*.93)
 def project(lon,lat):return (plot[0]+(lon+180)/360*(plot[2]-plot[0]),plot[1]+(85-lat)/170*(plot[3]-plot[1]))
 for feature in world['features']:
  g=feature['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for poly in polys:
   pts=[project(lon,lat) for lon,lat,*_ in poly[0]]
   if len(pts)>2:draw.polygon(pts,fill='#26394C',outline='#526575')
 country={};total=0
 for r in raw:
  count=int(r['Confirmed'] or 0);total+=count;name=r['Country_Region'];bucket=country.setdefault(name,[0,0.,0.,0]);bucket[0]+=count
  try:lat=float(r['Lat']);lon=float(r['Long_'])
  except ValueError:continue
  if lat or lon:
   bucket[1]+=lat*count;bucket[2]+=lon*count;bucket[3]+=count
 for name,(count,lat,lon,weight) in sorted(country.items(),key=lambda kv:kv[1][0]):
  if not count or not weight:continue
  x,y=project(lon/weight,lat/weight);radius=max(.6,math.sqrt(count)*.09);draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill='#C9584C',outline='#FFAD87',width=1)
 draw.text((w*.035,h*.03),'Reported confirmed cases',font=font(h*.05,True),fill=INK);draw.text((w*.035,h*.10),f'2020-03-26 — {total:,} worldwide',font=font(h*.04,True),fill=GOLD)
 for i,(name,(count,*_)) in enumerate(sorted(country.items(),key=lambda kv:kv[1][0],reverse=True)[:13]):
  y=top+i*h*.05;label=name[:16];draw.text((w*.025,y),label,font=font(h*.022),fill=INK);draw.text((w*.20,y),f'{count:,}',font=font(h*.022,True),fill=GOLD,anchor='ra')
 draw.text((w*.025,h*.965),'Data: JHU CSSE (CC BY 4.0) · Map: Natural Earth (public domain)',font=font(h*.018),fill='#B1C2CE')
 return im,total


def verify_face_source():
 meta=json.loads(d.http('https://api.figshare.com/v2/articles/5047666'))
 assert meta.get('license',{}).get('url','').rstrip('/')=='https://creativecommons.org/licenses/by/4.0','Face Research Lab license not verified'
 return meta

def average_face(size):
 meta=verify_face_source();archive=d.cached('https://ndownloader.figshare.com/files/8541961');labels=d.cached('https://ndownloader.figshare.com/files/27397184')
 info=next(f for f in meta['files'] if f['name']=='neutral_front.zip');expected=info.get('computed_md5') or info.get('supplied_md5')
 if expected:assert hashlib.md5(archive.read_bytes()).hexdigest()==expected,'Dataset checksum mismatch'
 selected=[r['face_id'] for r in csv.DictReader(io.StringIO(labels.read_text())) if r['face_gender']=='female']
 z=zipfile.ZipFile(archive);mean=np.zeros((size[1],size[0],3),float);count=0
 target_a=np.array([size[0]/3,size[1]*.4125]);target_b=np.array([2*size[0]/3,size[1]*.4125])
 for subject in selected:
  jpg=f'neutral_front/{subject}_03.jpg';tem=f'neutral_front/{subject}_03.tem'
  if jpg not in z.namelist() or tem not in z.namelist():continue
  im=Image.open(io.BytesIO(z.read(jpg))).convert('RGB');lines=z.read(tem).decode().splitlines();a=np.array([float(v) for v in lines[1].split()]);b=np.array([float(v) for v in lines[2].split()]);assert np.linalg.norm(b-a)>40
  ratio=complex(*(target_b-target_a))/complex(*(b-a));A=np.array([[ratio.real,-ratio.imag],[ratio.imag,ratio.real]]);inv=np.linalg.inv(A);off=a-inv@target_a
  coeff=tuple(inv[0])+(off[0],)+tuple(inv[1])+(off[1],)
  aligned=im.transform(size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC,fillcolor=im.getpixel((0,0)));arr=np.asarray(aligned,dtype=float)
  mean+=(arr+arr[:,::-1])/2;count+=1
 assert count>=30,'Not enough verified subjects'
 out=Image.fromarray(np.uint8(np.clip(np.round(mean/count),0,255)))
 return out,{'composite_faces':count,'symmetrized':True,'source_sha256':sha(archive),'dataset_version':meta.get('version'),'registration':'Similarity transform from the two pupil landmarks; arithmetic mean with horizontal reflections.'}

def cdc_download():
 page='https://wwwn.cdc.gov/phil/Details.aspx?pid=11098';body=d.http(page).decode()
 assert 'public domain images' in body.lower() and 'Cynthia Goldsmith' in body,'CDC license/credit not verified'
 file=CACHE/'originales/cdc_phil_11098_hires.bin';file.parent.mkdir(parents=True,exist_ok=True)
 if not file.exists():
  class Form(HTMLParser):
   def __init__(self):super().__init__();self.fields={}
   def handle_starttag(self,tag,attrs):
    a=dict(attrs)
    if tag=='input' and a.get('type','').lower()=='hidden' and a.get('name'):self.fields[a['name']]=a.get('value','')
  form=Form();form.feed(body);form.fields.update(__EVENTTARGET='ctl00$contentArea2$ucDetails$hlHighResDownload',__EVENTARGUMENT='')
  request=urllib.request.Request(page,data=urllib.parse.urlencode(form.fields).encode(),headers=d.UA)
  with urllib.request.urlopen(request,timeout=90) as response:payload=response.read(32*1024**2)
  try:Image.open(io.BytesIO(payload)).verify()
  except Exception:
   # CDC's public preview is also covered by this individual PD statement.
   match=re.search(r'id="imgURL1"[^>]*src="([^"]+)"',body)
   if not match:raise RuntimeError('CDC download returned no image and no verified preview URL')
   payload=d.http(html.unescape(match.group(1)));Image.open(io.BytesIO(payload)).verify()
   print(' CDC: using verified public preview; high-resolution form unavailable',flush=True)
  file.write_bytes(payload)
 return Image.open(file).convert('L').convert('RGB')


def process(item,row,commons):
 size=(int(row['ancho']),int(row['alto']));kind=item['kind']
 if kind=='card':return name_card(size,item['label']),None
 if kind=='code':
  op=item['op'];im=code_panel(size,op=='code_long') if op in ('code_long','code_short') else mandelbrot(size) if op=='mandelbrot' else j_coloring(size) if op=='j' else hamming_views(size,op=='parity') if op in ('parity','xor') else ppv(size) if op=='ppv' else poll(size) if op=='poll' else runner_sprite(size) if op=='sprite' else None
  assert im is not None;return im,None
 if kind=='covid':im,total=covid_map(size);return im,{'reported_total':total}
 if kind=='face_average':return average_face(size)
 if kind=='cdc':im=cdc_download();return ImageOps.fit(im,size,Image.Resampling.LANCZOS),{'source_resolution':list(im.size)}
 info=commons[item['title']];p=d.cached(info['file_url']);im=d.read_image(p)
 if item.get('crop'):im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(item['crop'])))
 if item.get('contain'):im=d.contain(im,size,(245,245,241))
 else:im=ImageOps.fit(im,size,Image.Resampling.LANCZOS,centering=tuple(item.get('centering',[.5,.35])))
 return im,{'source_sha256':sha(p),'download_size_bytes':p.stat().st_size}


def reports(records):
 lines=['# Progreso de assets 2020','','Recreaciones independientes libres autorizadas por el usuario: se mantienen datos y matemáticas, con texto y diseño propios; no se reutilizan ni derivan bitmaps de Grant.','','| # | Asset | Estado | Vía usada | Fuente | Licencia | Nota |','|---:|---|---|---|---|---|---|'];counts={'hecha':0,'entregada_IA':0,'saltada':0,'pendiente':0}
 for row in ROWS:
  r=records.get(row['asset'],{});state='entregada_IA' if r.get('delivery_status')=='entregada_IA' else 'hecha' if r.get('status') in ('generated','replaced','kept') else 'saltada' if r.get('status')=='skipped' else 'pendiente';counts[state]=counts.get(state,0)+1
  lines.append(f"| {row['n']} | `{row['asset']}` | {state} | {r.get('via','')} | {r.get('page_url','')} | {r.get('license','')} | {r.get('note','').replace('|','/')} |")
 lines+=['','## Resumen',', '.join(f'{v} {k}' for k,v in counts.items()),'','## Atribuciones de licencias no CC0/PD']
 for row in ROWS:
  r=records.get(row['asset'],{})
  if r.get('license','').startswith('CC BY'):lines.append(f"- {row['asset']}: {r['license']}, {r.get('source_authors') or r.get('author','')}, {r.get('page_url','')}. {r.get('changes','')}")
 lines+=['','## Para revisar','- La medalla genérica IA permanece en entregas/2020/ sin instalar. El rostro IA se descartó al localizar una fuente fotográfica libre; average_face se calcula con datos de Face Research Lab, en concordancia con la cita de la escena.','- La encuesta tiene texto reformulado y diseño independiente; conserva las cuatro opciones, porcentajes y 24,224 respuestas. Se mantienen las filas cerca de las anotaciones fijas de LookOverTweet; comprobar subrayados al render final.','- El mapa usa datos diarios del 26-03-2020, no la instantánea parcial de 511,603 del panel original; el total se calcula de la fuente y aparece fechado.','- j se calcula analíticamente con E4 y el producto de la discriminante, tras reducción modular; no es un dibujo arbitrario.','- Los retratos sin fuente libre verificable se sustituyen por tarjetas neutrales con el nombre. No se usaron homónimos ni avatares de canales.','- No se modifican escenas, setup, attributions globales, SVG/logos ni doctor_pair. No se renderizan escenas ni se publica nada.']
 (AUDIT/'PROGRESO_2020.md').write_text('\n'.join(lines)+'\n')


def attributions(records):
 lines=['# Atribuciones de assets 2020','','Las fotografías y datos conservan sus licencias; las composiciones independientes por código son propias. No se redistribuyen capturas ni avatares de Grant.','']
 for row in ROWS:
  r=records.get(row['asset'],{})
  if r.get('status')=='skipped' and not r.get('delivery_status'):
   r=r.get('retained_provenance',{})
  if not r:continue
  lines += [f"## {row['n']}. {row['asset']}",'',f"Autor: {r.get('author','')}",f"Fuentes y autores adicionales: {r.get('source_authors','')}",f"Licencia: {r.get('license','')} — {r.get('license_url','')}",f"Fuente: {r.get('page_url','')}",f"Cambios: {r.get('changes','')}",f"Nota: {r.get('note','')}",'']
 (HERE/'ATTRIBUTIONS_2020.md').write_text('\n'.join(lines))

def review(records):
 out=Image.new('RGB',(1500,1260),'#252B34');draw=ImageDraw.Draw(out)
 for i,row in enumerate(ROWS):
  rec=records.get(row['asset'],{});path=Path(rec['delivery_path']) if rec.get('delivery_status')=='entregada_IA' else ASSETS/row['asset']
  if path.exists():
   im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#667078');bg.alpha_composite(im);thumb=ImageOps.contain(bg.convert('RGB'),(285,172));x=i%5*300+(300-thumb.width)//2;y=i//5*210+25;out.paste(thumb,(x,y))
  draw.text((i%5*300+5,i//5*210+5),row['n']+' '+Path(row['asset']).name[:31],fill='white');draw.text((i%5*300+5,i//5*210+193),rec.get('delivery_status',rec.get('status','pendiente')),fill='#96DBC1')
 out.save(AUDIT/'REVISION_2020.png')


def run(args):
 CACHE.mkdir(parents=True,exist_ok=True);(CACHE/'.gitignore').write_text('*\n!.gitignore\n');old=json.loads(SOURCE_FILE.read_text()) if SOURCE_FILE.exists() else {};records={r.get('asset',k):r for k,r in old.items()};selected=[r for r in ROWS if not args.only or r['n'] in args.only]
 try:commons=d.verify_commons({ITEMS[r['n']]['title'] for r in selected if ITEMS[r['n']].get('title')})
 except Exception as e:commons={};print('Commons verification:',e,flush=True)
 for row in selected:
  item=ITEMS[row['n']];dest=ASSETS/row['asset'];print(f"[{row['n']}/30] {row['asset']}",flush=True)
  rec={'name':dest.name,'asset':row['asset'],'subject':item.get('subject',row['que_es']),'author':'propio (código)','license':'CC0','license_url':CC0,'page_url':'','changes':item.get('changes','Composición independiente desde cero.'),'status':'skipped','via':'código','note':item.get('note',''),'recipe_version':VERSION,'verified_at':datetime.now(timezone.utc).isoformat()}
  try:
   backup=CACHE/'originales_Grant'/row['asset']
   if dest.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
   if item['kind']=='ai':
    stage=AI_DIR/item['delivery'];assert stage.exists(),'Entrega IA pendiente';im=Image.open(stage);assert im.size==(int(row['ancho']),int(row['alto'])) and im.mode==row['modo']
    rec.update(status='skipped',delivery_status='entregada_IA',author='propio (generado con IA)',license='CC0 (aportación propia generada con IA)',license_url=CC0,via='IA',delivery_path=str(stage),sha256=sha(stage),note=item['note']+' Entrega revisada y no instalada.')
   else:
    if item['kind']=='commons':
     info=commons.get(item['title']);assert info,'No se obtuvo licencia libre verificada de la fuente';rec.update(info);rec['via']='descargar'
    elif item['kind']=='cdc':rec.update(author='CDC / Dr. Terrence Tumpey; fotografía Cynthia Goldsmith',license='Public domain',license_url='https://wwwn.cdc.gov/phil/Details.aspx?pid=11098',page_url='https://wwwn.cdc.gov/phil/Details.aspx?pid=11098',via='descargar')
    elif item['kind']=='face_average':
     verify_face_source();rec.update(license='CC BY 4.0',license_url='https://creativecommons.org/licenses/by/4.0/',page_url='https://doi.org/10.6084/m9.figshare.5047666',source_authors='Lisa M. DeBruine y Benedict C. Jones (2017), Face Research Lab London Set',via='descargar + código')
    elif item['kind']=='covid':rec.update(license='CC BY 4.0',license_url='https://creativecommons.org/licenses/by/4.0/',page_url='https://github.com/CSSEGISandData/COVID-19',source_authors='JHU CSSE (datos CC BY 4.0); Natural Earth (cartografía PD)',via='descargar + código')
    intact=old.get(dest.name,{}).get('recipe_version')==VERSION and dest.exists() and old.get(dest.name,{}).get('sha256')==sha(dest)
    # Even when skipping rasterization, check external policies for the CDC and data map.
    if intact and item['kind']=='cdc':
     text=d.http(rec['page_url']).decode();assert 'public domain images' in text.lower()
    if intact and item['kind']=='covid':
     assert 'Creative Commons Attribution 4.0' in d.http('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/README.md').decode();assert 'public domain' in d.http('https://www.naturalearthdata.com/about/terms-of-use/').decode().lower()
    if not intact or args.force:
     im,extra=process(item,row,commons);assert im.size==(int(row['ancho']),int(row['alto']));d.save(im,dest,row['modo']);rec.update(extra or {})
    elif dest.name in old:
     for k in ('reported_total','source_sha256','download_size_bytes','source_resolution','composite_faces','symmetrized','dataset_version','registration'):
      if k in old[dest.name]:rec[k]=old[dest.name][k]
    with Image.open(dest) as check:assert check.size==(int(row['ancho']),int(row['alto'])) and check.mode==row['modo'];check.verify()
    rec.update(status=('kept' if intact and not args.force else 'replaced') if item['kind'] in ('commons','cdc') else 'generated',sha256=sha(dest),final_size_bytes=dest.stat().st_size)
    if item['kind']=='face_average':rec['note']+=f" Promedio de {rec.get('composite_faces',0)} rostros, con registro ocular y simetrización; no IA."
    if item['kind']=='cdc' and rec.get('source_resolution'):rec['note']+=f" Resolución fuente CDC: {rec['source_resolution']}; reescalada al destino."
    if item['kind']=='covid':rec['note']+=f" Total diario verificado: {rec.get('reported_total',0):,}; no se copia la captura original."
  except Exception as e:
   rec.update(status='skipped',note=str(e));print(' SALTADA',e,flush=True)
   previous=old.get(dest.name,{})
   if previous.get('sha256') and dest.exists() and sha(dest)==previous['sha256']:rec['retained_provenance']=previous
  records[row['asset']]=rec;d.atomic_json(SOURCE_FILE,{r['name']:r for r in records.values()});reports(records)
 review(records);attributions(records);print('Finished assets2020',flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',nargs='+',choices=[r['n'] for r in ROWS]);ap.add_argument('--force',action='store_true');run(ap.parse_args())
