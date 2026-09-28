from pathlib import Path
import subprocess, concurrent.futures, json
from verify import ROOT, verify

def render(path):
 for fmt in ('svg','png'):
  subprocess.run(['plantuml','-charset','UTF-8','-t'+fmt,str(path)],check=True)
 return str(path.relative_to(ROOT))

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for item in pool.map(render,sorted(ROOT.glob('Task*/diagrams/*.puml'))):print('Rendered',item,flush=True)
 result=verify()
 (ROOT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS',len(result['diagrams']),'diagrams;',result['links_checked'],'links')
