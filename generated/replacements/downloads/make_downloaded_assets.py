"""59 real assets: verified free sources, cache, reversible replacement and audit.

python make_downloaded_assets.py [--only NUMBER ...] [--force] [--sources-only]
Requires Pillow and NumPy; ImageMagick for NASA EXR and the US SVG map.
Licenses are checked LIVE on every run, even when final files/cache exist.
No --no-verify switch: a network/license failure never authorizes redistribution.
Only assets explicitly listed below are written; scenes/setup are never modified.
Final assets <=10 MiB are recommended for the repo, larger originals stay cached.
"""
from __future__ import annotations
import argparse,csv,hashlib,html,io,json,math,re,shutil,subprocess,sys,time
import urllib.error,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageOps
# Known USGS JPEG is ~228 MP; JPEG draft decoding reduces it before loading.
Image.MAX_IMAGE_PIXELS=300_000_000

HERE=Path(__file__).resolve().parent
ASSETS=HERE.parents[2]
ROOT=ASSETS.parents[1]
AUDIT=ROOT/'_tools/assets_licencias/codex'
CACHE=ROOT/'_tools/.cache/downloads'
SOURCES=HERE/'downloads_sources.json'
UA={'User-Agent':'ManimLearningAssetFetcher/1.0 (educational open-source asset audit)'}
API='https://commons.wikimedia.org/w/api.php'
ALLOWED=re.compile(r'^(public domain|pd[- ].*|cc0.*|cc[- ]by([- ]sa)?[- ]\d(?:\.\d)?(?: [a-z]{2,3})?|no restrictions)$',re.I)
PD_URL='https://creativecommons.org/publicdomain/mark/1.0/'
NASA_POLICY='https://www.nasa.gov/nasa-brand-center/images-and-media/'
MANIFEST = {'1': {'file_url': 'https://www.solarsystemscope.com/textures/download/8k_sun.jpg',
       'page_url': 'https://www.solarsystemscope.com/textures/',
       'author': 'Solar System Scope / INOVE; textura visual basada en imágenes NASA',
       'license': 'CC BY 4.0',
       'license_url': 'https://creativecommons.org/licenses/by/4.0/',
       'policy_url': 'https://www.solarsystemscope.com/textures/',
       'policy_kind': 'sss',
       'process': 'texture',
       'changes': 'Mapa equirrectangular 2:1 real/fuente documentada, reescalado y convertido a JPEG RGB al '
                  'tamaño exacto.',
       'note': 'Textura visual CC BY 4.0: no se presenta como mapa científico medido de toda la fotosfera.',
       'usage_matches': ['_work/_2025/cosmic_distance/paralax/NearbyStars.py:33:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/paralax/ParalaxMeasurmentFromEarth.py:79:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/paralax/ShowConstellationsDuringOrbit.py:23:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/paralax/ParalxInSolarSystem.py:23:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/RadarToVenus.py:49:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/EarthAndVenus.py:29:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/LightAcrossEarthsOrbit.py:40:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/LightFromSunToEarth.py:52:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/ShowCreationOfAllOrbits.py:57:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/KeplersMethod.py:32:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/HighlightJupiterOrbit.py:54:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/HighlightMarsOrbit.py:54:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/HighlightEarthOrbit.py:54:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/NearestPlanets.py:54:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/EarthAroundSun.py:17:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/HowManyEarthsInsideSun.py:17:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/DistanceToSun.py:39:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/planets/PenumbraAndUmbra.py:20:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/part2/DemonstrateAnArcSecond.py:14:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                         '_work/_2025/cosmic_distance/supplements2/DemonstrateAnArcSecond.py:14:    sun = '
                         'TexturedSurface(Sphere(radius=radius), "SunTexture")'],
       'scene_note': '20 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                     'posiciones adicionales fijas detectadas.'},
 '2': {'file_url': 'https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_poles_4k.tif',
       'page_url': 'https://svs.gsfc.nasa.gov/4720/',
       'author': 'NASA/GSFC/SVS, Ernie Wright; LRO/LROC/LOLA',
       'license': 'Public domain',
       'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
       'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
       'policy_kind': 'nasa',
       'process': 'texture',
       'changes': 'Mapa equirrectangular 2:1 real/fuente documentada, reescalado y convertido a JPEG RGB al '
                  'tamaño exacto.',
       'usage_matches': ['_work/_2025/cosmic_distance/paralax/ParalaxMeasurmentFromEarth.py:66:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/RadarToVenus.py:36:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LightAcrossEarthsOrbit.py:27:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LightAcrossEarth.py:27:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LightFromSunToEarth.py:39:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LightFromEarthToMoon.py:27:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/PhasesOfTheMoon.py:4:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/DistanceToSun.py:26:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LineOfSight.py:23:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LuarEclipse.py:23:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")',
                         '_work/_2025/cosmic_distance/planets/LuarEclipse.py:217:            '
                         '"RedMoonTexture", "DarkMoonTexture",',
                         '_work/_2025/cosmic_distance/planets/PerspectivesOnEarth.py:23:    moon = '
                         'TexturedSurface(Sphere(radius=radius, resolution=resolution), "MoonTexture", '
                         '"DarkMoonTexture")'],
       'scene_note': 'Esfera con MoonTexture y DarkMoonTexture. Solo MoonTexture está en esta lista; revisar '
                     'derivación de DarkMoonTexture tras instalar, sin modificarla aquí.'},
 '3': {'file_url': 'https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004851/hiptyc_2020_8k.exr',
       'page_url': 'https://svs.gsfc.nasa.gov/4851/',
       'author': 'NASA/GSFC/SVS, Ernie Wright; catálogos Hipparcos y Tycho',
       'license': 'Public domain',
       'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
       'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
       'policy_kind': 'nasa',
       'process': 'texture',
       'changes': 'Mapa equirrectangular 2:1 real/fuente documentada, reescalado y convertido a JPEG RGB al '
                  'tamaño exacto.',
       'usage_matches': ['_work/_2025/cosmic_distance/paralax/NearbyStars.py:49:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/paralax/ParalaxMeasurmentFromEarth.py:95:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/paralax/ShowConstellationsDuringOrbit.py:39:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/paralax/ParalxInSolarSystem.py:39:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/planets/RadarToVenus.py:65:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/planets/EarthAndVenus.py:45:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/planets/ShowCreationOfAllOrbits.py:79:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/planets/KeplersMethod.py:54:        '
                         'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                         '_work/_2025/cosmic_distance/planets/HighlightJupiterOrbit.py:82:        '
                         'celestial_sphere = TexturedSurface(Sphere(radius=200), "hiptyc_2020_8k")',
                         '_work/_2025/cosmic_distance/planets/HighlightMarsOrbit.py:82:        '
                         'celestial_sphere = TexturedSurface(Sphere(radius=200), "hiptyc_2020_8k")',
                         '_work/_2025/cosmic_distance/planets/HighlightEarthOrbit.py:82:        '
                         'celestial_sphere = TexturedSurface(Sphere(radius=200), "hiptyc_2020_8k")',
                         '_work/_2025/cosmic_distance/planets/NearestPlanets.py:82:        celestial_sphere '
                         '= TexturedSurface(Sphere(radius=200), "hiptyc_2020_8k")'],
       'scene_note': '12 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                     'posiciones adicionales fijas detectadas.'},
 '4': {'file_url': 'https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004851/constellation_figures_4k.tif',
       'page_url': 'https://svs.gsfc.nasa.gov/4851/',
       'author': 'NASA/GSFC/SVS, Ernie Wright; figuras IAU',
       'license': 'Public domain',
       'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
       'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
       'policy_kind': 'nasa',
       'process': 'alpha_lines',
       'changes': 'TIFF gris 2:1; intensidad convertida a alfa, líneas blancas con fondo transparente.',
       'usage_matches': ['_work/_2025/cosmic_distance/paralax/NearbyStars.py:50:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/paralax/ParalaxMeasurmentFromEarth.py:96:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/paralax/ShowConstellationsDuringOrbit.py:40:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/paralax/ParalxInSolarSystem.py:40:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/planets/RadarToVenus.py:66:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/planets/EarthAndVenus.py:46:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/planets/ShowCreationOfAllOrbits.py:80:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),',
                         '_work/_2025/cosmic_distance/planets/KeplersMethod.py:55:        '
                         'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                         '"constellation_figures"),'],
       'scene_note': '8 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                     'posiciones adicionales fijas detectadas.'},
 '5': {'file_url': 'https://sdo.gsfc.nasa.gov/assets/img/browse/2020/01/16/20200116_171500_4096_HMIIC.jpg',
       'page_url': 'https://sdo.gsfc.nasa.gov/data/',
       'author': 'NASA/SDO; equipos AIA, EVE y HMI, observación 2020-01-16 17:15 UTC',
       'license': 'Public domain',
       'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
       'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
       'policy_kind': 'nasa',
       'process': 'sun',
       'changes': 'Misma observación solar fechada; recorte del disco, centrado y reescala. En PNG se aplica '
                  'alfa circular; en TIFF fondo negro.',
       'usage_matches': ['_work/_2025/cosmic_distance/paralax/TransitOfVenusMiddle.py:11:            im_path '
                         '= Path(path.parent.parent, "Paul Animations/6. Transit Of Venus/New Transit of '
                         'Venus scenes/JustSun.tif")',
                         '_work/_2025/cosmic_distance/paralax/TransitOfVenusSlightlyHigher.py:11:            '
                         'im_path = Path(path.parent.parent, "Paul Animations/6. Transit Of Venus/New '
                         'Transit of Venus scenes/JustSun.tif")',
                         '_work/_2025/cosmic_distance/paralax/TransitOfVenusHigher.py:11:            im_path '
                         '= Path(path.parent.parent, "Paul Animations/6. Transit Of Venus/New Transit of '
                         'Venus scenes/JustSun.tif")',
                         '_work/_2025/cosmic_distance/paralax/TransitOfVenus.py:11:            im_path = '
                         'Path(path.parent.parent, "Paul Animations/6. Transit Of Venus/New Transit of Venus '
                         'scenes/JustSun.tif")',
                         '_work/_2025/cosmic_distance/part2/SunInTheSky.py:9:        pure_sun = '
                         "ImageMobject(str(Path(base_path, 'Paul Animations/6. Transit Of Venus/New Transit "
                         "of Venus scenes/JustSunBackgroundRemoved.png')))",
                         '_work/_2025/cosmic_distance/part2/SunInTheSky.py:10:        clean_sun = '
                         "ImageMobject(str(Path(base_path, 'Paul Animations/6. Transit Of Venus/New Transit "
                         "of Venus scenes/JustSun.tif')))",
                         '_work/_2025/cosmic_distance/supplements2/SunInTheSky.py:9:        pure_sun = '
                         "ImageMobject(str(Path(base_path, 'Paul Animations/6. Transit Of Venus/New Transit "
                         "of Venus scenes/JustSunBackgroundRemoved.png')))",
                         '_work/_2025/cosmic_distance/supplements2/SunInTheSky.py:10:        clean_sun = '
                         "ImageMobject(str(Path(base_path, 'Paul Animations/6. Transit Of Venus/New Transit "
                         "of Venus scenes/JustSun.tif')))"],
       'scene_note': '8 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                     'posiciones adicionales fijas detectadas.'},
 '6': {'title': 'File:NGC 4414 (NASA-med).jpg',
       'process': 'contain',
       'usage_matches': ['_work/_2025/cosmic_distance/part2/LineToDistantStar.py:6:        # CAMBIO: '
                         'GalaxyStill.png vivía junto a la salida de video de Grant; ahora hay una galaxia '
                         'de relleno junto a este archivo.',
                         '_work/_2025/cosmic_distance/part2/LineToDistantStar.py:7:        path = '
                         'os.path.join(os.path.dirname(__file__), "GalaxyStill.png")',
                         '_work/_2025/cosmic_distance/supplements2/LineToDistantStar.py:6:        # CAMBIO: '
                         'GalaxyStill.png vivía junto a la salida de video de Grant; ahora hay una galaxia '
                         'de relleno junto a este archivo.',
                         '_work/_2025/cosmic_distance/supplements2/LineToDistantStar.py:7:        path = '
                         'os.path.join(os.path.dirname(__file__), "GalaxyStill.png")'],
       'scene_note': 'LineToDistantStar: línea entre (-.08,-.74) y (.6,1.54), ambos dentro de la galaxia '
                     'ilustrativa. Fuente NGC4414, no es una fotografía de la Vía Láctea; revisar contexto '
                     'del Sol con el coordinador.'},
 '7': {'title': 'File:Jupiter System Montage - GPN-2000-000451.jpg',
       'process': 'contain',
       'scene_note': 'LabelIo: la imagen no se añade a la escena (self.add(im) comentado); montaje '
                     'ilustrativo sin correspondencia con la elipse animada.',
       'usage_matches': ['_work/_2025/cosmic_distance/part2/LabelIo.py:6:        # CAMBIO: JovianSystem.png '
                         'vivía en el Dropbox de Grant; ahora hay una imagen de relleno junto a este '
                         'archivo.',
                         '_work/_2025/cosmic_distance/part2/LabelIo.py:7:        im = '
                         "ImageMobject(str(Path(__file__).parent / 'JovianSystem.png'))",
                         '_work/_2025/cosmic_distance/supplements2/LabelIo.py:6:        # CAMBIO: '
                         'JovianSystem.png vivía en el Dropbox de Grant; ahora hay una imagen de relleno '
                         'junto a este archivo.',
                         '_work/_2025/cosmic_distance/supplements2/LabelIo.py:7:        im = '
                         "ImageMobject(str(Path(__file__).parent / 'JovianSystem.png'))"]},
 '8': {'file_url': 'https://sdo.gsfc.nasa.gov/assets/img/browse/2020/01/16/20200116_171500_4096_HMIIC.jpg',
       'page_url': 'https://sdo.gsfc.nasa.gov/data/',
       'author': 'NASA/SDO; equipos AIA, EVE y HMI, observación 2020-01-16 17:15 UTC',
       'license': 'Public domain',
       'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
       'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
       'policy_kind': 'nasa',
       'process': 'sun',
       'changes': 'Misma observación solar fechada; recorte del disco, centrado y reescala. En PNG se aplica '
                  'alfa circular; en TIFF fondo negro.',
       'usage_matches': ['_work/_2025/cosmic_distance/part2/SunInTheSky.py:9:        pure_sun = '
                         "ImageMobject(str(Path(base_path, 'Paul Animations/6. Transit Of Venus/New Transit "
                         "of Venus scenes/JustSunBackgroundRemoved.png')))",
                         '_work/_2025/cosmic_distance/supplements2/SunInTheSky.py:9:        pure_sun = '
                         "ImageMobject(str(Path(base_path, 'Paul Animations/6. Transit Of Venus/New Transit "
                         "of Venus scenes/JustSunBackgroundRemoved.png')))"],
       'scene_note': '2 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                     'posiciones adicionales fijas detectadas.'},
 '9': {'file_url': 'https://astrogeology.usgs.gov/ckan/dataset/7131d503-cdc9-45a5-8f83-5126c0fd397e/resource/5ea881c6-01b3-41fa-a7af-42d2131b54f1/download/mars_viking_mdim21_clrmosaic_1km.jpg',
       'page_url': 'https://astrogeology.usgs.gov/search/map/mars_viking_colorized_global_mosaic_232m',
       'author': 'NASA Ames / USGS Astrogeology; Viking MDIM 2.1',
       'license': 'Public domain',
       'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
       'policy_url': 'https://astrogeology.usgs.gov/search/map/mars_viking_colorized_global_mosaic_232m',
       'policy_kind': 'usgs',
       'process': 'texture',
       'changes': 'Mapa equirrectangular 2:1 real/fuente documentada, reescalado y convertido a JPEG RGB al '
                  'tamaño exacto.',
       'usage_matches': [],
       'scene_note': '0 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                     'posiciones adicionales fijas detectadas.'},
 '10': {'title': 'File:Blank US Map (states only).svg',
        'process': 'states',
        'changes': 'SVG CC0 recoloreado por backtracking con cuatro colores; validación de todas las '
                   'fronteras estatales declaradas, raster a 1200×800.',
        'usage_matches': ['_work/_2026/cross_entropy/entropy/RandomNoiseIsIncompressible.py:689:            '
                          '"US_color_graph",',
                          '_work/_2025/grover/runtime/NPProblemExamples.py:8:            '
                          'ImageMobject("US_color_graph"),'],
        'scene_note': '2 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '11': {'title': 'File:Lunar eclipse composite.jpg',
        'process': 'eclipse',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/ShowFourLittleCircles.py:7:        '
                          'image_path = Path(__file__).parent / "LunarEclipseComposite.jpg"'],
        'scene_note': 'ShowFourLittleCircles: círculo en (-1,-.167), radio .62; cuatro centros en retícula '
                      '4×1 girada 8 grados, centrada (1.503,-.043).',
        'changes': 'Fases fotográficas reales del eclipse de 2019 recortadas y recompuestas sobre fondo '
                   'negro para coincidir con los cinco círculos fijos de ShowFourLittleCircles. No '
                   'representa trayectoria física ni posiciones simultáneas.',
        'note': 'Montaje derivado de fases observadas, recompuesto para las anotaciones de la escena; CC BY '
                '4.0 conservada.'},
 '12': {'file_url': 'https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57752/land_shallow_topo_8192.tif',
        'page_url': 'https://visibleearth.nasa.gov/images/57752/blue-marble-land-surface-shallow-water-and-shaded-topography',
        'author': 'NASA GSFC / Reto Stöckli, Robert Simmon, MODIS, USGS EROS',
        'license': 'Public domain',
        'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
        'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
        'policy_kind': 'nasa',
        'process': 'nile',
        'changes': 'Reproyección afín georreferenciada del mapa NASA. Alejandría (29.9187 E,31.2001 N) y '
                   'Asuán/Syene (32.8998 E,24.0889 N) alineadas a los dos puntos fijos de NileLabels; '
                   'orientación rotada.',
        'scene_note': 'NileLabels: Alejandría (-5.61,-0.8), Syene (2.78,1.12), FRAME 128/9×8; verificar '
                      'alineación sin cambiar escena.',
        'note': 'Mapa global recortado y girado para rótulos fijos; resolución local limitada por el mapa '
                'fuente.',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/NileLabels.py:6:        # CAMBIO: '
                          'Nile.png vivía junto a la salida de video de Grant; ahora hay un mapa de relleno '
                          'junto a este archivo.',
                          '_work/_2025/cosmic_distance/supplements/NileLabels.py:7:        image_path = '
                          'Path(__file__).parent / "Nile.png"']},
 '13': {'title': 'File:Caspar Netscher - Christiaan Huygens, the astronomer, 1671.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:75:            '
                          'ImageMobject("ChristiaanHuygens"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'crop': [0.12, 0.03, 0.88, 0.75]},
 '14': {'title': 'File:Nikolaus Kopernikus.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/CopernicusConclusions.py:3:class '
                          'CopernicusConclusions(InteractiveScene):',
                          '_work/_2025/cosmic_distance/supplements/CopernicusConclusions.py:6:        title '
                          '= TexText("Copernicus", font_size=48)',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:38:            '
                          '("Copernicus", 1473, 1543, 0.2, RED_A),',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:70:            '
                          'ImageMobject("Copernicus"),'],
        'scene_note': '4 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '15': {'title': 'File:Edmond Halley 072.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:73:            '
                          'ImageMobject("EdmondHalley"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '16': {'title': 'File:Studio portrait photograph of Edwin Powell Hubble (cropped).JPG',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:78:            '
                          'ImageMobject("EdwinHubble"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '17': {'title': 'File:Eratosthenes.jpg',
        'usage_matches': ['_work/_2024/antp/main/GiantSieve.py:4:class '
                          'SieveOfEratosthenes(InteractiveScene):',
                          '_work/_2024/antp/main/GiantSieve.py:58:class GiantSieve(SieveOfEratosthenes):',
                          '_work/_2024/antp/main/SieveOfEratosthenes.py:4:class '
                          'SieveOfEratosthenes(InteractiveScene):',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:35:            '
                          '("Eratosthenes", -276, -194, 0.2, BLUE_B),',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:67:            '
                          'ImageMobject("Eratosthenes"),'],
        'scene_note': '5 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '18': {'title': 'File:Friedrich Wilhelm Bessel, Kreidezeichnung von Heinrich Joachim Herterich,1825.png',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:76:            '
                          'ImageMobject("FriedrichBessel"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '19': {'title': 'File:Head of Aristotle.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:66:            '
                          'ImageMobject("Head_of_Aristotle"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '20': {'title': 'File:Henrietta Swan Leavitt.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:77:            '
                          'ImageMobject("HenriettaLeavitt"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '21': {'title': 'File:Portrait of Captain James Cook (4671407).jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:72:            '
                          'ImageMobject("JamesCook"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'crop': [0.16, 0.04, 0.91, 0.75]},
 '22': {'title': 'File:Johannes Kepler, portrait by Hans von Aachen.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/planets/ShowCreationOfAllOrbits.py:90:class '
                          'KeplersMethod(InteractiveScene):',
                          '_work/_2025/cosmic_distance/planets/ShowCreationOfAllOrbits.py:529:class '
                          'ShowCreationOfAllOrbits(KeplersMethod):',
                          '_work/_2025/cosmic_distance/planets/KeplersMethod.py:32:    sun = '
                          'TexturedSurface(Sphere(radius=radius), "SunTexture")',
                          '_work/_2025/cosmic_distance/planets/KeplersMethod.py:54:        '
                          'TexturedSurface(Sphere(radius=radius, clockwise=True), "hiptyc_2020_8k"),',
                          '_work/_2025/cosmic_distance/planets/KeplersMethod.py:55:        '
                          'TexturedSurface(Sphere(radius=0.99 * radius, clockwise=True), '
                          '"constellation_figures"),',
                          '_work/_2025/cosmic_distance/planets/KeplersMethod.py:65:class '
                          'KeplersMethod(InteractiveScene):',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:37:            '
                          '("Kepler", 1571, 1630, 0.2, RED_C),',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:69:            '
                          'ImageMobject("Kepler"),',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:103:        # Up '
                          'to Kepler'],
        'scene_note': '9 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '23': {'title': 'File:Ole Rømer (Jacob Coning painting).jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:74:            '
                          'ImageMobject("OleRomer"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '24': {'title': 'File:Tycho Brahe.JPG',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:71:            '
                          'ImageMobject("TychoBrahe"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '25': {'title': 'File:1898. Антон Чехов.jpg',
        'usage_matches': ['_work/_2024/inscribed_rect/supplements/ChekhovsGun.py:7:        image = '
                          'ImageMobject("AntonChekhovPortrait")'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '26': {'title': 'File:Computer history museum.jpg',
        # Coordinator: crop to 16:9 (leftover sky and grass) instead of black bars; the scene only does match_width
        'process': 'cover',
        'centering': [0.5, 0.2],
        'usage_matches': ['_work/_2024/transformers/chm/ThreeWordsToOne.py:30:        chm_image = '
                          'ImageMobject("/Users/grant/3Blue1Brown '
                          'Dropbox/3Blue1Brown/videos/2024/transformers/chm/images/CHM_Exterior.jpeg")'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '27': {'title': 'File:Cauchy Augustin Louis dibner coll SIL14-C2-03a.jpg',
        'process': 'extend',
        'changes': 'Retrato histórico real, fondo extendido por desenfoque del mismo escaneo (sin IA), '
                   'conservando busto y proporción.',
        'crop': [0.12, 0.073, 0.88, 0.617],
        'usage_matches': ['_work/_2022/galois/art_supplements/CauchyFourierPoisson.py:9:            '
                          'ImageMobject(os.path.join(folder, "Cauchy-Portrait-Cutoff")),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '28': {'title': 'File:2005 Dime Obv Unc P.png',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'white_bg': True,
        'usage_matches': ['_work/_2026/hairy_ball/supplements/DimensionGeneralization.py:3:class '
                          'DimensionGeneralization(InteractiveScene):',
                          '_work/_2026/hairy_ball/supplements/DimensionGeneralization.py:7:            '
                          'Text("Dimension"),',
                          '_work/_2024/transformers/embedding/HighDimensionalSpaceCompanion.py:86:class '
                          'HighDimensionalSpaceCompanion(InteractiveScene):',
                          '_work/_2025/cosmic_distance/part2/ShrinkADime.py:3:class '
                          'ShrinkADime(InteractiveScene):',
                          '_work/_2025/cosmic_distance/part2/ShrinkADime.py:15:        dime = '
                          'ImageMobject("Dime")',
                          '_work/_2026/spheres_talk/volumes/ShowNumericalValues.py:29:        x_label = '
                          'Text("Dimension")',
                          '_work/_2026/spheres_talk/volumes/VolumeGrid.py:67:        cols_label = '
                          'Text("Dimension")',
                          '_work/_2024/transformers/supplements/ContrastGPTDimensionSizes.py:4:class '
                          'ContrastGPTDimensionSizes(InteractiveScene):',
                          '_work/_2024/puzzles/supplements/SingleHypercube.py:3:class '
                          'DimensionsPointingToEachOther(InteractiveScene):',
                          '_work/_2024/puzzles/supplements/SingleHypercube.py:56:class '
                          'SingleHypercube(DimensionsPointingToEachOther):',
                          '_work/_2024/puzzles/supplements/DimensionsPointingToEachOther.py:3:class '
                          'DimensionsPointingToEachOther(InteractiveScene):',
                          '_work/_2025/grover/qc_supplements/MoreDimensionsNote.py:3:class '
                          'MoreDimensionsNote(InteractiveScene):',
                          '_work/_2024/transformers/supplements/DimensionComparrison.py:4:class '
                          'DimensionComparrison(InteractiveScene):',
                          '_work/_2021/newton_fractal/FractalDimensionWords.py:3:class '
                          'FractalDimensionWords(Scene):',
                          '_work/_2020/chess/HighDimensionalCount.py:135:class '
                          'HighDimensionalCount(ThreeDScene):',
                          '_work/_2020/monster/AskWhatTheMonsterActsOn.py:51:        # Dimension counts',
                          '_work/_2023/gauss_int/supplements/NDimensionalBallGrid.py:4:class '
                          'NDimensionalBallGrid(InteractiveScene):',
                          '_work/_2023/gauss_int/supplements/NDimensionalBallGrid.py:47:            '
                          'Text("Dimension"),',
                          '_work/_2023/gauss_int/supplements/WhoOrderedMoreDimensions.py:4:class '
                          'WhoOrderedMoreDimensions(TeacherStudentsScene):'],
        'scene_note': '19 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '29': {'file_url': 'https://images-assets.nasa.gov/image/PIA07746/PIA07746~orig.jpg',
        'page_url': 'https://images-api.nasa.gov/search?nasa_id=PIA07746',
        'author': 'NASA/JPL/Space Science Institute; Cassini PIA07746',
        'license': 'Public domain',
        'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
        'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
        'policy_kind': 'nasa',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:47:            '
                          'Text("Dione"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '30': {'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:45:            '
                          'Text("Enceladus"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'file_url': 'https://images-assets.nasa.gov/image/PIA06254/PIA06254~orig.jpg',
        'page_url': 'https://images-api.nasa.gov/search?nasa_id=PIA06254',
        'author': 'NASA/JPL/Space Science Institute; Cassini, mosaico PIA06254 (2005)',
        'license': 'Public domain',
        'license_url': 'https://creativecommons.org/publicdomain/mark/1.0/',
        'policy_url': 'https://www.nasa.gov/nasa-brand-center/images-and-media/',
        'policy_kind': 'nasa',
        'note': 'Mosaico de disco completo, falso color documentado por NASA; no es la comparación de tamaño '
                'con la Tierra.'},
 '31': {'title': 'File:Fourier2 - restoration1.jpg',
        'process': 'extend',
        'changes': 'Retrato histórico real, fondo extendido por desenfoque del mismo escaneo (sin IA), '
                   'conservando busto y proporción.',
        'usage_matches': ['_work/_2022/galois/art_supplements/CauchyFourierPoisson.py:10:            '
                          'ImageMobject(os.path.join(folder, "Fourier-Portrait")),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '32': {'title': 'File:Gustav Herglotz, Gaston Julia.jpeg',
        'crop': [0.51, 0, 0.98, 0.56],
        'process': 'cover',
        'changes': 'Recorte del matemático de la derecha (Gaston Julia) en la foto de MFO con Gustav '
                   'Herglotz; ajuste a busto 600×800. Licencia CC BY-SA conservada.',
        'note': 'Foto histórica libre localizada bajo el nombre de ambos matemáticos; resolución fuente '
                'reducida, ampliada sin inventar detalles.',
        'scene_note': 'ShowFatouAndJulia: busto de Julia recortado de la mitad derecha, no Herglotz; la '
                      'escena lo muestra a altura 3.'},
 '33': {'title': 'File:Letter Goldbach-Euler signature.svg',
        'subject': 'Firma documental de Christian Goldbach (1742), en lugar de un retrato inexistente.',
         'process': 'signature_card',
         'paper': '#F3EBDD',
         'ink': '#302B27',
         'signature_width': 0.8,
         'changes': 'Firma histórica de Christian Goldbach, vectorización de Carnby (2015) del recorte '
                    'documental; rasterizada sin inventar trazos, fondo eliminado y tinta engrosada 1 px, '
                    'centrada al 80% del ancho en tarjeta papel 800×1000 RGB, marco tenue. Sin texto añadido.',
         'note': 'Opción 1: firma auténtica en tarjeta. API Commons: descripción Christian Goldbachs '
                 'Unterschrift; autor original Christian Goldbach, vectorización Carnby; dominio público. La '
                 'fecha documental de Commons es 12-06-1742. Legibilidad revisada a 180×225.',
         'scene_note': 'GraphAndHistoryOfExponential: documento auténtico suyo en lugar de retrato inexistente. '
                       'Nombre añadido por la escena; no se imprime nombre ni fecha en la tarjeta.',
         'usage_matches': ['_work/_2021/matrix_exp/GraphAndHistoryOfExponential.py:207:        for name1, '
                           'name2, letter, year in [("Leibniz", "Huygens", "b", "1690"), ("Euler", "Goldbach", '
                           '"e", "1731")]:']},
 '34': {'title': 'File:Caspar Netscher - Christiaan Huygens, the astronomer, 1671.jpg',
        'usage_matches': ['_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:43:            '
                          '("Huygens", 1629, 1695, 0.5, BLUE_C),',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:75:            '
                          'ImageMobject("ChristiaanHuygens"),',
                          '_work/_2025/cosmic_distance/supplements/MainCharacterTimeline.py:152:        # '
                          'Romer and Huygens',
                          '_work/_2025/cosmic_distance/part2/CompareLightSpeedEstimates.py:7:            '
                          'TexText("Huygens\' Estimate: 212,000 km/s"),',
                          '_work/_2025/cosmic_distance/supplements2/CompareLightSpeedEstimates.py:7:            '
                          'TexText("Huygens\' Estimate: 212,000 km/s"),',
                          '_work/_2021/matrix_exp/GraphAndHistoryOfExponential.py:207:        for name1, '
                          'name2, letter, year in [("Leibniz", "Huygens", "b", "1690"), ("Euler", '
                          '"Goldbach", "e", "1731")]:'],
        'scene_note': '6 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'crop': [0.12, 0.03, 0.88, 0.75]},
 '35': {'title': 'File:Iapetus as seen by the Cassini probe - 20071008.jpg',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:50:            '
                          'Text("Iapetus"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'source_url': 'https://images-assets.nasa.gov/image/PIA08384/PIA08384~orig.jpg',
        'note': 'Mosaico Cassini en falso color documentado por NASA, no fotografía de color natural.'},
 '36': {'title': 'File:Introductio in analysin infinitorum. T. 1 - Leonhard Euler, 1748 (IA '
                 'introductioanaly00eule).pdf',
        'process': 'contain',
        'pdf_page': 9,
        'changes': 'Portada histórica verificada visualmente: página 9 del escaneo PDF del volumen I (1748); '
                   'renderizado y encajado a 900×1200, sin recortar texto.',
        'usage_matches': ['_work/_2021/matrix_exp/GraphAndHistoryOfExponential.py:267:        book = '
                          'ImageMobject("Introductio_in_Analysin_infinitorum")'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '37': {'title': 'File:Mimas Cassini.jpg',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:44:            '
                          'Text("Mimas"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'source_url': 'https://images-assets.nasa.gov/image/PIA12570/PIA12570~orig.jpg'},
 '38': {'title': 'File:Pierre Fatou.jpg',
        'usage_matches': ['_work/_2021/holomorphic_dynamics/ShowFatouAndJulia.py:50:            '
                          'get_figure("Pierre_Fatou", "Pierre Fatou", "1878-1929", **kw),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '39': {'title': 'File:Simeon Poisson.jpg',
        'process': 'extend',
        'changes': 'Retrato histórico real, fondo extendido por desenfoque del mismo escaneo (sin IA), '
                   'conservando busto y proporción.',
        'crop': [0, 0, 1, 0.89],
        'usage_matches': ['_work/_2022/galois/art_supplements/CauchyFourierPoisson.py:11:            '
                          'ImageMobject(os.path.join(folder, "Poisson-Portrait-Outpainted")),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'},
 '40': {'title': 'File:Rhea hi-res PIA07763.jpg',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:48:            '
                          'Text("Rhea"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'source_url': 'https://images-assets.nasa.gov/image/PIA07763/PIA07763~orig.jpg'},
 '41': {'title': 'File:Tethys PIA07738.jpg',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:46:            '
                          'Text("Tethys"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'source_url': 'https://images-assets.nasa.gov/image/PIA07738/PIA07738~orig.jpg'},
 '42': {'title': 'File:Titan in true color.jpg',
        'process': 'disc',
        'changes': 'Fondo exterior conectado eliminado por código; disco recortado, centrado con margen y '
                   'reducido a RGBA al tamaño exacto.',
        'usage_matches': ['_work/_2023/gauss_int/supplements/HerschelDescription.py:49:            '
                          'Text("Titan"),'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.',
        'source_url': 'https://images-assets.nasa.gov/image/PIA14602/PIA14602~orig.jpg'},
 '43': {'title': 'File:Flag of the United States.svg',
        'process': 'flag',
        'changes': 'Dibujo por código: 13 franjas, 50 estrellas, proporción 1.9:1 y geometría de Executive '
                   'Order 10834; diseño de dominio público.',
        'usage_matches': ['_work/_2022/puzzles/subsets/IMOLogo.py:9:        us_flag = '
                          'ImageMobject("US_Flag")'],
        'scene_note': '1 coincidencias revisadas en _work (sin .orig.py); tamaño/modo originales; sin '
                      'posiciones adicionales fijas detectadas.'}}
ROWS = [{'n': '1',
  'asset': 'raster_images/SunTexture.jpg',
  'tipo': 'textura',
  'ancho': '4096',
  'alto': '2048',
  'modo': 'RGB',
  'escenas': '20',
  'ejemplo': '_2025/cosmic_distance/paralax.py::NearbyStars',
  'que_es': 'Textura central del Sol (20 escenas, esfera).',
  'fuente_candidata': 'NASA SDO (sdo.gsfc.nasa.gov/data), imagen HMI/AIA del disco completo, dominio '
                      'público; hay que reproyectarla a equirrectangular con un script.'},
 {'n': '2',
  'asset': 'raster_images/MoonTexture.jpg',
  'tipo': 'textura',
  'ancho': '4096',
  'alto': '2048',
  'modo': 'RGB',
  'escenas': '13',
  'ejemplo': '_2025/cosmic_distance/paralax.py::ParalaxMeasurmentFromEarth',
  'que_es': 'Textura de esfera de la Luna (13 escenas).',
  'fuente_candidata': "NASA SVS 4720 'CGI Moon Kit' (LRO, mapa de color 4k/8k), dominio público."},
 {'n': '3',
  'asset': 'raster_images/hiptyc_2020_8k.jpg',
  'tipo': 'textura',
  'ancho': '8192',
  'alto': '4096',
  'modo': 'RGB',
  'escenas': '12',
  'ejemplo': '_2025/cosmic_distance/paralax.py::NearbyStars',
  'que_es': 'Fondo estelar (12 escenas); es el mapa de estrellas de la NASA.',
  'fuente_candidata': "NASA SVS 4851 'Deep Star Maps 2020' (starmap_2020_8k), dominio público."},
 {'n': '4',
  'asset': 'generated/2025/cosmic_distance/constellation_figures.png',
  'tipo': 'textura',
  'ancho': '4096',
  'alto': '2048',
  'modo': 'RGBA',
  'escenas': '8',
  'ejemplo': '_2025/cosmic_distance/paralax.py::NearbyStars',
  'que_es': 'Figuras de constelaciones sobre esfera (8 escenas).',
  'fuente_candidata': "NASA SVS 4851, 'constellation_figures_4k' (mismo conjunto), dominio público."},
 {'n': '5',
  'asset': 'generated/2025/cosmic_distance/Paul Animations/6. Transit Of Venus/New Transit of Venus '
           'scenes/JustSun.tif',
  'tipo': 'imagen',
  'ancho': '2229',
  'alto': '2230',
  'modo': 'RGB',
  'escenas': '6',
  'ejemplo': '_2025/cosmic_distance/paralax.py::TransitOfVenus',
  'que_es': 'Disco solar real (6 escenas, se ve a 0.23 unidades pero se anima).',
  'fuente_candidata': 'NASA SDO (HMI intensitygram o AIA 4500), dominio público.'},
 {'n': '6',
  'asset': 'generated/2025/cosmic_distance/GalaxyStill.png',
  'tipo': 'imagen',
  'ancho': '1920',
  'alto': '1080',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2025/cosmic_distance/part2.py::LineToDistantStar',
  'que_es': 'Galaxia espiral al fondo (2 escenas).',
  'fuente_candidata': 'NASA/JPL-Caltech (R. Hurt, SSC) o Hubble/ESA con licencia libre; verificar.'},
 {'n': '7',
  'asset': 'generated/2025/cosmic_distance/JovianSystem.png',
  'tipo': 'imagen',
  'ancho': '1920',
  'alto': '1080',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2025/cosmic_distance/part2.py::LabelIo',
  'que_es': 'Sistema joviano (LabelIo, 2 escenas).',
  'fuente_candidata': 'NASA/JPL, montaje de las lunas galileanas en Photojournal (dominio público) o '
                      'Commons.'},
 {'n': '8',
  'asset': 'generated/2025/cosmic_distance/Paul Animations/6. Transit Of Venus/New Transit of Venus '
           'scenes/JustSunBackgroundRemoved.png',
  'tipo': 'imagen',
  'ancho': '1978',
  'alto': '1978',
  'modo': 'RGBA',
  'escenas': '2',
  'ejemplo': '_2025/cosmic_distance/part2.py::SunInTheSky',
  'que_es': 'Disco solar con fondo transparente (2 escenas); mismo origen que JustSun.',
  'fuente_candidata': 'NASA SDO HMI intensitygram + canal alfa generado por código.'},
 {'n': '9',
  'asset': 'raster_images/MarsTexture.jpg',
  'tipo': 'textura',
  'ancho': '2048',
  'alto': '1024',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2025/cosmic_distance/planets.py::KeplersMethod',
  'que_es': 'Textura de esfera de Marte (2 escenas).',
  'fuente_candidata': 'USGS Astrogeology / NASA Viking MDIM 2.1 colorizado, dominio público.'},
 {'n': '10',
  'asset': 'raster_images/US_color_graph.png',
  'tipo': 'imagen',
  'ancho': '1200',
  'alto': '800',
  'modo': 'RGB',
  'escenas': '2',
  'ejemplo': '_2025/grover/runtime.py::NPProblemExamples',
  'que_es': 'Mapa de EE.UU. coloreado para el ejemplo del problema NP (2 escenas, pequeño).',
  'fuente_candidata': 'Commons: mapa en blanco de EE.UU. y colorearlo por código (cuatro colores); o dejar '
                      'el marcador.'},
 {'n': '11',
  'asset': 'generated/2025/cosmic_distance/LunarEclipseComposite.jpg',
  'tipo': 'imagen',
  'ancho': '1920',
  'alto': '1080',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::ShowFourLittleCircles',
  'que_es': 'Composición de eclipse lunar (1 escena).',
  'fuente_candidata': "Commons: categoría 'Lunar eclipse composites' (verificar licencia CC BY/BY-SA o "
                      'dominio público).'},
 {'n': '12',
  'asset': 'generated/2025/cosmic_distance/Nile.png',
  'tipo': 'imagen',
  'ancho': '1920',
  'alto': '1080',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::NileLabels',
  'que_es': 'Mapa/foto del Nilo (1 escena de rótulos).',
  'fuente_candidata': 'NASA Visible Earth / Earth Observatory (Landsat, delta del Nilo), dominio público.'},
 {'n': '13',
  'asset': 'generated/2025/cosmic_distance/names/ChristiaanHuygens.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '14',
  'asset': 'generated/2025/cosmic_distance/names/Copernicus.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '15',
  'asset': 'generated/2025/cosmic_distance/names/EdmondHalley.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '16',
  'asset': 'generated/2025/cosmic_distance/names/EdwinHubble.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '17',
  'asset': 'generated/2025/cosmic_distance/names/Eratosthenes.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '18',
  'asset': 'generated/2025/cosmic_distance/names/FriedrichBessel.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '19',
  'asset': 'generated/2025/cosmic_distance/names/Head_of_Aristotle.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '20',
  'asset': 'generated/2025/cosmic_distance/names/HenriettaLeavitt.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '21',
  'asset': 'generated/2025/cosmic_distance/names/JamesCook.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '22',
  'asset': 'generated/2025/cosmic_distance/names/Kepler.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '23',
  'asset': 'generated/2025/cosmic_distance/names/OleRomer.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '24',
  'asset': 'generated/2025/cosmic_distance/names/TychoBrahe.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/supplements.py::MainCharacterTimeline',
  'que_es': 'Retrato/busto de un personaje histórico que sale un instante en la línea de tiempo.',
  'fuente_candidata': 'Commons: retrato o busto de dominio público (grabado/óleo anterior a 1900; para '
                      'Hubble y Leavitt, foto de Commons con licencia libre; verificar).'},
 {'n': '25',
  'asset': 'raster_images/AntonChekhovPortrait.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2024/inscribed_rect/supplements.py::ChekhovsGun',
  'que_es': 'Retrato de Chéjov (ChekhovsGun).',
  'fuente_candidata': 'Commons: fotografía de 1898, dominio público.'},
 {'n': '26',
  'asset': 'raster_images/CHM_Exterior.jpeg',
  'tipo': 'imagen',
  'ancho': '1600',
  'alto': '900',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2024/transformers/chm.py::ThreeWordsToOne',
  'que_es': 'Foto del Museo de Historia de la Computación (ThreeWordsToOne).',
  'fuente_candidata': 'Commons: foto del Computer History Museum con licencia CC BY-SA (verificar autor y '
                      'atribuir).'},
 {'n': '27',
  'asset': 'raster_images/Cauchy-Portrait-Cutoff.png',
  'tipo': 'imagen',
  'ancho': '700',
  'alto': '900',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2022/galois/art_supplements::CauchyFourierPoisson',
  'que_es': 'Retrato histórico (CauchyFourierPoisson).',
  'fuente_candidata': 'Commons: litografías/retratos de dominio público (Cauchy ya está en '
                      "make_replacement_photos.py; añadir Fourier y Poisson); el 'outpainting' se rehace "
                      'extendiendo el fondo por código.'},
 {'n': '28',
  'asset': 'raster_images/Dime.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '800',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2025/cosmic_distance/part2.py::ShrinkADime',
  'que_es': 'Moneda de diez centavos para comparar tamaños angulares (cosmic_distance).',
  'fuente_candidata': 'Commons / U.S. Mint: foto de una moneda de 10 centavos de EE.UU., dominio público.'},
 {'n': '29',
  'asset': 'raster_images/Dione.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '30',
  'asset': 'raster_images/Enceladus.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '31',
  'asset': 'raster_images/Fourier-Portrait.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2022/galois/art_supplements::CauchyFourierPoisson',
  'que_es': 'Retrato histórico (CauchyFourierPoisson).',
  'fuente_candidata': 'Commons: litografías/retratos de dominio público (Cauchy ya está en '
                      "make_replacement_photos.py; añadir Fourier y Poisson); el 'outpainting' se rehace "
                      'extendiendo el fondo por código.'},
 {'n': '32',
  'asset': 'raster_images/Gaston_Julia.jpg',
  'tipo': 'imagen',
  'ancho': '600',
  'alto': '800',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2021/holomorphic_dynamics::ShowFatouAndJulia',
  'que_es': 'Retrato histórico de matemático en una escena de historia.',
  'fuente_candidata': 'Commons: retrato de dominio público; para Julia/Fatou verificar licencia, y si no hay '
                      'libre dejar el marcador.'},
 {'n': '33',
  'asset': 'raster_images/Goldbach.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2021/matrix_exp::GraphAndHistoryOfExponential',
  'que_es': 'Retrato histórico de matemático en una escena de historia.',
  'fuente_candidata': 'Commons: retrato de dominio público; para Julia/Fatou verificar licencia, y si no hay '
                      'libre dejar el marcador.'},
 {'n': '34',
  'asset': 'raster_images/Huygens.png',
  'tipo': 'imagen',
  'ancho': '800',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2021/matrix_exp::GraphAndHistoryOfExponential',
  'que_es': 'Retrato histórico de matemático en una escena de historia.',
  'fuente_candidata': 'Commons: retrato de dominio público; para Julia/Fatou verificar licencia, y si no hay '
                      'libre dejar el marcador.'},
 {'n': '35',
  'asset': 'raster_images/Iapetus.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '36',
  'asset': 'raster_images/Introductio_in_Analysin_infinitorum.png',
  'tipo': 'imagen',
  'ancho': '900',
  'alto': '1200',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2021/matrix_exp::GraphAndHistoryOfExponential',
  'que_es': 'Portada del libro de Euler (GraphAndHistoryOfExponential).',
  'fuente_candidata': 'Commons / e-rara.ch: portada digitalizada, dominio público.'},
 {'n': '37',
  'asset': 'raster_images/Mimas.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '38',
  'asset': 'raster_images/Pierre_Fatou.jpg',
  'tipo': 'imagen',
  'ancho': '600',
  'alto': '800',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2021/holomorphic_dynamics::ShowFatouAndJulia',
  'que_es': 'Retrato histórico de matemático en una escena de historia.',
  'fuente_candidata': 'Commons: retrato de dominio público; para Julia/Fatou verificar licencia, y si no hay '
                      'libre dejar el marcador.'},
 {'n': '39',
  'asset': 'raster_images/Poisson-Portrait-Outpainted.png',
  'tipo': 'imagen',
  'ancho': '900',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2022/galois/art_supplements::CauchyFourierPoisson',
  'que_es': 'Retrato histórico (CauchyFourierPoisson).',
  'fuente_candidata': 'Commons: litografías/retratos de dominio público (Cauchy ya está en '
                      "make_replacement_photos.py; añadir Fourier y Poisson); el 'outpainting' se rehace "
                      'extendiendo el fondo por código.'},
 {'n': '40',
  'asset': 'raster_images/Rhea.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '41',
  'asset': 'raster_images/Tethys.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '42',
  'asset': 'raster_images/Titan.png',
  'tipo': 'imagen',
  'ancho': '400',
  'alto': '400',
  'modo': 'RGBA',
  'escenas': '1',
  'ejemplo': '_2023/gauss_int/supplements::HerschelDescription',
  'que_es': 'Foto de una luna de Saturno en una lista de lunas (HerschelDescription, pequeña).',
  'fuente_candidata': 'NASA/JPL Cassini (photojournal.jpl.nasa.gov), dominio público.'},
 {'n': '43',
  'asset': 'raster_images/US_Flag.png',
  'tipo': 'imagen',
  'ancho': '1900',
  'alto': '1000',
  'modo': 'RGB',
  'escenas': '1',
  'ejemplo': '_2022/puzzles/subsets::IMOLogo',
  'que_es': 'Bandera de EE.UU. en IMOLogo.',
  'fuente_candidata': "Commons 'Flag of the United States.svg', dominio público."}]

# DESCARGAS_2: independent verified downloads, entries 44-59.
MANIFEST.update({'44': {'title': 'File:Portrait of Sir Isaac Newton, 1689 (brightened).jpg',
        'process': 'cover',
        'crop': [0.18, 0.035, 0.9, 0.72],
        'subject': 'Isaac Newton, retrato de Godfrey Kneller (1689), busto.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA. Recorte de busto desde el retrato completo de Kneller; se excluyen mano y parte inferior.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/shadows/FamousMathematicians.py y los usos indicados, sin .orig.py: se '
                      'conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '45': {'title': 'File:Leonhard Euler - Jakob Emanuel Handmann (Kunstmuseum Basel).jpg',
        'process': 'cover',
        'subject': 'Leonhard Euler, pastel de Jakob Emanuel Handmann (1753), con gorro claro y bata azul.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/matrix_exp/GraphAndHistoryOfExponential.py y los usos indicados, sin '
                      '.orig.py: se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '46': {'title': 'File:Leonhard Euler - Jakob Emanuel Handmann (Kunstmuseum Basel).jpg',
        'process': 'cover',
        'subject': 'El mismo pastel de Handmann, en grande y RGBA (opaco).',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant. Mismo pastel que Euler.jpg, a tamaño grande con alfa completamente opaco.',
        'scene_note': 'Revisado -.py y los usos indicados, sin .orig.py: se conserva sujeto, proporción y '
                      'encuadre; no se modifican escenas.'},
 '47': {'title': 'File:Carl Friedrich Gauss 1840 by Jensen.jpg',
        'process': 'cover',
        'subject': 'Carl Friedrich Gauss, óleo de Christian Albrecht Jensen (1840), con gorro negro.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/shadows/FamousMathematicians.py y los usos indicados, sin .orig.py: se '
                      'conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '48': {'title': 'File:Emmy Noether.jpg',
        'process': 'cover',
        'subject': 'Emmy Noether joven, foto de cuerpo entero (de pie, blusa blanca), principios del s. XX. '
                   'Escala de grises.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant. Misma fotografía libre que EmmyNoether de assets2020, convertida a L.',
        'scene_note': 'Revisado _2021/shadows/FamousMathematicians.py y los usos indicados, sin .orig.py: se '
                      'conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '49': {'title': 'File:Srinivasa Ramanujan - OPC - 1.jpg',
        'process': 'cover',
        'subject': 'Srinivasa Ramanujan, foto de ca. 1913, sentado, con chaqueta. Escala de grises.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/shadows/FamousMathematicians.py y los usos indicados, sin .orig.py: se '
                      'conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '50': {'title': 'File:William Rowan Hamilton painting.jpg',
        'process': 'cover',
        'subject': 'William Rowan Hamilton, retrato pintado, sentado junto a una mesa con papeles.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/newton_fractal/CommentsOnNaming.py y los usos indicados, sin .orig.py: '
                      'se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '51': {'title': 'File:Fourier2 - restoration1.jpg',
        'process': 'cover',
        'subject': 'Joseph Fourier, grabado de Julien-Léopold Boilly (busto, fondo claro).',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant. Misma fuente que Fourier-Portrait.png; ambas copias nuevas usan el mismo encuadre.',
        'scene_note': 'Revisado _2021/newton_fractal/CommentsOnNaming.py y los usos indicados, sin .orig.py: '
                      'se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '52': {'title': 'File:Christoph Bernhard Francke - Bildnis des Philosophen Leibniz (ca. 1695).jpg',
        'process': 'cover',
        'subject': 'Gottfried Wilhelm Leibniz, óleo de Christoph Bernhard Francke (ca. 1695), peluca negra '
                   'larga.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/matrix_exp/GraphAndHistoryOfExponential.py y los usos indicados, sin '
                      '.orig.py: se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '53': {'title': 'File:Jakob Bernoulli.jpg',
        'process': 'cover',
        'crop': [0, 0, 1, 0.91],
        'subject': 'Jacob Bernoulli, óleo de Niklaus Bernoulli (1687), con la mano sobre un globo.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA. Se recorta la cartela inferior del escaneo, conservando cabeza, gorguera, mano y globo.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/matrix_exp/BernoullisThoughts.py y los usos indicados, sin .orig.py: '
                      'se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '54': {'title': 'File:Euklid-von-Alexandria 1.jpg',
        'process': 'cover',
        'subject': 'Euclides, grabado coloreado de André Thevet (1584), escribiendo con compás; fondo '
                   'blanco.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant. Grabado histórico convencional de Euclides, no un retrato tomado del natural; autor '
                'no indicado en la ficha de Commons.',
        'scene_note': 'Revisado _2022/visual_proofs/lies/WhyWeNeedProofs.py y los usos indicados, sin '
                      '.orig.py: se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '55': {'title': 'File:Alan Turing Aged 16.jpg',
        'process': 'cover',
        'subject': 'Alan Turing a los 16 años (ca. 1928), foto de busto. Escala de grises.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2026/cross_entropy/entropy/RandomNoiseIsIncompressible.py y los usos '
                      'indicados, sin .orig.py: se conserva sujeto, proporción y encuadre; no se modifican '
                      'escenas.'},
 '56': {'title': 'File:Wreck of the Central America.jpg',
        'process': 'cover',
        'subject': 'Litografía del naufragio del vapor SS Central America (1857), barco escorado entre olas.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2026/cross_entropy/entropy/RandomNoiseIsIncompressible.py y los usos '
                      'indicados, sin .orig.py: se conserva sujeto, proporción y encuadre; no se modifican '
                      'escenas.'},
 '57': {'title': 'File:Flag of Slovakia.svg',
        'process': 'cover',
        'subject': 'Bandera de Eslovaquia.',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant. SVG auténtico de la bandera de Eslovaquia rasterizado; no se usa el generador de la '
                'bandera estadounidense.',
        'scene_note': 'Revisado _2024/puzzles/supplements/SlovokiaTeam.py y los usos indicados, sin '
                      '.orig.py: se conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '58': {'title': 'File:Fourier2 - restoration1.jpg',
        'process': 'cover',
        'subject': 'El mismo grabado de Fourier que la fila 51, con otro nombre (hoy lo copia '
                   'make_shadows_assets.py desde el archivo de Grant).',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant. Misma fuente que Fourier-Portrait.png; ambas copias nuevas usan el mismo encuadre.',
        'scene_note': 'Revisado _2021/shadows/FamousMathematicians.py y los usos indicados, sin .orig.py: se '
                      'conserva sujeto, proporción y encuadre; no se modifican escenas.'},
 '59': {'title': 'File:Georg Friedrich Bernhard Riemann.jpeg',
        'process': 'cover',
        'subject': 'Bernhard Riemann, foto de busto recortada (hoy es copia del Riemann.jpeg de Grant, la '
                   'hace make_shadows_assets.py).',
        'changes': 'Descarga independiente del original libre; recorte mínimo de encuadre y reescala Lanczos '
                   'al tamaño y modo exactos, sin IA.',
        'note': 'Fuente descargada de Commons y licencia verificada de nuevo; no se reutiliza el archivo de '
                'Grant.',
        'scene_note': 'Revisado _2021/shadows/FamousMathematicians.py y los usos indicados, sin .orig.py: se '
                      'conserva sujeto, proporción y encuadre; no se modifican escenas.'}})
ROWS.extend([{'n': '44',
  'asset': 'raster_images/Newton.jpg',
  'tipo': 'retrato',
  'ancho': '407',
  'alto': '559',
  'modo': 'RGB',
  'escenas': 'FamousMathematicians; HistoryWithNewton; CommentsOnNaming',
  'ejemplo': '_2021/shadows/FamousMathematicians',
  'que_es': 'Isaac Newton, retrato de Godfrey Kneller (1689), busto.',
  'fuente_candidata': 'File:Portrait of Sir Isaac Newton, 1689 (brightened).jpg (identificada por R3, que '
                      'comparó con el archivo actual; licencia según R3: Public domain). Verifícala de '
                      'nuevo.'},
 {'n': '45',
  'asset': 'raster_images/Euler.jpg',
  'tipo': 'retrato',
  'ancho': '461',
  'alto': '600',
  'modo': 'RGB',
  'escenas': 'FamousMathematicians; GraphAndHistoryOfExponential',
  'ejemplo': '_2021/matrix_exp/GraphAndHistoryOfExponential',
  'que_es': 'Leonhard Euler, pastel de Jakob Emanuel Handmann (1753), con gorro claro y bata azul.',
  'fuente_candidata': 'File:Leonhard Euler - Jakob Emanuel Handmann (Kunstmuseum Basel).jpg (identificada '
                      'por R3, que comparó con el archivo actual; licencia según R3: Public domain). '
                      'Verifícala de nuevo.'},
 {'n': '46',
  'asset': 'raster_images/Euler.png',
  'tipo': 'retrato',
  'ancho': '1414',
  'alto': '1774',
  'modo': 'RGBA',
  'escenas': '(ninguna en 2020-2026: ImageMobject("Euler") toma el .jpg; prioridad baja)',
  'ejemplo': '-',
  'que_es': 'El mismo pastel de Handmann, en grande y RGBA (opaco).',
  'fuente_candidata': 'File:Leonhard Euler - Jakob Emanuel Handmann (Kunstmuseum Basel).jpg (identificada '
                      'por R3, que comparó con el archivo actual; licencia según R3: Public domain). '
                      'Verifícala de nuevo.'},
 {'n': '47',
  'asset': 'raster_images/Gauss.jpg',
  'tipo': 'retrato',
  'ancho': '640',
  'alto': '815',
  'modo': 'RGB',
  'escenas': 'FamousMathematicians',
  'ejemplo': '_2021/shadows/FamousMathematicians',
  'que_es': 'Carl Friedrich Gauss, óleo de Christian Albrecht Jensen (1840), con gorro negro.',
  'fuente_candidata': 'File:Carl Friedrich Gauss 1840 by Jensen.jpg (identificada por R3, que comparó con el '
                      'archivo actual; licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '48',
  'asset': 'raster_images/Noether.jpg',
  'tipo': 'retrato',
  'ancho': '640',
  'alto': '975',
  'modo': 'L',
  'escenas': 'FamousMathematicians',
  'ejemplo': '_2021/shadows/FamousMathematicians',
  'que_es': 'Emmy Noether joven, foto de cuerpo entero (de pie, blusa blanca), principios del s. XX. Escala '
            'de grises.',
  'fuente_candidata': 'File:Emmy Noether (3x4 cropped).jpg (identificada por R3, que comparó con el archivo '
                      'actual; licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '49',
  'asset': 'raster_images/Ramanujan.jpg',
  'tipo': 'retrato',
  'ancho': '640',
  'alto': '877',
  'modo': 'L',
  'escenas': 'FamousMathematicians',
  'ejemplo': '_2021/shadows/FamousMathematicians',
  'que_es': 'Srinivasa Ramanujan, foto de ca. 1913, sentado, con chaqueta. Escala de grises.',
  'fuente_candidata': 'File:Srinivasa Ramanujan - OPC - 1.jpg (identificada por R3, que comparó con el '
                      'archivo actual; licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '50',
  'asset': 'raster_images/Hamilton.jpg',
  'tipo': 'retrato',
  'ancho': '640',
  'alto': '768',
  'modo': 'RGB',
  'escenas': 'CommentsOnNaming',
  'ejemplo': '_2021/newton_fractal/CommentsOnNaming',
  'que_es': 'William Rowan Hamilton, retrato pintado, sentado junto a una mesa con papeles.',
  'fuente_candidata': 'File:William Rowan Hamilton painting.jpg (identificada por R3, que comparó con el '
                      'archivo actual; licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '51',
  'asset': 'raster_images/Joseph Fourier.jpg',
  'tipo': 'retrato',
  'ancho': '484',
  'alto': '612',
  'modo': 'RGB',
  'escenas': 'CommentsOnNaming',
  'ejemplo': '_2021/newton_fractal/CommentsOnNaming',
  'que_es': 'Joseph Fourier, grabado de Julien-Léopold Boilly (busto, fondo claro).',
  'fuente_candidata': 'File:Fourier2 - restoration1.jpg (identificada por R3, que comparó con el archivo '
                      'actual; licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '52',
  'asset': 'raster_images/Leibniz.jpg',
  'tipo': 'retrato',
  'ancho': '316',
  'alto': '400',
  'modo': 'RGB',
  'escenas': 'GraphAndHistoryOfExponential',
  'ejemplo': '_2021/matrix_exp/GraphAndHistoryOfExponential',
  'que_es': 'Gottfried Wilhelm Leibniz, óleo de Christoph Bernhard Francke (ca. 1695), peluca negra larga.',
  'fuente_candidata': 'File:Christoph Bernhard Francke - Bildnis des Philosophen Leibniz (ca. 1695).jpg '
                      '(identificada por R3, que comparó con el archivo actual; licencia según R3: Public '
                      'domain). Verifícala de nuevo.'},
 {'n': '53',
  'asset': 'raster_images/Jacob_Bernoulli.png',
  'tipo': 'retrato',
  'ancho': '1032',
  'alto': '1160',
  'modo': 'RGBA',
  'escenas': 'BernoullisThoughts',
  'ejemplo': '_2021/matrix_exp/BernoullisThoughts',
  'que_es': 'Jacob Bernoulli, óleo de Niklaus Bernoulli (1687), con la mano sobre un globo.',
  'fuente_candidata': 'File:Jakob Bernoulli.jpg (identificada por R3, que comparó con el archivo actual; '
                      'licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '54',
  'asset': 'raster_images/Euclid.jpg',
  'tipo': 'retrato',
  'ancho': '262',
  'alto': '311',
  'modo': 'RGB',
  'escenas': 'WhyWeNeedProofs',
  'ejemplo': '_2022/visual_proofs/lies/WhyWeNeedProofs',
  'que_es': 'Euclides, grabado coloreado de André Thevet (1584), escribiendo con compás; fondo blanco.',
  'fuente_candidata': 'Commons: File:Euklid-von-Alexandria 1.jpg (o equivalente). Dominio público.'},
 {'n': '55',
  'asset': 'raster_images/Turing.jpg',
  'tipo': 'retrato',
  'ancho': '640',
  'alto': '871',
  'modo': 'L',
  'escenas': 'RandomNoiseIsIncompressible',
  'ejemplo': '_2026/cross_entropy/entropy/RandomNoiseIsIncompressible',
  'que_es': 'Alan Turing a los 16 años (ca. 1928), foto de busto. Escala de grises.',
  'fuente_candidata': 'File:Alan Turing Aged 16.jpg (identificada por R3, que comparó con el archivo actual; '
                      'licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '56',
  'asset': 'raster_images/ss_central_america.jpg',
  'tipo': 'obra',
  'ancho': '457',
  'alto': '306',
  'modo': 'RGB',
  'escenas': 'RandomNoiseIsIncompressible',
  'ejemplo': '_2026/cross_entropy/entropy/RandomNoiseIsIncompressible',
  'que_es': 'Litografía del naufragio del vapor SS Central America (1857), barco escorado entre olas.',
  'fuente_candidata': 'File:Wreck of the Central America.jpg (identificada por R3, que comparó con el '
                      'archivo actual; licencia según R3: Public domain). Verifícala de nuevo.'},
 {'n': '57',
  'asset': 'raster_images/flags/sk.png',
  'tipo': 'bandera',
  'ancho': '550',
  'alto': '367',
  'modo': 'RGB',
  'escenas': 'SlovokiaTeam',
  'ejemplo': '_2024/puzzles/supplements/SlovokiaTeam',
  'que_es': 'Bandera de Eslovaquia.',
  'fuente_candidata': 'Commons: File:Flag of Slovakia.svg, rasterizada al tamaño exacto (como au y kr en '
                      '2020). Dominio público.'},
 {'n': '58',
  'asset': 'raster_images/Fourier.jpg',
  'tipo': 'retrato',
  'ancho': '484',
  'alto': '612',
  'modo': 'RGB',
  'escenas': 'FamousMathematicians; UpshotOfLimitExample',
  'ejemplo': '_2021/shadows/FamousMathematicians',
  'que_es': 'El mismo grabado de Fourier que la fila 51, con otro nombre (hoy lo copia '
            'make_shadows_assets.py desde el archivo de Grant).',
  'fuente_candidata': 'La misma que la 51: File:Fourier2 - restoration1.jpg.'},
 {'n': '59',
  'asset': 'raster_images/Riemann_cropped.jpeg',
  'tipo': 'retrato',
  'ancho': '640',
  'alto': '699',
  'modo': 'L',
  'escenas': 'FamousMathematicians',
  'ejemplo': '_2021/shadows/FamousMathematicians',
  'que_es': 'Bernhard Riemann, foto de busto recortada (hoy es copia del Riemann.jpeg de Grant, la hace '
            'make_shadows_assets.py).',
  'fuente_candidata': 'File:Georg Friedrich Bernhard Riemann.jpeg (identificada por R3). Verifícala de '
                      'nuevo.'}])

MAX_BYTES=128*1024**2
REPO_MAX=10*1024**2
POLICIES={}
LAST_UPLOAD_REQUEST=0.0


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',s or ''))).strip()
def atomic_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def http(url,limit=MAX_BYTES):
 """Sequential requests; obey Retry-After and cap both declared/actual size."""
 host=urllib.parse.urlparse(url).hostname
 cooldown_file=CACHE/'host_cooldowns.json'
 cooldowns=json.loads(cooldown_file.read_text()) if cooldown_file.exists() else {}
 if cooldowns.get(host,0)>time.time():raise RuntimeError(f'Host {host} en pausa hasta {datetime.fromtimestamp(cooldowns[host],timezone.utc).isoformat()}')
 global LAST_UPLOAD_REQUEST
 if host=="upload.wikimedia.org":
  delay=6-(time.time()-LAST_UPLOAD_REQUEST)
  if delay>0:time.sleep(delay)
  LAST_UPLOAD_REQUEST=time.time()
 last=None
 for attempt in range(3):
  try:
   time.sleep(.65)
   with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90) as r:
    if int(r.headers.get('Content-Length','0'))>limit:raise ValueError('Original exceeds configured download limit')
    data=r.read(limit+1)
    if len(data)>limit:raise ValueError('Original exceeds configured download limit')
    return data
  except urllib.error.HTTPError as e:
   last=e
   if e.code not in (429,500,502,503,504):raise
   delay=max(4*(attempt+1),int(e.headers.get('Retry-After','5')))
   if e.code==429:
    cooldowns[host]=time.time()+delay;atomic_json(cooldown_file,cooldowns)
   if delay>60:raise RuntimeError(f'Server asks to retry after {delay}s; rerun later') from e
   time.sleep(delay)
  except (urllib.error.URLError,TimeoutError) as e:
   last=e
   if attempt<2:time.sleep(3*(attempt+1))
 raise RuntimeError(str(last))
def api(**params):return json.loads(http(API+'?'+urllib.parse.urlencode(dict(format='json',**params)),10*1024**2))
def verify_commons(titles):
 """One grouped query avoids the much tighter Commons search rate limits."""
 out={}
 if not titles:return out
 data=api(action='query',prop='imageinfo',iiprop='extmetadata|url|size',titles='|'.join(sorted(titles)))
 atomic_json(CACHE/'licencias/commons_latest.json',data)
 atomic_json(CACHE/'licencias'/('commons_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'.json'),data)
 for page in data.get('query',{}).get('pages',{}).values():
  if 'imageinfo' not in page:continue
  ii=page['imageinfo'][0];m=ii.get('extmetadata',{});g=lambda k:clean(m.get(k,{}).get('value',''))
  lic=g('LicenseShortName')
  if not ALLOWED.fullmatch(lic):continue
  out[page['title']]={'commons_title':page['title'],'page_url':ii['descriptionurl'],'file_url':ii['url'].split('?')[0],
   'license':lic,'license_url':g('LicenseUrl') or (PD_URL if lic.lower()=='public domain' else ''),
   'author':g('Artist') or g('Credit') or 'Autor no identificado en Commons',
   'date':g('DateTimeOriginal'),'source_size_bytes':ii['size'],'source_width':ii['width'],'source_height':ii['height'],
   'license_evidence':'Commons imageinfo/extmetadata consultado en esta ejecución'}
 return out

def cached(url,suffix=None):
 suffix=suffix or Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).suffix or '.bin'
 p=CACHE/'originales'/(hashlib.sha256(url.encode()).hexdigest()[:24]+suffix)
 if not p.exists():
  data=http(url); p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.part');t.write_bytes(data);t.replace(p)
 return p

def policy_source(spec):
 """Require both known official credit page and license policy on every run."""
 for url in (spec['page_url'],spec['policy_url']):
  if url not in POLICIES:
   body=http(url,12*1024**2).decode('utf-8','replace'); POLICIES[url]=body
   p=CACHE/'licencias'/(hashlib.sha256(url.encode()).hexdigest()[:24]+'.html');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
 body=clean(POLICIES[spec['policy_url']]).lower()
 if spec.get('policy_kind')=='sss':
  if 'attribution 4.0' not in body and 'creativecommons.org/licenses/by/4.0' not in body:raise ValueError('SSS no longer explicitly offers CC BY 4.0')
 elif spec.get('policy_kind')=='usgs':
  if 'public domain' not in body:raise ValueError('USGS public-domain statement missing')
 else:
  if not any(s in body for s in ['not subject to copyright','may be used for any purpose','not protected by copyright']):raise ValueError('Official media permission not verified')
 return {k:v for k,v in spec.items() if k in ('page_url','file_url','author','license','license_url','policy_url') }|{'license_evidence':'Página de crédito específica y política oficial consultadas en esta ejecución'}

def read_image(path):
 if path.suffix.lower() in ('.exr','.svg'):
  magick=shutil.which('magick')
  if not magick:raise RuntimeError('ImageMagick required for EXR/SVG; marker retained')
  png=CACHE/'procesados'/(path.stem+'.png');png.parent.mkdir(parents=True,exist_ok=True)
  args=[magick,str(path)]
  if path.suffix.lower()=='.exr':args+=['-colorspace','sRGB']
  args+=['-strip',str(png)];subprocess.run(args,check=True,timeout=120,capture_output=True)
  return Image.open(png).copy()
 return Image.open(path).copy()

def contain(im,size,bg=(0,0,0)):
 out=Image.new('RGB',size,bg)
 if im.mode=='RGBA':
  base=Image.new('RGBA',im.size,bg+(255,));base.alpha_composite(im);im=base.convert('RGB')
 thumb=ImageOps.contain(im.convert('RGB'),size,Image.Resampling.LANCZOS);out.paste(thumb,((size[0]-thumb.width)//2,(size[1]-thumb.height)//2));return out

def disc(im,size,white_bg=False):
 """Flood-remove only the connected external background, not dark craters."""
 im=im.copy();im.thumbnail((1000,1000),Image.Resampling.LANCZOS)
 im=im.convert('RGBA');a=np.array(im);rgb=a[:,:,:3]; threshold=np.min(rgb,axis=2)>235 if white_bg else np.max(rgb,axis=2)<18
 if not white_bg:
  yy,xx=np.mgrid[:im.height,:im.width];threshold |= np.hypot(xx-(im.width-1)/2,yy-(im.height-1)/2)>.495*min(im.size)
 # Pillow floodfill finds background connected to the canvas border.
 mark=Image.fromarray(np.uint8(threshold)*255).copy()
 for seed in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]:
  if mark.getpixel(seed)==255:ImageDraw.floodfill(mark,seed,128)
 alpha=np.where(np.array(mark)==128,0,255).astype('uint8')
 a[:,:,3]=np.minimum(a[:,:,3],alpha);cut=Image.fromarray(a);bbox=cut.getbbox()
 if not bbox:raise ValueError('Empty extracted disc')
 cut=cut.crop(bbox);cut=ImageOps.contain(cut,(round(size[0]*.94),round(size[1]*.94)),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',size);out.alpha_composite(cut,((size[0]-cut.width)//2,(size[1]-cut.height)//2));return out

def sun(im,size,rgba):
 # One dated SDO HMI intensitygram for BOTH solar discs; exclude timestamp strip.
 a=np.asarray(im.convert('RGB')); h,w=a.shape[:2]; yy,xx=np.mgrid[:h,:w]
 mask=(a.max(axis=2)>45)&((xx-w/2)**2+(yy-h/2)**2<(min(w,h)*.49)**2)
 ys,xs=np.where(mask);cx=(xs.min()+xs.max())/2;cy=(ys.min()+ys.max())/2;r=min(xs.max()-xs.min(),ys.max()-ys.min())/2
 crop=im.crop((round(cx-r),round(cy-r),round(cx+r),round(cy+r))).convert('RGB')
 square=ImageOps.fit(crop,(min(size),min(size)),Image.Resampling.LANCZOS)
 out=Image.new('RGBA' if rgba else 'RGB',size,(0,0,0,0) if rgba else (0,0,0));x=(size[0]-square.width)//2;y=(size[1]-square.height)//2
 if rgba:
  n=square.width;Y,X=np.mgrid[:n,:n];rad=np.hypot(X-(n-1)/2,Y-(n-1)/2);alpha=np.uint8(np.clip((n/2-1-rad)*255,0,255));square=square.convert('RGBA');square.putalpha(Image.fromarray(alpha))
 out.paste(square,(x,y));return out

def extend_portrait(im,size):
 bg=ImageOps.fit(im.convert('RGB'),size,Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(35))
 fg=ImageOps.contain(im.convert('RGB'),size,Image.Resampling.LANCZOS); bg.paste(fg,((size[0]-fg.width)//2,(size[1]-fg.height)//2));return bg

def nile(im,size):
 """Similarity in geographic equirectangular coordinates; align the TWO fixed dots."""
 # Imagery is global plate carree lon -180..180 and lat +90..-90.
 a=np.array([(29.9187+180)/360*im.width,(90-31.2001)/180*im.height])
 b=np.array([(32.8998+180)/360*im.width,(90-24.0889)/180*im.height])
 framew=128/9;target_a=np.array([(-5.61+framew/2)/framew*size[0],(4+.8)/8*size[1]])
 target_b=np.array([(2.78+framew/2)/framew*size[0],(4-1.12)/8*size[1]])
 src=complex(*(b-a));dst=complex(*(target_b-target_a));z=dst/src
 A=np.array([[z.real,-z.imag],[z.imag,z.real]]);inv=np.linalg.inv(A);off=a-inv@target_a
 coeff=tuple(inv[0])+ (off[0],)+tuple(inv[1])+(off[1],)
 out=im.convert('RGB').transform(size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
 return out

def eclipse(im,size):
 """Recompose OBSERVED phases to the existing scene's fixed circle anchors."""
 base=contain(im,(1920,1080))
 crops=[(387,841,200),(925,853,198),(987,309,39),(1435,869,206)]
 phases=[]
 for cx,cy,r in crops:
  cut=base.crop((cx-r,cy-r,cx+r,cy+r)).convert('RGBA')
  yy,xx=np.mgrid[:cut.height,:cut.width];alpha=np.uint8(np.clip((r-2-np.hypot(xx-r,yy-r))*255,0,255));cut.putalpha(Image.fromarray(alpha));phases.append(cut)
 out=Image.new('RGB',size,'black');fw=128/9;radius=.62*size[1]/8;diam=round(2*radius)
 points=[(-1,-.167,0)]
 for y,index in zip([1.86,.62,-.62,-1.86],range(4)):
  points.append((1.503-y*math.sin(math.radians(8)),-.043+y*math.cos(math.radians(8)),index))
 for x,y,index in points:
  cx=(x+fw/2)/fw*size[0];cy=(4-y)/8*size[1]
  cut=phases[index].resize((diam,diam),Image.Resampling.LANCZOS);out.paste(cut,(round(cx-diam/2),round(cy-diam/2)),cut)
 return out

ADJ='''AL:FL,GA,MS,TN;AZ:CA,NV,UT,NM;AR:LA,MS,MO,OK,TN,TX;CA:NV,OR;CO:KS,NE,NM,OK,UT,WY;CT:MA,NY,RI;DE:MD,NJ,PA;FL:GA;GA:NC,SC,TN;ID:MT,NV,OR,UT,WA,WY;IL:IN,IA,KY,MO,WI;IN:KY,MI,OH;IA:MN,MO,NE,SD,WI;KS:MO,NE,OK;KY:MO,OH,TN,VA,WV;LA:MS,TX;ME:NH;MD:PA,VA,WV;MA:NH,NY,RI,VT;MI:OH,WI;MN:ND,SD,WI;MS:TN;MO:NE,OK,TN;MT:ND,SD,WY;NE:SD,WY;NV:OR,UT;NH:VT;NJ:NY,PA;NM:OK,TX;NY:PA,VT;NC:SC,TN,VA;ND:SD;OH:PA,WV;OK:TX;OR:WA;PA:WV;SD:WY;TN:VA;UT:WY;VA:WV'''
def colored_states(path,size):
 g={s:set() for s in 'AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split()}
 for part in ADJ.split(';'):
  a,bs=part.split(':')
  for b in bs.split(','):g[a].add(b);g[b].add(a)
 g['DC'].update(['MD','VA']);g['MD'].add('DC');g['VA'].add('DC')
 colors={}
 def solve():
  if len(colors)==len(g):return True
  s=max((s for s in g if s not in colors),key=lambda s:(len({colors[x] for x in g[s] if x in colors}),len(g[s])))
  for c in range(4):
   if all(colors.get(t)!=c for t in g[s]):
    colors[s]=c
    if solve():return True
    del colors[s]
  return False
 assert solve() and all(colors[a]!=colors[b] for a in g for b in g[a])
 tree=ET.parse(path);root=tree.getroot();palette=['#e6ae51','#6cb6ad','#b5a6cf','#dc8885'];found=set()
 for elem in root.iter():
  codes=[x.upper() for x in elem.get('class','').split() if x.upper() in colors]
  if codes:elem.set('style','fill:'+palette[colors[codes[0]]]+';stroke:#303843;stroke-width:0.7');found.add(codes[0])
 assert len(found)>=50, f'Only {len(found)} state paths recognized'
 tmp=CACHE/'procesados/us_four_colors.svg';tmp.parent.mkdir(exist_ok=True,parents=True);tree.write(tmp)
 return contain(read_image(tmp),size,(248,248,245))

def flag(size):
 w,h=size;im=Image.new('RGB',size,'white');d=ImageDraw.Draw(im);red='#B31942';blue='#0A3161'
 for i in range(13):
  if i%2==0:d.rectangle((0,round(i*h/13),w,round((i+1)*h/13)-1),fill=red)
 cw=.76*h;ch=7*h/13;d.rectangle((0,0,round(cw)-1,round(ch)-1),fill=blue)
 radius=.0616*h/2
 for row in range(9):
  count=6 if row%2==0 else 5
  for col in range(count):
   cx=(col*2+1+(row%2))*.063*h;cy=(row+1)*.054*h
   pts=[]
   for k in range(10):
    r=radius if k%2==0 else radius*.381966;angle=-math.pi/2+k*math.pi/5;pts.append((cx+r*math.cos(angle),cy+r*math.sin(angle)))
   d.polygon(pts,fill='white')
 return im


def process(spec,info,row):
 size=(int(row['ancho']),int(row['alto']));kind=spec.get('process','cover')
 if kind=='flag':return flag(size)
 if spec.get('pdf_page'):
  res=api(action='query',prop='imageinfo',iiprop='url',titles=spec['title'],iiurlwidth=1200,iiurlparam=f"page{spec['pdf_page']}-1200px")
  ii=next(iter(res['query']['pages'].values()))['imageinfo'][0];p=cached(ii['thumburl'].split('?')[0],'.jpg')
 else:p=cached(info['file_url'])
 info['download_size_bytes']=p.stat().st_size
 if not spec.get('pdf_page'):info['source_size_bytes']=p.stat().st_size
 info['source_sha256']=digest(p)
 if kind=='texture' and p.suffix.lower() in ('.jpg','.jpeg'):
  im=Image.open(p);im.draft('RGB',size);im=im.copy()
 else:im=read_image(p)
 if kind=='signature_card':
  # Only the documentary signature card uses this processor. Recheck identity too.
  check=api(action='query',prop='imageinfo',iiprop='extmetadata',titles=spec['title'])
  metadata=next(iter(check['query']['pages'].values()))['imageinfo'][0]['extmetadata']
  description=clean(metadata.get('ImageDescription',{}).get('value',''))
  if 'goldbach' not in description.lower() or 'goldbach' not in info.get('author','').lower():
   raise ValueError('La descripción y autor de Commons no identifican la firma de Goldbach')
  rgba=im.convert('RGBA');white=Image.new('RGBA',rgba.size,'white');white.alpha_composite(rgba)
  mask=ImageOps.invert(white.convert('L'));bbox=mask.point(lambda v:255 if v>32 else 0).getbbox()
  if not bbox:raise ValueError('Firma vacía')
  mask=mask.crop(bbox);width=round(size[0]*spec.get('signature_width',.8))
  mask=mask.resize((width,round(mask.height*width/mask.width)),Image.Resampling.LANCZOS)
  mask=mask.filter(ImageFilter.MaxFilter(3))
  card=Image.new('RGB',size,spec.get('paper','#F3EBDD'))
  ImageDraw.Draw(card).rectangle((36,48,size[0]-37,size[1]-49),outline='#B5AA99',width=2)
  card.paste(spec.get('ink','#302B27'),((size[0]-mask.width)//2,(size[1]-mask.height)//2),mask)
  return card
 if kind=='states':return colored_states(p,size)
 if kind=='nile':return nile(im,size)
 if kind=='eclipse':return eclipse(im,size)
 if kind=='disc':return disc(im,size,spec.get('white_bg',False))
 if kind=='sun':return sun(im,size,row['modo']=='RGBA')
 if kind=='alpha_lines':
  gray=im.convert('L').resize(size,Image.Resampling.LANCZOS);out=Image.new('RGBA',size,'white');out.putalpha(gray);return out
 if kind=='texture':
  assert im.width==2*im.height, f'Not an equirectangular 2:1 source: {im.size}'
  return im.convert('RGB').resize(size,Image.Resampling.LANCZOS)
 if kind=='extend':
  if spec.get('crop'):im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(spec['crop'])))
  return extend_portrait(im,size)
 if kind=='contain':return contain(im,size)
 if spec.get('crop'):im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(spec['crop'])))
 return ImageOps.fit(im.convert('RGB'),size,Image.Resampling.LANCZOS,centering=tuple(spec.get('centering',[.5,.35])))


def save(im,dest,mode):
 im=im.convert(mode);temp=dest.with_name(dest.stem+'.tmp'+dest.suffix);dest.parent.mkdir(parents=True,exist_ok=True)
 opts={'quality':92,'optimize':True} if dest.suffix.lower() in ('.jpg','.jpeg') else {'compression':'tiff_adobe_deflate'} if dest.suffix.lower() in ('.tif','.tiff') else {'optimize':True}
 im.save(temp,**opts)
 with Image.open(temp) as check:assert check.size==im.size and check.mode==mode
 temp.replace(dest)

def reports(records):
 AUDIT.mkdir(parents=True,exist_ok=True)
 fields=['n','asset','estado','decision_repo','motivo','licencia','licencia_url','autor','fuente','archivo_url','bytes_final','bytes_original','sha256','cambios','revision_escena']
 lines=['# Progreso de descargas y assets libres','','Criterio de repo: se recomienda incluir la versión final si su licencia está verificada y pesa como máximo 10 MiB. Los originales y las evidencias temporales quedan en caché, fuera del repo. No se publica nada.','','| # | Asset | Estado | Fuente final | Licencia | Nota |','|---:|---|---|---|---|---|']
 csvrows=[]
 for row in ROWS:
  rec=records.get(row['asset'],{});state='hecha' if rec.get('status') in ('replaced','kept') else 'saltada' if rec.get('status')=='skipped' else 'pendiente'
  note=rec.get('note','');url=rec.get('page_url','');lic=rec.get('license','')
  lines.append(f"| {row['n']} | `{row['asset']}` | {state} | {url} | {lic} | {note.replace('|','/')} |")
  csvrows.append(dict(zip(fields,[row['n'],row['asset'],state,rec.get('repo_decision','pendiente'),note,lic,rec.get('license_url',''),rec.get('author',''),url,rec.get('file_url',''),rec.get('final_size_bytes',''),rec.get('source_size_bytes',''),rec.get('sha256',''),rec.get('changes',''),MANIFEST[row['n']].get('scene_note','Revisado uso en _work sin .orig.py; mismo tamaño y modo.')])))
 ok=sum(r['estado']=='hecha' for r in csvrows);skip=sum(r['estado']=='saltada' for r in csvrows)
 lines+=['','## Resumen',f'{ok} hechas; {skip} saltadas; {len(ROWS)-ok-skip} pendientes.','', 'Licencias que requieren atribución:']
 lines += [f"- {r['asset']}: {r['licencia']} — {r['autor']}." for r in csvrows if r['estado']=='hecha' and r['licencia'].startswith('CC BY')]
 lines+=['','Saltadas y motivo:']+[f"- {r['asset']}: {r['motivo']}" for r in csvrows if r['estado']=='saltada']
 lines+=['','Revisión del coordinador: los archivos locales duplicados en _work no se modifican; el setup debe propagar los assets centrales. Nile se georreferencia a los dos rótulos fijos; JovianSystem es un montaje documental y no una órbita medida (la escena no añade la imagen). El Sol 2:1 de Solar System Scope es una textura visual CC BY 4.0, no un mapa científico completo de la fotosfera. Revisar DarkMoonTexture, fuera de la lista, para que concuerde con la nueva Luna; GalaxyStill es una foto de NGC4414 usada de forma ilustrativa, no una vista de la Vía Láctea ni posiciones medidas del Sol.','', 'Criterio aplicado: 10 MiB por archivo final (ajustable con REPO_MAX), no un límite técnico de Git. El TIFF solar usa Deflate sin pérdida; todas las versiones finales actuales caben en este criterio. Originales grandes: NASA Hipparcos/Tycho EXR y mapas TIFF/USGS se descargan en caché; las versiones finales comprimidas son las candidatas para el repositorio. Nunca se relaja una licencia por usar un descargador.']
 batch=[r for r in csvrows if int(r['n'])>=44]
 lines+=['','## Tanda DESCARGAS_2',f"Filas 44–59: {sum(r['estado']=='hecha' for r in batch)} hechas; {sum(r['estado']=='saltada' for r in batch)} saltadas; {sum(r['estado']=='pendiente' for r in batch)} pendientes. Fuentes verificadas de forma independiente; solo esta tanda se sustituye. Comparación en REVISION_DESCARGAS_2.png; las hojas anteriores no se regeneran al ejecutar solo 44–59."]
 (AUDIT/'PROGRESO_DESCARGAS.md').write_text('\n'.join(lines)+'\n')
 with (AUDIT/'SITUACION_ASSETS.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(csvrows)

def write_attributions(records):
 lines=['# Atribuciones de los assets descargados','', 'Las licencias de estos archivos se conservan independientemente de la licencia del código del repositorio. Las obras CC BY-SA y sus adaptaciones continúan bajo la licencia indicada; no se presentan como obra propia ni implican respaldo de NASA u otros autores.','']
 for row in ROWS:
  r=records.get(row['asset'],{})
  if r.get('status') not in ('replaced','kept'):
   r=r.get('retained_provenance',{})
   if not r:continue
  lines += [f"## {row['n']}. `{row['asset']}`",'',f"- Autor/crédito: {r.get('author','')}",f"- Licencia: [{r.get('license','')}]({r.get('license_url','')})",f"- Fuente: {r.get('page_url','')}",f"- Cambios: {r.get('changes','')}",'']
 (HERE/'ATTRIBUTIONS_DOWNLOADS.md').write_text('\n'.join(lines))

def contact_sheet(records):
 sheet=Image.new('RGB',(1600,math.ceil(len(ROWS)/6)*200),'#272b33');d=ImageDraw.Draw(sheet)
 for i,row in enumerate(ROWS):
  x=(i%6)*266;y=(i//6)*200;path=ASSETS/row['asset'];rec=records.get(row['asset'],{})
  if path.exists():
   im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#555962');bg.alpha_composite(im);thumb=ImageOps.contain(bg.convert('RGB'),(250,157),Image.Resampling.LANCZOS);sheet.paste(thumb,(x+(260-thumb.width)//2,y+28))
  label=f"{row['n']} {Path(row['asset']).name}";d.text((x+5,y+4),label[:39],fill='white');d.text((x+5,y+184),rec.get('status','pendiente'),fill='#80dd9a' if rec.get('status') in ('replaced','kept') else '#f5b56e')
 sheet.save(AUDIT/'REVISION_DESCARGAS.png')

def native_review(records):
 """Native-pixel review sheet: no resampling; locations in a companion index."""
 free=[(0,0,12288,22000)];placements=[]
 for row in sorted(ROWS,key=lambda r:int(r['ancho'])*int(r['alto']),reverse=True):
  w,h=int(row['ancho']),int(row['alto']);choices=[(fw*fh,i) for i,(x,y,fw,fh) in enumerate(free) if w<=fw and h<=fh]
  if not choices:raise ValueError('Native review packing overflow')
  _,i=min(choices);x,y,fw,fh=free.pop(i);placements.append((row,x,y,w,h))
  if fw>w:free.append((x+w,y,fw-w,h))
  if fh>h:free.append((x,y+h,fw,fh-h))
 height=max(y+h for _,x,y,w,h in placements);sheet=Image.new('RGB',(12288,height),'#272b33');index=[]
 for row,x,y,w,h in placements:
  im=Image.open(ASSETS/row['asset']).convert('RGBA');bg=Image.new('RGBA',(w,h),'#555962');bg.alpha_composite(im);sheet.paste(bg.convert('RGB'),(x,y))
  index.append({'n':row['n'],'asset':row['asset'],'box':[x,y,x+w,y+h],'size':[w,h]})
 sheet.save(AUDIT/'REVISION_DESCARGAS_NATIVA.png',compress_level=6)
 atomic_json(HERE/'review_details/native_sheet_index.json',index)
 print(f'Native review: 12288 x {height} pixels, 43 assets without resizing',flush=True)

def contact_sheet_2(records):
 """Only the new batch: compare cached Grant files with verified replacements."""
 rows=[r for r in ROWS if int(r['n'])>=44]
 sheet=Image.new('RGB',(1600,math.ceil(len(rows)/4)*350),'#E6E6E2');draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows):
  x=(i%4)*400;y=(i//4)*350
  draw.text((x+8,y+6),row['n']+' '+Path(row['asset']).name,fill='#172B35')
  draw.text((x+40,y+28),'Antes (Grant)',fill='#172B35');draw.text((x+240,y+28),'Fuente libre',fill='#172B35')
  for col,path in enumerate((CACHE/'marcadores'/row['asset'],ASSETS/row['asset'])):
   if not path.exists():continue
   im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
   thumb=ImageOps.contain(bg.convert('RGB'),(190,274),Image.Resampling.LANCZOS)
   sheet.paste(thumb,(x+col*200+(200-thumb.width)//2,y+52+(274-thumb.height)//2))
  draw.text((x+8,y+331),records.get(row['asset'],{}).get('status','pendiente'),fill='#265438')
 sheet.save(AUDIT/'REVISION_DESCARGAS_2.png')


def run(args):
 CACHE.mkdir(parents=True,exist_ok=True); loaded=json.loads(SOURCES.read_text()) if SOURCES.exists() else {};old={r.get('asset',k):r for k,r in loaded.items()};records=dict(old)
 selected=[r for r in ROWS if not args.only or r['n'] in args.only]
 try:commons=verify_commons({MANIFEST[r['n']]['title'] for r in selected if MANIFEST[r['n']].get('title')})
 except Exception as e:commons={};print('Commons verification failed:',e,flush=True)
 for row in selected:
  original=ASSETS/row['asset'];backup=CACHE/'marcadores'/row['asset']
  if original.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,backup)
  spec=MANIFEST[row['n']];asset=row['asset'];dest=ASSETS/asset;print(f"[{row['n']}/{len(ROWS)}] {asset}",flush=True)
  rec={'author':'','license':'','license_url':'','page_url':'','file_url':'','name':Path(asset).name,'asset':asset,'subject':spec.get('subject',row['que_es']),'status':'skipped','changes':spec.get('changes','Recorte/reescala al tamaño y modo del marcador.'),'verified_at':datetime.now(timezone.utc).isoformat()}
  try:
   if spec.get('skip'):
    rec['page_url']=spec.get('research_url','');raise ValueError(spec['skip'])
   if spec.get('title'):
    info=commons.get(spec['title'])
    if not info:raise ValueError('No se obtuvo licencia admisible en Commons en esta ejecución')
   else: info=policy_source(spec)
   if spec.get('source_url'):
    info['commons_file_url']=info['file_url'];info['file_url']=spec['source_url']
   rec.update(info)
   for k in ('source_size_bytes','source_sha256','download_size_bytes','commons_file_url'):
    if k not in rec and k in old.get(asset,{}):rec[k]=old[asset][k]
   if not spec.get('pdf_page'):
    url=info.get('file_url','');ext=Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).suffix or '.bin'
    raw=CACHE/'originales'/(hashlib.sha256(url.encode()).hexdigest()[:24]+ext)
    if raw.exists():rec.update(source_size_bytes=raw.stat().st_size,source_sha256=digest(raw))
   expected=(int(row['ancho']),int(row['alto']))
   intact=old.get(asset,{}).get('sha256') and dest.exists() and digest(dest)==old[asset]['sha256']
   if not args.sources_only:
    if not intact or args.force:
     im=process(spec,info,row)
     if im.size!=expected:raise ValueError(f'Unexpected size {im.size}, expected {expected}')
     # Backup existing marker exactly once, BEFORE any replacement.
     backup=CACHE/'marcadores'/asset
     if dest.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
     save(im,dest,row['modo'])
     rec.update({k:info[k] for k in ('source_size_bytes','source_sha256','download_size_bytes','commons_file_url') if k in info})
    with Image.open(dest) as check:assert check.size==expected and check.mode==row['modo'];check.verify()
    rec.update(status='kept' if intact and not args.force else 'replaced',final_size_bytes=dest.stat().st_size,sha256=digest(dest))
    rec['repo_decision']='incluir_directamente' if dest.stat().st_size<=REPO_MAX else 'recrear_con_script_por_tamano'
    rec['note']=('Licencia verificada; versión final ligera apta para incluir en repo.' if rec['repo_decision']=='incluir_directamente' else 'Licencia permite redistribuir; final >10 MiB, se recomienda regenerarlo con el script.')+' '+spec.get('note','')
   else:
    for k in ('sha256','final_size_bytes','repo_decision'):
     if k in old.get(asset,{}):rec[k]=old[asset][k]
    rec.update(status=old.get(asset,{}).get('status','verified'),note='Licencia verificada sin escribir imagen.')
  except Exception as e:
   rec.update(status='skipped',repo_decision='descargar_con_script' if rec.get('license') else 'no_incluir_sin_resolver',note=str(e));print('  SALTADA:',e,flush=True)
   # If a previously installed asset exists, retain its attribution as provenance.
   if old.get(asset,{}).get('sha256') and dest.exists() and digest(dest)==old[asset]['sha256']:rec['retained_provenance']=old[asset]
  records[asset]=rec;atomic_json(SOURCES,{r['name']:r for r in records.values()});reports(records)
 if any(int(r["n"])<=43 for r in selected):contact_sheet(records)
 if any(int(r["n"])>=44 for r in selected):contact_sheet_2(records)
 write_attributions(records)
 if args.review_native:native_review(records)
 print('Finished. See PROGRESO_DESCARGAS.md and SITUACION_ASSETS.csv',flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',nargs='+',choices=[r['n'] for r in ROWS]);ap.add_argument('--force',action='store_true');ap.add_argument('--sources-only',action='store_true');ap.add_argument('--review-native',action='store_true');a=ap.parse_args();run(a)
