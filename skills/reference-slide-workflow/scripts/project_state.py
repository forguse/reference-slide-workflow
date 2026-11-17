"""Stable authored sources and refresh-only previews, independent of any preset."""
from pathlib import Path
import base64,copy,hashlib,json,mimetypes,re
import xml.etree.ElementTree as E

NS='http://www.w3.org/2000/svg';Q='{'+NS+'}';E.register_namespace('',NS)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def checked(root,relative):
    p=(root/relative).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('Path outside project: '+str(relative))
    return p

def validate_svg(root,canvas):
    if [float(x) for x in root.get('viewBox','').split()]!=[0,0,*canvas]:raise ValueError('SVG viewBox must match the style profile')
    for el in root.iter():
        if el.tag.rsplit('}',1)[-1] in ['script','foreignObject','iframe','style']:raise ValueError('Use static SVG attributes, not executable or external content')
        for k,v in el.attrib.items():
            if k.lower().startswith('on') or re.search(r'javascript:|@import',v,re.I):raise ValueError('Active SVG content is not supported')

def refresh(root):
    root=Path(root).resolve();m=read(root/'build.json')
    if m.get('schema')!=3:raise ValueError('Use an existing v3 project; do not reset it from a template')
    from plan_project import verify_build
    verify_build(root)
    profile=read(root/'project/style-profile.json');canvas=profile['canvas']
    if m['canvas']!=canvas:raise ValueError('Canvas changes require an explicitly reviewed project revision')
    contracts=read(root/'project/layout-contracts.json');shell=(root/'preview.html').read_text(encoding='utf-8')
    shell_digest=digest(re.sub(r'<main class="pages">.*?</main>','<main class="pages"></main>',shell,flags=re.S))
    if {Path(r['svg']).name for r in m['pages']}!={p.name for p in (root/'project/svg_output').glob('*.svg')}:raise ValueError('Unexpected page roster')
    rendered=[];files={root/'project/style-profile.json',root/'project/layout-contracts.json'};changes=[]
    for row in m['pages']:
        f=checked(root,row['svg']);s=E.parse(f).getroot();validate_svg(s,canvas);inputs=[f];preview=copy.deepcopy(s)
        for image in preview.iter(Q+'image'):
            href=image.get('href') or image.get('{http://www.w3.org/1999/xlink}href','')
            p=(f.parent/href).resolve()
            if not p.is_relative_to(root) or not p.is_file():raise ValueError('Materialize every image inside the project')
            inputs.append(p);image.set('href','data:'+(mimetypes.guess_type(p)[0] or 'image/png')+';base64,'+base64.b64encode(p.read_bytes()).decode())
            image.attrib.pop('{http://www.w3.org/1999/xlink}href',None)
        visual=digest({'inputs':[(p.relative_to(root).as_posix(),sha(p)) for p in inputs],
                       'profile':profile,'contract':contracts['pages'].get(str(row['page']),{}),'packager':sha(__file__),'shell':shell_digest})
        if visual!=row.get('visual_digest'):changes.append(row['page'])
        row['visual_digest']=visual;row['svg_sha256']=sha(f)
        note=root/'project/notes'/(f.stem+'.md')
        if note.exists():inputs.append(note)
        row['content_digest']=digest([(p.relative_to(root).as_posix(),sha(p)) for p in inputs]);files.update(inputs)
        rendered.append(f'<section class="page" id="page-{row["page"]}">'+E.tostring(preview,encoding='unicode')+'</section>')
    if shell.count('<main class="pages">')!=1:raise ValueError('Unknown preview shell')
    page=root/'preview.html';page.write_text(re.sub(r'<main class="pages">.*?</main>',lambda _: '<main class="pages">'+''.join(rendered)+'</main>',shell,flags=re.S),encoding='utf-8');files.add(page)
    for name in ['image_sources.json','reference-evidence.json','plan.json','outline.md','materials-and-decisions.md']:
        p=root/'project'/name
        if p.exists():files.add(p)
    m['files']=[{'path':p.relative_to(root).as_posix(),'sha256':sha(p)} for p in sorted(files)]
    m['build_digest']=digest(m['files']);m['changed_visual_pages']=changes;save(root/'build.json',m)
    print(json.dumps({'refreshed':len(m['pages']),'changed_visual_pages':changes,'source_rebuilt':False},ensure_ascii=False))

def verify_manifest(root,m=None):
    root=Path(root);m=m or read(root/'build.json')
    for row in m['files']:
        if sha(checked(root,row['path']))!=row['sha256']:raise ValueError('Stale build: '+row['path'])
    return m
