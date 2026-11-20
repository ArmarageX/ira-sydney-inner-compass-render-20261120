"""Render static build. Documented native environment: https://render.com/docs/environment-variables .
Only frozen public21 source files are published; canonical and schema relative IDs
are bound to the provider-assigned RENDER_EXTERNAL_URL. The commit/artifact
manifest is emitted to native build logs and retained outside the publish root.
No license is granted over third-party photographs or review quotations.
"""
import os,json,shutil,hashlib,re
from pathlib import Path
root=Path(__file__).resolve().parent
origin=os.environ['RENDER_EXTERNAL_URL'].rstrip('/')
assert re.fullmatch(r'https://[a-z0-9-]+\.onrender\.com',origin)
commit=os.environ.get('RENDER_GIT_COMMIT','LOCAL_BEFORE_PUBLISH')
out=root/'build/public'
if out.exists():shutil.rmtree(out)
shutil.copytree(root/'public',out)
p=out/'index.html';html=p.read_text()
assert '<link href="./" rel="canonical"/>' in html
html=html.replace('<link href="./" rel="canonical"/>','<link href="'+origin+'/" rel="canonical"/>')
a=html.index('<script type="application/ld+json">')+len('<script type="application/ld+json">');b=html.index('</script>',a)
graph=json.loads(html[a:b])
def bind(x):
 if isinstance(x,dict):return {k:bind(v) for k,v in x.items()}
 if isinstance(x,list):return [bind(v) for v in x]
 if isinstance(x,str) and x.startswith('./'):return origin+'/'+x[2:]
 return x
html=html[:a]+json.dumps(bind(graph))+html[b:];p.write_text(html)
files=[{'path':str(p.relative_to(out)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'length':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file()]
assert len(files)==21
manifest={'source_commit':commit,'origin':origin,'files':files}
(root/'build/manifest.json').write_text(json.dumps(manifest,indent=2))
print('RENDER_NATIVE_ARTIFACT_BINDING '+json.dumps(manifest,sort_keys=True))
