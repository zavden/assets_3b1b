"""Check SVG contracts in the consumer classes without importing or rendering scenes."""
from pathlib import Path
import ast,hashlib,importlib.util,json
import xml.etree.ElementTree as ET
import numpy as np
import manimlib
from manimlib import SVGMobject
ROOT=Path(__file__).resolve().parents[5];ASSETS=ROOT/'_lib/assets';HERE=ASSETS/'generated/replacements/assets2017';AUDIT=ROOT/'_tools/assets_licencias/codex';CACHE=ROOT/'_tools/.cache/assets2017'
sp=importlib.util.spec_from_file_location('a2017',HERE/'make_assets_2017.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
records=json.loads(m.SOURCE.read_text());assert len(records)==54
# Compile the exact two unchanged class definitions, excluding other module code.
module=ast.parse((ROOT/'_lib/custom/drawings.py').read_text());classes=[node for node in module.body if isinstance(node,ast.ClassDef) and node.name in ['BitcoinLogo','PartyHat']];assert len(classes)==2
namespace=dict(vars(manimlib));namespace['__name__']='assets2017_consumer_qa';exec(compile(ast.Module(body=classes,type_ignores=[]),'_lib/custom/drawings.py','exec'),namespace)
hashes={};checks=[]
for row in m.ROUND3_ROWS:
 p=ASSETS/row['asset'];backup=CACHE/'originales'/row['asset'];rec=records[row['asset']];assert rec['delivery_state']=='hecha';assert rec['author']=='propio (código)' and rec['license']=='CC0'
 assert backup.is_file() and m.sha(backup)!=m.sha(p);assert rec['sha256']==m.sha(p);m.validate(row,p);hashes[row['asset']]=m.sha(p)
 root=ET.parse(p).getroot();original=ET.parse(backup).getroot();assert root.get('viewBox')==original.get('viewBox')==row['alto']
 paths=root.findall('.//{http://www.w3.org/2000/svg}path');obj=SVGMobject(str(p));expected=2 if p.stem=='Bitcoin_logo' else 14;assert len(paths)==len(obj)==expected
 for part in obj:assert np.isfinite(part.get_points()).all() and len(part.get_points())>3
 assert not root.findall('.//{http://www.w3.org/2000/svg}text');assert not root.findall('.//{http://www.w3.org/2000/svg}image')
 if expected==2:
  coin=namespace['BitcoinLogo'](file_name=str(p));assert len(coin)==2;assert coin[0].get_width()>coin[1].get_width()*2
  # Recoloring the entire coin must leave a geometric gap around the inner bar.
  import svgelements as se
  from shapely.geometry import Polygon
  def coords(part):return [(float(seg.end.real),float(seg.end.imag)) for seg in part]
  loops=list(se.Path(paths[0].get('d')).as_subpaths());assert len(loops)==2
  outer=Polygon(coords(loops[0]));disc=Polygon(coords(loops[0]),[coords(loops[1])]);mark=Polygon(coords(se.Path(paths[1].get('d'))))
  assert disc.is_valid and mark.is_valid and outer.contains(mark) and disc.distance(mark)>3
  coin.set_color('#F7931A');assert len(coin)==2
  structure=['disco','marca'];consumer='BitcoinLogo'
 else:
  hat=namespace['PartyHat'](file_name=str(p));assert len(hat)==14 and len(hat.frills)==7 and len(hat.dots)==6
  assert hat.cone is hat[7];assert all(hat.frills[i] is hat[i] for i in range(7));assert all(hat.dots[i] is hat[8+i] for i in range(6))
  centers=[hat[i].get_center()[0] for i in range(7)];assert np.all(np.diff(centers)>0)
  assert all(hat[7].get_top()[1]>hat[i].get_top()[1] for i in list(range(7))+list(range(8,14)))
  assert all(hat[7].get_width()>hat[i].get_width()*4 for i in range(8,14));structure=['volante']*7+['cono']+['punto']*6;consumer='PartyHat'
 assert rec['structure_contract']==structure;assert rec['scene_review']['matches'] and rec['scene_review']['consumer_class']['class']==consumer
 checks.append({'asset':row['asset'],'viewBox':row['alto'],'paths':expected,'consumer':consumer,'structure':structure,'bytes':p.stat().st_size})
prior=json.loads((CACHE/'rondas_1_2_entrega/assets2017_sources.json').read_text());assert len(prior)==52
for asset,record in prior.items():assert records[asset]==record,('Previous provenance changed',asset)
protected=json.loads((CACHE/'round3_protected_snapshot.json').read_text())
for asset,digest in protected.items():assert m.sha(ASSETS/asset)==digest,('Previous asset changed',asset)
for name in ['REVISION_2017.png','REVISION_2017_ronda2.png']:assert m.sha(AUDIT/name)==m.sha(CACHE/'rondas_1_2_entrega'/name)
out=AUDIT/'ASSETS_2017_ronda3_checks.json';old=json.loads(out.read_text()) if out.exists() else {}
result={'rows_verified':2,'all_code_cc0':True,'consumer_classes_checked':True,'previous_assets_unchanged':len(protected),'previous_2017_assets_and_provenance_unchanged':52,'previous_contact_sheets_unchanged':True,'no_scene_renders':True,'no_ai':True,'idempotence_all_2_hashes_unchanged':old.get('idempotence_all_2_hashes_unchanged',False),'checks':checks}
out.write_text(json.dumps(result,indent=2)+'\n');(CACHE/'round3_before_idempotence.json').write_text(json.dumps(hashes,indent=2)+'\n');m.progress(records);print(json.dumps(result,indent=2))
