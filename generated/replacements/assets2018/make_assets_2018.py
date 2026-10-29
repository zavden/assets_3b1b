"""Independent replacements for the 2018 asset list; never reads original artwork as input.

Use --only NUMBER/asset ... or --priority P2/P3, optionally --force.
Needs Pillow, numpy, shapely, rsvg-convert and the project's existing helper modules.
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
HERE=Path(__file__).resolve().parent;ASSETS=HERE.parents[2];ROOT=ASSETS.parents[1];AUDIT=ROOT/'_tools/assets_licencias/codex';CACHE=ROOT/'_tools/.cache/assets2018';SOURCE=HERE/'assets2018_sources.json';FONTS=ASSETS/'fonts'
sp=importlib.util.spec_from_file_location('helpers2019',HERE.parent/'assets2019/make_assets_2019.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);d=h.d;d.CACHE=CACHE;d.UA={'User-Agent':'ManimLearningAssets2018/1.0 (educational independent asset audit)'}
CC0='https://creativecommons.org/publicdomain/zero/1.0/';VERSION='2018-independent-v1'
ROWS=[{'n': '1', 'prioridad': 'P2', 'asset': 'raster_images/Lost_Lecture_cover.jpg', 'ancho': '355', 'alto': '499', 'modo': 'RGB', 'escenas': '4', 'ejemplo': '_2018/lost_lecture/AngularMomentumArgument', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own flat book-cover mock-up with the title text (no publisher art); used in 12 scenes of the Lost Lecture video', 'nota': 'Book cover art (copyright)'}, {'n': '2', 'prioridad': 'P2', 'asset': 'raster_images/mars.png', 'ancho': '500', 'alto': '500', 'modo': 'RGBA', 'escenas': '4', 'ejemplo': '_2018/lost_lecture/AngularMomentumArgument', 'via': 'código', 'tipo': 'imagen', 'derechos': 'desconocido', 'que_crear': 'Shaded disc generated with numpy (reddish) or NASA public-domain Mars image', 'nota': 'Planet image, provenance unknown (probably NASA)'}, {'n': '3', 'prioridad': 'P2', 'asset': 'raster_images/mercury.png', 'ancho': '624', 'alto': '624', 'modo': 'P', 'escenas': '4', 'ejemplo': '_2018/lost_lecture/AngularMomentumArgument', 'via': 'código', 'tipo': 'imagen', 'derechos': 'desconocido', 'que_crear': 'Shaded disc generated with numpy (grey) or NASA public-domain Mercury image', 'nota': 'Planet image, provenance unknown (probably NASA)'}, {'n': '4', 'prioridad': 'P2', 'asset': 'raster_images/venus.png', 'ancho': '800', 'alto': '800', 'modo': 'P', 'escenas': '4', 'ejemplo': '_2018/lost_lecture/AngularMomentumArgument', 'via': 'código', 'tipo': 'imagen', 'derechos': 'desconocido', 'que_crear': 'Shaded disc generated with numpy (pale yellow) or NASA public-domain Venus image', 'nota': 'Planet image, provenance unknown (probably NASA)'}, {'n': '5', 'prioridad': 'P2', 'asset': 'svg_images/pinch_hand.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2018/quaternions/FelixViewOfProjection', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own pinching-hand pointer icon drawn by code (Hand class used to grab and rotate the stereographic spheres)', 'nota': 'Third-party vector icon, license unverified; used as a "hand" cursor in 9 quaternion scenes.'}, {'n': '6', 'prioridad': 'P2', 'asset': 'svg_images/radar_dish.svg', 'ancho': 'svg', 'alto': '0 0 90 90', 'modo': 'SVG', 'escenas': '4', 'ejemplo': '_2018/uncertainty/AmbiguityInLongEchos', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own radar-dish icon drawn by code (arc + stand); used in 6 scenes of the Doppler radar part', 'nota': 'Third-party icon'}, {'n': '7', 'prioridad': 'P2', 'asset': 'raster_images/GerminalDandelin.jpg', 'ancho': '1030', 'alto': '1198', 'modo': 'RGB', 'escenas': '3', 'ejemplo': '_2018/dandelin/CreativeConstruction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Public-domain portrait/drawing of G. P. Dandelin (1822 era, Wikimedia Commons)', 'nota': 'Old portrait, public domain'}, {'n': '8', 'prioridad': 'P2', 'asset': 'raster_images/comet.png', 'ancho': '500', 'alto': '500', 'modo': 'LA', 'escenas': '3', 'ejemplo': '_2018/dandelin/ShowOrbits', 'via': 'código', 'tipo': 'imagen', 'derechos': 'desconocido', 'que_crear': 'Comet picture drawn by code (bright nucleus, soft tail) or a public-domain NASA comet photo; used 13 times (Lost Lecture orbits)', 'nota': 'Provenance of the image unknown'}, {'n': '9', 'prioridad': 'P2', 'asset': 'raster_images/de_Broglie.png', 'ancho': '1693', 'alto': '2097', 'modo': 'L', 'escenas': '3', 'ejemplo': '_2018/uncertainty/HangingWeightsScene', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': '[CODEX] Free-licence portrait of Louis de Broglie (Nobel Foundation / Commons, check licence) or own silhouette', 'nota': 'Photo of a real person, licence unverified'}, {'n': '10', 'prioridad': 'P2', 'asset': 'svg_images/Dice-1.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/eop/chapter1/prob_dist_visuals/ProbabilityDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own die face SVG drawn by code (rounded square + pips), same size and name', 'nota': 'Die face icon of unknown authorship', 'svg_schema': {'width': '557', 'height': '557'}}, {'n': '11', 'prioridad': 'P2', 'asset': 'svg_images/Dice-2.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/eop/chapter1/prob_dist_visuals/ProbabilityDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own die face SVG drawn by code (rounded square + pips), same size and name', 'nota': 'Die face icon of unknown authorship', 'svg_schema': {'width': '557', 'height': '557'}}, {'n': '12', 'prioridad': 'P2', 'asset': 'svg_images/Dice-3.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/eop/chapter1/prob_dist_visuals/ProbabilityDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own die face SVG drawn by code (rounded square + pips), same size and name', 'nota': 'Die face icon of unknown authorship', 'svg_schema': {'width': '557', 'height': '557'}}, {'n': '13', 'prioridad': 'P2', 'asset': 'svg_images/Dice-4.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/eop/chapter1/prob_dist_visuals/ProbabilityDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own die face SVG drawn by code (rounded square + pips), same size and name', 'nota': 'Die face icon of unknown authorship', 'svg_schema': {'width': '557', 'height': '557'}}, {'n': '14', 'prioridad': 'P2', 'asset': 'svg_images/Dice-5.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/eop/chapter1/prob_dist_visuals/ProbabilityDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own die face SVG drawn by code (rounded square + pips), same size and name', 'nota': 'Die face icon of unknown authorship', 'svg_schema': {'width': '557', 'height': '557'}}, {'n': '15', 'prioridad': 'P2', 'asset': 'svg_images/Dice-6.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/eop/chapter1/prob_dist_visuals/ProbabilityDistributions', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own die face SVG drawn by code (rounded square + pips), same size and name', 'nota': 'Die face icon of unknown authorship', 'svg_schema': {'width': '557', 'height': '557'}}, {'n': '16', 'prioridad': 'P2', 'asset': 'svg_images/camera.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/basel/basel2/EarthScene', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own camera icon drawn by code (rectangle body, lens circle, flash)', 'nota': 'Icon of unknown origin without licence metadata'}, {'n': '17', 'prioridad': 'P2', 'asset': 'svg_images/speaker.svg', 'ancho': 'svg', 'alto': '0 0 64 64', 'modo': 'SVG', 'escenas': '3', 'ejemplo': '_2018/fourier/AddingPureFrequencies', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own loudspeaker icon drawn by code (trapezoid cone, rectangle, three arcs)', 'nota': 'Third-party vector icon, license unverified; the fourier scenes use it as the sound source.'}, {'n': '18', 'prioridad': 'P2', 'asset': 'raster_images/Kant.jpg', 'ancho': '964', 'alto': '1388', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2018/dandelin/CreativeConstruction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Public-domain portrait of Immanuel Kant (Wikimedia Commons)', 'nota': 'Old portrait, public domain'}, {'n': '19', 'prioridad': 'P2', 'asset': 'raster_images/Lewis_Richardson.png', 'ancho': '253', 'alto': '368', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2018/turbulence/FiguresOfFluidDynamics', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Photo of L. F. Richardson (d. 1953): free licence photo or neutral silhouette placeholder; never an AI-generated face', 'nota': 'PARA CODEX: photo of a real person, copyright unclear'}, {'n': '20', 'prioridad': 'P2', 'asset': 'raster_images/Lord Kelvin.jpg', 'ancho': '939', 'alto': '1176', 'modo': 'L', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Old portrait (19th century, public domain); download from Wikimedia Commons (Codex downloads) and keep the exact name"}, {'n': '21', 'prioridad': 'P2', 'asset': 'raster_images/Macfarlane Alexander.jpg', 'ancho': '202', 'alto': '286', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Old portrait (19th century, public domain); download from Wikimedia Commons (Codex downloads) and keep the exact name"}, {'n': '22', 'prioridad': 'P2', 'asset': 'raster_images/MeasurementCover.png', 'ancho': '800', 'alto': '1206', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2018/dandelin/LockhartQuote', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own flat book-cover mock-up titled "Measurement" (no publisher art)', 'nota': 'Book cover art (copyright)'}, {'n': '23', 'prioridad': 'P2', 'asset': 'raster_images/Oliver Heaviside.jpg', 'ancho': '513', 'alto': '789', 'modo': 'RGB', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Old portrait (19th century, public domain); download from Wikimedia Commons (Codex downloads) and keep the exact name"}, {'n': '24', 'prioridad': 'P2', 'asset': 'raster_images/Peter Tait.jpg', 'ancho': '465', 'alto': '564', 'modo': 'L', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Old portrait (19th century, public domain); download from Wikimedia Commons (Codex downloads) and keep the exact name"}, {'n': '25', 'prioridad': 'P2', 'asset': 'raster_images/Robert Ball.jpg', 'ancho': '958', 'alto': '1198', 'modo': 'L', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Old portrait (19th century, public domain); download from Wikimedia Commons (Codex downloads) and keep the exact name"}, {'n': '26', 'prioridad': 'P2', 'asset': 'raster_images/grey_gradient.png', 'ancho': '1921', 'alto': '1081', 'modo': 'RGBA', 'escenas': '2', 'ejemplo': '_2018/alt_calc/StartingCalc101', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Vertical grey gradient PNG (1921x1081, RGBA) made with numpy; used by color_using_background_image for a spring and a weight', 'nota': 'color_using_background_image("grey_gradient") in StartingCalc101'}, {'n': '27', 'prioridad': 'P2', 'asset': 'svg_images/hat.svg', 'ancho': 'svg', 'alto': '0 0 50000 50000', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own simple icon drawn by code (make_visual_svgs.py style)', 'nota': 'Third-party vector icon (Noun Project or similar), author and license not verifiable'}, {'n': '28', 'prioridad': 'P2', 'asset': 'svg_images/mouse.svg', 'ancho': 'svg', 'alto': '0 0 24 24', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2018/quat3d/Introduction', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own simple icon drawn by code (make_visual_svgs.py style)', 'nota': 'Third-party vector icon (Noun Project or similar), author and license not verifiable'}, {'n': '29', 'prioridad': 'P2', 'asset': 'svg_images/sailor_hat.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '2', 'ejemplo': '_2018/wallis/KeeperAndSailor', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own sailor-hat icon drawn by code', 'nota': 'Third-party icon'}, {'n': '30', 'prioridad': 'P3', 'asset': 'raster_images/3b1b_logo.png', 'ancho': '696', 'alto': '648', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/div_curl/ThoughtsOnAds', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': '', 'nota': "Un agente lo marcó 'usar_con_atribucion', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. 3Blue1Brown channel logo (own work of the channel); div_curl ThoughtsOnAds shows it."}, {'n': '31', 'prioridad': 'P3', 'asset': 'raster_images/AoPS_volume_2.jpg', 'ancho': '349', 'alto': '408', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/uncertainty/Promotion', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Plain book-cover mock-up drawn by code (flat color, own title text) instead of the AoPS volume cover', 'nota': 'Cover art of a published book (copyright)'}, {'n': '32', 'prioridad': 'P3', 'asset': 'raster_images/BroomBridgePlaque.jpg', 'ancho': '640', 'alto': '480', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/quaternions/IntroduceHamilton', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Free-licensed photo of the Broom Bridge plaque (Wikimedia Commons) or an own drawn plaque graphic with the carved Hamilton equation; photo of a real place: mark for Codex', 'nota': 'Photo of the Hamilton plaque at Broom Bridge, Dublin; copyright and photographer unknown (came from videos/assets).'}, {'n': '33', 'prioridad': 'P3', 'asset': 'raster_images/Calculus_Thumbnail.jpg', 'ancho': '1280', 'alto': '720', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanElementaryQuote', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Frame rendered by us from the series thumbnail scene (or a flat title card drawn by code)', 'nota': "Thumbnail of 3b1b's own video, kept in videos/assets/"}, {'n': '34', 'prioridad': 'P3', 'asset': 'raster_images/ChessGameOfTheCentury.jpg', 'ancho': '300', 'alto': '300', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/PatYourselfOnTheBack', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Chessboard diagram drawn by code (8x8 squares and a few pieces as simple glyphs) instead of the photo', 'nota': 'Photo/diagram of a famous game, copyright unknown'}, {'n': '35', 'prioridad': 'P3', 'asset': 'raster_images/CoderQuaternionResponse_0.png', 'ancho': '1056', 'alto': '478', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Own text card imitating a forum reply (rectangle + Text, invented wording, no real username)', 'nota': 'Screenshot of a third-party forum comment'}, {'n': '36', 'prioridad': 'P3', 'asset': 'raster_images/CoderQuaternionResponse_1.png', 'ancho': '1416', 'alto': '554', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Own text card imitating a forum reply (rectangle + Text, invented wording, no real username)', 'nota': 'Screenshot of a third-party forum comment'}, {'n': '37', 'prioridad': 'P3', 'asset': 'raster_images/CoderQuaternionResponse_2.png', 'ancho': '944', 'alto': '286', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Own text card imitating a forum reply (rectangle + Text, invented wording, no real username)', 'nota': 'Screenshot of a third-party forum comment'}, {'n': '38', 'prioridad': 'P3', 'asset': 'raster_images/CoderQuaternionResponse_3.png', 'ancho': '1456', 'alto': '494', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Own text card imitating a forum reply (rectangle + Text, invented wording, no real username)', 'nota': 'Screenshot of a third-party forum comment'}, {'n': '39', 'prioridad': 'P3', 'asset': 'raster_images/DandelionSphere.jpg', 'ancho': '558', 'alto': '544', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/dandelin/NameDandelin', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': '[CODEX] Photo of a dandelion seed head under a free licence (CC0/CC BY) or own drawing', 'nota': 'Photo of a dandelion, author and licence unknown'}, {'n': '40', 'prioridad': 'P3', 'asset': 'raster_images/Einstein.png', 'ancho': '2523', 'alto': '3313', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/uncertainty/HangingWeightsScene', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Public-domain portrait of Einstein (1921 photo, Wikimedia Commons)', 'nota': 'Portrait photo (public domain version exists on Commons)'}, {'n': '41', 'prioridad': 'P3', 'asset': 'raster_images/Feynman_Lectures_cover.png', 'ancho': '3264', 'alto': '2448', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanFame', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own flat book-cover mock-up with the title text (no publisher art)', 'nota': 'Book cover art (copyright)'}, {'n': '42', 'prioridad': 'P3', 'asset': 'raster_images/Feynman_Los_Alamos.jpg', 'ancho': '574', 'alto': '674', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanFame', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Own silhouette or a free-licence photo of the Los Alamos ID badge; no likeness of a real person is generated', 'nota': 'Photo of a real person, copyright probable'}, {'n': '43', 'prioridad': 'P3', 'asset': 'raster_images/Feynman_QED_cover.jpg', 'ancho': '869', 'alto': '1341', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanFame', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own flat book-cover mock-up with the title text (no publisher art)', 'nota': 'Book cover art (copyright)'}, {'n': '44', 'prioridad': 'P3', 'asset': 'raster_images/Feynman_Woods.jpg', 'ancho': '470', 'alto': '541', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/turbulence/FeynmanOnTurbulence', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Photo of Richard Feynman: free licence photo (Wikimedia Commons) or a neutral silhouette placeholder; never an AI-generated face', 'nota': 'PARA CODEX: copyrighted photo of a real person'}, {'n': '45', 'prioridad': 'P3', 'asset': 'raster_images/Fourier_Thumbnail.jpg', 'ancho': '1280', 'alto': '720', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanElementaryQuote', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Frame rendered by us from the series thumbnail scene (or a flat title card drawn by code)', 'nota': "Thumbnail of 3b1b's own video, kept in videos/assets/"}, {'n': '46', 'prioridad': 'P3', 'asset': 'raster_images/Geoffrey_Taylor.jpg', 'ancho': '250', 'alto': '248', 'modo': 'L', 'escenas': '1', 'ejemplo': '_2018/turbulence/FiguresOfFluidDynamics', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': 'Photo of G. I. Taylor: free licence photo or a neutral silhouette placeholder; never an AI-generated face', 'nota': 'PARA CODEX: photo of a real person (d. 1975), copyright unclear'}, {'n': '47', 'prioridad': 'P3', 'asset': 'raster_images/George_Stokes.jpg', 'ancho': '329', 'alto': '447', 'modo': 'L', 'escenas': '1', 'ejemplo': '_2018/turbulence/FiguresOfFluidDynamics', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. 19th century portrait of George Stokes; public domain"}, {'n': '48', 'prioridad': 'P3', 'asset': 'raster_images/GoogleDandelin.png', 'ancho': '1480', 'alto': '1082', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/dandelin/NameDandelin', 'via': 'código', 'tipo': 'imagen', 'derechos': 'captura_de_terceros', 'que_crear': 'Mock search-results page drawn by code (generic search box and result rows, no Google branding)', 'nota': 'Screenshot of a commercial site'}, {'n': '49', 'prioridad': 'P3', 'asset': 'raster_images/HackerNewsLogo.png', 'ancho': '257', 'alto': '257', 'modo': 'P', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Generic own badge (rounded square + initial letter), not the brand logo', 'nota': 'Trademarked logo'}, {'n': '50', 'prioridad': 'P3', 'asset': 'raster_images/Heisenberg.jpg', 'ancho': '497', 'alto': '789', 'modo': 'L', 'escenas': '1', 'ejemplo': '_2018/uncertainty/OneLevelDeeper', 'via': 'descargar o código', 'tipo': 'imagen', 'derechos': 'foto_terceros', 'que_crear': '[CODEX] Free-licence photo of Heisenberg (Bundesarchiv, CC BY-SA 3.0 de) with attribution, or own silhouette', 'nota': 'Photo of a real person, licence unverified'}, {'n': '51', 'prioridad': 'P3', 'asset': 'raster_images/Henry_As_Stick.png', 'ancho': '344', 'alto': '856', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/TakeOver', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Generic stick-figure drawn by code (no likeness of a real person)', 'nota': 'Joke stick figure of a real person'}, {'n': '52', 'prioridad': 'P3', 'asset': 'raster_images/Hermann_von_Helmholtz.jpg', 'ancho': '338', 'alto': '440', 'modo': 'L', 'escenas': '1', 'ejemplo': '_2018/turbulence/FiguresOfFluidDynamics', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. 19th century portrait of Helmholtz; public domain"}, {'n': '53', 'prioridad': 'P3', 'asset': 'raster_images/John_Wallis.jpg', 'ancho': '640', 'alto': '773', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/wallis/MentionJohnWallis', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Public-domain portrait of John Wallis (Wikimedia Commons)', 'nota': 'Old portrait, public domain'}, {'n': '54', 'prioridad': 'P3', 'asset': 'raster_images/Kepler2ndLaw.png', 'ancho': '1920', 'alto': '1080', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/HistoryOfAngularMomentum', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Equal-areas diagram (ellipse, sun, two sectors) drawn by code', 'nota': 'Diagram'}, {'n': '55', 'prioridad': 'P3', 'asset': 'raster_images/Leonhard_Euler.jpg', 'ancho': '461', 'alto': '600', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/turbulence/FiguresOfFluidDynamics', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Portrait of Euler (Handmann, 1753); public domain"}, {'n': '56', 'prioridad': 'P3', 'asset': 'raster_images/MadameBovary.jpg', 'ancho': '308', 'alto': '488', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/dandelin/LockhartQuote', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own flat book-cover mock-up titled "Madame Bovary"', 'nota': 'Book cover (copyright of the edition unknown)'}, {'n': '57', 'prioridad': 'P3', 'asset': 'raster_images/MonaLisa.jpg', 'ancho': '804', 'alto': '1198', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/dandelin/LockhartQuote', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': 'Public-domain reproduction of the Mona Lisa (Wikimedia Commons)', 'nota': 'Painting, public domain'}, {'n': '58', 'prioridad': 'P3', 'asset': 'raster_images/Pietro_Mengoli.gif', 'ancho': '160', 'alto': '160', 'modo': 'P', 'escenas': '1', 'ejemplo': '_2018/basel/basel2/IntroScene', 'via': 'descargar', 'tipo': 'imagen', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. 17th century portrait of Pietro Mengoli (160x160 gif); public domain"}, {'n': '59', 'prioridad': 'P3', 'asset': 'raster_images/Quanta logo.png', 'ancho': '914', 'alto': '129', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/quaternions/HoldUpQuanta', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Own generic magazine-style wordmark graphic made with code/text (no brand logo)', 'nota': 'Brand logo (Quanta Magazine); trademarked.'}, {'n': '60', 'prioridad': 'P3', 'asset': 'raster_images/RedditLogo.png', 'ancho': '720', 'alto': '720', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Generic own badge (rounded square + initial letter), not the brand logo', 'nota': 'Trademarked logo'}, {'n': '61', 'prioridad': 'P3', 'asset': 'raster_images/Surely_Youre_Joking_cover.jpg', 'ancho': '603', 'alto': '719', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanFame', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own flat book-cover mock-up with the title text (no publisher art)', 'nota': 'Book cover art (copyright)'}, {'n': '62', 'prioridad': 'P3', 'asset': 'raster_images/TwitterLogo.png', 'ancho': '1687', 'alto': '1687', 'modo': 'P', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Generic own badge (rounded square + initial letter), not the brand logo', 'nota': 'Trademarked logo'}, {'n': '63', 'prioridad': 'P3', 'asset': 'raster_images/YouTubeLogo.png', 'ancho': '1024', 'alto': '721', 'modo': 'P', 'escenas': '1', 'ejemplo': '_2018/quat3d/WhoCares', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Generic own badge (rounded square + initial letter), not the brand logo', 'nota': 'Trademarked logo'}, {'n': '64', 'prioridad': 'P3', 'asset': 'raster_images/alt_calc_hidden_image.png', 'ancho': '1920', 'alto': '1080', 'modo': 'RGB', 'escenas': '1', 'ejemplo': '_2018/alt_calc/StartingCalc101', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Any 1920x1080 picture (e.g. a numpy colour-noise or gradient image): the scene blurs it with a 50 px kernel and uses it as the content of the mystery box', 'nota': 'Loaded with cv2.imread(get_full_raster_image_path(...)) in StartingCalc101'}, {'n': '65', 'prioridad': 'P3', 'asset': 'raster_images/blue_yellow_gradient.png', 'ancho': '1924', 'alto': '1085', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/uncertainty/SummarizeFourierTradeoffForDoppler', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'Blue-to-yellow vertical gradient made with numpy (like make_vertical_temp_gradient.py)', 'nota': 'Plain gradient'}, {'n': '66', 'prioridad': 'P3', 'asset': 'raster_images/dartboard.png', 'ancho': '2000', 'alto': '2000', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/eop/chapter1/show_uncertainty_darts/ShowUncertaintyDarts', 'via': 'código', 'tipo': 'imagen', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own dartboard drawn by code (concentric rings and wedges, PIL/numpy)', 'nota': 'Dartboard picture of unknown authorship'}, {'n': '67', 'prioridad': 'P3', 'asset': 'raster_images/mathologer_logo.png', 'ancho': '566', 'alto': '562', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/basel/basel2/MathologerVideoWrapper', 'via': 'código', 'tipo': 'logo', 'derechos': 'logo_marca', 'que_crear': 'Generic own badge (circle with a stylised M by code); the real channel logo is a brand mark and must not be copied', 'nota': 'Brand logo of a third-party YouTube channel'}, {'n': '68', 'prioridad': 'P3', 'asset': 'raster_images/minute_physics_logo.png', 'ancho': '690', 'alto': '690', 'modo': 'P', 'escenas': '1', 'ejemplo': '_2018/uncertainty/MinutPhysicsWrapper', 'via': 'código', 'tipo': 'imagen', 'derechos': 'logo_marca', 'que_crear': 'Own stand-in emblem (text "MP" in a ring) drawn by code, not the channel logo', 'nota': 'Brand logo of another channel'}, {'n': '69', 'prioridad': 'P3', 'asset': 'raster_images/white_black_gradient.png', 'ancho': '4003', 'alto': '2258', 'modo': 'RGBA', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/TakeOver', 'via': 'código', 'tipo': 'imagen', 'derechos': 'obra_3b1b', 'que_crear': 'White-to-black gradient made with numpy', 'nota': 'Plain gradient'}, {'n': '70', 'prioridad': 'P3', 'asset': 'svg_images/8th_note.svg', 'ancho': 'svg', 'alto': '', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/eop/bayes/MusicExample', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own simple icon drawn by code (make_visual_svgs.py style)', 'nota': 'Third-party vector icon (Noun Project or similar), author and license not verifiable', 'svg_schema': {'version': '1.0', 'width': '90', 'height': '90', 'id': 'svg2'}}, {'n': '71', 'prioridad': 'P3', 'asset': 'svg_images/biplane.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/uncertainty/AmbiguityInLongEchos', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own biplane silhouette drawn by code (rectangles + circle)', 'nota': 'Third-party icon'}, {'n': '72', 'prioridad': 'P3', 'asset': 'svg_images/blimp.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/uncertainty/AmbiguityInLongEchos', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own blimp silhouette (ellipse + fin + gondola) drawn by code', 'nota': 'Third-party icon'}, {'n': '73', 'prioridad': 'P3', 'asset': 'svg_images/bongo.svg', 'ancho': 'svg', 'alto': '0 0 50 50', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanFame', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own bongo-drums icon drawn by code (two cylinders)', 'nota': 'Third-party icon'}, {'n': '74', 'prioridad': 'P3', 'asset': 'svg_images/euler-signature.svg', 'ancho': 'svg', 'alto': '0 0 957 215', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/pi_day/EulerSignature', 'via': 'descargar', 'tipo': 'svg_ilustracion', 'derechos': 'retrato_dominio_publico', 'que_crear': '', 'nota': "Un agente lo marcó 'usar', pero el archivo sigue siendo idéntico al de Grant (nivel 3): hay que reemplazarlo. Euler signature tracing (historic signature, public domain); keep or retrace by code"}, {'n': '75', 'prioridad': 'P3', 'asset': 'svg_images/falcon_heavy.svg', 'ancho': 'svg', 'alto': '0 0 1000 1302.5', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/uncertainty/AmbiguityInLongEchos', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own three-booster rocket silhouette drawn by code', 'nota': 'Third-party icon'}, {'n': '76', 'prioridad': 'P3', 'asset': 'svg_images/helicopter.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/uncertainty/AmbiguityInLongEchos', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own helicopter silhouette drawn by code', 'nota': 'Third-party icon'}, {'n': '77', 'prioridad': 'P3', 'asset': 'svg_images/plane2.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/turbulence/BumpyPlaneRide', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own airplane silhouette (side view) drawn by code with the same viewbox', 'nota': 'Icon of unknown origin without licence metadata'}, {'n': '78', 'prioridad': 'P3', 'asset': 'svg_images/safe.svg', 'ancho': 'svg', 'alto': '0 0 100 100', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/lost_lecture/FeynmanFame', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own safe icon drawn by code (box + dial)', 'nota': 'Third-party icon'}, {'n': '79', 'prioridad': 'P3', 'asset': 'svg_images/shamrock.svg', 'ancho': 'svg', 'alto': '0 0 40 45', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/quaternions/IntroduceHamilton', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own shamrock icon drawn by code (three circles/hearts plus stem, green)', 'nota': 'Third-party vector icon, license unverified; decorative.'}, {'n': '80', 'prioridad': 'P3', 'asset': 'svg_images/traffic_light.svg', 'ancho': 'svg', 'alto': '0 0 64 64', 'modo': 'SVG', 'escenas': '1', 'ejemplo': '_2018/uncertainty/TwoCarsAtRedLight', 'via': 'código', 'tipo': 'svg_icono', 'derechos': 'ilustracion_terceros', 'que_crear': 'Own traffic-light icon drawn by code (rounded box + three circles); the red light is used by TwoCarsAtRedLight', 'nota': 'Third-party icon'}]
CSV_SHA='ad4ae976e1dbafda3c6352453ab7a2270b2778cfd924417b59a9206520139ade'
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
 # Missing primary fills inherit the 2018 Cairo-compatible scene color (white).
 body=body.replace(' fill="#171D26"','').replace(' fill="#283A49"','')
 schema=row.get('svg_schema',{});vb=row['alto'];parts=vb.split() if vb else ['0','0',schema.get('width','100'),schema.get('height','100')];x,y,w,h_=map(float,parts);attrs=f'viewBox="{vb}"' if vb else f'width="{schema["width"]}" height="{schema["height"]}"'
 return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}><!-- Own independent geometry, CC0. --><g transform="translate({x} {y}) scale({w/100} {h_/100})">{body}</g></svg>'

def icon(name):
 if name.startswith('Dice-'):
  n=int(name[-1]);frame=round_box(5,5,95,95,10).difference(round_box(10,10,90,90,6));places={1:[(50,50)],2:[(28,28),(72,72)],3:[(28,28),(50,50),(72,72)],4:[(28,28),(72,28),(28,72),(72,72)],5:[(28,28),(72,28),(50,50),(28,72),(72,72)],6:[(28,25),(72,25),(28,50),(72,50),(28,75),(72,75)]}
  return compound(frame)+''.join(solid(ellipse(x,y,7),'#283A49') for x,y in places[n])
 if name=='pinch_hand':
  return path('M 23 93 L 20 73 Q 9 61 12 45 Q 13 38 19 42 L 30 56 L 34 24 Q 34 17 40 18 Q 46 18 45 26 L 45 47 L 58 37 Q 66 32 72 38 L 88 53 Q 92 60 87 64 L 79 70 Q 74 74 70 68 L 62 57 L 51 65 L 64 76 L 65 94 Z')+path('M 35 60 L 44 69 M 20 50 L 29 63','none','#D9E0DA',2)
 if name=='radar_dish':
  return path('M 17 12 Q 3 64 64 78 Q 48 50 17 12 Z')+line([(18,12),(65,76)],3,'#7D929D')+line([(42,48),(77,19)],4)+solid(ellipse(78,18,5))+path('M 44 72 L 37 92 L 77 92 L 58 75 Z')
 if name=='camera':
  body=round_box(8,27,92,82,7).difference(ellipse(51,54,20));return compound(body)+compound(ellipse(51,54,15).difference(ellipse(51,54,10)))+path('M 21 28 L 28 16 L 49 16 L 57 28 Z')+solid(box(73,35,84,43),'#9DB0B8')
 if name=='speaker':
  out=path('M 9 37 L 29 37 L 48 20 L 48 80 L 29 63 L 9 63 Z')
  for r in [18,29,40]:
   points=[(49+r*math.cos(t),50+r*math.sin(t)) for t in np.linspace(-.65,.65,25)];out+=line(points,3)
  return out
 if name=='hat':return path('M 24 64 L 20 16 Q 50 7 79 16 L 75 64 Z')+path('M 24 49 L 75 49 L 75 62 L 24 62 Z','#93A4AC')+path('M 8 64 Q 49 54 92 65 L 95 76 Q 50 87 5 75 Z')
 if name=='mouse':
  body=unary_union([ellipse(48,60,30,20),ellipse(69,48,17,20),ellipse(62,30,12),ellipse(78,33,10)])
  return solid(Polygon(body.exterior))+line([(25,65),(13,67),(6,54),(13,46),(18,51)],4)+solid(ellipse(76,45,2),'#DDE4DC')
 if name=='sailor_hat':return path('M 15 48 Q 18 17 50 18 Q 83 19 86 48 L 81 70 L 20 70 Z','#A9BAC1')+path('M 12 48 Q 51 58 89 48 L 86 70 Q 50 82 16 70 Z')
 if name=='8th_note':return h.VISUAL_P1('EighthNote')
 if name=='biplane':return path('M 12 40 L 92 40 L 92 48 L 12 48 Z M 12 67 L 92 67 L 92 75 L 12 75 Z M 44 12 Q 51 4 57 12 L 57 83 L 69 92 L 69 97 L 51 93 L 34 97 L 34 92 L 44 83 Z')+line([(20,48),(23,67)],3)+line([(79,48),(82,67)],3)
 if name=='blimp':return solid(ellipse(48,41,39,25))+path('M 77 36 L 96 20 L 93 43 L 97 61 L 77 50 Z')+path('M 31 66 L 38 78 L 61 78 L 67 64 Z')
 if name=='bongo':return path('M 8 30 Q 27 20 45 30 L 40 86 Q 26 93 14 85 Z M 48 18 Q 71 6 93 19 L 87 78 Q 68 87 54 78 Z')+solid(ellipse(26,30,19,7),'#9CB0B6')+solid(ellipse(70,19,23,8),'#9CB0B6')
 if name=='falcon_heavy':
  out=''
  for x in [23,50,77]:out+=path(f'M {x-10} 82 L {x-10} 24 Q {x-8} 11 {x} {6 if x==50 else 18} Q {x+8} 11 {x+10} 24 L {x+10} 82 Z')
  # Exactly nine final pieces: generic windows, bands and nozzles, never brand marks.
  for x in [23,50,77]:out+=solid(ellipse(x,35,3),'#7E96A2')+solid(box(x-9,63,x+9,68),'#7E96A2')+path(f'M {x-6} 82 L {x+6} 82 L {x+9} 95 L {x-9} 95 Z','#7E96A2')
  return out
 if name=='helicopter':return solid(ellipse(55,52,25,15))+path('M 32 47 L 7 32 L 3 37 L 31 61 Z')+line([(56,39),(56,24)],4)+line([(17,24),(95,24)],4)+line([(40,68),(38,78),(80,78)],3)+line([(70,66),(73,78)],3)
 if name=='plane2':return path('M 6 57 L 39 48 L 45 14 L 56 14 L 56 46 L 83 43 Q 99 43 96 52 L 65 65 L 36 66 L 18 80 L 12 78 L 18 64 L 6 63 Z')
 if name=='safe':
  frame=round_box(11,7,89,92,5).difference(round_box(19,15,81,85,2));return compound(frame)+solid(ellipse(51,51,15))+''.join(line([(51,51),(51+23*math.cos(a),51+23*math.sin(a))],4,'#8098A4') for a in np.arange(3)*2*math.pi/3)+solid(box(71,38,75,64))
 if name=='shamrock':return solid(unary_union([ellipse(33,33,20),ellipse(66,33,20),ellipse(50,16,20),Polygon([(47,40),(54,40),(65,94),(51,98)])]),'#4B7B68')
 if name=='traffic_light':
  # TrafficLight adds its post at index 0: source index 1 becomes scene index 2 (red).
  return solid(round_box(27,3,73,96,9))+solid(ellipse(50,24,13),'#D15E58')+solid(ellipse(50,50,13),'#82959D')+solid(ellipse(50,76,13),'#82959D')
 raise KeyError(name)

def fitted(text,width,size):return h.fitted(text,width,size)
def flat_card(size,title,subtitle='',mode='RGB'):
 im=Image.new('RGB',size,'#E6E5DB');dr=ImageDraw.Draw(im);w,hh=size;dr.rectangle((w*.07,hh*.06,w*.93,hh*.94),outline='#758B96',width=max(1,w//160));f=fitted(title,w*.76,min(w*.07,hh*.1));dr.multiline_text((w/2,hh*.43),title,font=f,fill='#253C4B',anchor='mm',align='center',spacing=max(5,hh*.02))
 if subtitle:dr.multiline_text((w/2,hh*.73),subtitle,font=fitted(subtitle,w*.76,min(w*.04,hh*.05)),fill='#536B76',anchor='mm',align='center',spacing=5)
 return im.convert(mode)

BOOKS={
 'Lost_Lecture_cover.jpg':("Feynman's\nLost Lecture",'David Goodstein\nJudith Goodstein'),
 'MeasurementCover.png':('Measurement','Paul Lockhart'),
 'AoPS_volume_2.jpg':('The Art of Problem Solving\nVolume 2','Richard Rusczyk · Sandor Lehoczky'),
 'Calculus_Thumbnail.jpg':('Cálculo','Una introducción visual'),
 'Fourier_Thumbnail.jpg':('Series de Fourier','Frecuencias y sumas de ondas'),
 'Feynman_Lectures_cover.png':('The Feynman Lectures\non Physics','Richard Feynman\nRobert Leighton · Matthew Sands'),
 'Feynman_QED_cover.jpg':('QED','Richard Feynman'),
 'MadameBovary.jpg':('Madame Bovary','Gustave Flaubert'),
 'Surely_Youre_Joking_cover.jpg':("Surely You're Joking,\nMr. Feynman!",'Richard Feynman')}
COMMENTS=[
 'Los cuaterniones me ayudan a componer rotaciones sin perder la orientación.',
 'Para una cámara 3D, interpolar orientaciones resulta más claro con cuaterniones.',
 'Una rotación y su inversa se combinan de forma muy compacta.',
 'Las matrices siguen siendo útiles; los cuaterniones ofrecen otra representación.']

def gradient(size,top,bottom):
 w,hh=size;y=np.linspace(0,1,hh)[:,None,None];rgb=(np.array(top)[None,None,:]*(1-y)+np.array(bottom)[None,None,:]*y);out=np.broadcast_to(rgb,(hh,w,3)).astype('uint8').copy();return Image.fromarray(out).convert('RGBA')
def planet(size,name):
 w,hh=size;x,y=np.meshgrid(np.linspace(-1.06,1.06,w),np.linspace(-1.06,1.06,hh));r2=x*x+y*y;z=np.sqrt(np.maximum(0,1-r2));mask=r2<=1;light=np.maximum(0,.50*x-.24*y+.83*z);rng=np.random.default_rng({'mars':318,'mercury':319,'venus':320}[name]);texture=np.zeros((hh,w))
 if name=='mars':
  base=np.array([163,77,48]);texture=.10*np.sin(7*x+3*np.sin(8*y))+.07*np.sin(21*y+13*x);color=(.19+.81*light[...,None])*base[None,None,:]*(1+texture[...,None]);cap=mask&(y<-.78);color[cap]=color[cap]*.35+np.array([220,211,195])*.65
 elif name=='venus':
  base=np.array([205,185,135]);texture=.05*np.sin(23*y+4*np.sin(9*x))+.035*np.cos(53*y+5*x);color=(.25+.75*light[...,None])*base[None,None,:]*(1+texture[...,None])
 else:
  base=np.array([146,148,151]);texture=.035*np.sin(x*30+y*41)
  for i in range(48):
   cx,cy=rng.uniform(-.9,.9,2);rr=rng.uniform(.02,.13);dist=np.hypot(x-cx,y-cy)/rr;texture-=.13*np.exp(-((dist-.6)/.35)**2);texture+=.10*np.exp(-((dist-1)/.16)**2)
  color=(.20+.8*light[...,None])*base[None,None,:]*(1+texture[...,None])
 rgba=np.zeros((hh,w,4),dtype='uint8');rgba[:,:,:3]=np.clip(color,0,255).astype('uint8');rgba[:,:,3]=mask.astype('uint8')*255;return Image.fromarray(rgba)
def rgba_to_mode(im,mode):
 if mode=='P':
  rgba=im.convert('RGBA');q=rgba.convert('RGB').quantize(colors=255);arr=np.array(q);arr[np.array(rgba.getchannel('A'))<128]=255;out=Image.fromarray(arr);out.putpalette((q.getpalette()+[0]*768)[:768]);out.info['transparency']=255;return out
 return im.convert(mode)

def raster(row):
 size=(int(row['ancho']),int(row['alto']));w,hh=size;name=Path(row['asset']).name;mode=row['modo']
 if name in BOOKS:return flat_card(size,*BOOKS[name],mode)
 if name in ['mars.png','mercury.png','venus.png']:return rgba_to_mode(planet(size,name.split('.')[0]),mode)
 if name=='comet.png':
  x,y=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,hh));dx=x-.28;dy=y-.65;core=np.exp(-((dx/.045)**2+(dy/.045)**2));distance=np.hypot(dx,dy);angle=(dx-dy)/math.sqrt(2);cross=(dx+dy)/math.sqrt(2);tail=np.exp(-np.maximum(angle,0)/.42)*np.exp(-(cross/(.025+.10*np.maximum(angle,0)))**2)*(angle>=0);alpha=np.clip(core+.52*tail,0,1);lum=np.clip(120+135*core,0,255);return Image.fromarray(np.stack([lum,alpha*255],axis=-1).astype('uint8'),'LA')
 if name in ['grey_gradient.png','blue_yellow_gradient.png','white_black_gradient.png']:
  colors={'grey_gradient.png':([230]*3,[42]*3),'blue_yellow_gradient.png':([49,100,167],[243,218,112]),'white_black_gradient.png':([255]*3,[0]*3)};return gradient(size,*colors[name])
 if name=='alt_calc_hidden_image.png':
  x,y=np.meshgrid(np.linspace(-2,2,w),np.linspace(-1,1,hh));arr=np.stack([.5+.5*np.sin(4*x+3*y),.5+.5*np.sin(3*y+2*x*x+2),.5+.5*np.sin(3*x-6*y+4)],axis=-1);return Image.fromarray((35+190*arr).astype('uint8'))
 if name.startswith('CoderQuaternionResponse_'):
  n=int(name.split('_')[-1].split('.')[0]);im=Image.new('RGBA',size,'#E7E9E3');dr=ImageDraw.Draw(im);dr.rectangle((10,10,w-11,hh-11),outline='#8296A2',width=2);text='\n'.join(textwrap.wrap(COMMENTS[n],width=max(20,int(w*.86/(min(42,hh*.12)*.62)))));f=fitted(text,w*.86,min(42,hh*.12));dr.multiline_text((w*.07,hh*.5),text,font=f,fill='#243B4B',anchor='lm',spacing=8);return im
 if name=='GoogleDandelin.png':
  im=Image.new('RGBA',size,'#ECEEE8');dr=ImageDraw.Draw(im);dr.rounded_rectangle((w*.07,hh*.06,w*.93,hh*.19),radius=15,fill='#D3DDE0');dr.text((w*.1,hh*.10),'Germinal Pierre Dandelin',font=font(w*.029),fill='#263D4C');items=[('Germinal Pierre Dandelin','Matemático e ingeniero · 1794–1847'),('Esferas de Dandelin','Una construcción geométrica de las secciones cónicas'),('Conos, planos y focos','Relaciones entre tangencia y elipses')]
  for i,(title,sub) in enumerate(items):
   yy=hh*(.31+i*.23);dr.text((w*.09,yy),title,font=font(w*.029),fill='#446E8A');dr.text((w*.09,yy+hh*.065),sub,font=fitted(sub,w*.82,w*.022),fill='#435761')
  return im
 if name=='Henry_As_Stick.png':
  im=Image.new('RGBA',size);dr=ImageDraw.Draw(im);cx=w*.5;dr.ellipse((w*.3,hh*.03,w*.7,hh*.19),outline='#CAD6DA',width=max(3,w//35));dr.line([(cx,hh*.2),(cx,hh*.6),(w*.2,hh*.96)],fill='#CAD6DA',width=max(3,w//35));dr.line([(cx,hh*.6),(w*.8,hh*.96)],fill='#CAD6DA',width=max(3,w//35));dr.line([(w*.1,hh*.43),(cx,hh*.3),(w*.88,hh*.39)],fill='#CAD6DA',width=max(3,w//35));return im
 if name=='Kepler2ndLaw.png':return kepler_diagram(size)
 if name=='ChessGameOfTheCentury.jpg':return chess_diagram(size)
 if name=='dartboard.png':return dartboard(size)
 if name in ['HackerNewsLogo.png','RedditLogo.png','TwitterLogo.png','YouTubeLogo.png','mathologer_logo.png','minute_physics_logo.png','3b1b_logo.png','Quanta logo.png']:return badge(size,name,mode)
 raise KeyError(name)

def badge(size,name,mode):
 w,hh=size;im=Image.new('RGBA',size);dr=ImageDraw.Draw(im)
 if name=='Quanta logo.png':
  dr.rounded_rectangle((2,2,w-3,hh-3),radius=hh*.15,fill='#354F64');dr.text((w/2,hh/2),'CUADERNO',font=font(hh*.55,True),fill='#E5ECEC',anchor='mm');return im
 if name=='3b1b_logo.png':label='TB';color='#466479'
 elif name=='minute_physics_logo.png':label='MP';color='#4C6575'
 elif name=='mathologer_logo.png':label='M';color='#63566E'
 else:label='';color='#465F73'
 if name in ['mathologer_logo.png','minute_physics_logo.png','3b1b_logo.png']:dr.ellipse((w*.08,hh*.08,w*.92,hh*.92),fill=color)
 else:dr.rounded_rectangle((w*.08,hh*.08,w*.92,hh*.92),radius=min(w,hh)*.16,fill=color)
 if label:dr.text((w*.5,hh*.5),label,font=font(min(w,hh)*(.32 if len(label)==2 else .48),True),fill='#E3E9E7',anchor='mm')
 elif name=='YouTubeLogo.png':dr.polygon([(w*.41,hh*.27),(w*.41,hh*.73),(w*.70,hh*.5)],fill='#DDE7E7')
 elif name=='TwitterLogo.png':
  dr.ellipse((w*.28,hh*.28,w*.73,hh*.64),fill='#DDE7E7');dr.polygon([(w*.38,hh*.59),(w*.3,hh*.76),(w*.56,hh*.63)],fill='#DDE7E7')
 elif name=='RedditLogo.png':
  for yy in [.3,.45,.6]:dr.line((w*.29,hh*yy,w*.72,hh*yy),fill='#DDE7E7',width=max(2,int(w*.06)))
 else:
  dr.line([(w*.25,hh*.66),(w*.43,hh*.44),(w*.56,hh*.56),(w*.76,hh*.28)],fill='#DDE7E7',width=max(2,int(w*.065)))
 return rgba_to_mode(im,mode)

def chess_diagram(size):
 w,hh=size;im=Image.new('RGB',size,'#ECE8DD');dr=ImageDraw.Draw(im);cell=min(w,hh)/8
 for r in range(8):
  for c in range(8):dr.rectangle((c*cell,r*cell,(c+1)*cell,(r+1)*cell),fill='#A4B2AE' if (r+c)%2 else '#EEE9DC')
 pieces=[(4,0,'king',False),(6,7,'king',True),(2,2,'rook',False),(3,4,'pawn',True),(5,3,'pawn',False),(0,6,'pawn',True),(7,1,'rook',False)]
 for c,r,kind,white in pieces:
  x=(c+.5)*cell;y=(r+.5)*cell;color='#F6F5ED' if white else '#293B48';edge='#293B48' if white else '#E2E7E1';dr.ellipse((x-cell*.16,y-cell*.30,x+cell*.16,y),fill=color,outline=edge,width=1);dr.polygon([(x-cell*.08,y-cell*.03),(x+cell*.08,y-cell*.03),(x+cell*.24,y+cell*.29),(x-cell*.24,y+cell*.29)],fill=color)
  if kind=='king':dr.line((x,y-cell*.4,x,y-cell*.14),fill=color,width=max(1,int(cell*.07)));dr.line((x-cell*.12,y-cell*.3,x+cell*.12,y-cell*.3),fill=color,width=max(1,int(cell*.07)))
  if kind=='rook':dr.rectangle((x-cell*.2,y-cell*.32,x+cell*.2,y-cell*.16),fill=color)
 return im

def dartboard(size):
 w,hh=size;im=Image.new('RGBA',size);dr=ImageDraw.Draw(im);cx,cy=w/2,hh/2;radius=min(w,hh)*.46
 for i in range(20):
  start=-99+i*18;end=start+18;dr.pieslice((cx-radius,cy-radius,cx+radius,cy+radius),start,end,fill='#D6D3BD' if i%2 else '#293C46')
  for outer,inner in [(.95,.89),(.59,.54)]:
   # Ring segments use polygons so inner holes stay transparent to the underlying sectors.
   pts=[(cx+radius*outer*math.cos(a),cy+radius*outer*math.sin(a)) for a in np.linspace(math.radians(start),math.radians(end),12)]+[(cx+radius*inner*math.cos(a),cy+radius*inner*math.sin(a)) for a in np.linspace(math.radians(end),math.radians(start),12)];dr.polygon(pts,fill='#AB4B49' if i%2 else '#4A7A70')
 dr.ellipse((cx-radius*.09,cy-radius*.09,cx+radius*.09,cy+radius*.09),fill='#4A7A70');dr.ellipse((cx-radius*.035,cy-radius*.035,cx+radius*.035,cy+radius*.035),fill='#AB4B49');return im

def kepler_diagram(size):
 w,hh=size;im=Image.new('RGBA',size,'#14232E');dr=ImageDraw.Draw(im);a_=w*.40;b_=hh*.31;e=math.sqrt(1-(b_/a_)**2);cx=w*.5;cy=hh*.5;focus=(cx-a_*e,cy)
 def ecc(M):
  E=M
  for _ in range(15):E-=(E-e*math.sin(E)-M)/(1-e*math.cos(E))
  return E
 areas=[]
 for M0,color in [(0.10,'#DAB36D'),(2.25,'#73ADB4')]:
  M1=M0+.62;points=[(cx-a_*math.cos(ecc(M)),cy-b_*math.sin(ecc(M))) for M in np.linspace(M0,M1,160)];dr.polygon([focus]+points+[focus],fill=color);q=np.array([focus]+points+[focus]);area=abs(np.dot(q[:,0],np.roll(q[:,1],-1))-np.dot(q[:,1],np.roll(q[:,0],-1)))/2;assert math.isclose(area,.5*a_*b_*(M1-M0),rel_tol=.001);areas.append(area)
 dr.ellipse((cx-a_,cy-b_,cx+a_,cy+b_),outline='#CAD9DD',width=max(2,w//450));rr=hh*.025;dr.ellipse((focus[0]-rr,focus[1]-rr,focus[0]+rr,focus[1]+rr),fill='#F2D08A');assert math.isclose(areas[0],areas[1],rel_tol=.001);return im

SPECS={'raster_images/GerminalDandelin.jpg': {'title': 'File:Germinal Pierre Dandelin (1794-1847).jpg', 'extend': True, 'person': 'Germinal Pierre Dandelin'}, 'raster_images/de_Broglie.png': {'title': 'File:Louis de Broglie.jpg', 'person': 'Louis de Broglie'}, 'raster_images/Kant.jpg': {'title': 'File:Kant gemaelde 3.jpg', 'person': 'Immanuel Kant'}, 'raster_images/Lewis_Richardson.png': {'title': 'File:Lewis Fry Richardson.png', 'person': 'Lewis Fry Richardson'}, 'raster_images/Lord Kelvin.jpg': {'title': 'File:Lord Kelvin photograph.jpg', 'person': 'William Thomson\nLord Kelvin'}, 'raster_images/Macfarlane Alexander.jpg': {'title': 'File:Macfarlane Alexander math.jpg', 'person': 'Alexander Macfarlane', 'crop':[0,0,1,.9], 'note':'Retrato histórico libre; se retira el texto de pie del escaneo mediante un recorte.'}, 'raster_images/Oliver Heaviside.jpg': {'title': 'File:Oliver Heaviside2.jpg', 'person': 'Oliver Heaviside'}, 'raster_images/Peter Tait.jpg': {'title': 'File:Peter Guthrie Tait.jpg', 'person': 'Peter Guthrie Tait'}, 'raster_images/Robert Ball.jpg': {'title': 'File:Sir Robert Stawell Ball (engraved portrait).png', 'person': 'Robert Stawell Ball'}, 'raster_images/Geoffrey_Taylor.jpg': {'card': 'G. I. Taylor', 'note': 'Tarjeta neutra: la foto de Wikipedia es local y no libre (wikipedia/en); no se encontró un retrato adecuado con licencia admisible en Commons. No se genera ninguna persona.'}, 'raster_images/Einstein.png': {'title': 'File:Einstein 1921 by F Schmutzer - restoration.jpg', 'person': 'Albert Einstein'}, 'raster_images/Feynman_Los_Alamos.jpg': {'title': 'File:Richard Feynman Los Alamos ID badge (cropped).jpg', 'person': 'Richard Feynman'}, 'raster_images/Feynman_Woods.jpg': {'title': 'File:RichardFeynman-PaineMansionWoods1984 copyrightTamikoThiel bw.jpg', 'person': 'Richard Feynman'}, 'raster_images/George_Stokes.jpg': {'title': 'File:George Gabriel Stokes 1875.jpg', 'person': 'George Gabriel Stokes'}, 'raster_images/Hermann_von_Helmholtz.jpg': {'title': 'File:Hermann von Helmholtz.jpg', 'person': 'Hermann von Helmholtz'}, 'raster_images/John_Wallis.jpg': {'title': 'File:John Wallis by Sir Godfrey Kneller, Bt.jpg', 'person': 'John Wallis'}, 'raster_images/Leonhard_Euler.jpg': {'title': 'File:Leonhard Euler - Jakob Emanuel Handmann (Kunstmuseum Basel).jpg', 'person': 'Leonhard Euler'}, 'raster_images/MonaLisa.jpg': {'title': 'File:Mona Lisa, by Leonardo da Vinci, from C2RMF retouched.jpg'}, 'raster_images/Pietro_Mengoli.gif': {'title': 'File:Pietro Mengoli.gif', 'person': 'Pietro Mengoli'}, 'raster_images/Heisenberg.jpg': {'title': 'File:Heisenberg,Werner 1926.jpeg', 'person': 'Werner Heisenberg'}, 'raster_images/BroomBridgePlaque.jpg': {'title': 'File:William Rowan Hamilton Plaque - geograph.org.uk - 347941.jpg'}, 'raster_images/DandelionSphere.jpg': {'title': 'File:Dandelion clock.jpg'}, 'svg_images/euler-signature.svg': {'title': "File:Euler's signature.svg"}}

def scene_audit(row):
 file=ROOT/'_work'/(row['ejemplo']+'.py');stem=Path(row['asset']).stem
 if not file.exists():return {'scene':row['ejemplo'],'matches':[],'note':'No se encontró el ejemplo indicado.'}
 lines=file.read_text().splitlines();hits=[]
 for i,l in enumerate(lines):
  if stem.lower() in l.lower() or stem.startswith('Dice-') and 'Dice-' in l:hits.append({'line':i+1,'context':'\n'.join(lines[max(0,i-1):i+5])})
 return {'scene':str(file.relative_to(ROOT)),'matches':hits[:8],'indirect_name':stem.replace('_',' ') if not hits else ''}
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
 counts={s:sum(r.get('delivery_state')==s for r in records.values()) for s in ['hecha','ya_existe','entregada_IA','saltada']};pending=[r for r in ROWS if r['asset'] not in records];n=pending[0] if pending else None
 lines=['# Progreso de assets 2018','','## AHORA',f'Completados: {len(records)}/{len(ROWS)}; {len(pending)} pendientes.',f'Estados: {counts}.',f"Sigue: {n['n']+' '+n['asset'] if n else 'entrega completa; revisar hoja y comprobaciones'}.",f"Comando: `python _lib/assets/generated/replacements/assets2018/make_assets_2018.py --priority {n['prioridad'] if n else 'P3'}`.",'','| # | Prioridad | Asset | Estado | Vía | Fuente | Licencia | Nota |','|---:|---|---|---|---|---|---|---|']
 for row in ROWS:
  r=records.get(row['asset'],{});lines.append('| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in [row['n'],row['prioridad'],row['asset'],r.get('delivery_state','pendiente'),r.get('via',row['via']),r.get('page_url',''),r.get('license',''),r.get('note','')])+' |')
 lines+=['','## Resumen',str(counts)+f'; {len(pending)} pendientes.','','## Atribuciones']
 lines += [f"- {asset}: {r.get('author')}; {r.get('license')}; {r.get('page_url')}." for asset,r in records.items() if r.get('license','').startswith(('CC BY','MIT'))]
 lines+=['','## Para revisar','No se han renderizado escenas. No se modifican fotogramas, diferidas ni assets fuera de esta lista. Sin IA. Los planetas son ilustraciones esquemáticas por código, no mapas científicos ni fotografías de NASA. Los comentarios de foro son inventados; el tablero de ajedrez es ilustrativo, no una reconstrucción de la partida histórica. Las áreas de Kepler se calculan con intervalos iguales de anomalía media.']
 (AUDIT/'PROGRESO_2018.md').write_text('\n'.join(lines)+'\n')

def review(records):
 out=Image.new('RGB',(1500,math.ceil(len(ROWS)/6)*185),'#E3E7E3');dr=ImageDraw.Draw(out)
 for i,row in enumerate(ROWS):
  x=i%6*250;y=i//6*185;dr.text((x+4,y+4),row['n']+' '+Path(row['asset']).name,fill='#283F4E');r=records.get(row['asset'])
  if not r:continue
  p=ASSETS/row['asset']
  try:
   if p.suffix=='.svg':im=Image.open(io.BytesIO(subprocess.check_output(['rsvg-convert','--keep-aspect-ratio','-w','230','-h','140',str(p)],stderr=subprocess.DEVNULL))).convert('RGBA')
   else:im=Image.open(p).convert('RGBA')
   im=ImageOps.contain(im,(230,140));bg=Image.new('RGBA',im.size,'#1E303D' if row['modo']=='LA' or Path(row['asset']).name=='Henry_As_Stick.png' else 'white');bg.alpha_composite(im);out.paste(bg.convert('RGB'),(x+(250-im.width)//2,y+24))
  except Exception as e:dr.text((x+5,y+65),'Sin miniatura: '+str(e)[:20],fill='red')
  dr.text((x+4,y+168),r['delivery_state'],fill='#386452')
 out.save(AUDIT/'REVISION_2018.png')

def validate(row,p):
 if row['modo']=='SVG':
  root=ET.parse(p).getroot();assert root.get('viewBox')==(row['alto'] or None);paths=root.findall('.//{http://www.w3.org/2000/svg}path')
  if p.stem=='traffic_light':assert len(paths)==4
  if p.stem=='falcon_heavy':assert len(paths)==12
 else:
  with Image.open(p) as im:assert im.size==(int(row['ancho']),int(row['alto'])) and im.mode==row['modo']

def generate(row,spec,dest,rec):
 if spec.get('title'):return download(row,spec,dest,rec)
 if spec.get('card'):im=flat_card((int(row['ancho']),int(row['alto'])),spec['card'],mode=row['modo']);rec['note']=spec.get('note','Tarjeta neutra: no se obtuvo una fotografía libre adecuada. No se genera una persona.');d.save(im,dest,row['modo']);return
 if row['modo']=='SVG':atomic(dest,svg(row,icon(dest.stem)).encode());return
 im=raster(row);d.save(im,dest,row['modo'])
 if dest.stem in ['mars','mercury','venus']:rec['note']='Planeta esquemático propio: iluminación y textura procedurales, no es una fotografía ni un mapa científico.'
 if dest.stem=='3b1b_logo':rec['note']='Emblema TB propio; no se encontró un generador anterior reutilizable de TB en generated/replacements; no se copia el logo de 3b1b.'

def commons_html(title):
 """Verify file-specific license templates from the public page, not site footer.
 Wikimedia APIs returned 503 during this task; the normal public file pages work.
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
 return {'commons_title':title,'source_author_credit':(author if names else full_credit)[:1500],'source_credit':credit,'source_description':description,'page_url':page_url,'file_url':original['href'].split('?')[0],'license':lic,'license_url':lic_url,'author':author,'license_evidence':'Ficha pública de Commons consultada en esta ejecución; plantilla licensetpl_short específica del archivo, no licencia del pie del sitio. API indisponible (503).','evidence_sha256':hashlib.sha256(raw).hexdigest()}

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
  for folder in ['downloads','assets2019','assets2020']:
   old=ROOT/'_tools/.cache'/folder/'originales'/name
   if old.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,target);break
 if not target.exists():atomic(target,d.http(url))
 info.update(source_sha256=sha(target),source_size_bytes=target.stat().st_size,download_size_bytes=target.stat().st_size)
 return target

def signature(row,raw):
 import svgelements as se
 source=se.SVG.parse(str(raw));paths=[]
 for element in source.elements():
  if isinstance(element,se.Path):
   p=se.Path(element);p.reify()
   if len(p):paths.append(p)
 if not paths:raise ValueError('La firma verificada no contiene paths')
 bounds=[p.bbox() for p in paths];x0=min(b[0] for b in bounds);y0=min(b[1] for b in bounds);x1=max(b[2] for b in bounds);y1=max(b[3] for b in bounds);w,hh=map(float,row['alto'].split()[2:]);scale=min(w*.94/(x1-x0),hh*.82/(y1-y0));tx=(w-(x1-x0)*scale)/2-x0*scale;ty=(hh-(y1-y0)*scale)/2-y0*scale
 body=''.join(path(p.d(),'#283A49').replace(' fill="#283A49"','') for p in paths);return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{row["alto"]}"><g transform="translate({tx} {ty}) scale({scale})">{body}</g></svg>'.encode()

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
 lines=['# Atribuciones de los assets de 2018','','Los 58 reemplazos propios por código se ofrecen como CC0. Las 22 descargas conservan sus licencias individuales; no se presentan como obra propia. Las adaptaciones de imágenes CC BY-SA siguen bajo la licencia indicada.','']
 for row in ROWS:
  r=records.get(row['asset'],{})
  if r.get('via')!='descargar':continue
  if r.get('status')=='skipped':r=r.get('retained_provenance',{})
  if not r:continue
  lines += [f"## {row['n']}. `{row['asset']}`",'',f"- Autor/crédito: {r.get('author','')}",f"- Licencia: [{r.get('license','')}]({r.get('license_url','')})",f"- Fuente: {r.get('page_url','')}",f"- Cambios: {r.get('changes','')}"]
  if r.get('source_credit'):lines += [f"- Procedencia indicada por Commons: {r['source_credit']}"]
  lines+=['']
 lines+=['## Fuentes tipográficas','','Se utilizan únicamente las fuentes libres ya presentes en `_lib/assets/fonts/`: JetBrains Mono y, cuando lo requiere una utilidad compartida, CMU Serif. Sus avisos están incluidos en esa carpeta. No se distribuyen portadas, emblemas ni capturas de terceros.','', '## Verificación de fuentes','','La API de Wikimedia devolvió 503 durante esta tarea. El generador consulta en vivo las fichas públicas de Commons y verifica sus plantillas `licensetpl_short` específicas del archivo. No interpreta la licencia del pie de página como licencia de la imagen. La evidencia HTML y los originales descargados se guardan en la caché ignorada; cada registro conserva sus hashes.']
 (HERE/'ATTRIBUTIONS_2018.md').write_text('\n'.join(lines)+'\n')


def run(args):
 if (AUDIT/'assets2018.csv').exists() and sha(AUDIT/'assets2018.csv')!=CSV_SHA:raise RuntimeError('assets2018.csv cambió: revisar la lista antes de continuar.')
 CACHE.mkdir(parents=True,exist_ok=True);(CACHE/'.gitignore').write_text('*\n!.gitignore\n');records=json.loads(SOURCE.read_text()) if SOURCE.exists() else {};progress(records);selected=[r for r in ROWS if (not args.only or any(v in [r['n'],r['asset'],Path(r['asset']).name] for v in args.only)) and (not args.priority or r['prioridad']==args.priority)]
 global COMMONS
 titles={SPECS[r['asset']]['title'] for r in selected if SPECS.get(r['asset'],{}).get('title')}
 try:COMMONS=verify_pages(titles)
 except Exception as e:COMMONS={};print('No se pudo verificar Commons:',e,flush=True)
 for row in selected:
  asset=row['asset'];p=ASSETS/asset;old=records.get(asset);spec=SPECS.get(asset,{});print(f"[{row['n']}/{len(ROWS)}] {asset}",flush=True)
  prev=existing(row)
  if prev:
   records[asset]=prev|{'delivery_state':'ya_existe','note':'Reemplazo previo verificado por coincidencia de hash; no se modifica.'};d.atomic_json(SOURCE,records);progress(records);continue
  if old and old.get('recipe_version')==VERSION and p.exists() and sha(p)==old.get('sha256') and not spec.get('title') and not args.force:
   if spec.get('card'):old['subject']='Tarjeta neutra: '+spec['card']
   if p.stem=='3b1b_logo':old['subject']='Emblema TB propio'
   records[asset]=old;d.atomic_json(SOURCE,records);progress(records);continue
  rec={'asset':asset,'name':p.name,'subject':row['que_crear'] or row['nota'],'author':'propio (código)','license':'CC0','license_url':CC0,'page_url':'','status':'skipped','changes':'Creación independiente desde cero, sin usar el archivo de Grant como entrada.','via':'código','note':'','recipe_version':VERSION,'verified_at':datetime.now(timezone.utc).isoformat(),'scene_review':scene_audit(row),'old_sha256':None if args.force else (old or {}).get('sha256')}
  if spec.get('person'):rec['subject']='Retrato de '+spec['person'].replace('\n',' ')
  elif spec.get('card'):rec['subject']='Tarjeta neutra: '+spec['card']
  elif p.stem=='3b1b_logo':rec['subject']='Emblema TB propio'
  elif p.stem=='euler-signature':rec['subject']='Firma histórica de Leonhard Euler'
  if spec.get('title'):rec.update(author='',license='',license_url='',via='descargar',previous_download=bool(old and old.get('via')=='descargar'))
  try:
   backup=CACHE/'originales'/asset
   if p.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
   generate(row,spec,p,rec);validate(row,p);rec.update(status=rec['status'] if rec['status'] in ['replaced','kept'] else 'generated',delivery_state='hecha',sha256=sha(p),final_size_bytes=p.stat().st_size,note=rec['note'] or 'Reemplazo propio; uso de la escena y tamaño/modo o lienzo SVG revisados.')
  except Exception as e:
   rec.update(status='skipped',delivery_state='saltada',note=str(e));print('  SALTADA',e,flush=True)
   if old and p.exists() and old.get('sha256')==sha(p):rec['retained_provenance']=old
  if rec.get('author')=='Unknown authorUnknown author':rec['author']='Autor desconocido (Commons)'
  records[asset]=rec;d.atomic_json(SOURCE,records);progress(records)
 review(records)
 write_attributions(records)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',nargs='+');ap.add_argument('--priority',choices=['P2','P3']);ap.add_argument('--force',action='store_true');run(ap.parse_args())
