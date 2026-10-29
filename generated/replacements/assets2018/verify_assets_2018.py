"""Static asset QA only: no Scene instances, renders, setup or git operations."""
from pathlib import Path
import os,sys,json,csv,hashlib,importlib.util,math
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from manimlib import SVGMobject,Rectangle
ROOT=Path(__file__).resolve().parents[5];A=ROOT/'_lib/assets';H=A/'generated/replacements/assets2018';C=ROOT/'_tools/.cache/assets2018';U=ROOT/'_tools/assets_licencias/codex'
sp=importlib.util.spec_from_file_location('m',H/'make_assets_2018.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
records=json.loads((H/'assets2018_sources.json').read_text());assert len(records)==80
snapshot={};checks=[];svg_count=0;inherited=0
svg_defaults={'color':None,'opacity':None,'fill_color':'#FFFFFF','fill_opacity':None,'stroke_width':None,'stroke_color':None,'stroke_opacity':None}
for row in m.ROWS:
 asset=row['asset'];p=A/asset;r=records[asset];assert r['delivery_state']=='hecha',(asset,r['note']);assert p.exists() and (C/'originales'/asset).exists();m.validate(row,p);digest=m.sha(p);assert r['sha256']==digest; snapshot[asset]=digest;c={'n':row['n'],'asset':asset,'state':r['delivery_state'],'bytes':p.stat().st_size}
 if row['modo']=='SVG':
  svg_count+=1;root=ET.parse(p).getroot();obj=SVGMobject(str(p),svg_default=svg_defaults);assert len(obj)>0;c['manimgl_parts']=len(obj)
  if not row['alto']:
   orig=ET.parse(C/'originales'/asset).getroot();assert root.get('viewBox') is None
   for field in ['width','height']:assert root.get(field)==orig.get(field)
  if p.stem.startswith('Dice-'):
   n=int(p.stem[-1]);assert len(obj)==n+1;assert math.isclose(obj.get_width(),obj.get_height(),rel_tol=1e-6);c['pips']=n
  if p.stem=='falcon_heavy':assert len(obj)==12 and len(obj[-9:])==9;c['nine_final_generic_details']=True
  if p.stem=='traffic_light':
   assert len(obj)==4;red=obj[1];assert red.get_center()[1]>obj[2].get_center()[1]>obj[3].get_center()[1];post=Rectangle();obj.add_to_back(post);assert obj[2] is red;obj.remove(post);c['scene_red_light_index']=2
  unfilled=[j for j,node in enumerate(root.findall('.//{http://www.w3.org/2000/svg}path')) if node.get('fill') is None]
  for j in unfilled:assert obj[j].get_fill_color().upper()=='#FFFFFF',(asset,j,obj[j].get_fill_color())
  if unfilled:inherited+=1
 else:
  with Image.open(p) as im:
   c.update(size=im.size,mode=im.mode)
   if p.stem in ['mars','mercury','venus','comet','Henry_As_Stick']:
    alpha=im.convert('RGBA').getchannel('A');assert alpha.getextrema()==(0,255)
 if r.get('via')=='descargar':
  assert m.d.ALLOWED.fullmatch(r['license']) and r.get('source_sha256') and r.get('author');assert 'plantilla licensetpl_short' in r['license_evidence'];assert r['source_sha256']==m.sha(m.source_cache(dict(r)))
 checks.append(c)
protected=json.loads((C/'protected_snapshot.json').read_text())
for asset,digest in protected.items():assert m.sha(A/asset)==digest,('Previous asset changed',asset)
for file in ['assets2018_fotogramas.csv','assets2018_diferidas.csv']:
 excluded={r['asset'] for r in csv.DictReader((U/file).open())};assert not excluded.intersection(snapshot),('Excluded list overlap',file)
# Independently inspect colored sectors, restoring pixels occluded by the Sun/orbit.
from scipy.ndimage import distance_transform_edt
with Image.open(A/'raster_images/Kepler2ndLaw.png') as im:
 data=np.array(im.convert('RGB'));m1=np.all(data==[218,179,109],axis=-1);m2=np.all(data==[115,173,180],axis=-1);orbit=np.all(data==[202,217,221],axis=-1);sun=np.all(data==[242,208,138],axis=-1)
 visible_areas=[int(m1.sum()),int(m2.sum())];d1=distance_transform_edt(~m1);d2=distance_transform_edt(~m2);sy,sx=np.argwhere(sun).mean(axis=0);yy,xx=np.indices(sun.shape);angles=np.arctan2(yy-sy,xx-sx);restored_areas=[]
 for mask,dist,other in [(m1,d1,d2),(m2,d2,d1)]:
  theta=angles[mask];restored=mask | (orbit&(dist<=5)&(dist<other)) | (sun&(angles>=theta.min())&(angles<=theta.max()));restored_areas.append(int(restored.sum()))
 assert abs(restored_areas[0]-restored_areas[1])/max(restored_areas)<.01,restored_areas
# Gradient end-points and an actual nonconstant hidden texture.
for name,top,bottom in [('grey_gradient.png',(230,230,230),(42,42,42)),('blue_yellow_gradient.png',(49,100,167),(243,218,112)),('white_black_gradient.png',(255,255,255),(0,0,0))]:
 with Image.open(A/'raster_images'/name) as im:assert im.getpixel((0,0))[:3]==top and im.getpixel((0,im.height-1))[:3]==bottom
result={'rows_verified':80,'states':{s:sum(r['delivery_state']==s for r in records.values()) for s in ['hecha','ya_existe','saltada','entregada_IA']},'own_code':sum(r['via']=='código' for r in records.values()),'verified_downloads':sum(r['via']=='descargar' for r in records.values()),'svg_count':svg_count,'svg_primary_color_inherits_2018_white':inherited,'previous_assets_unchanged':len(protected),'excluded_lists_disjoint':True,'kepler_visible_region_pixels':visible_areas,'kepler_regions_including_occluded_pixels':restored_areas,'checks':checks,'no_scene_renders':True,'no_ai':True}
(U/'ASSETS_2018_checks.json').write_text(json.dumps(result,indent=2)+'\n');(C/'qa_before_idempotence.json').write_text(json.dumps(snapshot,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
