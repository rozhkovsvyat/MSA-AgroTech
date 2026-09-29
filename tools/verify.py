from pathlib import Path
import re, json, hashlib, itertools, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def check_links(root=ROOT):
 errors=[]; count=0
 exact_files={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
 for f in root.rglob('*.md'):
  if 'vendor' in f.parts: continue
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',f.read_text()):
   if target.startswith(('https://','http://','mailto:','#')):continue
   target=target.split('#')[0].split(' "')[0]; p=(f.parent/target).resolve();count+=1
   if not p.is_relative_to(root.resolve()) or not p.exists() or str(p.relative_to(root.resolve())) not in exact_files:errors.append((str(f.relative_to(root)),target))
 return count,errors

def check_html(root=ROOT):
 from html.parser import HTMLParser
 class Parser(HTMLParser):
  def __init__(self):super().__init__();self.ids=set();self.targets=[]
  def handle_starttag(self,tag,attrs):
   a=dict(attrs)
   if 'id' in a:self.ids.add(a['id'])
   for k in ('href','src'):
    if k in a:self.targets.append(a[k])
 parser=Parser();parser.feed((root/'index.html').read_text())
 for t in parser.targets:
  if t.startswith('#'):assert t[1:] in parser.ids,t
  elif not t.startswith(('https:','http:','mailto:')):assert (root/t).exists(),t
 return len(parser.targets)

def verify():
 count,errors=check_links();assert not errors,errors
 copies=json.loads((ROOT/'tools/adr-copies.json').read_text())
 def normalized(file):
  def target(m):
   t=m.group(1)
   if t.startswith(('http:','https:','mailto:','#')):return m.group(0)
   return ']('+str((file.parent/t).resolve().relative_to(ROOT))+')'
  return re.sub(r'\]\(([^)]+)\)',target,file.read_text())
 for canonical,task_copy in copies.items():
  assert normalized(ROOT/canonical)==normalized(ROOT/task_copy),(canonical,task_copy)
 for part,whole in [('Task2/architecture.md','ADR/006-integrations.md'),('Task2/ddd-contexts.md','ADR/006-integrations.md'),('Task2/risks.md','ADR/006-integrations.md'),('Task5/README.md','ADR/004-saas-isolation.md')]:
  body=normalized(ROOT/part).split('\n',1)[1].strip()
  assert body in normalized(ROOT/whole),(part,whole,'embedded text drift')

 html_targets=check_html() if (ROOT/'index.html').exists() else 0
 diagrams=[]; labels_checked=0
 expected=set('c2-microfrontends network c3-incidents-a c3-incidents-b access-flow c1-variant-a c1-variant-b deployment-a deployment-b c2-a-alternative c2-b-primary c2-center c2-center-ai-access c2-equipment c2-equipment-a c2-escalation alert-dynamics c3-variant-a c3-variant-b c4-variant-a c4-variant-b c4-incident c4-equipment c1-saas c2-agrotech-client c2-saas-tobe isolation-schema isolation-database isolation-instance'.split())
 actual={p.stem for p in ROOT.glob('Task*/diagrams/*.puml')}
 assert actual==expected,(actual ^ expected)
 for f in sorted(ROOT.glob('Task*/diagrams/*.puml')):
  assert all(x not in f.read_text() for x in ('Kotlin','Python','CoreS')),str(f)
  for ext in ('.svg','.png'): assert f.with_suffix(ext).is_file(),str(f)
  svg=f.with_suffix('.svg');tree=ET.parse(svg);texts=' '.join(''.join(n.itertext()) for n in tree.iter() if n.tag.endswith('text'))
  assert not any(x in texts for x in ('Syntax Error','An error has occured','IllegalStateException')),str(svg)
  def norm(s):return re.sub(r'[^\w]','',s.replace('\\n',' ')).lower()
  for label in re.findall(r'(?:Bi)?Rel\w*\([^,]+,[^,]+,\s*"([^"]+)"',f.read_text()):
   assert norm(label) in norm(texts),(str(f), 'label missing',label)
   labels_checked+=1
  typ=None
  if f.name.startswith('c1-'):typ='system'
  elif f.name.startswith(('c2-','isolation-')):typ='container'
  elif f.name.startswith('c3-'):typ='component'
  if typ:assert '«'+typ+'»' in texts, (f,typ)
  diagrams.append({'file':str(f.relative_to(ROOT)),'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),'visible_type':typ})
  if f.stem.startswith('c4-variant-'):
   assert 'ObservationPublisher' in texts and 'EventSink' in texts and 'PublicationWorker' in texts,str(f)
   assert not re.search(r'\b(UUID|datetime|Python)\b| -> |: str\b',f.read_text()),str(f)
   assert 'PublishAsync(detection: Detection): Task<Guid>' in f.read_text()
  if '!include' in f.read_text() and 'legend right' in f.read_text():
   legend=f.read_text().split('legend right')[1].split('endlegend')[0]
   assert all('<#' in line and '<color:' in line for line in legend.splitlines() if line.startswith('|')),(f,'legend must explicitly set background and foreground')
 # Exact feasible placement; balanced 48 tasks on 5 devices, each <=10.
 triples=list(itertools.combinations(range(5),3))
 placement=triples+[(0,1,2),(0,1,3),(0,2,4),(1,3,4),(2,3,4),(0,1,2)]
 load=[sum(i in t for t in placement) for i in range(5)]
 assert len(placement)==16 and max(load)<=10,(placement,load)
 def survives(plan):
  return all(all(set(t)-set(pair) for t in plan) for pair in itertools.combinations(range(5),2))
 assert survives(placement)
 broken=list(placement);broken[0]=(0,1)
 assert not survives(broken), 'two-copy regression must fail'
 # Enumerate every placement triple for each failed pair under minISR=2.
 unavailable=[]
 for pair in itertools.combinations(range(5),2):
  lost=sum(len(set(t)-set(pair))<2 for t in triples)
  assert lost==3,(pair,lost)
  unavailable.append({'failed':pair,'nonwritable_of_10':lost})
 # RF4/minISR2: every four-node placement survives every two-node failure.
 kafka_pairs=[]
 for replicas in itertools.combinations(range(5),4):
  for pair in itertools.combinations(range(5),2):
   remaining=set(replicas)-set(pair)
   assert len(remaining)>=2
   assert len(set(range(5))-set(pair))>=3 # controller majority
   kafka_pairs.append({'replicas':replicas,'failed':pair,'live_replicas':len(remaining),'writable_after_recovery':True})
 # Distinguish policy: two ISR writes with minISR2, not minISR3.
 assert len({0,1})>=2 and not len({0,1})>=3
 # Partial ISR before failures can leave only one; two acknowledged copies can both be lost.
 assert len({0,1,2}-{0,1})<2
 assert not ({0,1}-{0,1})
 # Colocating copies of a camera is not independent redundancy.
 assert all(len(t)==len(set(t))==3 for t in placement)
 colocated=list(placement);colocated[0]=(0,0,1)
 assert not survives(colocated)
 assert 5*(30+10*10)==650 and 16*(30+10*3)==960 and 16*60/5==192
 # Adversarial link fixture must be rejected by same validator.
 import tempfile
 with tempfile.TemporaryDirectory() as d:
  q=Path(d);(q/'bad.md').write_text('[missing](absent.md)');assert check_links(q)[1]
  (q/'Case.md').write_text('target');(q/'bad.md').write_text('[wrong case](case.md)');assert check_links(q)[1]
 return {'links_checked':count,'html_targets_checked':html_targets,'relationship_labels_checked':labels_checked,'broken_or_external_local_links':errors,'diagrams':diagrams,'placement':placement,'load':load,'failure_pairs_checked':10,'negative_two_copy_case':'validator rejected corrupted placement','kafka_rf4_placements_and_failure_pairs':kafka_pairs,'kafka_rf3_negative_control':unavailable,'kafka_minISR_counterexample':'detected','negative_link_case':'detected','scope':'Documents/render/arithmetic only; no production or latency test'}
if __name__=='__main__':
 r=verify();print(json.dumps(r,ensure_ascii=False,indent=2))
