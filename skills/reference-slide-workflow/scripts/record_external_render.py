"""Bind real PPT-exported PNGs to a project when a host-specific renderer is unavailable."""
import argparse,shutil
from pathlib import Path
from project_state import read,save,sha,digest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--png-dir',type=Path,required=True);p.add_argument('--renderer',required=True,help='Actual application, version and export settings');a=p.parse_args()
    root=a.out.resolve();ex=read(root/'export-manifest.json')
    if sha(Path(ex['pptx']))!=ex['pptx_sha256']:raise ValueError('PPTX changed after export checks')
    expected=[f'{i:02}.png' for i in range(1,len(ex['pages'])+1)]
    if sorted(p.name for p in a.png_dir.glob('*.png'))!=expected:raise ValueError('Supply exactly 01.png through the final numbered page, from the actual PPTX')
    target=root/'ppt-render';target.mkdir(exist_ok=True);rows=[]
    for name,row in zip(expected,ex['pages']):
        source=(a.png_dir/name).resolve();dest=(target/name).resolve()
        if source!=dest:shutil.copyfile(source,dest)
        rows.append({'page':row['page'],'visual_fingerprint':row['visual_fingerprint'],'screenshot_sha256':sha(dest),'reused':False})
    save(root/'ppt-render-report.json',{'status':'passed','pptx_sha256':ex['pptx_sha256'],'renderer':digest(a.renderer),'renderer_description':a.renderer,'pages':rows})
    print('Screenshots registered. Actual visual review is still required.')
