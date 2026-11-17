"""Apply an explicit, version-checked patch to the current SVG source, then refresh HTML."""
import argparse,copy,json,shutil
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as E
from project_state import Q,read,save,sha,checked,verify_manifest,refresh

def apply(root,patch,dry=False):
    root=Path(root).resolve();m=verify_manifest(root);request=read(patch)
    if request.get('base_digest')!=m['build_digest']:raise ValueError('Patch targets another revision; inspect the current source first.')
    edits=request.get('edits',[])
    if not edits:raise ValueError('No edits supplied')
    pending={};pages=set();allowed={'x','y','width','height','text-anchor','transform','font-size','font-weight','fill','stroke','stroke-width','d','x1','y1','x2','y2','data-pptx-frame'}
    for edit in edits:
        row=next((r for r in m['pages'] if r['page']==edit['page']),None)
        if not row:raise ValueError('Unknown page')
        path=checked(root,row['svg']);tree=pending.setdefault(path,E.parse(path));nodes=[n for n in tree.getroot().iter() if n.get('id')==edit['id']]
        if len(nodes)!=1:raise ValueError('Expected exactly one matching element: '+edit['id'])
        el=nodes[0];before=edit.get('expect',{})
        if 'text' in before and ''.join(el.itertext())!=before['text']:raise ValueError('Text precondition failed: '+edit['id'])
        if any(el.get(k)!=str(v) for k,v in before.get('attrs',{}).items()):raise ValueError('Geometry precondition failed: '+edit['id'])
        if not before:raise ValueError('Supply expect.text or expect.attrs for every edit')
        if 'text' in edit:
            if el.tag!=Q+'text' or len(el):raise ValueError('Plain text edits require a plain text node; use lines/runs explicitly for rich text.')
            el.text=str(edit['text'])
        if 'lines' in edit:
            if el.tag!=Q+'text':raise ValueError('lines requires text element')
            lines=edit['lines'];leading=edit.get('leading')
            if not lines or (len(lines)>1 and (not isinstance(leading,(int,float)) or leading<=0)):raise ValueError('Explicit positive leading is required')
            for child in list(el):el.remove(child)
            el.text=lines[0]
            for line in lines[1:]:E.SubElement(el,Q+'tspan',x=str(edit.get('attrs',{}).get('x',el.get('x'))),dy=str(leading)).text=line
        if 'runs' in edit:
            if el.tag!=Q+'text':raise ValueError('runs requires text element')
            for child in list(el):el.remove(child)
            el.text=None
            for run in edit['runs']:E.SubElement(el,Q+'tspan',fill=run.get('color',el.get('fill','#111821'))).text=run['text']
        for key,val in edit.get('attrs',{}).items():
            if key not in allowed:raise ValueError('Unsupported geometry/style attribute: '+key)
            el.set(key,str(val))
        if el.tag==Q+'text' and ('lines' in edit or 'runs' in edit):
            for key in list(el.attrib):
                if key.startswith('data-paragraph') or key in ['data-pptx-text-model','data-pptx-text-baseline']:del el.attrib[key]
        pages.add(row['page'])
    # All preconditions are checked before writing any source file.
    result={'pages':sorted(pages),'files':[p.relative_to(root).as_posix() for p in pending],'base_digest':m['build_digest'],'reason':request.get('reason','')}
    if dry:return result
    backup=root/'revisions'/datetime.now().strftime('%Y%m%dT%H%M%S%f');backup.mkdir(parents=True)
    for path,tree in pending.items():
        dest=backup/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
        tree.write(path,encoding='utf-8')
    save(backup/'patch.json',request);refresh(root)
    new=read(root/'build.json');result['new_digest']=new['build_digest'];save(root/'last-revision.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--patch',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    print(json.dumps(apply(a.out,a.patch,a.dry_run),ensure_ascii=False))
