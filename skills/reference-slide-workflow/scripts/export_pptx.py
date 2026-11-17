#!/usr/bin/env python3
"""Export the already-reviewed HTML/SVG build through official ppt-master."""
import argparse,hashlib,json,os,re,subprocess,sys
import xml.etree.ElementTree as E
from pathlib import Path
from verify_pptx import verify
from review_gate import require
from plan_project import verify_build
SKILL=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True,type=Path,help='Directory produced by build_html.py')
    ap.add_argument('--ppt-master',type=Path,default=os.environ.get('PPT_MASTER_SKILL_DIR'))
    ap.add_argument('--pptx',type=Path,help='Defaults to OUT/template.pptx')
    ap.add_argument('--allow-different-version',action='store_true',help='Use only after explicitly accepting a different converter version')
    a=ap.parse_args();root=a.out.resolve()
    verify_build(root,final=True)
    prior=root/'export-manifest.json'
    if prior.exists():
        last=json.loads(prior.read_text(encoding='utf-8'));p=Path(last['pptx'])
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=last['pptx_sha256']:
            raise ValueError('The last PPTX was edited outside this project. Adopt that PPTX through the native edit route before exporting; do not replace manual edits from stale SVGs.')
    if not a.ppt_master:raise ValueError('Pass --ppt-master to the complete official skill directory')
    master=a.ppt_master.resolve();lock=json.loads((SKILL/'references/dependency-lock.json').read_text(encoding='utf-8'))['ppt_master']
    skill_file=master/'SKILL.md'
    if not skill_file.is_file():raise FileNotFoundError(skill_file)
    actual=hashlib.sha256(skill_file.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    if actual!=lock['skill_md_sha256'] and not a.allow_different_version:raise ValueError('ppt-master version differs from the tested package; use the pinned version or explicitly accept and re-check it.')
    m=json.loads((root/'build.json').read_text(encoding='utf-8'))
    for item in m['files']:
        if hashlib.sha256((root/item['path']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Source changed after HTML build: '+item['path'])
    report_file=root/'preview-report.json'
    if not report_file.is_file():raise ValueError('First render and inspect HTML using render_check.cjs')
    report=json.loads(report_file.read_text(encoding='utf-8'))
    if report.get('status')!='passed' or report.get('build_digest')!=m['build_digest']:raise ValueError('HTML check failed or is stale; rebuild/check before PPT export')
    require(root,'html')
    dest=(a.pptx or root/'template.pptx').resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise FileExistsError('Use a new PPTX filename for a revision; do not overwrite an open or unrelated presentation.')
    project=root/'project'
    env=os.environ.copy();env['PYTHONUTF8']='1'
    def run(script,*args):subprocess.run([sys.executable,str(SKILL/'scripts/keep_temp_runner.py'),str(master/'scripts'/script),*map(str,args)],check=True,env=env)
    run('attribution_guard.py')
    run('svg_quality_checker.py',project,'--quick-generate','--canonical-authoring','--stage','final','--json')
    run('svg_to_pptx.py',project,'--quick-generate','--with-notes','--no-animations','--primary-language',json.loads((root/'project/style-profile.json').read_text(encoding='utf-8')).get('language','en-US'),'-o',dest)
    result=verify(dest,len(m['pages']),m['canvas']);(root/'pptx-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if result['status']!='passed':raise ValueError('PPTX package verification failed')
    normalize=lambda text:re.sub(r'\s+','',text)
    for source,page in zip(m['pages'],result['pages']):
        readback=normalize(page['text'])
        for text in E.parse(root/source['svg']).getroot().iter('{http://www.w3.org/2000/svg}text'):
            expected=normalize(''.join(text.itertext()))
            if expected and expected not in readback:raise ValueError('Exported text missing on page '+str(source['page'])+': '+expected[:70])
    expected_notes=sum(bool(p.read_text(encoding='utf-8').strip()) for p in (root/'project/notes').glob('*.md'))
    if result['notes']<expected_notes:raise ValueError('Speaker notes count decreased during export')
    (root/'export-manifest.json').write_text(json.dumps({'schema':1,'build_digest':m['build_digest'],'pptx':str(dest),'pptx_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'pages':result['pages']},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'pptx':str(dest),'pages':result['slides'],'status':'passed','next':'Render/read back the PPTX and compare with the HTML screenshots.'},ensure_ascii=False))

if __name__=='__main__':main()
