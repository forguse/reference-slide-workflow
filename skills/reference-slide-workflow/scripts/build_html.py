"""Initialize once from authored SVGs or an explicitly selected preset; refresh without redesign."""
import argparse,copy,html,json,re,shutil
from pathlib import Path
import xml.etree.ElementTree as E
from project_state import Q,read,save,sha,refresh,validate_svg
from plan_project import validate as validate_plan, write_documents
SKILL=Path(__file__).resolve().parents[1]

def initialize(spec_path,out,preset_demo=False):
    spec=read(spec_path);base=spec_path.parent
    profile=read(base/spec['profile']);canvas=profile.get('canvas')
    if not isinstance(canvas,list) or len(canvas)!=2 or any(not isinstance(x,(int,float)) or x<100 or x>10000 for x in canvas):raise ValueError('Profile needs a positive two-dimensional canvas')
    if not profile.get('typography'):raise ValueError('Profile must declare typography roles')
    if out.exists() and any(out.iterdir()):raise ValueError('Use an empty output directory; use --refresh for an existing project')
    slides=spec.get('slides',[])
    if not slides:raise ValueError('No slides supplied')
    plan_path=(base/spec['plan']).resolve() if spec.get('plan') else None
    if not plan_path and not preset_demo and not str(spec.get('planning_waiver','')).strip():
        raise ValueError('First save the detailed outline; provide plan in the spec (see brief-and-outline.md)')
    if plan_path:
        plan=validate_plan(read(plan_path))
        if [s['id'] for s in plan['slides']]!=[s.get('id',f'slide-{i:02}') for i,s in enumerate(slides,1)]:
            raise ValueError('Slide order must match the detailed outline')
    for d in ['project/svg_output','project/images','project/notes']:(out/d).mkdir(parents=True,exist_ok=True)
    if plan_path:
        save(out/'project/plan.json',plan);write_documents(out/'project/plan.json')
    save(out/'project/style-profile.json',profile);pages=[];contracts={'schema':1,'pages':{}};sources=[]
    for i,row in enumerate(slides,1):
        ident=row.get('id',f'slide-{i:02}')
        if not re.fullmatch('[a-z0-9][a-z0-9_-]*',ident):raise ValueError('Slide id must be a portable stable name')
        source=(base/row['svg']).resolve();svg=E.parse(source).getroot();validate_svg(svg,canvas)
        ids={e.get('id'):f'p{i}-'+e.get('id') for e in svg.iter() if e.get('id')}
        if len(ids)!=sum(bool(e.get('id')) for e in svg.iter()):raise ValueError('Duplicate source IDs')
        for el in svg.iter():
            for attr,val in list(el.attrib.items()):
                if attr=='id':el.set(attr,ids[val]);continue
                for old,new in ids.items():val=val.replace(f'url(#{old})',f'url(#{new})')
                if val.startswith('#') and val[1:] in ids:val='#'+ids[val[1:]]
                el.set(attr,val)
        for image in svg.iter(Q+'image'):
            href=image.get('href') or image.get('{http://www.w3.org/1999/xlink}href','')
            if re.match(r'^[a-z]+://|^data:',href,re.I):raise ValueError('Download/verify raster assets locally before authoring')
            asset=(source.parent/href).resolve()
            if asset.suffix.lower() not in ['.png','.jpg','.jpeg','.webp']:raise ValueError('Use local raster assets for SVG image elements')
            name=sha(asset)[:20]+asset.suffix.lower();dest=out/'project/images'/name
            if not dest.exists():shutil.copyfile(asset,dest)
            image.set('href','../images/'+name);image.attrib.pop('{http://www.w3.org/1999/xlink}href',None)
            original_id=image.get('id').split('-',1)[1]
            sources.append({'page':i,'slot':original_id,'file':name,'source':row.get('image_sources',{}).get(original_id,'User-provided asset; record the original source before delivery')})
        filename=f'{i:02}_{ident}.svg';(out/'project/svg_output'/filename).write_text(E.tostring(svg,encoding='unicode'),encoding='utf-8')
        (out/'project/notes'/(Path(filename).stem+'.md')).write_text(row.get('notes',''),encoding='utf-8')
        c=copy.deepcopy(row.get('contract',{'rules':[]}))
        for rule in c.get('rules',[])+c.get('allow_overlap',[]):
            rule['items']=[ids.get(x,x) for x in rule.get('items',[])]
            if 'owner' in rule:rule['owner']=ids.get(rule['owner'],rule['owner'])
            if 'offsets' in rule:rule['offsets']={ids.get(k,k):v for k,v in rule['offsets'].items()}
        contracts['pages'][str(i)]=c;pages.append({'page':i,'id':ident,'name':row.get('name',ident),'svg':'project/svg_output/'+filename})
    save(out/'project/layout-contracts.json',contracts);save(out/'project/image_sources.json',sources)
    w,h=canvas;title=spec.get('title','Presentation preview');language=profile.get('language','en-US');labels=['上一页','下一页','全部页面'] if language.lower().startswith('zh') else ['Previous','Next','All pages'];opts=''.join(f'<option value="{p["page"]}">{p["page"]} {html.escape(p["name"])}</option>' for p in pages)
    document='''<!doctype html><html lang="'''+html.escape(language)+'''"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+html.escape(title)+'''</title><style>
*{box-sizing:border-box}body{margin:0;background:#e5e7eb;font-family:Arial,sans-serif}.toolbar{display:flex;align-items:center;gap:12px;background:white;padding:12px 24px;position:sticky;top:0;z-index:2}.toolbar b{margin-right:auto}.toolbar button,.toolbar select{padding:8px}.pages{max-width:'''+str(w+56)+'''px;margin:22px auto;padding:0 28px}.page{width:100%;aspect-ratio:'''+str(w)+'/'+str(h)+''';background:white;margin-bottom:24px;overflow:hidden;line-height:0;box-shadow:0 3px 15px #0002}.page svg{width:100%;height:100%;display:block}.single .page{display:none}.single .page.selected{display:block}@media print{.toolbar{display:none}.pages{padding:0;margin:0}.page{display:block!important;page-break-after:always;box-shadow:none;margin:0}}@page{size:'''+str(w)+'px '+str(h)+'''px;margin:0}</style><body><nav class="toolbar"><b>'''+html.escape(title)+'''</b><button data-action="previous" onclick="step(-1)">'''+labels[0]+'''</button><select id="pageSelect" onchange="show(+this.value)">'''+opts+'''</select><button data-action="next" onclick="step(1)">'''+labels[1]+'''</button><button data-action="all" onclick="allPages()">'''+labels[2]+'''</button></nav><main class="pages"></main><script>
const pageCount='''+str(len(pages))+''';let current=1;function show(n){current=Math.min(pageCount,Math.max(1,n));document.body.classList.add('single');document.querySelectorAll('.page').forEach((p,i)=>p.classList.toggle('selected',i===current-1));document.querySelector('#pageSelect').value=current;window.scrollTo(0,0)}function step(d){show(current+d)}function allPages(){document.body.classList.remove('single')}document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1)});show(1);
</script></body></html>'''
    (out/'preview.html').write_text(document,encoding='utf-8')
    save(out/'build.json',{'schema':3,'title':title,'canvas':canvas,'pages':pages,'planning_required':bool(plan_path),'planning_exemption':'bundled-preset-preview' if preset_demo else spec.get('planning_waiver')});refresh(out)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--spec',type=Path);g.add_argument('--preset',choices=['academic-blue','editorial-light','structured-blue']);g.add_argument('--refresh',action='store_true')
    a=p.parse_args();root=a.out.resolve()
    if a.refresh:refresh(root)
    else:initialize(a.spec.resolve() if a.spec else SKILL/'assets/presets'/a.preset/'deck.json',root,preset_demo=bool(a.preset))
