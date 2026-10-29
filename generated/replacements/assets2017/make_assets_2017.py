"""Independent replacements for the 2017 asset list; never reads original artwork as input.

Use --round 1/2/3, --only GLOBAL_NUMBER/asset ... or --priority P2/P3, optionally --force.
Needs Pillow, numpy, shapely, beautifulsoup4, rsvg-convert and the project's existing helper modules.
No scene rendering, setup, git or publishing commands are executed.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,importlib.util,io,json,math,re,shutil,subprocess,sys,textwrap
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from shapely.geometry import Point,Polygon,LineString,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parent;ASSETS=HERE.parents[2];ROOT=ASSETS.parents[1];AUDIT=ROOT/'_tools/assets_licencias/codex';CACHE=ROOT/'_tools/.cache/assets2017';SOURCE=HERE/'assets2017_sources.json';FONTS=ASSETS/'fonts'
sp=importlib.util.spec_from_file_location('helpers2019',HERE.parent/'assets2019/make_assets_2019.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);d=h.d;d.CACHE=CACHE;d.UA={'User-Agent':'ManimLearningAssets2017/1.0 (educational independent asset audit)'}
CC0='https://creativecommons.org/publicdomain/zero/1.0/';VERSION='2017-independent-v1'
ROWS=[{'n': '1', 'prioridad': 'P2', 'asset': 'svg_images/electricity.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/mug/AboutToyPuzzles', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Lightning bolt icon (one polygon)', 'nota': 'Utility icon of the three-utilities puzzle (mug); icon of unknown origin', 'svg_schema': {'viewBox': '0 0 100 100'}}, {'n': '2', 'prioridad': 'P2', 'asset': 'svg_images/ethereum_logo.svg', 'ancho': 'svg', 'alto': '0 0 256 417', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/crypto/BigDifferenceBetweenLDAndCryptocurrencies', 'via': 'código', 'tipo': 'svg_logo', 'derechos': 'logo_marca', 'que_crear': 'Own generic gem: a diamond made of 4 coloured facets (grey shades) without the Ethereum proportions, 4 sub-shapes (EthereumLogo recolors its parts)', 'nota': 'Ethereum logo, used by the EthereumLogo class of crypto/256 (colors parts with color_chars)', 'svg_schema': {'viewBox': '0 0 256 417'}}, {'n': '3', 'prioridad': 'P2', 'asset': 'svg_images/fire.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/mug/AboutToyPuzzles', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Flame icon: one teardrop silhouette with a notch', 'nota': 'Utility icon of the three-utilities puzzle (mug); icon of unknown origin', 'svg_schema': {'viewBox': '0 0 100 100'}}, {'n': '4', 'prioridad': 'P2', 'asset': 'svg_images/house.svg', 'ancho': 'svg', 'alto': '0 0 62.6 59.6', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/mug/AboutToyPuzzles', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'House icon: a pentagon-shaped silhouette with a door cut-out (valid closed paths only: the current file ends with a degenerate `M x,y` path that GL cannot parse; CL17-D shims it)', 'nota': 'House icon of the utilities puzzle (mug, 31 uses); icon of unknown origin; the original SVG has a stray one-point path', 'svg_schema': {'viewBox': '0 0 62.6 59.6'}}, {'n': '5', 'prioridad': 'P2', 'asset': 'svg_images/litecoin_logo.svg', 'ancho': 'svg', 'alto': '0.847 0.876 329.254 329.256', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/crypto/BigDifferenceBetweenLDAndCryptocurrencies', 'via': 'código', 'tipo': 'svg_logo', 'derechos': 'logo_marca', 'que_crear': "Own coin icon: silver disc with a bold 'L' with a diagonal bar; not the Litecoin logo", 'nota': 'Litecoin logo, used by the LitecoinLogo class', 'svg_schema': {'width': '329.254px', 'height': '329.256px', 'viewBox': '0.847 0.876 329.254 329.256'}}, {'n': '6', 'prioridad': 'P2', 'asset': 'svg_images/paint_bucket.svg', 'ancho': 'svg', 'alto': '0 0 50 50', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/mug/AskAboutRegions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Paint bucket icon: tilted bucket with handle and a drip', 'nota': 'Icon of unknown origin', 'svg_schema': {'viewBox': '0 0 50 50'}}, {'n': '7', 'prioridad': 'P2', 'asset': 'svg_images/water.svg', 'ancho': 'svg', 'alto': '0 0 60.633 100', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2017/mug/AboutToyPuzzles', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Water drop icon', 'nota': 'Utility icon of the three-utilities puzzle (mug); icon of unknown origin', 'svg_schema': {'viewBox': '0 0 60.633 100'}}, {'n': '8', 'prioridad': 'P2', 'asset': 'raster_images/Astrolabe.jpg', 'ancho': '375', 'alto': '500', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2017/nn/part2/RandomlyLabeledImageData', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Free-licence image of the subject (Astrolabe) from Wikimedia Commons, only used as a small training-example picture', 'nota': 'CODEX: photo (third-party); find a free-licence photo or draw a simple illustration'}, {'n': '9', 'prioridad': 'P2', 'asset': 'raster_images/Pierre_de_Fermat.png', 'ancho': '1172', 'alto': '1500', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2017/nn/part2/RandomlyLabeledImageData', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Use raster_images/Fermat.jpg (already replaced by Codex in 2019, public-domain portrait) under this name, or the same Commons portrait', 'nota': 'CODEX: copy/alias the already replaced public-domain Fermat portrait (raster_images/Fermat.jpg) as Pierre_de_Fermat.png'}, {'n': '10', 'prioridad': 'P2', 'asset': 'raster_images/Sculling.jpg', 'ancho': '500', 'alto': '333', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2017/nn/part2/RandomlyLabeledImageData', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Free-licence image of the subject (Sculling) from Wikimedia Commons, only used as a small training-example picture', 'nota': 'CODEX: photo (third-party); find a free-licence photo or draw a simple illustration'}, {'n': '11', 'prioridad': 'P2', 'asset': 'raster_images/Trilobite.jpg', 'ancho': '500', 'alto': '333', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2017/nn/part2/RandomlyLabeledImageData', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Free-licence image of the subject (Trilobite) from Wikimedia Commons, only used as a small training-example picture', 'nota': 'CODEX: photo (third-party); find a free-licence photo or draw a simple illustration'}, {'n': '12', 'prioridad': 'P2', 'asset': 'raster_images/ripple_logo.png', 'ancho': '500', 'alto': '500', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2017/crypto/CompareBlockTimes', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Own generic mark (three small dots joined by arcs in a circle) in the same size; not the Ripple logo', 'nota': 'Brand logo (Ripple, XRP); simple enough to draw by code'}, {'n': '13', 'prioridad': 'P2', 'asset': 'svg_images/Norway.svg', 'ancho': 'svg', 'alto': '0 0 899.8 1080', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/fractal_dimension/CompareBritainAndNorway', 'via': 'código', 'tipo': '', 'derechos': 'desconocido', 'que_crear': '', 'nota': 'SIN FILA en los CSV de los agentes (lo detectó el chequeo estático); decide tú el tipo y los derechos.', 'svg_schema': {'viewBox': '0 0 899.8 1080'}}, {'n': '14', 'prioridad': 'P2', 'asset': 'svg_images/bank_building.svg', 'ancho': 'svg', 'alto': '0 0 100 125', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/crypto/FromBankToDecentralizedSystem', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Simple classical building icon: triangular pediment, four columns and a base, one connected silhouette, 1 colour', 'nota': "Icon of unknown origin (ListOfAttributes uses SVGMobject('%s_building'%word) with bank/government/...)", 'svg_schema': {'viewBox': '0 0 100 125'}}, {'n': '15', 'prioridad': 'P2', 'asset': 'svg_images/euro_symbol.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/crypto/ShowLDAndOtherCurrencyExchanges', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'dominio_publico', 'que_crear': "Euro sign drawn by code (a 'C'-shaped arc with two horizontal bars)", 'nota': 'Currency symbol (generic glyph); level 3 only because it comes from videos/assets/', 'svg_schema': {'width': '430', 'height': '432'}}, {'n': '16', 'prioridad': 'P2', 'asset': 'svg_images/gpu.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/256/MainBreakdown', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Graphics card icon: rectangle with two fans (circles with blades) and a row of connector pins', 'nota': 'Icon of unknown origin', 'svg_schema': {'viewBox': '0 0 100 100'}}, {'n': '17', 'prioridad': 'P2', 'asset': 'svg_images/yen_symbol.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/crypto/ShowLDAndOtherCurrencyExchanges', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'dominio_publico', 'que_crear': "Yen sign drawn by code (a 'Y' with two horizontal bars)", 'nota': 'Currency symbol (generic glyph); level 3 only because it comes from videos/assets/', 'svg_schema': {}}, {'n': '18', 'prioridad': 'P3', 'asset': 'raster_images/Barrow.jpg', 'ancho': '529', 'alto': '631', 'modo': 'L', 'escenas': '1', 'ejemplo': '_2017/eoc/chapter2/FathersOfCalculus', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Retrato de Isaac Barrow (pintura), dominio publico"}, {'n': '19', 'prioridad': 'P3', 'asset': 'raster_images/Mandelbrot.jpg', 'ancho': '792', 'alto': '985', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2017/fractal_dimension/WhatAreFractals', 'via': 'código', 'tipo': '', 'derechos': 'desconocido', 'que_crear': '', 'nota': 'SIN FILA en los CSV de los agentes (lo detectó el chequeo estático); decide tú el tipo y los derechos.'}, {'n': '20', 'prioridad': 'P3', 'asset': 'raster_images/Weierstrass.jpg', 'ancho': '640', 'alto': '939', 'modo': 'L', 'escenas': '1', 'ejemplo': '_2017/eoc/chapter2/FathersOfCalculus', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Retrato de Weierstrass (foto del siglo XIX), dominio publico"}, {'n': '21', 'prioridad': 'P3', 'asset': 'raster_images/bitcoin_mining_graphic.png', 'ancho': '1088', 'alto': '830', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/crypto/NoCommentOnSpeculation', 'via': 'código', 'tipo': 'imagen', 'derechos': 'desconocido', 'que_crear': 'CODEX: illustration of a crypto-mining rig: a rack/shelf of GPU cards with fans and cables, flat vector style, transparent background, about 1200x800', 'nota': 'CODEX: complex illustration of unknown origin (a mining-rig picture); cannot be drawn well by code'}, {'n': '22', 'prioridad': 'P3', 'asset': 'raster_images/eater.jpg', 'ancho': '288', 'alto': '288', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2017/qa_round_two/Thumbnail', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Silueta de perfil neutra (sin rasgos de persona real) sobre fondo de montaña difuminado, 288x288', 'nota': 'CODEX: foto de una persona real (perfil, sudadera, montañas); qa_round_two::Thumbnail. No generar caras de personas reales.'}, {'n': '23', 'prioridad': 'P3', 'asset': 'raster_images/milky_way.jpg', 'ancho': '1024', 'alto': '1024', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2017/256/MainBreakdown', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Own Milky Way look-alike generated by code: dark blue gradient with a bright diagonal band and random star dots, 1920x1080', 'nota': 'Astronomy photo of unknown origin; a procedural star field is enough for the decorative use'}, {'n': '24', 'prioridad': 'P3', 'asset': 'svg_images/circuit.svg', 'ancho': 'svg', 'alto': '0 0 5 5', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/256/StateOfBitcoin', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Simple circuit-board icon: a few right-angle traces ending in circles', 'nota': 'Icon of unknown origin', 'svg_schema': {'viewBox': '0 0 5 5'}}, {'n': '25', 'prioridad': 'P3', 'asset': 'svg_images/credit_card.svg', 'ancho': 'svg', 'alto': '0 0 100 64', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/crypto/UnderlyingSystemVsUserFacing', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Credit card icon: rounded rectangle with a stripe and a small chip', 'nota': 'Icon of unknown origin (not a brand card)', 'svg_schema': {'viewBox': '0 0 100 64'}}, {'n': '26', 'prioridad': 'P3', 'asset': 'svg_images/galaxy.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/256/MainBreakdown', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Spiral galaxy icon: logarithmic spiral with 2 arms made of dots/strokes', 'nota': 'Icon of unknown origin', 'svg_schema': {'viewBox': '0 0 100 100'}}, {'n': '27', 'prioridad': 'P3', 'asset': 'svg_images/government_building.svg', 'ancho': 'svg', 'alto': '0 0 100 125', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/crypto/ListOfAttributes', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Simple capitol-style icon: dome on a wide base with steps, one silhouette, 1 colour', 'nota': 'Icon of unknown origin (see bank_building)', 'svg_schema': {'viewBox': '0 0 100 125'}}, {'n': '28', 'prioridad': 'P3', 'asset': 'svg_images/phone.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/crypto/UnderlyingSystemVsUserFacing', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Smartphone icon: rounded rectangle with a screen and a home button', 'nota': 'Icon of unknown origin (not a brand phone)', 'svg_schema': {'viewBox': '0 0 100 100'}}, {'n': '29', 'prioridad': 'P3', 'asset': 'svg_images/shield_locked.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/256/Thumbnail', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'desconocido', 'que_crear': 'Shield icon with a padlock in the middle', 'nota': 'Icon of unknown origin', 'svg_schema': {'viewBox': '0 0 100 100'}}, {'n': '30', 'prioridad': 'P3', 'asset': 'svg_images/visa_logo.svg', 'ancho': 'svg', 'alto': '0 0 1000 323.7', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/crypto/ShowBitcoinBlockSize', 'via': 'código', 'tipo': 'svg_logo', 'derechos': 'logo_marca', 'que_crear': "Own generic card mark: a rounded blue card with the plain word 'CARD' (not the Visa logo)", 'nota': 'Brand logo (Visa)', 'svg_schema': {'viewBox': '0 0 1000 323.7'}}]
CSV_SHA='02bf9ac563159291b39f4505c8972cdc91824751c77118233394ea59f687c00c'
ROUND2_ROWS=[{'n': '31', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_eight.png', 'ancho': '28', 'alto': '28', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '1'}, {'n': '32', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_four.png', 'ancho': '28', 'alto': '28', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '2'}, {'n': '33', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_horizontal_line.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '3'}, {'n': '34', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_loop.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '4'}, {'n': '35', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_loop_edge1.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '5'}, {'n': '36', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_loop_edge2.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '6'}, {'n': '37', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_loop_edge3.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '7'}, {'n': '38', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_loop_edge4.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '8'}, {'n': '39', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_loop_edge5.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '9'}, {'n': '40', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_lower_loop.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '10'}, {'n': '41', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_nine.png', 'ancho': '28', 'alto': '28', 'modo': 'RGB', 'escenas': '3', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '11'}, {'n': '42', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_right_line.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '3', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '12'}, {'n': '43', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_right_line_edge1.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '13'}, {'n': '44', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_right_line_edge2.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '14'}, {'n': '45', 'prioridad': 'P3', 'asset': 'raster_images/handwritten_right_line_edge3.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2017/nn/part1/BreakUpMicroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '15'}, {'n': '46', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_upper_left_line.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '16'}, {'n': '47', 'prioridad': 'P2', 'asset': 'raster_images/handwritten_upper_loop.png', 'ancho': '28', 'alto': '28', 'modo': 'RGBA', 'escenas': '3', 'ejemplo': '_2017/nn/part1/BreakUpMacroPatterns', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '28x28 digit/stroke image (a handwritten-style MNIST sample or a crop of one); regenerate by code from the MNIST digits in nn/image_map (crop / mask the strokes) -- no illustration needed', 'nota': 'Trazo/dígito de 28x28 como los de MNIST (la escena los muestra ampliados y los pasa por la red). Dibuja el trazo descrito en el nombre (loop, right_line, upper_left_line, edge1..5 = bordes de ese trazo; eight/four/nine = el dígito) por código (Pillow/numpy), sin copiar el original. Mismo tamaño y modo; los RGBA llevan fondo transparente o negro como el original (compara con `.cache/assets2017/originales/` tras hacer la copia). 28x28 MNIST-style sample used by nn/part1 BreakUpMacroPatterns / BreakUpMicroPatterns (patterns that make up a digit). Not CODEX: reproducible by code.', 'ronda': '2', 'ronda_n': '17'}, {'n': '48', 'prioridad': 'P3', 'asset': 'raster_images/sci_youtubers_thumbnail.jpg', 'ancho': '1280', 'alto': '720', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2017/mug/NewMugThumbnail', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'CODEX: neutral thumbnail background (abstract science icons and plain silhouettes, NO real people, no logos) in the 16:9 frame of the original thumbnail', 'nota': 'Miniatura neutra 1280x720: fondo liso con íconos científicos abstractos (átomo, matraz, planeta) en siluetas planas; NINGUNA persona, cara, silueta humana ni logo. CODEX: collage thumbnail with faces/logos of real YouTubers (third-party screenshot); only used by NewMugThumbnail', 'ronda': '2', 'ronda_n': '18'}, {'n': '49', 'prioridad': 'P2', 'asset': 'svg_images/VennDiagram_in_A_in_B.svg', 'ancho': 'svg', 'alto': '0 0 884.3 737.7', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/bell/ReEmphasizeVennDiagram', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'obra_3b1b', 'que_crear': 'Venn diagram of three overlapping circles A, B, C with the labelled regions filled; regenerate with Circle/Intersection code in a make_*.py', 'nota': 'Diagrama de Venn de tres círculos A, B, C con la región indicada en el nombre resaltada (in_A_in_B = A y B; out_C = fuera de C...). SVG por código, mismo viewBox 0 0 884.3 737.7; mira cuántos subtrazos usa la escena (`bell/ReEmphasizeVennDiagram`). Sin texto de marca. Simple geometry (3 circles with a highlighted region): reproducible by code. Not CODEX.', 'ronda': '2', 'ronda_n': '19', 'svg_schema': {'viewBox': '0 0 884.3 737.7'}}, {'n': '50', 'prioridad': 'P2', 'asset': 'svg_images/VennDiagram_in_A_in_B_out_C.svg', 'ancho': 'svg', 'alto': '0 0 884.3 737.7', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/bell/ReEmphasizeVennDiagram', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'obra_3b1b', 'que_crear': 'Venn diagram of three overlapping circles A, B, C with the labelled regions filled; regenerate with Circle/Intersection code in a make_*.py', 'nota': 'Diagrama de Venn de tres círculos A, B, C con la región indicada en el nombre resaltada (in_A_in_B = A y B; out_C = fuera de C...). SVG por código, mismo viewBox 0 0 884.3 737.7; mira cuántos subtrazos usa la escena (`bell/ReEmphasizeVennDiagram`). Sin texto de marca. Simple geometry (3 circles with a highlighted region): reproducible by code. Not CODEX.', 'ronda': '2', 'ronda_n': '20', 'svg_schema': {'viewBox': '0 0 884.3 737.7'}}, {'n': '51', 'prioridad': 'P2', 'asset': 'svg_images/VennDiagram_in_A_out_B.svg', 'ancho': 'svg', 'alto': '0 0 884.3 737.7', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/bell/ReEmphasizeVennDiagram', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'obra_3b1b', 'que_crear': 'Venn diagram of three overlapping circles A, B, C with the labelled regions filled; regenerate with Circle/Intersection code in a make_*.py', 'nota': 'Diagrama de Venn de tres círculos A, B, C con la región indicada en el nombre resaltada (in_A_in_B = A y B; out_C = fuera de C...). SVG por código, mismo viewBox 0 0 884.3 737.7; mira cuántos subtrazos usa la escena (`bell/ReEmphasizeVennDiagram`). Sin texto de marca. Simple geometry (3 circles with a highlighted region): reproducible by code. Not CODEX.', 'ronda': '2', 'ronda_n': '21', 'svg_schema': {'viewBox': '0 0 884.3 737.7'}}, {'n': '52', 'prioridad': 'P2', 'asset': 'svg_images/VennDiagram_in_A_out_C.svg', 'ancho': 'svg', 'alto': '0 0 884.3 737.7', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2017/bell/ReEmphasizeVennDiagram', 'via': 'código', 'tipo': 'svg_ilustracion', 'derechos': 'obra_3b1b', 'que_crear': 'Venn diagram of three overlapping circles A, B, C with the labelled regions filled; regenerate with Circle/Intersection code in a make_*.py', 'nota': 'Diagrama de Venn de tres círculos A, B, C con la región indicada en el nombre resaltada (in_A_in_B = A y B; out_C = fuera de C...). SVG por código, mismo viewBox 0 0 884.3 737.7; mira cuántos subtrazos usa la escena (`bell/ReEmphasizeVennDiagram`). Sin texto de marca. Simple geometry (3 circles with a highlighted region): reproducible by code. Not CODEX.', 'ronda': '2', 'ronda_n': '22', 'svg_schema': {'viewBox': '0 0 884.3 737.7'}}]
ROUND2_CSV_SHA='c46ceca579c6723340203a49b118a557985bcd1a60ee7fe769f30ac68a5814ce'
ROUND1_ROWS=ROWS.copy()
ROUND3_ROWS=[{'n': '53', 'prioridad': 'P1', 'asset': 'svg_images/Bitcoin_logo.svg', 'ancho': 'svg', 'alto': '0 0 65.4 64', 'modo': 'SVG', 'escenas': '12', 'ejemplo': '_2017/crypto/BlockRewards', 'via': 'código o descargar', 'tipo': 'logo', 'derechos': 'logo_marca', 'que_crear': 'Logo de moneda (Bitcoin): 2 sub-trazos (disco exterior + marca interior) y el mismo viewBox 0 0 65.4 64.', 'nota': "Lo carga la clase `BitcoinLogo(SVGMobject)` de `_lib/custom/drawings.py` (file_name='Bitcoin_logo', height=1), por eso el chequeo estático no la atribuía a ninguna escena; la verificación con assets limpios falla en 12 escenas activas (11 de crypto + 256::StateOfBitcoin) con `OSError: Bitcoin_logo not Found`. Las escenas lo colorean (naranja); mantén EXACTAMENTE 2 sub-trazos en ese orden (disco, marca). Opciones: (a) gráfico propio por código (disco + una marca simple tipo moneda/barra, sin copiar el original de Grant); (b) el logotipo oficial de Bitcoin si su licencia es CC0/dominio público en Commons (verifica la página y anota la URL). Mismo nombre, mismo viewBox.", 'ronda': '3', 'ronda_n': '1', 'svg_schema': {'viewBox': '0 0 65.4 64'}}, {'n': '54', 'prioridad': 'P3', 'asset': 'svg_images/party_hat.svg', 'ancho': 'svg', 'alto': '0 0 512 512', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2017/efvgt/Anniversary', 'via': 'código', 'tipo': 'icono', 'derechos': 'desconocido', 'que_crear': 'Gorro de fiesta con 14 sub-formas en este orden: 7 volantes (0-6), 1 cono (7) y 6 puntos/círculos (8-13); viewBox 0 0 512 512.', 'nota': 'Lo carga la clase `PartyHat(SVGMobject)` de `_lib/custom/drawings.py`, que colorea por índice (`self[:7]` volantes con degradado, `self[7]` cono, `self[8:]` puntos), por eso también lo escondía el chequeo estático; falla `efvgt::Anniversary` con `OSError: party_hat not Found`. Dibújalo por código con EXACTAMENTE 14 sub-formas en ese orden, sin copiar el original. Mismo nombre y viewBox.', 'ronda': '3', 'ronda_n': '2', 'svg_schema': {'viewBox': '0 0 512 512'}}]
ROUND3_CSV_SHA='e8051ea1d8b1bd306a7d4b7e127fcb41e339def2b21bfb9e5a2ea0fdc9ce8445'
ROWS=ROUND1_ROWS+ROUND2_ROWS+ROUND3_ROWS
COMMONS={};EXTERNAL=None
path=h.path;solid=h.solid;line=h.line;ellipse=h.ellipse;font=h.font

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,data):h.atomic(p,data)
def compound(g,fill='#283A49'):
 ds=h.polygon_path(Polygon(g.exterior.coords))
 for ring_ in g.interiors:ds+=' '+h.polygon_path(Polygon(ring_.coords))
 return path(ds,fill)
def round_box(x0,y0,x1,y1,r=3):return box(x0+r,y0+r,x1-r,y1-r).buffer(r,quad_segs=12)
def svg(row,body):
 # Explicit white keeps uncolored 2017 icons visible; constructor colors still override it.
 body=body.replace(' fill="#171D26"',' fill="#FFFFFF"').replace(' fill="#283A49"',' fill="#FFFFFF"')
 schema=row.get('svg_schema',{});vb=row['alto'];parts=vb.split() if vb else ['0','0',schema.get('width','100'),schema.get('height','100')];x,y,w,h_=map(lambda v:float(v.removesuffix('px')),parts);attrs=' '.join(f'{k}="{v}"' for k,v in schema.items() if k in ['width','height','viewBox'])
 if Path(row['asset']).stem=='ethereum_logo':
  factor=min(w,h_)/100;transform=f'translate({x+(w-factor*100)/2} {y+(h_-factor*100)/2}) scale({factor})'
 else:transform=f'translate({x} {y}) scale({w/100} {h_/100})'
 return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}><!-- Own independent geometry, CC0. --><g transform="{transform}">{body}</g></svg>'

def icon(name):
 # All geometry below is independently designed; primary fills inherit scene color.
 if name=='electricity':return path('M 51 5 L 17 57 L 43 57 L 34 95 L 84 37 L 57 37 L 68 5 Z')
 if name=='fire':return path('M 51 5 C 59 28 91 39 88 66 C 87 92 61 99 39 93 C 10 85 7 63 19 44 C 18 61 31 63 33 49 C 34 32 48 22 51 5 Z')
 if name=='water':return path('M 50 3 C 39 24 12 48 12 65 C 12 106 88 106 88 65 C 88 47 61 23 50 3 Z')
 if name=='house':
  g=Polygon([(5,44),(50,5),(95,44),(85,44),(85,94),(15,94),(15,44)]).difference(box(42,67,58,96));return compound(g)
 if name=='ethereum_logo':
  # A broad square-cut gem with four facets, deliberately unlike a tall split crystal.
  return ''.join(path(ds,c) for ds,c in [
   ('M 12 30 L 36 12 L 50 44 Z','#ACB7BC'),('M 36 12 L 64 12 L 88 30 L 50 44 Z','#D1D9DD'),
   ('M 12 30 L 50 44 L 50 76 Z','#627A88'),('M 50 44 L 88 30 L 50 76 Z','#91A5AF')])
 if name=='litecoin_logo':
  # No L, slashed glyph, or trademark: silver coin and a generic square aperture.
  coin=ellipse(50,50,43);aperture=box(33,33,67,67);return compound(coin.difference(aperture),'#A7B4BD')+compound(ellipse(50,50,35).difference(ellipse(50,50,31)).difference(box(28,28,72,72)),'#647F8E')
 if name=='paint_bucket':
  bucket=Polygon([(20,36),(48,15),(77,52),(49,74)]).difference(Polygon([(30,37),(47,24),(66,50),(49,64)]));handle=LineString([(25,35),(16,22),(35,8),(48,18)]).buffer(3)
  return compound(bucket)+solid(handle)+path('M 76 50 C 87 64 95 76 87 85 C 74 92 69 76 76 68 Z','#819BA7')
 if name=='bank_building':
  g=unary_union([Polygon([(8,32),(50,10),(92,32)]),box(10,31,90,41),box(8,85,92,92),box(4,91,96,98),*[box(x,39,x+9,87) for x in [17,36,55,74]]]);return compound(g)
 if name=='government_building':
  dome=ellipse(50,31,25,22).intersection(box(0,0,100,32));g=unary_union([dome,box(46,6,54,15),box(18,31,82,40),box(10,38,90,44),box(10,84,90,91),box(5,91,95,98),*[box(x,42,x+9,85) for x in [17,36,55,74]]]);return compound(g)
 if name=='euro_symbol':
  ring=ellipse(55,50,33,41).difference(ellipse(55,50,23,30));ring=ring.difference(box(67,20,100,80));return compound(unary_union([ring,box(11,39,69,46),box(11,55,65,62)]))
 if name=='yen_symbol':
  return solid(unary_union([LineString([(19,9),(50,49),(81,9)]).buffer(5),box(45,46,55,94),box(23,51,77,58),box(23,67,77,74)]))
 if name=='gpu':
  body=round_box(8,27,91,73,4).difference(ellipse(32,50,15)).difference(ellipse(68,50,15));out=compound(body)+solid(box(9,72,15,85))+solid(box(15,19,20,79))
  for cx in [32,68]:
   out+=solid(ellipse(cx,50,4))
   for t in np.arange(5)*2*math.pi/5:
    out+=solid(Polygon([(cx+4*math.cos(t),50+4*math.sin(t)),(cx+12*math.cos(t+.2),50+12*math.sin(t+.2)),(cx+9*math.cos(t+.7),50+9*math.sin(t+.7))]))
  return out+''.join(solid(box(x,73,x+4,80),'#A3B5BD') for x in range(28,79,7))
 if name=='circuit':
  out=compound(round_box(32,30,68,70,4))
  for pts in [[(32,40),(16,40),(16,13)],[(32,57),(9,57),(9,85)],[(68,40),(85,40),(85,16)],[(68,57),(92,57),(92,85)],[(42,30),(42,9)],[(58,70),(58,91)]]:
   out+=solid(unary_union([LineString(pts).buffer(2.4),ellipse(*pts[-1],5)]))
  return out
 if name=='credit_card':
  card=round_box(4,8,96,92,7).difference(box(5,29,95,41));return compound(card)+compound(round_box(17,53,36,74,3),'#819BA7')
 if name=='phone':
  body=round_box(27,4,73,96,7).difference(round_box(32,17,68,78,2)).difference(ellipse(50,87,3));return compound(body)
 if name=='shield_locked':
  shield=Polygon([(50,5),(91,21),(87,60),(74,81),(50,97),(26,81),(13,60),(9,21)]);inner=Polygon([(50,16),(80,29),(76,57),(65,73),(50,83),(35,73),(24,57),(20,29)])
  arch=LineString([(39,48),(39,37),(44,30),(56,30),(61,37),(61,48)]).buffer(3.5);lock=round_box(34,46,66,70,3).difference(ellipse(50,56,3).union(box(48,56,52,64)))
  return compound(shield.difference(inner))+solid(arch,'#819BA7')+compound(lock,'#819BA7')
 if name=='galaxy':
  # Closed ribbon paths remain visible when the scene requests fill=0, stroke=3.
  out=solid(ellipse(50,50,5))
  for offset in [0,math.pi]:
   ts=np.linspace(.2,2.4*math.pi,180);rs=3+5.2*ts;pts=[(50+r*math.cos(t+offset),50+.73*r*math.sin(t+offset)) for t,r in zip(ts,rs)];out+=line(pts,2)
  return out
 if name=='visa_logo':
  # Wide generic payment card, with a final detachable chip for scene indexing.
  return compound(round_box(3,10,97,90,9).difference(box(4,29,96,39)),'#597D93')+compound(round_box(15,51,33,72,3),'#C4B58C')
 raise KeyError(name)

def raster(row):
 size=(int(row['ancho']),int(row['alto']));w,hh=size;name=Path(row['asset']).name
 if name=='ripple_logo.png':
  im=Image.new('RGBA',size);dr=ImageDraw.Draw(im);dr.ellipse((w*.12,hh*.12,w*.88,hh*.88),outline='#718F9E',width=w//22)
  for x,y in [(.32,.38),(.68,.38),(.5,.68)]:dr.ellipse((w*(x-.065),hh*(y-.065),w*(x+.065),hh*(y+.065)),fill='#B0C5CC')
  dr.line([(w*.38,hh*.39),(w*.62,hh*.39)],fill='#718F9E',width=w//32);dr.line([(w*.64,hh*.44),(w*.54,hh*.61)],fill='#718F9E',width=w//32);return im
 if name=='eater.jpg':
  # No person, silhouette, face, or name; only an independently drawn landscape.
  im=Image.new('RGB',size,'#9EAFBB');dr=ImageDraw.Draw(im)
  dr.polygon([(0,205),(57,105),(111,167),(177,80),(288,213),(288,288),(0,288)],fill='#697F91');dr.polygon([(0,248),(102,164),(185,230),(247,159),(288,216),(288,288),(0,288)],fill='#4B6579');return im.filter(ImageFilter.GaussianBlur(8))
 if name=='milky_way.jpg':
  rng=np.random.default_rng(201723);y,x=np.mgrid[-1:1:complex(hh),-1:1:complex(w)];dist=(y+.65*x-.08);band=np.exp(-(dist/.21)**2);cloud=.55+.18*np.sin(x*19+y*13)+.18*np.sin(x*47-y*21);a=np.zeros((hh,w,3));a[:]=[7,13,29];a+=band[...,None]*cloud[...,None]*[57,61,76];a+=rng.uniform(0,3,(hh,w,1));im=Image.fromarray(np.uint8(np.clip(a,0,255)));dr=ImageDraw.Draw(im)
  for _ in range(4600):
   xx,yy=rng.integers(0,w),rng.integers(0,hh);bright=int(rng.integers(60,245));r=.4 if bright<215 else .8;dr.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(bright,bright,min(255,bright+15)))
  return im
 if name=='Mandelbrot.jpg':
  # Mathematical set, not a synthetic portrait. Smooth escape-time coloring.
  half_y=1.5*hh/w;y,x=np.mgrid[-half_y:half_y:complex(hh),-2.35:.65:complex(w)];c=x+1j*y;z=np.zeros_like(c);active=np.ones(c.shape,bool);escape=np.zeros(c.shape);iters=260
  for k in range(iters):
   z[active]=z[active]**2+c[active];escaped=active&(np.abs(z)>4)
   escape[escaped]=k+1-np.log2(np.log(np.abs(z[escaped])));active[escaped]=False
  t=escape/22;rgb=np.stack([.5+.5*np.cos(t+1.3),.5+.5*np.cos(t+3.4),.5+.5*np.cos(t+5.2)],axis=-1);rgb=np.uint8(255*rgb);rgb[active]=[8,15,25];return Image.fromarray(rgb)
 if name=='bitcoin_mining_graphic.png':
  # Antialiased own hardware illustration, no crypto logos or inscriptions.
  s=2;im=Image.new('RGBA',(w*s,hh*s));dr=ImageDraw.Draw(im)
  def rect(b,fill,width=0,outline=None):dr.rounded_rectangle(tuple(int(v*s) for v in b),radius=7*s,fill=fill,outline=outline,width=width*s)
  for xx in [100,968]:rect((xx,70,xx+22,764),'#6C8594')
  for yy in [104,378,674]:rect((81,yy,1007,yy+22),'#8FA6B2')
  for yy in [146,419]:
   for xx in [139,425,711]:
    rect((xx,yy,xx+234,yy+170),'#3C556B',3,'#A4BAC6')
    for cx in [xx+65,xx+170]:
     dr.ellipse(((cx-47)*s,(yy+41)*s,(cx+47)*s,(yy+135)*s),fill='#172F44',outline='#8DA7B5',width=3*s)
     for a in np.arange(7)*2*math.pi/7:
      pts=[(cx,yy+88),(cx+39*math.cos(a),yy+88+39*math.sin(a)),(cx+33*math.cos(a+.5),yy+88+33*math.sin(a+.5))];dr.polygon([(int(x*s),int(y*s)) for x,y in pts],fill='#668B9E')
     dr.ellipse(((cx-8)*s,(yy+80)*s,(cx+8)*s,(yy+96)*s),fill='#B7CCD1')
    dr.line([(int(vx*s),int(vy*s)) for vx,vy in [(xx+214,yy+165),(xx+244,yy+194),(xx+249,yy+228),(xx+270,yy+228)]],fill='#B69B68',width=7*s)
  rect((153,718,940,766),'#344F65');return im.resize(size,Image.Resampling.LANCZOS)
 raise KeyError(name)


def handwritten_masks():
 # Independent pen geometry shared by digits and all of their component strokes.
 scale=12;size=(28*scale,28*scale)
 def pen(points,width):
  canvas=Image.new('L',size);dr=ImageDraw.Draw(canvas);xy=[(round(x*scale),round(y*scale)) for x,y in points];dr.line(xy,fill=245,width=round(width*scale),joint='curve')
  for x,y in [xy[0],xy[-1]]:
   radius=width*scale/2;dr.ellipse((x-radius,y-radius,x+radius,y+radius),fill=245)
  return np.array(canvas.resize((28,28),Image.Resampling.LANCZOS))
 t=np.linspace(0,2*math.pi,240)
 loop=pen([(13+6*math.cos(a)+.35*math.sin(2*a),9+5*math.sin(a)) for a in t],2.25)
 t=np.linspace(0,1,130);right=pen([(19-.8*u-1.2*u*u,8+16*u) for u in t],2.35)
 lower=pen([(12.5+6.5*math.cos(a)+.25*math.sin(2*a),18.5+5.5*math.sin(a)) for a in np.linspace(0,2*math.pi,240)],2.25)
 left=pen([(11-4*u+.3*math.sin(math.pi*u),4+11*u) for u in t],2.25)
 horizontal=pen([(7+14*u,15-.25*math.sin(math.pi*u)) for u in t],2.25)
 masks={'upper_loop':loop,'loop':loop,'right_line':right,'lower_loop':lower,'upper_left_line':left,'horizontal_line':horizontal,
        'nine':np.maximum(loop,right),'eight':np.maximum(loop,lower),'four':np.maximum.reduce([right,left,horizontal])}
 yy,xx=np.indices((28,28));angle=np.mod(np.arctan2((yy-9)/5,(xx-13)/6)+math.pi/2,2*math.pi);sector=np.minimum((angle/(2*math.pi)*5).astype(int),4)
 for i in range(5):masks[f'loop_edge{i+1}']=np.where(sector==i,loop,0).astype('uint8')
 for i,sel in enumerate([yy<11,(yy>=11)&(yy<18),yy>=18]):masks[f'right_line_edge{i+1}']=np.where(sel,right,0).astype('uint8')
 return masks

def handwritten(row):
 key=Path(row['asset']).stem.removeprefix('handwritten_');mask=handwritten_masks()[key];im=Image.fromarray(mask).convert('RGB')
 # The scene reads RGB channel 0 as activation, then computes alpha itself.
 # All inspected originals use opaque black backgrounds, including RGBA files.
 return im.convert(row['modo'])

def venn_region(name):
 # Same mathematical circle positions as the consuming scene, not traced artwork.
 a=Point(0,1).buffer(3,quad_segs=256);b=Point(-math.sqrt(3)/2,-.5).buffer(3,quad_segs=256);c=Point(math.sqrt(3)/2,-.5).buffer(3,quad_segs=256)
 if name=='VennDiagram_in_A_in_B':return a.intersection(b)
 if name=='VennDiagram_in_A_in_B_out_C':return a.intersection(b).difference(c)
 if name=='VennDiagram_in_A_out_B':return a.difference(b)
 if name=='VennDiagram_in_A_out_C':return a.difference(c)
 raise KeyError(name)

def venn_svg(row):
 from shapely.affinity import affine_transform
 geom=venn_region(Path(row['asset']).stem);assert geom.geom_type=='Polygon' and geom.is_valid
 width,height=map(float,row['alto'].split()[2:]);factor=min(width/(6+math.sqrt(3)),height/7.5)*.92
 geom=affine_transform(geom,[factor,0,0,-factor,width/2,height/2+.25*factor])
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{row["alto"]}"><!-- Independent Boolean circle region, CC0; no full-circle outlines: overlay mask. -->{compound(geom,"#E8C75C")}</svg>'.encode()

def science_thumbnail(row):
 # Three own science pictograms; no people, logos, lettering, or copied thumbnail.
 w,hh=int(row['ancho']),int(row['alto']);im=Image.new('RGB',(w,hh),'#183348');dr=ImageDraw.Draw(im)
 for x in [230,640,1050]:dr.ellipse((x-163,194,x+163,520),fill='#24465C')
 for angle in [0,math.pi/3,2*math.pi/3]:
  pts=[]
  for t in np.linspace(0,2*math.pi,200):
   xx,yy=119*math.cos(t),44*math.sin(t);pts.append((230+xx*math.cos(angle)-yy*math.sin(angle),355+xx*math.sin(angle)+yy*math.cos(angle)))
  dr.line(pts,fill='#93D1D0',width=7,joint='curve')
 dr.ellipse((216,341,244,369),fill='#E8C75C')
 flask=[(614,249),(666,249),(666,326),(737,445),(734,470),(546,470),(543,445),(614,326)]
 dr.polygon(flask,fill='#A6C7D5');dr.polygon([(593,365),(687,365),(725,447),(721,456),(559,456),(555,447)],fill='#78B4B7');dr.line([(606,249),(674,249)],fill='#D7E6E8',width=9)
 for x,y,r in [(621,406,8),(662,428,11),(647,378,6)]:dr.ellipse((x-r,y-r,x+r,y+r),fill='#C5E4DE')
 dr.ellipse((964,269,1136,441),fill='#C7AC77');dr.arc((912,318,1188,395),0,180,fill='#D5D9CB',width=13);dr.arc((912,318,1188,395),180,360,fill='#839FAB',width=7)
 return im

def round3_svg(row):
 # Independent geometry: source files from Grant are never used as drawing input.
 if Path(row['asset']).stem=='Bitcoin_logo':
  # A generic perforated coin and a bar, with negative space surviving monochrome recoloring.
  disc=ellipse(50,50,46).difference(round_box(25,33,75,67,5))
  body=compound(disc,'#D59B4B')+compound(round_box(34,43,66,57,3),'#F4E6BF')
 else:
  # Index contract: seven visible base frills, cone, six circular spots.
  colors=['#AF6987','#A36990','#97699A','#8A69A3','#7E69AD','#7269B6','#6669BF'];body=''
  for i,color in enumerate(colors):
   x=20+60*i/7;dx=60/7
   body+=path(f'M {x:.5f} 79 L {x+dx:.5f} 79 L {x+dx+.8:.5f} 92 L {x+dx/2:.5f} 96 L {x-.8:.5f} 92 Z',color)
  body+=path('M 50 7 L 81 82 Q 50 90 19 82 Z','#75A48C')
  for x,y in [(49,28),(40,47),(59,50),(32,68),(50,72),(68,70)]:body+=solid(ellipse(x,y,3.3),'#EAD08A')
 return svg(row,body).encode()

def scene_audit(row):
 file=ROOT/'_work'/(row['ejemplo']+'.py');stem=Path(row['asset']).stem
 if not file.exists():return {'scene':row['ejemplo'],'matches':[],'note':'No se encontró el ejemplo indicado.'}
 lines=file.read_text().splitlines();hits=[]
 for i,l in enumerate(lines):
  if stem.lower() in l.lower() or stem.startswith('Dice-') and 'Dice-' in l or stem.startswith('handwritten_') and ('handwritten_' in l or '"'+stem.removeprefix('handwritten_')+'"' in l) or stem.startswith('VennDiagram_') and 'VennDiagram_' in l:hits.append({'line':i+1,'context':'\n'.join(lines[max(0,i-1):i+5])})
 result={'scene':str(file.relative_to(ROOT)),'matches':hits[:8],'indirect_name':stem.replace('_',' ') if not hits else ''}
 if row.get('ronda')=='3':
  cls='BitcoinLogo' if stem=='Bitcoin_logo' else 'PartyHat';result['matches']=[{'line':i+1,'context':'\n'.join(lines[max(0,i-1):i+5])} for i,l in enumerate(lines) if cls in l][:8]
  custom=ROOT/'_lib/custom/drawings.py';content=custom.read_text().splitlines();start=next(i for i,l in enumerate(content) if l.startswith('class '+cls+'('));end=next((i for i in range(start+1,len(content)) if content[i].startswith('class ')),len(content));result['consumer_class']={'file':str(custom.relative_to(ROOT)),'class':cls,'line':start+1,'context':'\n'.join(content[start:end])[:5000]}
 return result

def existing(row):
 global EXTERNAL
 if EXTERNAL is None:
  EXTERNAL={}
  for f in HERE.parent.rglob('*sources.json'):
   if f.parent==HERE:continue
   data=json.loads(f.read_text());items=data.values() if isinstance(data,dict) else data
   for r in items:
    if not isinstance(r,dict):continue
    asset=r.get('asset') or 'raster_images/'+r.get('name','')
    if r.get('sha256') and r.get('status') in ['generated','replaced','kept']:EXTERNAL[asset]=r|{'provenance_file':str(f.relative_to(ROOT))}
 p=ASSETS/row['asset'];r=EXTERNAL.get(row['asset']);return r if r and p.exists() and sha(p)==r['sha256'] else None

def progress(records):
 states=['hecha','ya_existe','entregada_IA','saltada'];counts={state:sum(r.get('delivery_state')==state for r in records.values()) for state in states}
 pending=sorted([r for r in ROWS if records.get(r['asset'],{}).get('delivery_state') not in ['hecha','ya_existe','entregada_IA']],key=lambda r:(r['prioridad'],int(r['n'])));n=pending[0] if pending else None
 command='python _lib/assets/generated/replacements/assets2017/make_assets_2017.py --round '+(n.get('ronda','1') if n else '3')
 lines=['# Progreso de assets 2017','','## AHORA',f"Completados: {sum(counts[state] for state in ['hecha','ya_existe','entregada_IA'])}/{len(ROWS)}; {len(pending)} pendientes.",f'Estados: {counts}.',f"Sigue: {n['asset'] if n else 'rondas 1, 2 y 3 completas; revisar hojas y comprobaciones'}.",f'Comando: `{command}`.','']
 for label,rows in [('Ronda 1',ROUND1_ROWS),('Ronda 2',ROUND2_ROWS),('Ronda 3',ROUND3_ROWS)]:
  done=sum(records.get(r['asset'],{}).get('delivery_state') in ['hecha','ya_existe','entregada_IA'] for r in rows)
  lines += ['## '+label,'',f'{done}/{len(rows)} completados. Numeración global: 1–30 en ronda 1; 31–52 en ronda 2 (fila CSV + 30); 53–54 en ronda 3 (fila CSV + 52).','','| # | CSV | Prioridad | Asset | Estado | Vía | Fuente | Licencia | Nota |','|---:|---:|---|---|---|---|---|---|---|']
  for row in rows:
   r=records.get(row['asset'],{});values=[row['n'],row.get('ronda_n',row['n']),row['prioridad'],row['asset'],r.get('delivery_state','pendiente'),r.get('via',row['via']),r.get('page_url',''),r.get('license',''),r.get('note','')];lines.append('| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in values)+' |')
  lines+=['']
 lines+=['## Resumen','',str(counts)+f'; {len(pending)} pendientes. Todas las creaciones propias se ofrecen como CC0. Las fuentes libres de la primera ronda conservan sus licencias individuales.','','## Atribuciones']
 lines += [f"- {asset}: {r.get('author')}; {r.get('license')}; {r.get('page_url')}." for asset,r in records.items() if r.get('license','').startswith('CC BY')]
 lines+=['','## Revisión y decisiones','','Primera ronda: eater es un paisaje sin persona; milky_way es ilustrativo, Mandelbrot es el conjunto matemático, las marcas son símbolos genéricos. Norway es una costa simplificada de Natural Earth, sin valor para medir una dimensión fractal. La primera entrega y sus 30 archivos permanecen intactos.','','Ronda 2: los dígitos y sus componentes proceden de trazos propios compartidos, sin muestras MNIST ni originales de Grant. Los RGBA mantienen fondo negro opaco (como los originales inspeccionados); la escena toma el canal rojo como activación. Los cinco arcos reconstruyen el bucle y los tres segmentos reconstruyen la línea. Los Venn son máscaras de la región indicada, sin círculos de contexto ni rótulos: la escena ya los dibuja y escala las máscaras por sus límites. La miniatura solo contiene iconos abstractos propios. Sin IA ni renders de escenas.']
 qa=AUDIT/'ASSETS_2017_ronda2_checks.json'
 if qa.exists():
  data=json.loads(qa.read_text());lines+=['','## Verificación de ronda 2','',f"22/22 formatos y respaldos verificados; 4 SVG cargan en ManimGL; composición exacta de dígitos, partición de trazos y regiones de Venn comprobadas. Archivos anteriores protegidos: {data.get('previous_assets_unchanged')}. Idempotencia: {data.get('idempotence_all_22_hashes_unchanged',False)}."]
 lines+=['','## Decisiones de ronda 3','','Moneda genérica propia, sin logotipo oficial ni letras: disco exterior perforado y barra interior. Gorro propio: siete volantes, cono y seis puntos. Ambos CC0, con originales respaldados, sin IA ni renders.']
 qa3=AUDIT/'ASSETS_2017_ronda3_checks.json'
 if qa3.exists():
  data=json.loads(qa3.read_text());lines+=['','## Verificación de ronda 3','',f"2/2 SVG verificados en ManimGL y en sus clases consumidoras: 2 y 14 submobjetos en el orden pedido. Archivos anteriores protegidos: {data.get('previous_assets_unchanged')}. Idempotencia: {data.get('idempotence_all_2_hashes_unchanged',False)}."]
 (AUDIT/'PROGRESO_2017.md').write_text('\n'.join(lines)+'\n')

def review(records,round_id='3'):
 rows={'1':ROUND1_ROWS,'2':ROUND2_ROWS,'3':ROUND3_ROWS}[round_id]
 out=Image.new('RGB',(min(6,len(rows))*250,math.ceil(len(rows)/6)*185),'#E3E7E3');dr=ImageDraw.Draw(out)
 for i,row in enumerate(rows):
  x=i%6*250;y=i//6*185;dr.text((x+4,y+4),row['n']+' '+Path(row['asset']).name,fill='#283F4E');r=records.get(row['asset'])
  if not r:continue
  p=ASSETS/row['asset']
  try:
   if p.suffix=='.svg':
    # A no-viewBox/no-size source has no intrinsic viewport; give the preview only a canvas.
    node=ET.parse(p).getroot()
    if not node.get('viewBox'):
     node.set('viewBox','0 0 '+node.get('width','100').removesuffix('px')+' '+node.get('height','100').removesuffix('px'))
    preview=ET.tostring(node)
    im=Image.open(io.BytesIO(subprocess.check_output(['rsvg-convert','--keep-aspect-ratio','-w','230','-h','140'],input=preview,stderr=subprocess.DEVNULL))).convert('RGBA')
   else:
    im=Image.open(p).convert('RGBA')
    if p.stem.startswith('handwritten_'):im=im.resize((140,140),Image.Resampling.NEAREST)
   im=ImageOps.contain(im,(230,140));bg=Image.new('RGBA',im.size,'#1E303D' if row['modo']=='SVG' else '#F5F5EF');bg.alpha_composite(im);out.paste(bg.convert('RGB'),(x+(250-im.width)//2,y+24))
  except Exception as e:dr.text((x+5,y+65),'Sin miniatura: '+str(e)[:20],fill='red')
  dr.text((x+4,y+168),r['delivery_state'],fill='#386452')
 out.save(AUDIT/('REVISION_2017.png' if round_id=='1' else f'REVISION_2017_ronda{round_id}.png'))

def validate(row,p):
 if row['modo']=='SVG':
  root=ET.parse(p).getroot();assert root.get('viewBox')==(row['alto'] or None);paths=root.findall('.//{http://www.w3.org/2000/svg}path')
  if p.stem=='ethereum_logo':assert len(paths)==4
  if p.stem=='Norway':assert len(paths)==1
  if p.stem=='Bitcoin_logo':assert len(paths)==2
  if p.stem=='party_hat':assert len(paths)==14
 else:
  with Image.open(p) as im:assert im.size==(int(row['ancho']),int(row['alto'])) and im.mode==row['modo']

SPECS={
 'raster_images/Astrolabe.jpg':{'title':'File:Astrolabes, circa 1400 and 1625.jpg','centering':[.5,.5]},
 'raster_images/Pierre_de_Fermat.png':{'title':'File:Pierre de Fermat.jpg','alias':'raster_images/Fermat.jpg','person':'Pierre de Fermat'},
 'raster_images/Sculling.jpg':{'title':'File:Sculling past Stourbridge Common - geograph.org.uk - 5589384.jpg','centering':[.5,.5]},
 'raster_images/Trilobite.jpg':{'title':'File:Fossil Trilobite (9964973146).jpg','centering':[.5,.5]},
 'svg_images/Norway.svg':{'norway':True},
 'raster_images/Barrow.jpg':{'title':'File:Isaac Barrow by Mary Beale.jpg','person':'Isaac Barrow'},
 'raster_images/Weierstrass.jpg':{'title':'File:Karl Weierstrass.jpg','person':'Karl Weierstrass'},
}


def generate(row,spec,dest,rec):
 if row.get('ronda')=='3':
  atomic(dest,round3_svg(row));rec['subject']='Moneda genérica propia sin marca' if dest.stem=='Bitcoin_logo' else 'Gorro de fiesta propio de 14 piezas'
  rec['note']='Dos paths: disco exterior perforado y barra interior genérica; sin letras ni logotipo oficial.' if dest.stem=='Bitcoin_logo' else '14 paths: volantes 0–6, cono 7 y puntos 8–13; compatibles con PartyHat.'
  rec['structure_contract']=['disco','marca'] if dest.stem=='Bitcoin_logo' else ['volante']*7+['cono']+['punto']*6
  return
 if row.get('ronda')=='2':
  rec['subject']='Creación propia: '+dest.stem
  if dest.stem.startswith('handwritten_'):d.save(handwritten(row),dest,row['modo']);rec['note']='Trazos propios compartidos: componentes y dígitos encajan exactamente por máximo de intensidad. Fondo negro opaco; la escena convierte el canal rojo en activación.'
  elif dest.stem.startswith('VennDiagram_'):atomic(dest,venn_svg(row));rec['note']='Solo la región booleana pedida; los círculos y rótulos ya los dibuja la escena. Un path cerrado continuo, viewBox exacto.'
  else:d.save(science_thumbnail(row),dest,row['modo']);rec['note']='Miniatura propia: átomo, matraz y planeta; sin personas, siluetas humanas, logos ni texto.'
  return
 if spec.get('norway'):return norway(row,dest,rec)
 if spec.get('alias'):return fermat_alias(row,spec,dest,rec)
 if spec.get('title'):return download(row,spec,dest,rec)
 if row['modo']=='SVG':atomic(dest,svg(row,icon(dest.stem)).encode());return
 d.save(raster(row),dest,row['modo'])
 rec['note']='Ilustración propia por código, sin marcas, personas ni material original de Grant.'

def fitted(text,width,size):return h.fitted(text,width,size)
def flat_card(size,title,subtitle='',mode='RGB'):
 im=Image.new('RGB',size,'#E6E5DB');dr=ImageDraw.Draw(im);w,hh=size;dr.rectangle((w*.07,hh*.06,w*.93,hh*.94),outline='#758B96',width=max(1,w//160));f=fitted(title,w*.76,min(w*.07,hh*.1));dr.multiline_text((w/2,hh*.43),title,font=f,fill='#253C4B',anchor='mm',align='center',spacing=max(5,hh*.02))
 if subtitle:dr.multiline_text((w/2,hh*.73),subtitle,font=fitted(subtitle,w*.76,min(w*.04,hh*.05)),fill='#536B76',anchor='mm',align='center',spacing=5)
 return im.convert(mode)



def fermat_alias(row,spec,dest,rec):
 # Reuse only the hash-verified, independently sourced 2019 replacement.
 info=COMMONS.get(spec['title'])
 if not info:raise ValueError('No se pudo revalidar la licencia del retrato libre de Fermat.')
 previous=json.loads((HERE.parent/'assets2019/assets2019_sources.json').read_text())[spec['alias']];source=ASSETS/spec['alias']
 if sha(source)!=previous['sha256']:raise ValueError('El reemplazo libre de Fermat de 2019 cambió; requiere revisión.')
 source_cache(info);intact=dest.exists() and rec.get('old_sha256')==sha(dest)
 if not intact:
  im=Image.open(source).convert('RGBA');im=ImageOps.fit(im,(int(row['ancho']),int(row['alto'])),Image.Resampling.LANCZOS);d.save(im,dest,row['modo'])
 rec.update(info,status='kept' if intact else 'replaced',via='descargar',reused_asset=spec['alias'],reused_asset_sha256=previous['sha256'],changes='Alias del reemplazo libre de Fermat de 2019, ajustado a PNG RGBA y tamaño exacto; se revalida en vivo la licencia de su fuente.',note='Se reutiliza el retrato libre de Fermat de 2019. No se usa Pierre_de_Fermat original de Grant.')

def norway(row,dest,rec):
 # Natural Earth coastline, clipped to Norway mainland; no tracing of Grant's SVG.
 from bs4 import BeautifulSoup
 from shapely.geometry import shape
 from shapely.ops import linemerge
 import urllib.request
 license_url='https://www.naturalearthdata.com/about/terms-of-use/'
 with urllib.request.urlopen(urllib.request.Request(license_url,headers=d.UA),timeout=30) as response:evidence=response.read(1024**2)
 text=BeautifulSoup(evidence,'html.parser').get_text(' ',strip=True)
 if 'All versions of Natural Earth raster + vector map data found on this website are in the public domain.' not in text:raise ValueError('No se pudo verificar el dominio público de Natural Earth.')
 atomic(CACHE/'licencias/naturalearth_terms.html',evidence)
 base='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/'
 sources=[];layers={}
 for layer in ['ne_50m_admin_0_countries','ne_50m_coastline']:
  url=base+layer+'.geojson';raw=CACHE/'descargados'/(layer+'.geojson')
  if not raw.exists():atomic(raw,d.http(url))
  layers[layer]=json.loads(raw.read_text());sources.append({'file_url':url,'sha256':sha(raw),'bytes':raw.stat().st_size})
 country=next(f for f in layers['ne_50m_admin_0_countries']['features'] if f['properties'].get('ADMIN')=='Norway');geom=shape(country['geometry']);mainland=max(geom.geoms,key=lambda g:g.area) if geom.geom_type=='MultiPolygon' else geom
 pieces=[]
 def collect(g):
  if g.is_empty:return
  if g.geom_type=='LineString':pieces.append(g)
  elif hasattr(g,'geoms'):
   for item in g.geoms:collect(item)
 for f in layers['ne_50m_coastline']['features']:
  geom=shape(f['geometry'])
  if geom.intersects(mainland):collect(geom.intersection(mainland.buffer(.00001)))
 merged=linemerge(pieces);lines=list(merged.geoms) if hasattr(merged,'geoms') else [merged];coast=max(lines,key=lambda g:g.length).simplify(.006,preserve_topology=False)
 coords=np.array(coast.coords);assert len(coords)>150,('Coast too simple',len(coords))
 # Local equirectangular projection, preserving aspect; west coast only, open stroke.
 coords[:,0]*=math.cos(math.radians(64));coords[:,1]*=-1;x0,y0=coords.min(axis=0);x1,y1=coords.max(axis=0);w,hh=map(float,row['alto'].split()[2:]);scale=min(w*.9/(x1-x0),hh*.9/(y1-y0));coords=(coords-[x0,y0])*scale+[(w-(x1-x0)*scale)/2,(hh-(y1-y0)*scale)/2]
 body='M '+' L '.join(f'{x:.3f} {y:.3f}' for x,y in coords)
 data=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{row["alto"]}"><path d="{body}" fill="none" stroke="#FFFFFF" stroke-width="2"/></svg>'.encode()
 intact=dest.exists() and rec.get('old_sha256')==sha(dest)
 if not intact:atomic(dest,data)
 rec.update(author='Natural Earth; Tom Patterson, Nathaniel Vaughn Kelso y colaboradores',license='Public domain',license_url=license_url,page_url='https://www.naturalearthdata.com/',file_url=sources[1]['file_url'],source_sha256=sources[1]['sha256'],source_files=sources,evidence_sha256=hashlib.sha256(evidence).hexdigest(),license_evidence='Términos oficiales de Natural Earth consultados en esta ejecución; todos sus datos vectoriales son de dominio público.',status='kept' if intact else 'replaced',via='descargar',coast_points=len(coords),changes='Datos Natural Earth 50m v5.1.2: costa continental más larga de Noruega; sin frontera terrestre ni islas, simplificación 0.006 grados, proyección local y ajuste al viewBox, un solo trazo abierto.',note='Costa continental de Natural Earth; una ruta continua abierta, sin frontera terrestre. Ilustración simplificada, no sirve para medir una dimensión fractal real.')

def commons_html(title):
 """Verify file-specific license templates from the public page, not site footer.
 The public file-specific license templates are verified directly on every run.
 """
 from bs4 import BeautifulSoup
 import urllib.request,urllib.parse,time
 url='https://commons.wikimedia.org/wiki/'+urllib.parse.quote(title.replace(' ','_'),safe=':/()')
 time.sleep(.7)
 with urllib.request.urlopen(urllib.request.Request(url,headers=d.UA),timeout=30) as response:raw=response.read(8*1024**2)
 soup=BeautifulSoup(raw,'html.parser');shorts=[e.get_text(' ',strip=True) for e in soup.select('.licensetpl_short')];valid=[v for v in shorts if d.ALLOWED.fullmatch(v)]
 if not valid:raise ValueError('No hay una plantilla de licencia admisible en '+title)
 lic=sorted(valid,key=lambda v:0 if v.startswith('CC BY-SA') else 1 if v.startswith('CC BY') else 2 if v.startswith('CC0') else 3)[0];original=soup.select_one('.fullMedia a.internal')
 if not original:raise ValueError('No se encontró el archivo original en '+title)
 def cell_for(selector):
  node=soup.select_one(selector)
  if node is None:return None
  label=node if node.name in ['td','th'] else node.find_parent(['td','th'])
  return label.find_next_sibling('td') if label else None
 desc=cell_for('#fileinfotpl_desc');description=desc.get_text(' ',strip=True)[:650] if desc else ''
 author_cell=cell_for('#fileinfotpl_aut, #fileinfotpl_art');full_credit=author_cell.get_text(' ',strip=True) if author_cell else ''
 names=list(dict.fromkeys(n.get_text(' ',strip=True) for n in author_cell.select('.fn') if not n.select_one('.fn'))) if author_cell else []
 author='; '.join(names) if names else full_credit
 if not author:author='Autor desconocido (Commons)'
 if re.fullmatch(r'(Unknown author\s*){1,2}',author):author='Autor desconocido (Commons)'
 if lic.lower()=='public domain':lic_url=d.PD_URL
 elif lic.lower().startswith('cc0'):lic_url=CC0
 else:
  m=re.fullmatch(r'CC BY(-SA)? (\d+(?:\.\d+)?)(?: ([a-z]+))?',lic,re.I)
  if not m:raise ValueError('No se pudo interpretar la licencia '+lic)
  lic_url='https://creativecommons.org/licenses/by'+('-sa' if m[1] else '')+'/'+m[2]+'/'+(m[3]+'/' if m[3] else '')
 evidence=CACHE/'licencias'/(hashlib.sha256(title.encode()).hexdigest()[:24]+'.html');atomic(evidence,raw)
 canonical=soup.select_one('link[rel=canonical]');page_url=canonical.get('href') if canonical else url
 credit=cell_for('#fileinfotpl_src');credit=credit.get_text(' ',strip=True)[:350] if credit else ''
 return {'commons_title':title,'source_author_credit':(author if names else full_credit)[:1500],'source_credit':credit,'source_description':description,'page_url':page_url,'file_url':original['href'].split('?')[0],'license':lic,'license_url':lic_url,'author':author,'license_evidence':'Ficha pública de Commons consultada en esta ejecución; plantilla licensetpl_short específica del archivo, no licencia del pie del sitio.','evidence_sha256':hashlib.sha256(raw).hexdigest()}

def verify_pages(titles):
 out={}
 for title in sorted(titles):
  try:out[title]=commons_html(title)
  except Exception as e:print('  Fuente no verificada:',title,str(e),flush=True)
 return out

def source_cache(info):
 from urllib.parse import urlparse,unquote
 url=info['file_url'];suffix=Path(unquote(urlparse(url).path)).suffix or '.bin';name=hashlib.sha256(url.encode()).hexdigest()[:24]+suffix;target=CACHE/'descargados'/name
 if not target.exists():
  for folder in ['downloads','assets2018','assets2019','assets2020']:
   old=ROOT/'_tools/.cache'/folder/'originales'/name
   if old.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,target);break
 if not target.exists():atomic(target,d.http(url))
 info.update(source_sha256=sha(target),source_size_bytes=target.stat().st_size,download_size_bytes=target.stat().st_size)
 return target

def download(row,spec,dest,rec):
 info=COMMONS.get(spec['title'])
 if not info:
  if spec.get('person'):
   if rec.get('previous_download'):raise ValueError('No se pudo revalidar la foto anterior; se conserva su procedencia sin sobrescribirla.')
   im=flat_card((int(row['ancho']),int(row['alto'])),spec['person'],mode=row['modo']);
   if not (dest.exists() and rec.get('old_sha256')==sha(dest)):d.save(im,dest,row['modo'])
   rec.update(author='propio (código)',license='CC0',license_url=CC0,via='código',status='generated',note='Tarjeta neutra con el nombre: no se pudo verificar una foto adecuada en esta ejecución. No se genera una cara.');return
  raise ValueError('Fuente o licencia sin verificar: '+spec['title'])
 raw=source_cache(info);intact=dest.exists() and rec.get('old_sha256')==sha(dest)
 if row['modo']=='SVG':
  if not intact:atomic(dest,signature(row,raw))
 else:
  im=Image.open(raw).convert('RGB');info.update(source_width=im.width,source_height=im.height)
  if not intact:
   if spec.get('crop'):im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(spec['crop'])))
   size=(int(row['ancho']),int(row['alto']))
   if spec.get('extend'):im=d.extend_portrait(im,size)
   else:im=ImageOps.fit(im,size,Image.Resampling.LANCZOS,centering=tuple(spec.get('centering',[.5,.4])))
   if row['modo']=='P':im=im.quantize(colors=256)
   d.save(im,dest,row['modo'])
 rec.update(info);rec.update(status='kept' if intact else 'replaced',via='descargar',changes='Descarga independiente de una fuente libre verificada; ajuste de encuadre y tamaño/modo. No se utiliza el archivo de Grant.',note=spec.get('note','Licencia específica verificada en la ficha pública de Commons en esta ejecución.'))


def write_attributions(records):
 """Keep file-specific credits next to the generator on every execution."""
 lines=['# Atribuciones de los assets de 2017','','Las creaciones propias por código se ofrecen como CC0. Las fuentes descargadas y la reutilización del retrato libre de Fermat conservan sus licencias individuales; no se presentan como obra propia. Las adaptaciones de imágenes CC BY-SA siguen bajo la licencia indicada.','']
 for row in ROWS:
  r=records.get(row['asset'],{})
  if r.get('via')!='descargar':continue
  if r.get('status')=='skipped':r=r.get('retained_provenance',{})
  if not r:continue
  lines += [f"## {row['n']}. `{row['asset']}`",'',f"- Autor/crédito: {r.get('author','')}",f"- Licencia: [{r.get('license','')}]({r.get('license_url','')})",f"- Fuente: {r.get('page_url','')}",f"- Cambios: {r.get('changes','')}"]
  if r.get('source_credit'):lines += [f"- Procedencia indicada por Commons: {r['source_credit']}"]
  lines+=['']
 lines+=['## Fuentes tipográficas','','Se utilizan únicamente las fuentes libres ya presentes en `_lib/assets/fonts/`: JetBrains Mono y, cuando lo requiere una utilidad compartida, CMU Serif. Sus avisos están incluidos en esa carpeta. No se distribuyen portadas, emblemas ni capturas de terceros.','', '## Verificación de fuentes','','El generador consulta en vivo las fichas públicas de Commons y verifica sus plantillas `licensetpl_short` específicas del archivo. No interpreta la licencia del pie de página como licencia de la imagen. La evidencia HTML y los originales descargados se guardan en la caché ignorada; cada registro conserva sus hashes.']
 (HERE/'ATTRIBUTIONS_2017.md').write_text('\n'.join(lines)+'\n')


def run(args):
 if (AUDIT/'assets2017.csv').exists() and sha(AUDIT/'assets2017.csv')!=CSV_SHA:raise RuntimeError('assets2017.csv cambió: revisar la lista antes de continuar.')
 if sha(AUDIT/'assets2017_ronda3.csv')!=ROUND3_CSV_SHA:raise RuntimeError('assets2017_ronda3.csv cambió: revisar la lista.')
 if sha(AUDIT/'assets2017_ronda2.csv')!=ROUND2_CSV_SHA:raise RuntimeError('assets2017_ronda2.csv cambió: revisar la lista.')
 CACHE.mkdir(parents=True,exist_ok=True);(CACHE/'.gitignore').write_text('*\n!.gitignore\n');records=json.loads(SOURCE.read_text()) if SOURCE.exists() else {};progress(records);selected=[r for r in sorted(ROWS,key=lambda r:(r['prioridad'],int(r['n']))) if (not args.round or (r.get('ronda','1')==args.round)) and (not args.only or any(v in [r['n'],r['asset'],Path(r['asset']).name] for v in args.only)) and (not args.priority or r['prioridad']==args.priority)]
 global COMMONS
 titles={SPECS[r['asset']]['title'] for r in selected if SPECS.get(r['asset'],{}).get('title')}
 try:COMMONS=verify_pages(titles)
 except Exception as e:COMMONS={};print('No se pudo verificar Commons:',e,flush=True)
 for row in selected:
  asset=row['asset'];p=ASSETS/asset;old=records.get(asset);spec=SPECS.get(asset,{});recipe={'2':'2017-round2-v1','3':'2017-round3-v1'}.get(row.get('ronda'),VERSION);print(f"[{row['n']}/{len(ROWS)}] {asset}",flush=True)
  prev=existing(row)
  if prev:
   records[asset]=prev|{'delivery_state':'ya_existe','note':'Reemplazo previo verificado por coincidencia de hash; no se modifica.'};d.atomic_json(SOURCE,records);progress(records);continue
  if old and old.get('recipe_version')==recipe and p.exists() and sha(p)==old.get('sha256') and not (spec.get('title') or spec.get('norway')) and not args.force:
   if spec.get('card'):old['subject']='Tarjeta neutra: '+spec['card']
   records[asset]=old;d.atomic_json(SOURCE,records);progress(records);continue
  rec={'asset':asset,'name':p.name,'subject':row['que_crear'] or row['nota'],'author':'propio (código)','license':'CC0','license_url':CC0,'page_url':'','status':'skipped','changes':'Creación independiente desde cero, sin usar el archivo de Grant como entrada.','via':'código','note':'','recipe_version':recipe,'verified_at':datetime.now(timezone.utc).isoformat(),'scene_review':scene_audit(row),'old_sha256':None if args.force else (old or {}).get('sha256')}
  if p.stem=='eater':rec['subject']='Paisaje neutro difuminado sin figura humana'
  if spec.get('person'):rec['subject']='Retrato de '+spec['person'].replace('\n',' ')
  elif spec.get('card'):rec['subject']='Tarjeta neutra: '+spec['card']
  if spec.get('title') or spec.get('norway'):rec.update(author='',license='',license_url='',via='descargar',previous_download=bool(old and old.get('via')=='descargar'))
  try:
   backup=CACHE/'originales'/asset
   if p.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
   generate(row,spec,p,rec);validate(row,p);rec.update(status=rec['status'] if rec['status'] in ['replaced','kept'] else 'generated',delivery_state='hecha',sha256=sha(p),final_size_bytes=p.stat().st_size,note=rec['note'] or 'Reemplazo propio; uso de la escena y tamaño/modo o lienzo SVG revisados.')
  except Exception as e:
   rec.update(status='skipped',delivery_state='saltada',note=str(e) or type(e).__name__);print('  SALTADA',e,flush=True)
   if old and p.exists() and old.get('sha256')==sha(p):rec['retained_provenance']=old
  if rec.get('author')=='Unknown authorUnknown author':rec['author']='Autor desconocido (Commons)'
  records[asset]=rec;d.atomic_json(SOURCE,records);progress(records)
 review(records,args.round or '3')
 write_attributions(records)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',nargs='+');ap.add_argument('--priority',choices=['P1','P2','P3']);ap.add_argument('--round',choices=['1','2','3']);ap.add_argument('--force',action='store_true');run(ap.parse_args())
