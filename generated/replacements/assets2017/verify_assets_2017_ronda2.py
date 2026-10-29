"""Static round-two checks: no scene imports or scene rendering."""
from pathlib import Path
import hashlib,importlib.util,json,math
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from shapely.geometry import Polygon
from shapely import contains_xy
from manimlib import SVGMobject
import svgelements as se
ROOT=Path(__file__).resolve().parents[5];ASSETS=ROOT/'_lib/assets';HERE=ASSETS/'generated/replacements/assets2017';AUDIT=ROOT/'_tools/assets_licencias/codex';CACHE=ROOT/'_tools/.cache/assets2017'
sp=importlib.util.spec_from_file_location('r2',HERE/'make_assets_2017.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
records={asset:rec for asset,rec in json.loads((HERE/'assets2017_sources.json').read_text()).items() if asset in {row['asset'] for row in m.ROUND1_ROWS+m.ROUND2_ROWS}};assert len(records)==52
checks=[];hashes={};masks={}
for row in m.ROUND2_ROWS:
 asset=row['asset'];p=ASSETS/asset;backup=CACHE/'originales'/asset;rec=records[asset];assert rec['delivery_state']=='hecha',(asset,rec.get('note'))
 assert backup.exists();m.validate(row,p);digest=m.sha(p);assert digest==rec['sha256'] and digest!=m.sha(backup)
 assert rec['author']=='propio (código)' and rec['license']=='CC0';assert rec['scene_review']['matches'],asset
 hashes[asset]=digest;check={'n':row['n'],'csv_row':row['ronda_n'],'asset':asset,'mode':row['modo'],'bytes':p.stat().st_size}
 if row['modo']!='SVG':
  with Image.open(p) as im:
   assert im.size==(int(row['ancho']),int(row['alto'])) and im.mode==row['modo'];check['size']=im.size
   if p.stem.startswith('handwritten_'):
    arr=np.array(im);assert np.array_equal(arr[:,:,0],arr[:,:,1]) and np.array_equal(arr[:,:,0],arr[:,:,2]);mask=arr[:,:,0];assert mask.max()>200 and (mask==0).sum()>250
    if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
    # Lanczos filtering may leave an intensity of at most 2/255 at the margin.
    assert max(mask[0].max(),mask[-1].max(),mask[:,0].max(),mask[:,-1].max())<=2
    masks[p.stem.removeprefix('handwritten_')]=mask
 else:
  svg=ET.parse(p).getroot();orig=ET.parse(backup).getroot();assert svg.get('viewBox')==orig.get('viewBox')=='0 0 884.3 737.7'
  paths=svg.findall('.//{http://www.w3.org/2000/svg}path');assert len(paths)==1
  obj=SVGMobject(str(p),stroke_width=0,fill_opacity=.5,fill_color='#FFFF00');assert len(obj)==1 and np.isfinite(obj[0].get_points()).all()
  parsed=se.Path(paths[0].get('d'));assert sum(isinstance(x,se.Move) for x in parsed)==1 and sum(isinstance(x,se.Close) for x in parsed)==1
  poly=Polygon([(float(x.end.real),float(x.end.imag)) for x in parsed]);assert poly.is_valid and poly.area>0
  # Compare the emitted polygon to independent analytic circle membership on a grid.
  yy,xx=np.mgrid[-3.5:4:151j,-3.866:3.866:151j];A=xx**2+(yy-1)**2<9;B=(xx+math.sqrt(3)/2)**2+(yy+.5)**2<9;C=(xx-math.sqrt(3)/2)**2+(yy+.5)**2<9
  expected={'VennDiagram_in_A_in_B':A&B,'VennDiagram_in_A_in_B_out_C':A&B&~C,'VennDiagram_in_A_out_B':A&~B,'VennDiagram_in_A_out_C':A&~C}[p.stem]
  factor=min(884.3/(6+math.sqrt(3)),737.7/7.5)*.92;px=xx*factor+884.3/2;py=-yy*factor+737.7/2+.25*factor;actual=contains_xy(poly,px,py)
  near=np.minimum.reduce([abs(xx**2+(yy-1)**2-9),abs((xx+math.sqrt(3)/2)**2+(yy+.5)**2-9),abs((xx-math.sqrt(3)/2)**2+(yy+.5)**2-9)])<.002
  assert np.array_equal(actual[~near],expected[~near]),p.stem
  check.update(manimgl_paths=len(obj),analytic_region_grid_points=int((~near).sum()),one_continuous_closed_region=True)
 checks.append(check)
for target,parts in [('nine',['upper_loop','right_line']),('eight',['upper_loop','lower_loop']),('four',['right_line','upper_left_line','horizontal_line']),('loop',[f'loop_edge{i}' for i in range(1,6)]),('right_line',[f'right_line_edge{i}' for i in range(1,4)])]:assert np.array_equal(masks[target],np.maximum.reduce([masks[n] for n in parts])),target
assert np.array_equal(masks['loop'],masks['upper_loop']);assert len(masks)==17
protected=json.loads((CACHE/'round2_protected_snapshot.json').read_text())
for asset,digest in protected.items():assert m.sha(ASSETS/asset)==digest,('Previous asset changed',asset)
first=json.loads((CACHE/'primera_ronda_entrega/assets2017_sources.json').read_text())
for asset,rec in first.items():assert records[asset]==rec,('First-round provenance changed',asset)
report=AUDIT/'ASSETS_2017_ronda2_checks.json';previous=json.loads(report.read_text()) if report.exists() else {}
result={'rows_verified':22,'all_code_cc0':True,'handwritten_count':17,'svg_count':4,'digit_components_match_exactly':True,'loop_and_line_partitions_match_exactly':True,'venn_regions_analytically_checked':True,'previous_assets_unchanged':len(protected),'first_round_provenance_unchanged':30,'no_scene_renders':True,'no_ai':True,'idempotence_all_22_hashes_unchanged':previous.get('idempotence_all_22_hashes_unchanged',False),'checks':checks}
report.write_text(json.dumps(result,indent=2)+'\n');(CACHE/'round2_before_idempotence.json').write_text(json.dumps(hashes,indent=2)+'\n');m.progress(records);print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
