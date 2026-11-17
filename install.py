"""Install the public skill locally; never overwrite an existing installation."""
import argparse,hashlib,os,shutil
from pathlib import Path

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--skills-dir',type=Path);a=ap.parse_args()
    source=Path(__file__).resolve().parent/'skills/reference-slide-workflow'
    parent=a.skills_dir or Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'skills'
    target=parent/'reference-slide-workflow'
    if target.exists():raise FileExistsError('An installation already exists. Keep or back it up explicitly before installing a new version.')
    if not (source/'SKILL.md').is_file():raise FileNotFoundError('Keep the complete repository directory')
    for f in source.rglob('*'):
        if not f.is_file() or '__pycache__' in f.parts or f.suffix=='.pyc':continue
        out=target/f.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,out)
        assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(out.read_bytes()).digest()
    print('Installed reference-slide-workflow. It is available on the next Codex turn.')
