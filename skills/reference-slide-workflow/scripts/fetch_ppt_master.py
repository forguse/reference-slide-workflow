#!/usr/bin/env python3
"""Download the pinned complete official skill into an explicitly named empty directory."""
import argparse,hashlib,json,subprocess,sys,urllib.request,zipfile
from pathlib import Path,PurePosixPath
SKILL=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--dest',required=True,type=Path);a=ap.parse_args()
    dest=a.dest.resolve();lock=json.loads((SKILL/'references/dependency-lock.json').read_text(encoding='utf-8'))['ppt_master']
    if dest.exists() and any(dest.iterdir()):raise ValueError('Destination must be empty; nothing will be deleted or replaced')
    dest.mkdir(parents=True,exist_ok=True)
    archive=dest.parent/('ppt-master-'+lock['commit']+'.zip')
    if not archive.exists():
        url='https://codeload.github.com/hugohe3/ppt-master/zip/'+lock['commit']
        print('Downloading pinned official ppt-master archive...',flush=True)
        with urllib.request.urlopen(url,timeout=90) as response,archive.open('wb') as output:
            while True:
                block=response.read(1024*1024)
                if not block:break
                output.write(block)
    print('Verifying and extracting archive ('+str(archive.stat().st_size)+' bytes)...',flush=True)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Download is incomplete; inspect the named archive manually, then retry with a fresh destination')
        prefix=z.namelist()[0].split('/')[0]+'/'+lock['skill_subpath']+'/'
        for info in z.infolist():
            if not info.filename.startswith(prefix) or info.is_dir():continue
            rel=PurePosixPath(info.filename[len(prefix):])
            if '..' in rel.parts or rel.is_absolute():raise ValueError('Unexpected archive path')
            target=(dest/Path(*rel.parts)).resolve()
            if not target.is_relative_to(dest):raise ValueError('Archive path leaves destination')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(info))
    skill=dest/'SKILL.md'
    if hashlib.sha256(skill.read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=lock['skill_md_sha256']:raise ValueError('Pinned source identity mismatch')
    subprocess.run([sys.executable,str(dest/'scripts/attribution_guard.py')],check=True)
    print(json.dumps({'ppt_master':str(dest),'version':lock['version'],'commit':lock['commit']},ensure_ascii=False))

if __name__=='__main__':main()
