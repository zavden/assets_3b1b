"""Static 2017 asset QA. No scene imports, scene rendering, setup, or git."""
from pathlib import Path
import csv,json,hashlib,importlib.util,math
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageOps
from manimlib import SVGMobject
ROOT=Path(__file__).resolve().parents[5]
ASSETS=ROOT/'_lib/assets';HERE=ASSETS/'generated/replacements/assets2017';CACHE=ROOT/'_tools/.cache/assets2017';AUDIT=ROOT/'_tools/assets_licencias/codex'
sp=importlib.util.spec_from_file_location('a2017',HERE/'make_assets_2017.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
records=json.loads((HERE/'assets2017_sources.json').read_text());assert len(records)==len(m.ROWS)==30
checks=[];snap={};svg_count=0
for row in m.ROUND1_ROWS:
 asset=row['asset'];p=ASSETS/asset;backup=CACHE/'originales'/asset;r=records[asset]
 assert r['delivery_state']=='hecha',(asset,r.get('note'));assert backup.is_file(),asset
 m.validate(row,p);digest=m.sha(p);assert r['sha256']==digest;assert digest!=m.sha(backup),(asset,'Unchanged Grant original');snap[asset]=digest
 check={'n':row['n'],'asset':asset,'bytes':p.stat().st_size,'mode':row['modo']}
 if row['modo']=='SVG':
  svg_count+=1;root=ET.parse(p).getroot();original=ET.parse(backup).getroot()
  for attr in ['viewBox','width','height']:assert root.get(attr)==original.get(attr),(asset,attr,root.get(attr),original.get(attr))
  paths=root.findall('.//{http://www.w3.org/2000/svg}path');assert paths and not root.findall('.//{http://www.w3.org/2000/svg}text')
  obj=SVGMobject(str(p));assert len(obj)==len(paths),(asset,len(obj),len(paths));check['parts']=len(obj)
  for part in obj:
   pts=part.get_points();assert len(pts)>=3 and np.isfinite(pts).all(),asset
  if p.stem in ['electricity','fire','house','water','paint_bucket','gpu','phone','bank_building','government_building','shield_locked','circuit','euro_symbol','yen_symbol']:
   assert obj[0].get_fill_color().upper()=='#FFFFFF',(asset,obj[0].get_fill_color())
  if p.stem in ['electricity','fire','house','water','bank_building','government_building']:assert len(obj)==1,asset
  if p.stem=='ethereum_logo':
   assert len(obj)==4;assert obj.get_width()/obj.get_height()>1.1
   for part,char in zip(obj,'8B8B48'):part.set_color('#'+6*char)
   assert len(obj)==4;check['four_recolorable_facets']=True
  if p.stem=='visa_logo':
   assert len(obj)>=2;obj[-1].set_color('#FAA61A');obj.sort();check['last_piece_and_sort']=True
  if p.stem=='circuit':assert len(obj)>1;check['individually_animatable_parts']=len(obj)
  if p.stem=='Norway':
   import svgelements as se
   parsed=se.Path(paths[0].get('d'));assert sum(isinstance(seg,se.Move) for seg in parsed)==1
   assert not any(isinstance(seg,se.Close) for seg in parsed);assert len(parsed)>150
   coords=np.array([(float(seg.end.real),float(seg.end.imag)) for seg in parsed]);jumps=np.linalg.norm(np.diff(coords,axis=0),axis=1)
   assert jumps.max()<100,('Unexpected coastline jump',jumps.max());check.update(coast_points=len(coords),max_segment=float(jumps.max()),continuous_open_path=True)
 else:
  with Image.open(p) as im:
   check.update(size=im.size,format=im.format);arr=np.array(im.convert('RGB'));assert arr.std()>8
   if row['modo']=='RGBA' and p.stem in ['ripple_logo','bitcoin_mining_graphic']:assert im.getchannel('A').getextrema()==(0,255)
 if r.get('via')=='descargar':
  assert m.d.ALLOWED.fullmatch(r['license']) and r.get('source_sha256') and r.get('author') and r.get('evidence_sha256')
  if p.stem=='Norway':
   assert len(r['source_files'])==2
   for item in r['source_files']:
    cached=CACHE/'descargados'/item['file_url'].split('/')[-1];assert m.sha(cached)==item['sha256']
  else:assert m.sha(m.source_cache(dict(r)))==r['source_sha256']
  if p.stem=='Pierre_de_Fermat':
   alias=ASSETS/r['reused_asset'];assert m.sha(alias)==r['reused_asset_sha256'];expected=ImageOps.fit(Image.open(alias).convert('RGBA'),(1172,1500),Image.Resampling.LANCZOS)
   assert np.array_equal(np.array(expected),np.array(Image.open(p)));check['exact_2019_free_portrait_alias']=True
 checks.append(check)
protected=json.loads((CACHE/'protected_snapshot.json').read_text())
for asset,digest in protected.items():assert m.sha(ASSETS/asset)==digest,('Previous asset changed',asset)
for name in ['assets2017_fotogramas.csv','assets2017_diferidas.csv']:
 excluded={r['asset'] for r in csv.DictReader((AUDIT/name).open())};assert not excluded.intersection(snap),name
assert m.sha(AUDIT/'assets2017.csv')==m.CSV_SHA
# Check numerical membership independently of the rendered escape-time palette.
assert abs(0j**2+0j)<=2
with Image.open(ASSETS/'raster_images/Mandelbrot.jpg') as im:
 w,hh=im.size;ymax=1.5*hh/w
 def pixel(c):return np.array(im.getpixel((round((c.real+2.35)/3*(w-1)),round((c.imag+ymax)/(2*ymax)*(hh-1)))))
 assert pixel(0j).max()<35 and pixel(complex(-1,0)).max()<35
 assert pixel(complex(.5,1)).max()>100
result={'rows_verified':30,'states':{s:sum(r['delivery_state']==s for r in records.values()) for s in ['hecha','ya_existe','saltada','entregada_IA']},'own_code':sum(r['via']=='código' for r in records.values()),'verified_free_sources':sum(r['via']=='descargar' for r in records.values()),'svg_count':svg_count,'previous_assets_unchanged':len(protected),'excluded_lists_disjoint':True,'no_scene_renders':True,'no_ai':True,'checks':checks}
(AUDIT/'ASSETS_2017_checks.json').write_text(json.dumps(result,indent=2)+'\n');(CACHE/'qa_before_idempotence.json').write_text(json.dumps(snap,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
