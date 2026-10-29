"""Independent 2019 replacements. No original bitmap/vector/audio is used as input.
Run --priority P1/P2/P3 or --only N ...; no option renders scenes. Originals backed up.
Requires Pillow, numpy, shapely, rsvg-convert. Downloads verified live each run.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,importlib.util,io,json,math,re,shutil,subprocess,sys,tarfile,wave
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from shapely.geometry import Point,Polygon,LineString,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parent;ASSETS=HERE.parents[2];ROOT=ASSETS.parents[1];AUDIT=ROOT/'_tools/assets_licencias/codex';CACHE=ROOT/'_tools/.cache/assets2019';FONTS=ASSETS/'fonts';SOURCE=HERE/'assets2019_sources.json'
CC0='https://creativecommons.org/publicdomain/zero/1.0/';VERSION='2019-own-v1'
# Prefer the active environment, then the project's own ManimGL dependencies.
try:import matplotlib
except ImportError:
 dep=ROOT.parent/'manimgl/venv/lib'/f'python{sys.version_info.major}.{sys.version_info.minor}'/'site-packages'
 if dep.is_dir():sys.path.append(str(dep))

sp=importlib.util.spec_from_file_location('download_helper',HERE.parent/'downloads/make_downloaded_assets.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d);d.CACHE=CACHE;d.UA={'User-Agent':'ManimLearningAssets2019/1.0 (independent educational asset audit)'}
ROWS=[{'n': '1', 'prioridad': 'P1', 'asset': 'svg_images/TrebleClef.svg', 'ancho': 'svg', 'alto': '0 0 1200 1200', 'modo': 'SVG', 'escenas': '40', 'ejemplo': '_2019/diffyq/part2/fourier_series/ExplainCircleAnimations', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Clave de sol', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); sirve de silueta que dibujan los círculos de Fourier: el reemplazo debe ser UN contorno limpio'}, {'n': '2', 'prioridad': 'P1', 'asset': 'sounds/pen_click.wav', 'ancho': 'wav', 'alto': '', 'modo': 'WAV', 'escenas': '32', 'ejemplo': '_2019/clacks/solution2/mirror_scenes/MirrorAndWiresOverlay', 'via': 'código', 'tipo': 'sonido', 'derechos': 'obra_3b1b', 'que_crear': 'Sonido sintetizado propio (replacements/sounds)', 'nota': 'Clic de bolígrafo de Grant (autoría presunta)'}, {'n': '3', 'prioridad': 'P1', 'asset': 'svg_images/EighthNote.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '29', 'ejemplo': '_2019/diffyq/part2/fourier_series/FourierOfEighthNote', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Nota corchea', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); sirve de silueta que dibujan los círculos de Fourier: el reemplazo debe ser UN contorno limpio'}, {'n': '4', 'prioridad': 'P1', 'asset': 'svg_images/Nail_And_Gear.svg', 'ancho': 'svg', 'alto': '0 0 939 627.59998', 'modo': 'SVG', 'escenas': '29', 'ejemplo': '_2019/diffyq/part2/fourier_series/FourierNailAndGear', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Engranaje cruzado por una barra/clavo', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); sirve de silueta que dibujan los círculos de Fourier: el reemplazo debe ser UN contorno limpio'}, {'n': '5', 'prioridad': 'P1', 'asset': 'svg_images/dart.svg', 'ancho': 'svg', 'alto': '0 0 809 824', 'modo': 'SVG', 'escenas': '21', 'ejemplo': '_2019/hyperdarts/ContrastDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Dardo', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '6', 'prioridad': 'P1', 'asset': 'svg_images/book.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '11', 'ejemplo': '_2019/bayes/footnote/Rearrange', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Libro abierto de contorno', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '7', 'prioridad': 'P1', 'asset': 'svg_images/farming.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '11', 'ejemplo': '_2019/bayes/part1/CorrectViewOfFarmersAndLibrarians', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Tres espigas de trigo sobre surcos', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '8', 'prioridad': 'P1', 'asset': 'svg_images/steve.svg', 'ancho': 'svg', 'alto': '0 0 64 64', 'modo': 'SVG', 'escenas': '11', 'ejemplo': '_2019/bayes/part1/AlternatePhrasings', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Busto de hombre con gafas (Steve)', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '9', 'prioridad': 'P2', 'asset': 'raster_images/flags/*.png', 'ancho': 'varios', 'alto': '199 archivos', 'modo': 'PNG', 'escenas': '6', 'ejemplo': '_2019/windmill/Describe2011IMO', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'dominio_publico', 'que_crear': '199 banderas nacionales: descarga de una fuente libre (flag-icons, MIT/CC0, o Commons) en el setup, o dibujo por código de las sencillas', 'nota': 'Banderas de países de la IMO (bandera nacional: sin copyright del diseño); el archivo de Grant es de origen desconocido. us.png va aparte'}, {'n': '10', 'prioridad': 'P2', 'asset': 'raster_images/kahneman.jpg', 'ancho': '1044', 'alto': '1369', 'modo': 'RGB', 'escenas': '5', 'ejemplo': '_2019/bayes/part1/IntroduceKahnemanAndTversky', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Daniel Kahneman', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '11', 'prioridad': 'P2', 'asset': 'raster_images/tversky.jpg', 'ancho': '217', 'alto': '305', 'modo': 'L', 'escenas': '5', 'ejemplo': '_2019/bayes/part1/IntroduceKahnemanAndTversky', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Amos Tversky', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '12', 'prioridad': 'P2', 'asset': 'svg_images/FourierOneLine.svg', 'ancho': 'svg', 'alto': '0 0 1920 1080', 'modo': 'SVG', 'escenas': '5', 'ejemplo': '_2019/diffyq/part4/fourier_series_scenes/DE4Thumbnail', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'obra_3b1b', 'que_crear': '', 'nota': 'Contorno de una sola línea del retrato de Fourier trazado por Grant sobre un retrato de dominio público (FourierOfBritain/FourierOneLine)'}, {'n': '13', 'prioridad': 'P2', 'asset': 'raster_images/imo_2011_p1.png', 'ancho': '2036', 'alto': '1934', 'modo': 'RGBA', 'escenas': '4', 'ejemplo': '_2019/windmill/AskWhatsOnTest', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Hoja propia con los enunciados escritos con LaTeX (los problemas de la IMO 2011, p. 1 y 2) sin el logo de la IMO', 'nota': 'Captura del examen oficial de la IMO 2011 (texto y emblema de la IMO)'}, {'n': '14', 'prioridad': 'P2', 'asset': 'raster_images/imo_2011_p2.png', 'ancho': '2036', 'alto': '1930', 'modo': 'RGBA', 'escenas': '4', 'ejemplo': '_2019/windmill/AskWhatsOnTest', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Hoja propia con los enunciados escritos con LaTeX (los problemas de la IMO 2011, p. 1 y 2) sin el logo de la IMO', 'nota': 'Captura del examen oficial de la IMO 2011 (texto y emblema de la IMO)'}, {'n': '15', 'prioridad': 'P2', 'asset': 'raster_images/Dirichlet.jpg', 'ancho': '493', 'alto': '545', 'modo': 'RGB', 'escenas': '3', 'ejemplo': '_2019/spirals/DirichletComingUp', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Dirichlet de dominio público (Commons)', 'nota': 'Grabado/litografía del siglo XIX: dominio público probable'}, {'n': '16', 'prioridad': 'P2', 'asset': 'svg_images/bunny.svg', 'ancho': 'svg', 'alto': '0 0 512 512', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2019/clacks/solution1/AltShowTwoPopulations', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Silueta de conejo', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '17', 'prioridad': 'P2', 'asset': 'svg_images/fox.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2019/clacks/solution1/AltShowTwoPopulations', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Zorro de contorno', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '18', 'prioridad': 'P2', 'asset': 'svg_images/linda.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2019/bayes/part1/AlternatePhrasings', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Busto de mujer (Linda)', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '19', 'prioridad': 'P2', 'asset': 'svg_images/rabbit.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2019/clacks/solution1/AltShowTwoPopulations', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Conejo de contorno', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '20', 'prioridad': 'P2', 'asset': 'raster_images/Archimedes.jpg', 'ancho': '640', 'alto': '853', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Arquímedes de dominio público (Domenico Fetti, 1620; descarga de Commons en el setup)', 'nota': 'Pintura del siglo XVII (probablemente Domenico Fetti): dominio público casi seguro; no verificado en Commons'}, {'n': '21', 'prioridad': 'P2', 'asset': 'raster_images/Cantor.jpg', 'ancho': '534', 'alto': '700', 'modo': 'L', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Georg Cantor de dominio público (Commons)', 'nota': 'Fotografía de hacia 1910 (autor desconocido, Cantor murió en 1918): dominio público probable'}, {'n': '22', 'prioridad': 'P2', 'asset': 'raster_images/Fermat.jpg', 'ancho': '299', 'alto': '400', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Fermat de dominio público (Commons)', 'nota': 'Pintura anónima del siglo XVII: dominio público casi seguro'}, {'n': '23', 'prioridad': 'P2', 'asset': 'raster_images/Godel.jpg', 'ancho': '212', 'alto': '270', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Gödel de dominio público (Commons) o dibujo propio', 'nota': 'Fotografía de hacia 1925 (la que usa Wikipedia, marcada como dominio público): hay que confirmar en Commons'}, {'n': '24', 'prioridad': 'P2', 'asset': 'raster_images/Johann_Bernoulli2.jpg', 'ancho': '500', 'alto': '620', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Johann Bernoulli de dominio público (Commons)', 'nota': 'Pintura del siglo XVIII: dominio público casi seguro'}, {'n': '25', 'prioridad': 'P2', 'asset': 'raster_images/Pythagoras.jpg', 'ancho': '449', 'alto': '599', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Foto del busto de Pitágoras de Commons (CC0/CC BY) o dibujo propio', 'nota': 'El busto es antiguo (dominio público) pero la fotografía tiene autor: comprobar su licencia (Commons) antes de usarla'}, {'n': '26', 'prioridad': 'P2', 'asset': 'raster_images/Riemann.jpeg', 'ancho': '640', 'alto': '699', 'modo': 'L', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/staging/CommentOnFouriersImmortality', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Retrato de Riemann de dominio público (Commons)', 'nota': 'Grabado/fotografía de 1863 aprox.: dominio público casi seguro'}, {'n': '27', 'prioridad': 'P2', 'asset': 'raster_images/earth.png', 'ancho': '1826', 'alto': '1815', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2019/diffyq/part1/staging/BreakingSecondOrderIntoTwoFirstOrder', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'dominio_publico', 'que_crear': 'Textura NASA (Blue Marble, dominio público) descargada en el setup', 'nota': 'Imagen de la Tierra tipo NASA Blue Marble: dominio público probable (NASA); origen exacto no verificado'}, {'n': '28', 'prioridad': 'P2', 'asset': 'raster_images/moon.png', 'ancho': '624', 'alto': '624', 'modo': 'P', 'escenas': '2', 'ejemplo': '_2019/diffyq/part1/staging/BreakingSecondOrderIntoTwoFirstOrder', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'dominio_publico', 'que_crear': 'Luna NASA (LRO, dominio público) descargada en el setup', 'nota': 'Luna llena de tipo NASA/LRO: dominio público probable; la usa también derivados de 2025'}, {'n': '29', 'prioridad': 'P2', 'asset': 'svg_images/Britain.svg', 'ancho': 'svg', 'alto': '0 0 899.8 1080', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/long_fourier_scenes/FourierOfBritain', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Contorno de Gran Bretaña', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); sirve de silueta que dibujan los círculos de Fourier: el reemplazo debe ser UN contorno limpio'}, {'n': '30', 'prioridad': 'P2', 'asset': 'svg_images/SeattleSkyline.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2019/diffyq/part4/long_fourier_scenes/FourierOfSeattle', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Silueta de la ciudad de Seattle', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); sirve de silueta que dibujan los círculos de Fourier: el reemplazo debe ser UN contorno limpio'}, {'n': '31', 'prioridad': 'P2', 'asset': 'svg_images/plane.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2019/clacks/solution2/position_phase_space/ShowMomentumConservation', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Avión visto desde arriba', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '32', 'prioridad': 'P2', 'asset': 'svg_images/programmer.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2019/bayes/part1/ShowProgrammer', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Persona con portátil y </>', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '33', 'prioridad': 'P3', 'asset': 'raster_images/AlanKay.jpg', 'ancho': '1024', 'alto': '682', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/clacks/solution2/simple_scenes/FinalQuote', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Alan Kay en una conferencia', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '34', 'prioridad': 'P3', 'asset': 'raster_images/AskWhatsOnTest_final_image.png', 'ancho': '2560', 'alto': '1440', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2019/windmill/ReadQuestions', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Hoja propia con los problemas escritos con LaTeX (ver imo_2011_p1/p2)', 'nota': 'Composición de Grant con capturas del examen oficial de la IMO 2011'}, {'n': '35', 'prioridad': 'P3', 'asset': 'raster_images/ChaosBookCover.jpg', 'ancho': '1650', 'alto': '2531', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part1/wordy_scenes/GleickQuote', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': "Tarjeta propia (rectángulo con el título y el autor, como texto) en lugar de la portada: Portada de 'Chaos' (Gleick)", 'nota': 'Portada de un libro (copyright del editor)'}, {'n': '36', 'prioridad': 'P3', 'asset': 'raster_images/CodingTrainFourier.jpg', 'ancho': '1280', 'alto': '720', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part4/staging/OtherResources', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Tarjeta propia (make_video_cards.py) con el título del video de The Coding Train', 'nota': 'Miniatura de YouTube de otro canal (contiene personas y personajes con copyright)'}, {'n': '37', 'prioridad': 'P3', 'asset': 'raster_images/Feynman.jpg', 'ancho': '1038', 'alto': '1038', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/clacks/solution2/simple_scenes/ClacksSolution2Thumbnail', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Richard Feynman', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '38', 'prioridad': 'P3', 'asset': 'raster_images/Feynman_teaching.jpg', 'ancho': '1505', 'alto': '1198', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/clacks/solution2/simple_scenes/ClacksSolution2Thumbnail', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Feynman en una pizarra (Caltech)', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '39', 'prioridad': 'P3', 'asset': 'raster_images/Fourier paper.jpg', 'ancho': '1023', 'alto': '1434', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part3/staging/FourierNameIntro', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': "Portada de la 'Théorie analytique de la chaleur' (1822), facsímil de Commons/Gallica", 'nota': 'Portada de un libro de 1822: dominio público; el facsímil digital concreto hay que verificarlo'}, {'n': '40', 'prioridad': 'P3', 'asset': 'raster_images/InfinitePowers.jpg', 'ancho': '994', 'alto': '1500', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part2/staging/StrogatzMention', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': "Tarjeta propia (rectángulo con el título y el autor, como texto) en lugar de la portada: Portada de 'Infinite Powers' (Strogatz)", 'nota': 'Portada de un libro (copyright del editor)'}, {'n': '41', 'prioridad': 'P3', 'asset': 'raster_images/JamesGleick.jpg', 'ancho': '640', 'alto': '853', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part1/wordy_scenes/GleickQuote', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de James Gleick', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '42', 'prioridad': 'P3', 'asset': 'raster_images/KhanLogo.png', 'ancho': '200', 'alto': '200', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2019/diffyq/part2/pi_scenes/ReferenceKhanVideo', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Gráfico propio genérico (hexágono verde con figura) sin la marca de Khan Academy', 'nota': 'Logo de Khan Academy (marca registrada)'}, {'n': '43', 'prioridad': 'P3', 'asset': 'raster_images/MathologerFourier.jpg', 'ancho': '1280', 'alto': '720', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part4/staging/OtherResources', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Tarjeta propia (make_video_cards.py) con el título del video de Mathologer', 'nota': 'Miniatura de YouTube de otro canal (contiene personas y personajes con copyright)'}, {'n': '44', 'prioridad': 'P3', 'asset': 'raster_images/Strogatz_by_bricks.JPG', 'ancho': '758', 'alto': '1136', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/diffyq/part2/staging/StrogatzMention', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Steven Strogatz', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '45', 'prioridad': 'P3', 'asset': 'raster_images/TerryTao.jpg', 'ancho': '1280', 'alto': '720', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/windmill/TerryTaoQuote', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Ilustración propia (silueta) o foto con licencia libre en lugar de la foto de Terence Tao', 'nota': 'Foto reciente de una persona real con copyright probable (autor y licencia desconocidos); sin personas reales en imágenes generadas'}, {'n': '46', 'prioridad': 'P3', 'asset': 'raster_images/flags/us.png', 'ancho': '550', 'alto': '289', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/windmill/USProcessAlt', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'dominio_publico', 'que_crear': 'Bandera de EE. UU. dibujada por código (13 franjas y 50 estrellas)', 'nota': 'Bandera nacional: diseño sin copyright; el archivo concreto es de origen desconocido'}, {'n': '47', 'prioridad': 'P3', 'asset': 'raster_images/nobel_prize.png', 'ancho': '849', 'alto': '845', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/IntroduceKahnemanAndTversky', 'via': 'código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Medalla dorada propia (círculo con relieve, hecha por código)', 'nota': 'Foto de la medalla Nobel (marca/diseño de la Fundación Nobel; foto de origen desconocido)'}, {'n': '48', 'prioridad': 'P3', 'asset': 'raster_images/sun.png', 'ancho': '2229', 'alto': '2230', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2019/clacks/solution2/simple_scenes/ClacksSolution2Thumbnail', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'dominio_publico', 'que_crear': 'Imagen del Sol NASA/SDO (dominio público) descargada en el setup', 'nota': 'Imagen del Sol en falso color tipo NASA/SDO: dominio público probable'}, {'n': '49', 'prioridad': 'P3', 'asset': 'raster_images/thinking_fast_and_slow.jpg', 'ancho': '1083', 'alto': '1717', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/IntroduceKahnemanAndTversky', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': "Tarjeta propia (rectángulo con el título y el autor, como texto) en lugar de la portada: Portada de 'Thinking, Fast and Slow'", 'nota': 'Portada de un libro (copyright del editor)'}, {'n': '50', 'prioridad': 'P3', 'asset': 'raster_images/undoing_project.jpg', 'ancho': '1672', 'alto': '2560', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/IntroduceKahnemanAndTversky', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': "Tarjeta propia (rectángulo con el título y el autor, como texto) en lugar de la portada: Portada de 'The Undoing Project'", 'nota': 'Portada de un libro (copyright del editor)'}, {'n': '51', 'prioridad': 'P3', 'asset': 'svg_images/IP_logo2.svg', 'ancho': 'svg', 'alto': '0 0 2560 1440', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/diffyq/part2/fourier_series/FourierOfIP', 'via': 'código', 'tipo': 'svg_logo', 'derechos': 'obra_3b1b', 'que_crear': '', 'nota': 'Trazo de una sola línea (garabato) hecho por Grant para FourierOfIP; no es un logo de una marca conocida'}, {'n': '52', 'prioridad': 'P3', 'asset': 'svg_images/Mammoth.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/diffyq/part3/staging/CarbonDecayingInMammoth', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Silueta de mamut (5 trazos; el cuerpo es el último)', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '53', 'prioridad': 'P3', 'asset': 'svg_images/black_hole.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/clacks/question/CompareToGalacticMass', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Espiral de agujero negro', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '54', 'prioridad': 'P3', 'asset': 'svg_images/brain.svg', 'ancho': 'svg', 'alto': '0 0 1000 780.724', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/ReprogrammingThought', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Cerebro de contorno', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '55', 'prioridad': 'P3', 'asset': 'svg_images/gold_bars.svg', 'ancho': 'svg', 'alto': '0 0 50 50', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/StateGoal', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Pila de barras de oro', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '56', 'prioridad': 'P3', 'asset': 'svg_images/google_logo.svg', 'ancho': 'svg', 'alto': '0 0 272 92', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/diffyq/part2/fourier_series/FourierGoogleG', 'via': 'código', 'tipo': 'svg_logo', 'derechos': 'logo_marca', 'que_crear': "Una 'G' propia de colores en un círculo, sin el logo de Google", 'nota': 'Logo de Google (marca registrada); lo usa FourierGoogleG (CL1)'}, {'n': '57', 'prioridad': 'P3', 'asset': 'svg_images/imo_2011_2_underline-01.svg', 'ancho': 'svg', 'alto': '0 0 1920 1080', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/windmill/ReadQuestions', 'via': 'código', 'tipo': 'svg_diagrama', 'derechos': 'obra_3b1b', 'que_crear': '', 'nota': 'Subrayados que dibujó Grant sobre el enunciado del problema 2 (formas simples propias)'}, {'n': '58', 'prioridad': 'P3', 'asset': 'svg_images/magnifying_glass.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/footnote/Rearrange', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Lupa', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '59', 'prioridad': 'P3', 'asset': 'svg_images/quixote.svg', 'ancho': 'svg', 'alto': '0 0 1920 1080', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/windmill/QuixoteReference', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Grabado de Don Quijote (Doré, dominio público) o dibujo propio', 'nota': 'Grabado tipo Gustave Doré (1863), dominio público probable; no verificado'}, {'n': '60', 'prioridad': 'P3', 'asset': 'svg_images/rain.svg', 'ancho': 'svg', 'alto': '0 0 397.63 397.63', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/WhenDiscreteChunksArentSoClean', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Nube con lluvia, de contorno', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '61', 'prioridad': 'P3', 'asset': 'svg_images/rain_cloud.svg', 'ancho': 'svg', 'alto': '0 0 339 321', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/WhenDiscreteChunksArentSoClean', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Nube rellena con gotas', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '62', 'prioridad': 'P3', 'asset': 'svg_images/santa_hat.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/QA_2to21/HolidayStorePromotionTime', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Gorro de Papá Noel', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '63', 'prioridad': 'P3', 'asset': 'svg_images/science.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/StateGoal', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Matraz con burbujas', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '64', 'prioridad': 'P3', 'asset': 'svg_images/scientist.svg', 'ancho': 'svg', 'alto': '0 0 128 128', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/UsesOfBayesTheorem', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Científica con matraz', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '65', 'prioridad': 'P3', 'asset': 'svg_images/sunny.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/bayes/part1/WhenDiscreteChunksArentSoClean', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Sol con rayos', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '66', 'prioridad': 'P3', 'asset': 'svg_images/windmill.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/windmill/QuixoteReference', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Icono propio dibujado por código (make_visual_svgs.py): Molino de viento', 'nota': 'Icono vectorial de terceros (Noun Project/similar, autor y licencia no verificables); decorativo; no se verificó el origen'}, {'n': '67', 'prioridad': 'P3', 'asset': 'svg_images/windmill_fairytale.svg', 'ancho': 'svg', 'alto': '0 0 1920 1080', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2019/windmill/WindmillFairyTale', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'obra_3b1b', 'que_crear': '', 'nota': "Texto en cursiva 'Once upon a time, there was a windmill...' compuesto por Grant (texto propio)"}]
SPECS={}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,b):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.stem+'.part'+p.suffix);tmp.write_bytes(b);tmp.replace(p)
def font(n,bold=False,serif=False):return ImageFont.truetype(str(FONTS/('CMUSerif-Roman.ttf' if serif else 'JetBrainsMono-Bold.ttf' if bold else 'JetBrainsMono-Regular.ttf')),max(6,int(n)))
def fitted(text,width,size):
 while size>7 and max(font(size).getlength(s) for s in text.split('\n'))>width:size-=1
 return font(size)
def path(ds,fill='#171D26',stroke='none',sw=0):return f'<path fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" d="{ds}"/>'
def polygon_path(g):
 assert g.geom_type=='Polygon' and not g.is_empty
 pts=list(g.exterior.coords);return 'M '+' L '.join(f'{x:.5f} {y:.5f}' for x,y in pts)+' Z'
def solid(g,color='#171D26'):return path(polygon_path(g),color)
def line(points,width=3,color='#171D26'):
 return solid(LineString(points).buffer(width/2,cap_style='round',join_style='round'),color)
def ellipse(x,y,rx,ry=None):
 from shapely.affinity import scale
 return scale(Point(x,y).buffer(1,quad_segs=24),rx,ry or rx,origin=(x,y))
def ring(x,y,r,t=3):
 a=ellipse(x,y,r);b=ellipse(x,y,r-t);return path(polygon_path(a)+' '+polygon_path(b)[::-1]) if False else path(polygon_path(a)+' '+polygon_path(Polygon(list(b.exterior.coords)[::-1])))
def svg(row,body):
 vb=row['alto'];x,y,w,h=map(float,vb.split());return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><!-- Independent drawing, CC0, own code. -->\n<g transform="translate({x} {y}) scale({w/100} {h/100})">{body}</g></svg>'

def clean_contour(ds):
 """Outline the OWN Beziers as one simple closed contour, opening tiny counter slits.
 Never reads an original asset. Short bridges join own decorative pieces; nearest
 cuts open enclosed counters so a Fourier traversal never jumps to a second loop.
 """
 import svgelements as se
 from shapely.ops import nearest_points
 p=se.Path(ds);pts=[]
 for seg in p:
  if isinstance(seg,se.Move):pts.append(tuple(seg.end))
  else:pts.extend(tuple(seg.point(i/40)) for i in range(1,41))
 g=Polygon(pts).buffer(0)
 while g.geom_type=='MultiPolygon':
  pieces=list(g.geoms);a=max(pieces,key=lambda q:q.area);b=min((q for q in pieces if q is not a),key=lambda q:q.distance(a));u,v=nearest_points(a,b);g=unary_union([g,LineString([u,v]).buffer(.3)])
 while g.interiors:
  interior=LineString(g.interiors[0].coords);u,v=nearest_points(interior,g.exterior);g=g.difference(LineString([u,v]).buffer(.18,cap_style='round'))
  assert g.geom_type=='Polygon'
 g=g.simplify(.01,preserve_topology=True);assert g.is_valid and not g.interiors
 return polygon_path(g)

def visual(name):
 if name=='TrebleClef':
  # Open-slotted spiral ribbon: one handwritten contour, no interior subpaths.
  return path(clean_contour('M 50 91 C 35 101 31 87 40 83 C 45 81 47 88 42 90 C 49 94 56 87 53 78 L 42 29 C 38 11 53 1 59 7 C 72 22 49 40 35 48 C 12 63 29 86 51 78 C 70 71 62 48 46 49 C 35 49 31 64 42 66 L 43 61 C 39 59 41 54 47 55 C 57 55 60 69 50 73 C 32 80 23 62 39 52 C 61 38 75 18 62 5 C 51 -5 32 12 36 31 L 48 80 C 51 86 49 91 43 92 C 40 92 39 89 41 88 C 44 92 48 89 46 85 C 40 77 28 85 34 94 C 38 101 48 100 53 95 Z'))
 if name=='EighthNote':return path('M 58 13 L 65 13 C 67 25 83 25 84 40 C 84 47 79 52 72 55 C 81 43 70 36 65 35 L 65 78 C 64 91 41 99 29 90 C 16 80 28 66 43 67 C 48 67 53 69 58 72 Z')
 if name=='Nail_And_Gear':
  pts=[]
  for i in range(48):
   a=2*math.pi*i/48;r=28 if i%4 in (1,2) else 23;pts.append((53+r*math.cos(a),58+r*math.sin(a)))
  g=unary_union([Polygon(pts),LineString([(16,91),(79,13)]).buffer(4),LineString([(70,6),(89,22)]).buffer(5)])
  return solid(Polygon(g.exterior))
 if name=='dart':return path('M 8 91 L 45 47 L 40 29 L 61 8 L 66 31 L 89 34 L 68 55 L 51 52 Z')+path('M 46 46 L 64 32 L 88 34 L 66 53 Z','#61758B')
 if name=='book':return path('M 8 20 Q 30 12 48 26 L 48 83 Q 28 69 8 77 Z M 53 26 Q 73 12 94 20 L 94 77 Q 72 69 53 83 Z')+path('M 15 29 Q 31 25 40 34 M 15 41 Q 31 37 40 46 M 62 34 Q 77 25 87 29 M 62 46 Q 77 37 87 41','none','#F6F1E4',2)
 if name=='farming':
  out=''
  for x in [25,50,75]:
   out+=line([(x,66),(x,23)],3)
   for y in [28,38,48]:out+=path(f'M {x} {y+7} Q {x-15} {y+7} {x-11} {y-4} Q {x-1} {y-1} {x} {y+7} Z M {x} {y+7} Q {x+15} {y+7} {x+11} {y-4} Q {x+1} {y-1} {x} {y+7} Z')
  return out+''.join(line([(7,y+8),(45,y),(93,y+7)],3) for y in [72,83,92])
 if name in ['steve','linda']:
  out=path('M 12 94 L 17 77 Q 27 66 39 64 L 61 64 Q 76 68 85 78 L 90 94 Z')
  head=ellipse(50,37,22,27)
  if name=='steve':
   holes=unary_union([box(29,34,47,45),box(53,34,71,45),box(47,36,53,39)])
   out+=path(polygon_path(head)+' '+polygon_path(Polygon(list(holes.exterior.coords)[::-1])))
  else:out+=solid(head)+path('M 26 54 Q 15 19 40 9 Q 74 2 77 39 L 80 65 L 66 61 L 69 30 Q 45 31 33 20 L 32 60 Z')
  return out
 raise KeyError(name)
# All geometry below is newly authored; no original SVG is parsed or traced.
def font_outline(text,x,y,width,height):
 from matplotlib.textpath import TextPath
 from matplotlib.font_manager import FontProperties
 tp=TextPath((0,0),text,prop=FontProperties(fname=str(FONTS/'Caveat[wght].ttf')),size=100);bb=tp.get_extents();ds=[]
 for poly in tp.to_polygons():
  pts=[(x+(px-bb.x0)/bb.width*width,y+height-(py-bb.y0)/bb.height*height) for px,py in poly]
  ds.append('M '+' L '.join(f'{xx:.5f} {yy:.5f}' for xx,yy in pts)+' Z')
 return path(' '.join(ds))

def windmill():
 out=path('M 33 91 L 39 44 L 59 44 L 68 91 Z')+path('M 33 45 L 49 29 L 65 45 Z','#6B7B8C')
 for a in range(4):
  angle=math.pi*a/2;pts=[]
  for x,y in [(0,-4),(31,-4),(31,6),(7,5)]:pts.append((49+x*math.cos(angle)-y*math.sin(angle),43+x*math.sin(angle)+y*math.cos(angle)))
  out+=solid(Polygon(pts),'#A5B6BD')
 return out+solid(ellipse(49,43,5))

VISUAL_P1=visual
def visual(name):
 if name in ['TrebleClef','EighthNote','Nail_And_Gear','dart','book','farming','steve','linda']:return VISUAL_P1(name)
 if name=='FourierOneLine':raise ValueError('Use fourier_portrait con fuente Commons verificada')
 if name in ['bunny','rabbit']:
  return path('M 14 80 C 2 70 8 60 20 63 C 15 50 22 38 36 39 L 36 14 C 35 1 46 2 48 16 L 51 40 L 60 12 C 64 0 75 4 71 17 L 64 43 C 85 46 90 59 82 69 L 92 75 L 84 84 L 67 83 L 75 92 L 52 92 L 46 83 C 34 91 20 90 14 80 Z')+solid(ellipse(69,56,2),'#F4F0E7')
 if name=='fox':return path('M 12 76 Q 1 46 18 37 Q 17 62 36 67 Q 26 46 42 31 L 38 10 L 57 26 L 73 10 L 76 33 Q 95 39 92 51 L 75 64 L 66 61 L 60 78 L 70 89 L 48 89 L 42 79 Q 22 94 12 76 Z')+path('M 56 43 L 68 52 L 83 44 L 76 60 L 67 62 Z','#F4F0E7')
 if name=='Britain':return path('M 56 5 L 67 8 L 63 19 L 65 28 L 60 32 L 53 39 L 56 43 L 60 48 L 63 54 L 67 62 L 68 69 L 80 74 L 80 81 L 76 83 L 83 85 L 74 89 L 62 87 L 51 89 L 42 87 L 25 95 L 18 96 L 26 91 L 37 86 L 40 81 L 33 79 L 33 74 L 29 72 L 34 69 L 43 70 L 48 67 L 44 61 L 43 55 L 35 49 L 34 44 L 30 42 L 34 38 L 27 35 L 33 29 L 26 25 L 33 21 L 32 17 L 38 17 L 43 7 L 49 9 Z')
 if name=='SeattleSkyline':
  shapes=[box(5,85,95,94),box(7,57,18,88),box(20,68,30,88),box(33,40,43,88),box(48,49,56,88),box(76,63,89,88),box(88,72,95,88),box(65,28,69,88),ellipse(67,28,14,5),box(66,9,68,28)]
  return solid(Polygon(unary_union(shapes).exterior))
 if name=='plane':return path('M 48 5 Q 51 1 54 5 L 57 40 L 92 66 L 92 74 L 57 62 L 57 82 L 70 93 L 70 98 L 51 93 L 32 98 L 32 93 L 45 82 L 45 62 L 10 74 L 10 66 L 45 40 Z')
 if name in ['programmer','scientist']:
  head=solid(ellipse(50,26,16,19));body=path('M 13 89 L 20 61 Q 30 48 50 48 Q 73 49 81 62 L 88 89 Z')
  if name=='programmer':return head+body+path('M 24 64 L 77 64 L 73 91 L 28 91 Z','#829AA3')+path('M 45 73 L 38 79 L 45 84 M 56 73 L 63 79 L 56 84 M 49 85 L 53 72','none','#172831',3)
  return head+body+path('M 38 47 L 50 66 L 62 47 L 70 87 L 30 87 Z','#D7E0DC')+path('M 76 58 L 86 58 L 86 70 L 95 85 Q 97 92 88 92 L 73 92 Q 65 92 68 85 L 76 70 Z','#839CAA')
 if name=='IP_logo2':return path('M 20 72 Q 10 36 33 28 Q 47 23 50 47 Q 54 67 72 59 Q 90 50 77 31 L 85 26 Q 103 54 79 70 Q 50 88 41 51 Q 38 34 29 39 Q 20 48 29 68 Z')
 if name=='Mammoth':
  # Exactly five paths; the body is last as the installed scene explicitly selects [4].
  return path('M 73 62 Q 98 82 99 55 Q 96 67 80 54 Z','#BDA77F')+solid(ellipse(74,36,2),'#D4C5A4')+path('M 74 55 Q 95 70 99 46 Q 95 60 81 49 Z','#D4C5A4')+path('M 8 46 Q 0 50 5 64 L 11 59 Z')+path('M 12 80 L 12 44 Q 11 19 30 15 Q 45 6 59 18 Q 78 15 87 35 L 90 66 Q 94 79 99 68 L 99 78 Q 81 94 79 62 L 75 51 L 68 66 L 67 94 L 54 94 L 52 74 L 36 74 L 32 94 L 18 94 L 20 73 Z '+polygon_path(ellipse(74,36,2)))
 if name=='black_hole':
  pts=[]
  for t in np.linspace(0,5*math.pi,240):r=3+2.5*t;pts.append((50+r*math.cos(t),50+r*math.sin(t)))
  return line(pts,4)+solid(ellipse(50,50,9))
 if name=='brain':return path('M 49 17 Q 38 5 28 18 Q 10 15 14 33 Q 1 44 12 55 Q 2 74 21 78 Q 28 95 43 86 L 49 91 Z M 54 17 Q 67 5 76 18 Q 93 17 88 34 Q 100 46 89 57 Q 98 74 79 80 Q 72 96 59 86 L 54 91 Z')+path('M 28 23 Q 39 29 30 43 Q 17 42 23 57 Q 39 52 38 72 M 75 24 Q 60 31 72 44 Q 86 42 80 58 Q 64 55 66 74','none','#E8EBE4',3)
 if name=='gold_bars':return path('M 8 67 L 17 49 L 44 49 L 51 67 Z M 48 67 L 56 49 L 83 49 L 92 67 Z M 26 44 L 34 27 L 64 27 L 74 44 Z','#BD9B56')
 if name=='google_logo':
  c='#334958'
  dots=''.join(solid(ellipse(3+i*2,95,.35),c) for i in range(5))
  glyph=path('M 66 18 L 66 36 L 62 36 C 59 8 36 8 34 47 C 32 83 53 94 64 70 L 64 59 L 54 59 L 54 52 L 72 52 L 72 59 L 69 59 L 69 84 L 66 84 L 63 79 C 43 100 27 79 28 48 C 29 14 49 1 61 15 L 64 9 Z',c)
  return dots+'<g transform="translate(15 0) scale(.7 1)">'+glyph+'</g>'
 if name=='magnifying_glass':return ring(40,40,27,7)+line([(59,60),(88,90)],12)
 if name=='quixote':
  return path('M 21 70 L 14 89 L 7 91 L 12 68 L 21 58 L 45 60 L 55 46 L 68 43 L 73 50 L 65 59 L 61 72 L 66 90 L 59 91 L 50 73 L 35 76 L 29 93 L 22 93 L 27 73 Z')+path('M 33 59 L 30 41 L 32 30 L 44 29 L 49 42 L 45 60 Z')+solid(ellipse(37,22,6,8))+line([(46,45),(73,7)],2)+path('M 26 19 L 46 19 L 40 13 L 33 13 Z')
 if name in ['rain','rain_cloud']:
  cloud=unary_union([ellipse(30,40,18),ellipse(49,28,22),ellipse(71,39,18),box(25,35,74,55)])
  return solid(Polygon(cloud.exterior),'#4E677A')+''.join(line([(x+4,66),(x-1,82)],4,'#547A95') for x in [27,49,71])
 if name=='santa_hat':return path('M 19 73 Q 23 18 61 13 Q 77 10 88 44 L 77 48 Q 66 30 57 34 Q 65 53 70 75 Z','#934A48')+solid(ellipse(85,47,12),'#DADCD5')+path('M 12 72 Q 41 63 75 74 L 77 88 Q 46 78 11 88 Z','#DADCD5')
 if name=='science':return path('M 35 10 L 65 10 L 65 18 L 60 18 L 60 43 L 86 79 Q 92 92 76 94 L 25 94 Q 9 91 16 78 L 40 43 L 40 18 L 35 18 Z','#647E85')+path('M 30 66 L 71 66 L 80 83 Q 84 88 73 88 L 28 88 Q 17 88 23 80 Z','#D5DFDA')+solid(ellipse(70,29,4),'#647E85')+solid(ellipse(78,14,3),'#647E85')
 if name=='sunny':
  return solid(ellipse(50,50,22),'#C4A05B')+''.join(line([(50+31*math.cos(a),50+31*math.sin(a)),(50+42*math.cos(a),50+42*math.sin(a))],5,'#C4A05B') for a in np.arange(8)*math.pi/4)
 if name=='windmill':return windmill()
 if name=='windmill_fairytale':return font_outline('Once upon a time,',4,6,91,24)+font_outline('there was',26,38,49,21)+font_outline('a windmill...',18,69,69,24)
 if name=='imo_2011_2_underline-01':
  # Eleven semantic text lines; scene groups them [1,2,3,2,1,2].
  return ''.join(path(f'M 0 {50+(i-5)*(56/2380*100*1920/1080):.5f} L {100*len(WIND_LINES[i])/len(WIND_LINES[0]):.5f} {50+(i-5)*(56/2380*100*1920/1080):.5f}','none','#517B83',.25) for i in range(11))
 raise KeyError(name)


def synth_audio(dest,params):
 sr,channels,width,frames=params;t=np.arange(frames)/sr;rng=np.random.default_rng(2019)
 x=.65*rng.normal(size=frames)*np.exp(-t/0.005)+.3*np.sin(2*np.pi*3300*t)*np.exp(-t/.009)
 x+=.20*rng.normal(size=frames)*np.exp(-np.maximum(t-.035,0)/.006)*(t>=.035)
 x*=np.minimum(t/.0006,1);x*=np.minimum((t[-1]-t)/.004,1);x=np.clip(x,-.92,.92)
 a=np.repeat(x[:,None],channels,axis=1)
 if width==2:raw=(a*32767).astype('<i2').tobytes()
 else:raise ValueError('Only PCM16 source schema supported')
 b=io.BytesIO()
 with wave.open(b,'wb') as f:f.setnchannels(channels);f.setsampwidth(width);f.setframerate(sr);f.writeframes(raw)
 atomic(dest,b.getvalue())

def existing(row):
 # Verified source manifests; legacy kept records without content hashes are not evidence.
 dest=ASSETS/row['asset']
 if not dest.is_file():return None
 for file in HERE.parent.rglob('*sources.json'):
  if file.parent==HERE:continue
  data=json.loads(file.read_text());records=data.values() if isinstance(data,dict) else data
  for r in records:
   if not isinstance(r,dict):continue
   asset=r.get('asset') or ('raster_images/'+r.get('name',''))
   if asset==row['asset'] and r.get('status') in ('generated','replaced','kept') and r.get('sha256')==sha(dest):return r|{'provenance_file':str(file.relative_to(ROOT))}
 return None

def scene_audit(row):
 file=ROOT/'_work'/(row['ejemplo']+'.py');name=Path(row['asset']).stem
 if not file.exists():return {'scene':str(file),'matches':[],'note':'Example path missing; inspect related class before implementation.'}
 lines=file.read_text().splitlines();matches=[]
 for i,line_ in enumerate(lines):
  if name.lower() in line_.lower():matches.append({'line':i+1,'context':'\n'.join(lines[max(0,i-1):i+4])})
 return {'scene':str(file.relative_to(ROOT)),'matches':matches[:12]}

def progress(records):
 done={k:r.get('delivery_state','hecha' if r.get('status') in ['generated','kept','replaced'] else 'saltada') for k,r in records.items()};counts={s:list(done.values()).count(s) for s in ['hecha','ya_existe','entregada_IA','saltada']};pending=[r for r in ROWS if r['asset'] not in records];next_=pending[0] if pending else None
 lines=['# Progreso de assets 2019','','## AHORA',f"Último paso: {list(records)[-1] if records else 'inventario inicial'}.",f"Estados: {counts}; pendientes: {len(pending)}.",f"Sigue: {next_['n']+' '+next_['asset'] if next_ else 'tanda terminada; revisar hoja y atribuciones'}.",f"Continuar: `python _lib/assets/generated/replacements/assets2019/make_assets_2019.py --priority {next_['prioridad'] if next_ else 'P3'}`.",'','| # | Prioridad | Asset | Estado | Vía | Fuente | Licencia | Nota |','|---:|---|---|---|---|---|---|---|']
 for row in ROWS:
  r=records.get(row['asset'],{});lines.append('| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in [row['n'],row['prioridad'],row['asset'],done.get(row['asset'],'pendiente'),r.get('via',row['via']),r.get('page_url',''),r.get('license',''),r.get('note','')])+' |')
 lines+=['','## Resumen',str(counts)+f'; {len(pending)} pendientes.','','## Atribuciones']
 lines += [f"- {k}: {r.get('author')}; {r.get('license')}; {r.get('page_url')}." for k,r in records.items() if r.get('license','').startswith(('CC BY','MIT'))]
 lines+=['','## Revisión','Sin renders de escenas, cambios en escenas, git ni publicación. Las fuentes y los contornos se validan por archivo. IA: ninguna. Los SVG se escriben desde geometría propia, sin derivar los originales.']
 (AUDIT/'PROGRESO_2019.md').write_text('\n'.join(lines)+'\n')

def review(records):
 sheet=Image.new('RGB',(1500,math.ceil(len(ROWS)/6)*190),'#DFE3E2');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(ROWS):
  x=i%6*250;y=i//6*190;dest=ASSETS/row['asset'];draw.text((x+5,y+4),row['n']+' '+Path(row['asset']).name,fill='#17303B')
  if row['asset'] not in records:continue
  try:
   if dest.suffix=='.svg':im=Image.open(io.BytesIO(subprocess.check_output(['rsvg-convert','-w','230','-h','140',str(dest)],stderr=subprocess.DEVNULL))).convert('RGBA')
   elif dest.suffix=='.wav':
    with wave.open(str(dest)) as w:a=np.frombuffer(w.readframes(w.getnframes()),'<i2');a=a[::w.getnchannels()]
    im=Image.new('RGBA',(230,140),'white');dd=ImageDraw.Draw(im);bins=np.array_split(a,230)
    for j,b in enumerate(bins):v=max(abs(b.astype(float)))/32768*62;dd.line((j,70-v,j,70+v),fill='#36738C')
   elif '*' in str(dest):
    im=Image.open(AUDIT/'REVISION_2019_BANDERAS.png').convert('RGBA')
   else:im=Image.open(dest).convert('RGBA')
   thumb=ImageOps.contain(im,(230,140));bg=Image.new('RGBA',thumb.size,'white');bg.alpha_composite(thumb);sheet.paste(bg.convert('RGB'),(x+(250-thumb.width)//2,y+25))
  except Exception as e:draw.text((x+5,y+70),'Review: '+str(e)[:25],fill='red')
  draw.text((x+5,y+173),records[row['asset']].get('delivery_state','hecha'),fill='#326448')
 sheet.save(AUDIT/'REVISION_2019.png')

def generate(row,spec,dest,rec):
 if row['modo']=='SVG':atomic(dest,svg(row,visual(dest.stem)).encode());rec['svg_paths']=len(ET.parse(dest).getroot().findall('.//{http://www.w3.org/2000/svg}path'))
 elif row['modo']=='WAV':
  backup=CACHE/'originales'/row['asset']
  with wave.open(str(backup)) as w:params=(w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())
  synth_audio(dest,params);rec['audio_schema']=params
 else:raise KeyError(row['asset'])
FLAG_COMMIT='ac7e0eb3259eb62aa6100c435607e2fe03896a97'
SPECS.update({
 '10':{'title':'File:Weaving a Wake of Memories.jpg','crop':[850/4731,1400/3744,1650/4731,2450/3744],'refine_note':'Recorte de busto a cabeza, sin texto ni terceros; fuente 4731×3744, recorte 800×1050, ampliación 1.305×.'},
 '11':{'card':'Amos Tversky','reason':'No se localizó una fotografía individual adecuada con licencia libre verificable; Wikipedia no ofrece imagen libre y la búsqueda Commons devolvió documentos ajenos.'},
 '15':{'title':'File:Peter Gustav Lejeune Dirichlet.jpg'},
 '20':{'title':'File:Domenico-Fetti Archimedes 1620.jpg'},
 '21':{'title':'File:Georg Cantor (Porträt).jpg'},
 '22':{'title':'File:Pierre de Fermat.jpg'},
 '23':{'title':'File:Kurt gödel.jpg'},
 '24':{'title':'File:Johann Bernoulli2.jpg'},
 '25':{'title':'File:Pythagoras in the Roman Forum, Colosseum.jpg'},
 '26':{'title':'File:Georg Friedrich Bernhard Riemann.jpeg'},
 '27':{'title':'File:The Earth seen from Apollo 17.jpg','disc':True},
 '28':{'title':'File:FullMoon2010.jpg','disc':True},
 '33':{'title':'File:Alan Kay (3097597186).jpg','crop':[1450/4752,200/3164,3754/4752,1736/3164],'refine_note':'Recorte de busto centrado con fondo negro limpio: sin rótulos, logos ni otras personas. Fuente 4752×3164; recorte 2304×1536; reducción a 0.444×.'},
 '35':{'card':'Chaos\n\nJames Gleick'},
 '36':{'card':'Drawing with Fourier Transform\nand Epicycles\n\nThe Coding Train'},
 '37':{'title':'File:Richard Feynman 1959.png'},
 '38':{'title':'File:Richard Feynman 1988.png','crop':[0,0,1,.58],'refine_note':'Foto distinta de Feynman de pie junto a una pizarra; no es la toma de 1959 de Feynman.jpg.'},
 '39':{'title':'File:Fourier - Théorie analytique de la chaleur, 1822.djvu','pdf_page':9},
 '40':{'card':'Infinite Powers\n\nSteven Strogatz'},
 '41':{'title':'File:James Gleick color.jpg'},
 '43':{'card':"Epicycles, complex Fourier series\nand Homer Simpson's orbit\n\nMathologer"},
 '44':{'title':'File:Steven Strogatz in 2025.jpg'},
 '45':{'extend':True,'title':"File:Terence Tao at IPAM's Fireside Chat 2026 (50m16s) (cropped).jpg"},
 '48':{'title':"File:The Sun by the Atmospheric Imaging Assembly of NASA's Solar Dynamics Observatory - 20100819.jpg",'disc':True},
 '49':{'card':'Thinking, Fast and Slow\n\nDaniel Kahneman'},
 '50':{'card':'The Undoing Project\n\nMichael Lewis'}
})
COMMONS={}
EXTERNAL=None

def existing(row):
 global EXTERNAL
 dest=ASSETS/row['asset']
 if not dest.is_file():return None
 if EXTERNAL is None:
  EXTERNAL={}
  for file in HERE.parent.rglob('*sources.json'):
   if file.parent==HERE:continue
   data=json.loads(file.read_text());records=data.values() if isinstance(data,dict) else data
   for r in records:
    if not isinstance(r,dict):continue
    asset=r.get('asset') or ('raster_images/'+r.get('name',''))
    if r.get('status') in ('generated','replaced','kept') and r.get('sha256'):EXTERNAL[asset]=r|{'provenance_file':str(file.relative_to(ROOT))}
 r=EXTERNAL.get(row['asset'])
 if r and sha(dest)==r['sha256']:return r
 if row['n']=='46':
  # The current task explicitly identifies this file as an existing code-generated flag.
  with Image.open(dest) as im:
   if im.size!=(550,289) or im.mode!='RGB':return None
  return {'asset':row['asset'],'name':dest.name,'author':'propio (código), reemplazo anterior identificado por ASSETS_2019.md','license':'CC0','license_url':CC0,'status':'generated','sha256':sha(dest),'via':'código','provenance_file':'_tools/assets_licencias/codex/ASSETS_2019.md#banderas'}
 return None

def flags(rec):
 license_url=f'https://raw.githubusercontent.com/lipis/flag-icons/{FLAG_COMMIT}/LICENSE';lic=d.http(license_url).decode();assert 'MIT License' in lic and 'Permission is hereby granted' in lic
 atomic(CACHE/'licencias/flag-icons-LICENSE.txt',lic.encode());atomic(HERE/'licenses/flag-icons-MIT.txt',lic.encode())
 archive=d.cached(f'https://codeload.github.com/lipis/flag-icons/tar.gz/{FLAG_COMMIT}', '.tar.gz')
 with tarfile.open(archive,'r:gz') as tf:
  members={m.name.split('/flags/',1)[1]:m for m in tf.getmembers() if '/flags/' in m.name and m.isfile()}
  records=json.loads((HERE/'flags_sources.json').read_text()) if (HERE/'flags_sources.json').exists() else {}
  for dest in sorted((ASSETS/'raster_images/flags').glob('*.png')):
   if dest.stem=='us':continue # Separate row46; do not overwrite its existing own-code flag.
   asset=str(dest.relative_to(ASSETS));prior=existing({'asset':asset,'n':'9'})
   if prior:records[asset]=prior|{'delivery_state':'ya_existe'};continue
   backup=CACHE/'originales'/asset
   if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
   with Image.open(backup) as old:size,mode=old.size,old.mode
   code={'uk':'gb','ks':'xk'}.get(dest.stem,dest.stem);key=('1x1/' if code=='ch' else '4x3/')+code+'.svg'
   if key not in members:raise ValueError('Flag not available in verified archive: '+code)
   raw=tf.extractfile(members[key]).read();source_svg=CACHE/'flag-icons'/(code+'.svg');atomic(source_svg,raw)
   oldrec=records.get(asset,{})
   if oldrec.get('sha256')!=sha(dest):
    data=subprocess.check_output(['rsvg-convert','-w',str(max(size)),'-h',str(max(size)),str(source_svg)],stderr=subprocess.DEVNULL);im=Image.open(io.BytesIO(data)).convert('RGBA')
    if code=='np':
     im=im.crop(im.getchannel('A').getbbox());fg=ImageOps.contain(im,size,Image.Resampling.LANCZOS);im=Image.new('RGBA',size);im.alpha_composite(fg,((size[0]-fg.width)//2,(size[1]-fg.height)//2))
    else:im=im.resize(size,Image.Resampling.LANCZOS)
    if mode=='P':
     bg=Image.new('RGBA',size,'white');bg.alpha_composite(im);im=bg.convert('RGB').quantize(colors=256)
    elif mode=='RGB':
     bg=Image.new('RGBA',size,'white');bg.alpha_composite(im);im=bg.convert('RGB')
    d.save(im,dest,mode)
   records[asset]={'asset':asset,'name':dest.name,'status':'replaced' if not oldrec else 'kept','author':'Panayiotis Lipiridis and flag-icons contributors','license':'MIT','license_url':license_url,'page_url':f'https://github.com/lipis/flag-icons/blob/{FLAG_COMMIT}/flags/'+key,'source_sha256':hashlib.sha256(raw).hexdigest(),'sha256':sha(dest),'size':list(size),'mode':mode,'changes':'SVG libre rasterizado y ajustado al tamaño/modo existentes; Nepal conserva silueta y transparencia.','delivery_state':'hecha'}
   d.atomic_json(HERE/'flags_sources.json',records)
   print('  flag',code,flush=True)
  d.atomic_json(HERE/'flags_sources.json',records)
 rec.update(author='Panayiotis Lipiridis and flag-icons contributors',license='MIT',license_url=license_url,page_url='https://github.com/lipis/flag-icons',status='replaced',via='descargar',flag_count=len(records),source_sha256=sha(archive),note=f'{len(records)} banderas (us va aparte); se conservan au/kr/sk ya verificadas. MIT admitida expresamente en la sección de banderas. Ver flags_sources.json; tamaños/modos individuales preservados.',sha256=sha(HERE/'flags_sources.json'))
 # Readable flag contact, not a native sheet.
 sheet=Image.new('RGB',(1120,math.ceil(len(records)/14)*68),'#E3E8E5');draw=ImageDraw.Draw(sheet)
 for i,(asset,r) in enumerate(records.items()):
  im=Image.open(ASSETS/asset).convert('RGBA');im.thumbnail((64,42));bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);x=i%14*80;y=i//14*68;sheet.paste(bg.convert('RGB'),(x+5,y+18));draw.text((x+5,y+2),Path(asset).stem,fill='black')
 sheet.save(AUDIT/'REVISION_2019_BANDERAS.png')

def card(size,label):
 im=Image.new('RGB',size,'#E7E8DF');dr=ImageDraw.Draw(im);w,h=size;dr.rectangle((w*.06,h*.06,w*.94,h*.94),outline='#879C9C',width=max(1,w//180));f=fitted(label,w*.8,min(w*.08,h*.085));dr.multiline_text((w/2,h/2),label,font=f,fill='#263B46',anchor='mm',align='center',spacing=max(5,int(h*.02)));return im

def math_image(formula,width):
 from matplotlib import rc_context
 from matplotlib.mathtext import math_to_image
 from matplotlib.font_manager import FontProperties
 pattern=lambda name:FontProperties(fname=str(FONTS/name)).get_fontconfig_pattern()
 settings={'mathtext.fontset':'custom','mathtext.rm':pattern('JetBrainsMono-Regular.ttf'),'mathtext.it':pattern('CMUSerif-Italic.ttf'),'mathtext.bf':pattern('CMUSerif-Bold.ttf'),'mathtext.sf':pattern('JetBrainsMono-Regular.ttf'),'mathtext.tt':pattern('JetBrainsMono-Regular.ttf'),'mathtext.cal':pattern('CMUSerif-Italic.ttf'),'mathtext.fallback':None}
 stream=io.BytesIO()
 with rc_context(settings):math_to_image('$'+formula+'$',stream,prop=FontProperties(fname=str(FONTS/'CMUSerif-Roman.ttf'),size=30),dpi=150,format='png',color='#25353B')
 stream.seek(0);im=Image.open(stream).convert('RGBA');return ImageOps.contain(im,(width,120))

# Independently phrased statements; mathematical facts checked against the official paper.
PROBLEMS=[
 ('Four integers',['Choose four different positive integers a1, a2, a3, a4.','Count pairs whose sum divides the total of all four.','Determine every set attaining the maximum pair count.'],r's_A=a_1+a_2+a_3+a_4,\quad a_i+a_j\mid s_A\quad(i<j)'),
 ('Windmill',['A finite planar set S has at least two points; no three are collinear.','A line starts through P in S and turns clockwise about P.','When it first meets another point Q, Q becomes the pivot.','Repeat forever. Find a starting point and line so that','every point becomes the pivot infinitely often.'],None),
 ('Functional inequality',['For real-valued f on R and every real x,y, assume','the inequality below. Prove f(x)=0 whenever x is nonpositive.'],r'f(x+y)\leq y f(x)+f(f(x))'),
 ('Balance',['For positive integer n, take weights 1,2,...,2^(n-1).','Place them one at a time on either pan of a balance.','The right pan must never outweigh the left.','Count all orders and choices of pans.'],r'1,\ 2,\ 2^2,\ \ldots,\ 2^{n-1}'),
 ('Integer-valued function',['For f: Z -> positive integers, assume the divisibility below.','Prove that f(m)<=f(n) always implies f(m) divides f(n).'],r'f(m-n)\mid f(m)-f(n)'),
 ('Reflected tangents',['Reflect a tangent of the circumcircle of an acute triangle','in its three side-lines. Prove that the circle through the','three intersections of the reflected lines touches the','original circumcircle.'],None)]

def problem_page(size,day):
 im=Image.new('RGBA',size,'#F5F3EC');dr=ImageDraw.Draw(im);w,h=size
 dr.text((w*.09,h*.10),'Mathematics · 2011',font=font(w*.043,True),fill='#283C46');dr.text((w*.09,h*.18),'Day '+str(day)+' / problems '+('1–3' if day==1 else '4–6'),font=font(w*.026),fill='#4B6066')
 for i in range(3):
  k=(day-1)*3+i;title,lines,formula=PROBLEMS[k];y=[h/2+w*.09-(w*(.095+.16+.1)+w*.0254*2)/2, h/2+w*.09-(w*(.095+.16+.1)+w*.0254*2)/2+w*.1204, h/2+w*.09-(w*(.095+.16+.1)+w*.0254*2)/2+w*.3058][i];dr.text((w*.09,y),f'{k+1}. '+title,font=font(w*.018,True),fill='#25353B');f=fitted('\n'.join(lines),w*.82,w*.015)
  for j,l in enumerate(lines):dr.text((w*.09,y+w*.020+j*w*.014),l,font=f,fill='#25353B')
  if formula:
   m=ImageOps.contain(math_image(formula,int(w*.78)),(int(w*.78),int(w*.025)));im.alpha_composite(m,(int(w*.11),int(y+w*.020+len(lines)*w*.014+w*.002)))
 dr.text((w*.09,h*.94),'4 h 30 min · 7 points per problem',font=font(w*.021),fill='#4B6066');return im

WIND_LINES=[
 'A finite set S in the plane has at least two points; no three are collinear.',
 'A line passes through a selected point P in S.',
 'Rotate that line clockwise, keeping P fixed.',
 'Stop at its first meeting with another point Q in S.',
 'Use Q as the new pivot, and keep turning clockwise.',
 'At the next encounter, switch to that point as pivot.',
 'Continue this process without an end.',
 'Find a suitable initial point P and initial line',
 'for which the resulting windmill process',
 'visits every point of the finite set S as a pivot',
 'infinitely many times.'
]
def windmill_background(size):
 im=Image.new('RGBA',size,'#E6E8E2');dr=ImageDraw.Draw(im);w,h=size;sx=w/2560;sy=h/1440
 dr.text((90*sx,65*sy),'2011 · Mathematical problems',font=font(56*sx,True),fill='#263B46')
 dr.text((90*sx,190*sy),'1. Four distinct positive integers: maximize the number',font=font(34*sx),fill='#78837D')
 dr.text((90*sx,238*sy),'of pair sums dividing their total; determine all maximizers.',font=font(34*sx),fill='#78837D')
 dr.text((90*sx,353*sy),'2. Windmill',font=font(43*sx,True),fill='#263B46')
 # First text/underline spans 2380px. All other widths use identical character ratios.
 f=font(49*sx);base_width=f.getlength(WIND_LINES[0])
 for i,text in enumerate(WIND_LINES):
  raw_width=math.ceil(f.getlength(text))+2;strip=Image.new('RGBA',(raw_width,int(100*sy)));dd=ImageDraw.Draw(strip);dd.text((0,70*sy),text,font=f,fill='#25353B',anchor='ls')
  strip=strip.resize((round(2380*sx*len(text)/len(WIND_LINES[0])),int(100*sy)),Image.Resampling.LANCZOS)
  im.alpha_composite(strip,(round(90*sx),round((446+56*i-70)*sy)))
 dr=ImageDraw.Draw(im);dr.text((90*sx,1125*sy),'3. Functional inequality',font=font(38*sx,True),fill='#78837D')
 dr.text((90*sx,1180*sy),'For real-valued f on R satisfying the inequality for all x,y,',font=font(31*sx),fill='#78837D')
 dr.text((90*sx,1230*sy),'prove that f(x)=0 for all nonpositive x.',font=font(31*sx),fill='#78837D')
 m=ImageOps.contain(math_image(r'f(x+y)\leq y f(x)+f(f(x))',int(1300*sx)),(int(1300*sx),int(80*sy)));im.alpha_composite(m,(round(90*sx),round(1290*sy)))
 return im

def britain_from_data(row,rec):
 terms_url='https://www.naturalearthdata.com/about/terms-of-use/'
 terms=d.http(terms_url).decode('utf-8','replace');assert 'public domain' in terms.lower()
 url='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_110m_admin_0_countries.geojson'
 raw=d.cached(url,'.geojson');features=json.loads(raw.read_text())['features'];feature=next(f for f in features if f['properties'].get('ADM0_A3')=='GBR')
 geom=feature['geometry'];rings=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']];g=max((Polygon(p[0]) for p in rings),key=lambda p:p.area)
 points=np.array(g.exterior.coords);points[:,0]*=math.cos(math.radians(55));lo=points.min(axis=0);hi=points.max(axis=0);w,h=map(float,row['alto'].split()[2:]);factor=min(w*.9/(hi[0]-lo[0]),h*.9/(hi[1]-lo[1]));out=[]
 for x,y in points:out.append(((w-(hi[0]-lo[0])*factor)/2+(x-lo[0])*factor,(h-(hi[1]-lo[1])*factor)/2+(hi[1]-y)*factor))
 out=[(x/w*100,y/h*100) for x,y in out];body=solid(Polygon(out));rec.update(page_url=terms_url,source_url=url,source_sha256=sha(raw),source_authors='Natural Earth (cartografía de dominio público)',source_license='Public domain',source_license_url=terms_url,license_evidence='Condiciones de Natural Earth consultadas en esta ejecución.',via='código con datos libres',changes='SVG propio calculado desde cartografía Natural Earth 1:110m de dominio público, versión fijada por commit; solo la isla principal, sin Irlanda ni islas desconectadas.',note='Contorno geográfico simplificado real, un único path cerrado; no se deriva del SVG de Grant.')
 return body


GEN_BASE=generate
def generate(row,spec,dest,rec):
 if row['n']=='9':flags(rec);return
 if row['n']=='12':
  data=fourier_portrait(row,rec)
  if not (dest.exists() and rec.get('old_sha256')==sha(dest)):atomic(dest,data)
  rec['svg_paths']=1;return
 if row['n']=='29':
  body=britain_from_data(row,rec)
  if not (dest.exists() and rec.get('old_sha256')==sha(dest)):atomic(dest,svg(row,body).encode())
  rec['svg_paths']=1;return
 if row['modo']=='SVG':
  if dest.stem=='google_logo':rec['note']='Seis piezas del mismo gris azulado; índice 5 = G propia con remate y espolón, cinco puntos minúsculos auxiliares, sin paleta de marca.'
  GEN_BASE(row,spec,dest,rec);return
 if row['modo']=='WAV':GEN_BASE(row,spec,dest,rec);return
 size=(int(row['ancho']),int(row['alto']));mode=row['modo']
 if spec.get('title'):
  info=COMMONS.get(spec['title'])
  if not info:raise ValueError('No se verificó una licencia libre para '+spec['title'])
  if row['n'] in ['10','33','38']:
   raw_verified=d.cached(info['file_url']);info.update(source_sha256=sha(raw_verified),download_size_bytes=raw_verified.stat().st_size)
  opts={'title':spec['title'],'process':'cover','centering':[.5,.4]}
  if spec.get('pdf_page'):opts['pdf_page']=spec['pdf_page']
  if spec.get('disc'):opts['process']='disc'
  if spec.get('extend'):opts['process']='extend'
  if spec.get('crop'):opts['crop']=spec['crop']
  if row['n'] in ['10','33']:
   sw,sh=info['source_width'],info['source_height'];c=spec.get('crop',[0,0,1,1]);box_=[round(v*(sw if i%2==0 else sh)) for i,v in enumerate(c)];cw,ch=box_[2]-box_[0],box_[3]-box_[1];scale=max(size[0]/cw,size[1]/ch)
   assert scale<=1.5, f'Recorte insuficiente: ampliación {scale:.3f}x'
   rec.update(crop_source_box=box_,source_crop_size=[cw,ch],upscale_factor=scale)
  # Seed originals from earlier verified caches if exactly the same download URL is known.
  url=info['file_url'];ext=Path(__import__('urllib').parse.unquote(__import__('urllib').parse.urlparse(url).path)).suffix or '.bin';cache_name=hashlib.sha256(url.encode()).hexdigest()[:24]+ext
  for folder in ['downloads','assets2020']:
   old=ROOT/'_tools/.cache'/folder/'originales'/cache_name
   new=CACHE/'originales'/cache_name
   if old.is_file() and not new.exists():new.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,new)
  intact=dest.exists() and rec.get('old_sha256')==sha(dest)
  if not intact:
   im=d.process(opts,info,row)
   if mode=='P':
    # Palette with a transparent exterior reserved as index 255 for the Moon.
    rgba=im.convert('RGBA');p=rgba.convert('RGB').quantize(colors=255);arr=np.array(p);arr[np.array(rgba.getchannel('A'))<128]=255;p=Image.fromarray(arr,'P');pal=im.convert('RGB').quantize(colors=255).getpalette();p.putpalette((pal+[0]*768)[:768]);p.info['transparency']=255;im=p
   d.save(im,dest,mode)
  rec.update(info);rec.update(status='kept' if intact else 'replaced',via='descargar',changes='Fuente libre descargada independientemente; recorte/reescala al tamaño y modo exactos; sin IA.',note='Licencia consultada en esta ejecución. No se usa el original de Grant.'+(' Facsímil, página '+str(spec['pdf_page'])+'.' if spec.get('pdf_page') else '')+(' Se conserva el encuadre completo y se extiende el fondo de la propia fuente.' if spec.get('extend') else '')+(' '+spec['refine_note'] if spec.get('refine_note') else ''));return
 if spec.get('card'):
  im=card(size,spec['card']);rec['note']=spec.get('reason','Tarjeta propia tipográfica con título y autor/canal; sin portada, logotipo ni fotograma ajeno.')
 elif row['n'] in ['13','14']:im=problem_page(size,1 if row['n']=='13' else 2);rec.update(page_url='https://www.imo-official.org/assets/documents/problems/2011/2011_eng.pdf',note='Enunciados reformulados independientemente, mismas condiciones matemáticas; fórmulas LaTeX renderizadas por mathtext. Diseño propio sin emblema de la IMO.')
 elif row['n']=='34':im=windmill_background(size);rec['note']='Hoja propia del problema del molino. Once líneas coordinadas con los once subrayados de la escena y sus seis grupos.'
 elif row['n']=='42':
  # Generic video player: no hexagon, green, person or lettering.
  k=4;im=Image.new('RGBA',(size[0]*k,size[1]*k));dr=ImageDraw.Draw(im)
  dr.rounded_rectangle((20*k,45*k,180*k,155*k),radius=13*k,fill='#364D61',outline='#90A4B4',width=4*k)
  dr.polygon([(83*k,73*k),(83*k,127*k),(130*k,100*k)],fill='#EDF2F5')
  im=im.resize(size,Image.Resampling.LANCZOS);rec['note']='Icono propio de miniatura de video con play, paleta gris azulada y transparencia; sin hexágono, verde, figura humana ni texto.'
 elif row['n']=='47':
  im=Image.new('RGBA',size);dr=ImageDraw.Draw(im);w,h=size
  for r,color in [(.46,'#8B6129'),(.44,'#DAB663'),(.40,'#AE813C'),(.38,'#E1C77A')]:dr.ellipse((w*(.5-r),h*(.5-r),w*(.5+r),h*(.5+r)),fill=color)
  for a in np.arange(32)*math.pi/16:
   x=w*(.5+.42*math.cos(a));y=h*(.5+.42*math.sin(a));rr=w*.006;dr.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#F3D88B')
 else:raise KeyError('No implementation for '+row['asset'])
 assert im.size==size;d.save(im,dest,mode)


def validate_asset(row,dest):
 if '*' in row['asset']:return
 if row['modo']=='SVG':
  root=ET.parse(dest).getroot();assert root.get('viewBox')==row['alto']
  paths=root.findall('.//{http://www.w3.org/2000/svg}path');name=dest.stem
  if name in ['TrebleClef','EighthNote','Nail_And_Gear','FourierOneLine','Britain','SeattleSkyline','IP_logo2']:
   assert len(paths)==1 and len(re.findall('[Mm]',paths[0].get('d')))==1 and len(re.findall('[Zz]',paths[0].get('d')))==1
  for n,c in [('Mammoth',5),('google_logo',6),('windmill_fairytale',3),('imo_2011_2_underline-01',11)]:
   if name==n:assert len(paths)==c
 elif row['modo']=='WAV':
  with wave.open(str(dest)) as a,wave.open(str(CACHE/'originales'/row['asset'])) as b:assert a.getparams()==b.getparams()
 else:
  with Image.open(dest) as im:assert im.size==(int(row['ancho']),int(row['alto'])) and im.mode==row['modo']


REFINE_ORDER=['12','38','42','56','10','33']
SPECS['12']={'title':'File:Fourier2 - restoration1.jpg'}

def fourier_portrait(row,rec):
 import cv2
 from scipy.spatial import cKDTree
 info=COMMONS.get(SPECS['12']['title'])
 if not info:raise ValueError('No se verificó el retrato libre de Fourier')
 url=info['file_url'];ext='.jpg';key=hashlib.sha256(url.encode()).hexdigest()[:24]+ext
 raw=CACHE/'originales'/key
 for folder in ['downloads','assets2020']:
  old=ROOT/'_tools/.cache'/folder/'originales'/key
  if old.exists() and not raw.exists():raw.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,raw)
 raw=d.cached(url);gray=ImageOps.grayscale(Image.open(raw));gray=gray.resize((340,430),Image.Resampling.LANCZOS)
 edges=cv2.Canny(cv2.GaussianBlur(np.array(gray),(3,3),.75),55,125)
 edges[:8]=0;edges[-35:]=0;edges[:,:8]=0;edges[:,-8:]=0
 contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 contours=sorted((c for c in contours if cv2.arcLength(c,True)>16),key=lambda c:cv2.arcLength(c,True),reverse=True)[:230]
 curves=[]
 for c in contours:
  q=cv2.approxPolyDP(c,.65,True)[:,0,:].astype(float)
  if len(q)>=3:curves.append(q)
 n=len(curves);assert n>30;trees=[cKDTree(q) for q in curves];best=np.full(n,np.inf);parents=[None]*n;visited={0};children=[{} for _ in curves];longest=0
 # Prim tree over contour-to-contour nearest pairs; each link is traversed out and back.
 current=0
 for step in range(n-1):
  for j in range(n):
   if j in visited:continue
   distance,index=trees[current].query(curves[j]);b=int(np.argmin(distance));dist=float(distance[b])
   if dist<best[j]:best[j]=dist;parents[j]=(current,int(index[b]),b)
  j=min((k for k in range(n) if k not in visited),key=lambda k:best[k]);parent,a,b=parents[j];children[parent].setdefault(a,[]).append((j,b));longest=max(longest,float(best[j]));visited.add(j);current=j
 route=[]
 def walk(i,start):
  points=curves[i]
  for k in range(len(points)):
   idx=(start+k)%len(points);route.append(points[idx])
   for child,anchor in children[i].get(idx,[]):walk(child,anchor);route.append(points[idx])
  route.append(points[start])
 walk(0,0);arr=np.array(route);lo=arr.min(axis=0);hi=arr.max(axis=0);factor=810/(hi[1]-lo[1]);arr=(arr-lo)*factor;arr[:,0]+=(1920-(hi[0]-lo[0])*factor)/2;arr[:,1]+=135
 ds='M '+' L '.join(f'{x:.2f} {y:.2f}' for x,y in arr)+' Z'
 body=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{row["alto"]}"><!-- Traced from verified public-domain Boilly portrait, not Grant SVG. -->'+path(ds,'none','#26333E',1.3)+'</svg>'
 assert len(body.encode())<300000
 rec.update(info);rec.update(status='generated',author=info['author'],via='trazado de dominio público',source_sha256=sha(raw),source_contours=n,trace_points=len(arr),max_connector_source_pixels=longest,changes='Bordes Canny del retrato histórico libre, simplificación de contornos y unión mediante árbol de vecinos más próximos; recorrido cerrado continuo con enlaces de ida/vuelta, sin SVG de Grant.',note='Retrato reconocible de Fourier: un path, un M, cierre Z, sin relleno; 75% del alto del viewBox. '+str(len(body.encode()))+' bytes.')
 return body.encode()

def normalize_authors(records):
 for r in records.values():
  if r.get('author')=='Unknown authorUnknown author':r['author']='Autor desconocido (Commons)'

progress_base=progress
def progress(records):
 progress_base(records);file=AUDIT/'PROGRESO_2019.md';text=file.read_text();rows=[next(r for r in ROWS if r['n']==n) for n in REFINE_ORDER];done=[(r,records.get(r['asset'],{})) for r in rows if records.get(r['asset'],{}).get('refinement_state')];pending=[r for r in rows if not records.get(r['asset'],{}).get('refinement_state')];next_=pending[0] if pending else None
 ah=['## AHORA',f'Refinado: {len(done)}/6 revisados; {len(pending)} pendientes.',f"Último: {max(done,key=lambda pair:pair[1].get('refined_at',''))[0]['asset'] if done else 'preparación de la segunda pasada'}.",f"Sigue: {next_['asset'] if next_ else 'refinado terminado; revisar hoja antes/después'}.",f"Comando: `python _lib/assets/generated/replacements/assets2019/make_assets_2019.py --only {next_['asset'] if next_ else 'FourierOneLine.svg'}`."]
 text=re.sub(r'## AHORA\n.*?(?=\n\| #)', '\n'.join(ah)+'\n',text,flags=re.S)
 text+='\n## Refinado\n\n| Archivo | Estado | Fuente | Licencia | Nota |\n|---|---|---|---|---|\n'
 for row in rows:
  r=records.get(row['asset'],{});text+='| '+' | '.join(str(v).replace('|','/') for v in [row['asset'],r.get('refinement_state','pendiente'),r.get('page_url',''),r.get('license',''),r.get('refinement_note','')])+' |\n'
 text+='\nLimpieza: el autor duplicado «Unknown authorUnknown author» se normaliza como «Autor desconocido (Commons)», sin alterar los demás campos de las entradas ajenas al refinado. No se modifican otros assets ni escenas.\n';file.write_text(text)

def refinement_review(records):
 rows=[next(r for r in ROWS if r['n']==n) for n in REFINE_ORDER];sheet=Image.new('RGB',(1200,6*330),'#E3E7E4');draw=ImageDraw.Draw(sheet)
 def image_(p):
  if p.suffix=='.svg':return Image.open(io.BytesIO(subprocess.check_output(['rsvg-convert','-w','540','-h','270',str(p)],stderr=subprocess.DEVNULL))).convert('RGBA')
  im=Image.open(p).convert('RGBA');return ImageOps.contain(im,(540,270))
 for i,row in enumerate(rows):
  y=i*330;draw.text((15,y+5),row['asset'],font=font(17),fill='#243B48');draw.text((30,y+30),'ANTES',font=font(15),fill='#53646C');draw.text((630,y+30),'DESPUÉS',font=font(15),fill='#53646C')
  for col,p in enumerate([CACHE/'previos'/row['asset'],ASSETS/row['asset']]):
   if not p.exists():continue
   im=image_(p);bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);xx=col*600+(600-im.width)//2;yy=y+55+(270-im.height)//2;sheet.paste(bg.convert('RGB'),(xx,yy))
   if row['n']=='56':
    draw.rectangle((xx+im.width*.32,yy+im.height*.03,xx+im.width*.81,yy+im.height*.93),outline='#29748B',width=2);draw.text((xx+im.width*.81,yy+im.height*.7),'[5] G',font=font(14),fill='#235468')
 sheet.save(AUDIT/'REVISION_2019_REFINADO.png')

def run(args):
 CACHE.mkdir(parents=True,exist_ok=True);(CACHE/'.gitignore').write_text('*\n!.gitignore\n');records=json.loads(SOURCE.read_text()) if SOURCE.exists() else {};normalize_authors(records);d.atomic_json(SOURCE,records);progress(records)
 selected=[r for r in ROWS if (not args.only or any(v in (r['n'],r['asset'],Path(r['asset']).name) for v in args.only)) and (not args.priority or r['prioridad']==args.priority)]
 global COMMONS
 titles={SPECS[r['n']]['title'] for r in selected if SPECS.get(r['n'],{}).get('title')}
 try:COMMONS=d.verify_commons(titles)
 except Exception as e:print('Commons verification failed:',e,flush=True);COMMONS={}
 for row in selected:
  asset=row['asset'];dest=ASSETS/asset;old=records.get(asset);print(f"[{row['n']}/67] {asset}",flush=True)
  if old and not args.force and old.get('delivery_state')=='ya_existe' and dest.is_file() and sha(dest)==old.get('sha256'):continue
  spec=SPECS.get(row['n'],{});rec={'asset':asset,'name':dest.name,'subject':row['que_crear'] or row['nota'],'author':'propio (código)','license':'CC0','license_url':CC0,'page_url':'','changes':'Recreación independiente desde cero, no deriva del original.','status':'skipped','via':'código','recipe_version':VERSION,'verified_at':datetime.now(timezone.utc).isoformat(),'scene_review':scene_audit(row),'note':'','old_sha256':None if args.force else (old or {}).get('sha256')}
  if row['n'] in REFINE_ORDER:rec['subject']={'12':'Retrato histórico de Joseph Fourier trazado en una única línea continua','38':'Fotografía distinta de Richard Feynman junto a una pizarra','42':'Miniatura genérica de video con play, sin marca ni figura humana','56':'G propia monocroma, pieza de índice 5','10':'Retrato de Daniel Kahneman, sin texto ni terceros','33':'Retrato de Alan Kay, sin texto ni terceros'}[row['n']]
  if spec.get('title') or row['n']=='9':rec.update(author='',license='',license_url='',via='descargar')
  try:
   prev=existing(row) if not old else None
   if prev:rec.update(prev);rec.update(delivery_state='ya_existe',note='Reemplazo existente con hash coincidente; no se modifica.');records[asset]=rec;d.atomic_json(SOURCE,records);progress(records);continue
   if old and old.get('sha256') and dest.is_file() and sha(dest)==old['sha256'] and not args.force and old.get('via')=='código':
    if row['n'] in REFINE_ORDER:
     old['subject']=rec['subject'];records[asset]=old;normalize_authors(records);d.atomic_json(SOURCE,records);progress(records)
    continue
   backup=CACHE/'originales'/asset
   if dest.is_file() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
   if row['n'] in REFINE_ORDER:
    previous=CACHE/'previos'/asset
    if not previous.exists():previous.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,previous)
   generate(row,spec,dest,rec)
   validate_asset(row,dest)
   rec.update(status=rec.get('status') if rec.get('status') in ('replaced','kept') else 'generated',delivery_state='hecha',sha256=sha(dest) if dest.is_file() else rec.get('sha256'),final_size_bytes=dest.stat().st_size if dest.is_file() else 0,note=rec.get('note') or 'Código propio; tamaño/modo o viewBox conservados. Uso de escena revisado.')
  except Exception as e:
   rec.update(status='skipped',delivery_state='saltada',note=str(e));print('  SKIPPED',e,flush=True)
   if old and dest.is_file() and old.get('sha256')==sha(dest):rec['retained_provenance']=old
  if row['n'] in REFINE_ORDER:
   rec.update(refinement_state='mejorada' if rec.get('delivery_state')=='hecha' else 'saltada',refinement_note=rec.get('note',''),refined_at=datetime.now(timezone.utc).isoformat())
  records[asset]=rec;normalize_authors(records);d.atomic_json(SOURCE,records);progress(records)
 refinement_review(records)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',nargs='+');ap.add_argument('--priority',choices=['P1','P2','P3']);ap.add_argument('--force',action='store_true');run(ap.parse_args())
