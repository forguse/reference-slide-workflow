#!/usr/bin/env python3
"""Read-only package verification. Does not claim PowerPoint UI verification."""
import argparse,hashlib,json,posixpath,zipfile
from pathlib import Path
import xml.etree.ElementTree as E
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def ordered_slides(z):
    rel={e.get('Id'):posixpath.normpath(posixpath.join('ppt',e.get('Target'))).lstrip('/') for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    return [rel[e.get('{'+R+'}id')] for e in E.fromstring(z.read('ppt/presentation.xml')).findall(f'.//{{{P}}}sldId')]

def slide_fingerprints(z,slides):
    cache={}
    def dependencies(part,seen):
        if part in seen:return
        seen.add(part);rel=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
        if rel not in z.namelist():return
        # Skip speaker notes for visual caching; package hash still binds all notes.
        values=[]
        for e in E.fromstring(z.read(rel)):
            if e.get('Type','').endswith('/notesSlide'):continue
            values.append(E.tostring(e))
            if e.get('TargetMode')!='External':dependencies(posixpath.normpath(posixpath.join(posixpath.dirname(part),e.get('Target'))).lstrip('/'),seen)
        cache[rel]=hashlib.sha256(b''.join(values)).hexdigest();seen.add(rel)
    result=[]
    for part in slides:
        seen=set();dependencies(part,seen)
        for p in seen:
            if p not in cache:cache[p]=hashlib.sha256(z.read(p)).hexdigest()
        result.append(hashlib.sha256(''.join(p+':'+cache[p]+'\n' for p in sorted(seen)).encode()).hexdigest())
    return result

def verify(file,expected=None,canvas=None):
    with zipfile.ZipFile(file) as z:
        names=set(z.namelist());missing=[];xml_count=0
        for name in names:
            if name.endswith(('.xml','.rels')):root=E.fromstring(z.read(name));xml_count+=1
            if name.endswith('.rels'):
                for rel in root:
                    if rel.get('TargetMode')=='External':continue
                    target=rel.get('Target');parent=posixpath.dirname(posixpath.dirname(name))
                    resolved=posixpath.normpath(posixpath.join(parent,target)).lstrip('/')
                    if resolved not in names:missing.append({'part':name,'target':target})
        pr=E.fromstring(z.read('ppt/presentation.xml'));count=len(pr.findall(f'.//{{{P}}}sldId'))
        size=dict(pr.find(f'{{{P}}}sldSz').attrib);pages=[];tiny=[];notes=0
        slides=ordered_slides(z);fingerprints=slide_fingerprints(z,slides)
        for i,part in enumerate(slides,1):
            s=E.fromstring(z.read(part))
            relfile=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
            if relfile in names:notes+=sum(e.get('Type','').endswith('/notesSlide') for e in E.fromstring(z.read(relfile)))
            def scan(parent,sx=1,sy=1):
                for el in parent:
                    if el.tag==f'{{{P}}}grpSp':
                        xf=el.find(f'{{{P}}}grpSpPr/{{{A}}}xfrm');xx,yy=sx,sy
                        if xf is not None:
                            ext=xf.find(f'{{{A}}}ext');ch=xf.find(f'{{{A}}}chExt')
                            if ext is not None and ch is not None:
                                xx*=int(ext.get('cx'))/max(1,int(ch.get('cx')));yy*=int(ext.get('cy'))/max(1,int(ch.get('cy')))
                        scan(el,xx,yy)
                    elif el.tag==f'{{{P}}}sp' and ''.join(t.text or '' for t in el.iter(f'{{{A}}}t')).strip():
                        ext=el.find(f'{{{P}}}spPr/{{{A}}}xfrm/{{{A}}}ext');sizes=[int(e.get('sz')) for e in el.iter() if e.get('sz')]
                        if ext is not None and sizes:
                            nominal=min(sizes)/100*12700
                            if int(ext.get('cx'))*sx<nominal*.25 or int(ext.get('cy'))*sy<nominal*.25:tiny.append({'page':i,'text':''.join(t.text or '' for t in el.iter(f'{{{A}}}t')),'reason':'Text frame unexpectedly tiny in slide coordinates'})
            scan(s.find(f'{{{P}}}cSld/{{{P}}}spTree'))
            pages.append({'page':i,'part':part,'visual_fingerprint':fingerprints[i-1],'text_shapes':len(s.findall(f'.//{{{P}}}sp/{{{P}}}txBody')),'images':len(s.findall(f'.//{{{P}}}pic')),'text':' '.join(t.text or '' for t in s.iter('{'+A+'}t'))})
        ok=z.testzip() is None and not missing and not tiny and (expected is None or count==expected) and int(size.get('cx','0'))>0 and int(size.get('cy','0'))>0 and (canvas is None or abs(int(size['cx'])/int(size['cy'])-canvas[0]/canvas[1])<1e-5)
        return {'status':'passed' if ok else 'failed','slides':count,'notes':notes,'size':size,'xml_parsed':xml_count,'missing_relationships':missing,'tiny_text_frames':tiny,'pages':pages,'visual_review_required':True}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('pptx',type=Path);ap.add_argument('--expected',type=int);ap.add_argument('--report',type=Path);a=ap.parse_args()
    r=verify(a.pptx,a.expected)
    if a.report:a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['status']=='passed' else 1)
