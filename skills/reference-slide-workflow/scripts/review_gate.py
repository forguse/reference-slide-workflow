"""Bind the agent's actual visual review to exact source, screenshots and exported PPTX."""
import argparse,json
from pathlib import Path
from project_state import read,save,sha,digest,verify_manifest
from verify_pptx import verify

def evidence(root,stage):
    m=verify_manifest(root)
    if stage=='html':
        r=read(root/'preview-report.json')
        if r.get('status')!='passed' or r.get('build_digest')!=m['build_digest']:raise ValueError('HTML geometry/font check is failed or stale')
        rows={}
        for page in r['pages']:
            p=page['page'];f=root/f'screenshots/{p:02}.png'
            if sha(f)!=page['screenshot_sha256']:raise ValueError('Screenshot changed since browser check')
            rows[str(p)]={'visual_digest':page['visual_digest'],'measurement_digest':page['measurement_digest'],'screenshot_sha256':sha(f),'environment':r['environment']}
        return rows
    r=read(root/'ppt-render-report.json');ex=read(root/'export-manifest.json')
    if r['pptx_sha256']!=sha(Path(ex['pptx'])) or ex['build_digest']!=m['build_digest']:raise ValueError('PPT render/export is stale')
    if r.get('status')!='passed' or len(r['pages'])!=len(m['pages']):raise ValueError('Incomplete PPT rendering')
    rows={}
    for page in r['pages']:
        p=page['page'];f=root/f'ppt-render/{p:02}.png'
        if sha(f)!=page['screenshot_sha256']:raise ValueError('PPT screenshot changed since rendering')
        rows[str(p)]={'visual_fingerprint':page['visual_fingerprint'],'screenshot_sha256':sha(f),'renderer':r['renderer'],'source_visual_digest':m['pages'][p-1]['visual_digest']}
    return rows

def pending(root,stage):
    rows=evidence(root,stage);f=root/'visual-review.json';review=read(f) if f.exists() else {}
    return [int(p) for p,v in rows.items() if review.get(stage,{}).get(p,{}).get('evidence')!=v]

def require(root,stage):
    todo=pending(root,stage)
    if todo:raise ValueError(f'Agent must view and record {stage} pages {todo}; a numeric check is not visual approval.')

def record(root,stage,pages,note):
    if len(note.strip())<12:raise ValueError('Record concrete visual observations, not only "passed"')
    rows=evidence(root,stage);f=root/'visual-review.json';review=read(f) if f.exists() else {}
    for p in pages:
        if str(p) not in rows:raise ValueError('Unknown page '+str(p))
    for p in pages:review.setdefault(stage,{})[str(p)]={'evidence':rows[str(p)],'observation':note}
    save(f,review)

def finalize(root):
    require(root,'html');require(root,'ppt');m=verify_manifest(root);ex=read(root/'export-manifest.json')
    check=verify(Path(ex['pptx']),len(m['pages']),m['canvas'])
    if check['status']!='passed':raise ValueError('PPT package failed')
    result={'status':'passed','build_digest':m['build_digest'],'pptx':ex['pptx'],'pptx_sha256':sha(Path(ex['pptx'])),'pages':len(m['pages']),
            'checks':['HTML geometry, overlap, fonts','HTML visual review','official PPT Master conversion','PPTX package integrity','PPT rendered visual review'],
            'review_digest':sha(root/'visual-review.json')}
    save(root/'delivery-report.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['pending','record','finalize','finalize-preview']);p.add_argument('--out',required=True,type=Path);p.add_argument('--stage',choices=['html','ppt'],default='html');p.add_argument('--pages');p.add_argument('--observation');a=p.parse_args();root=a.out.resolve()
    if a.action=='pending':result={'stage':a.stage,'needs_visual_review':pending(root,a.stage)}
    elif a.action=='record':
        if not a.pages or not a.observation:p.error('record needs --pages and --observation after actual inspection')
        record(root,a.stage,[int(x) for x in a.pages.split(',')],a.observation);result={'needs_visual_review':pending(root,a.stage)}
    elif a.action=='finalize-preview':
        require(root,'html');m=verify_manifest(root)
        result={'status':'preview_verified','build_digest':m['build_digest'],'pages':len(m['pages']),'html_sha256':sha(root/'preview.html'),'ppt_verified':False}
        save(root/'preview-delivery-report.json',result)
    else:result=finalize(root)
    print(json.dumps(result,ensure_ascii=False))
