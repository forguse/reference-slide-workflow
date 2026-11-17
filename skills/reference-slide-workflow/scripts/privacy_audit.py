"""Inspect a publication tree, including text inside Office ZIPs. Does not upload anything."""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
PATTERNS={
 'personal_path':r'(?i)(?:[a-z]:[\\/](?:users|documents and settings)[\\/][a-z0-9_. -]+|/(?:home|Users)/[a-z0-9_.-]+)',
 'email':r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
 'token':r'\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,}|sk-[A-Za-z0-9]{25,})\b',
 'institution_marker':r'大学|学院|研究院|学校|(?i:\b(?:university|college|institute)\b)',
}
TEXT={'.md','.py','.js','.cjs','.mjs','.json','.yaml','.yml','.html','.htm','.svg','.txt','.xml','.rels','.toml','.csv'}
SKIP={'.git','__pycache__','node_modules','.venv','work','private','browser-profile','test-browser-profile'}

def audit(root,deny=(),media_review=None):
    findings=[];media=[];count=0;review=media_review or {}
    def scan(text,label):
        for kind,pattern in PATTERNS.items():
            if kind=='institution_marker' and label.endswith('/scripts/privacy_audit.py'):continue # The scanner's own keyword definition is not an identity asset.
            if re.search(pattern,text):findings.append({'file':label,'kind':kind})
        for term in deny:
            if term and term.casefold() in text.casefold():findings.append({'file':label,'kind':'private_denylist_match'})
    def raster(raw,label):
        fingerprint=hashlib.sha256(raw).hexdigest();entry=review.get(label,{})
        media.append({'file':label,'sha256':fingerprint,'reviewed':entry.get('sha256')==fingerprint and bool(entry.get('observation'))})
    for f in sorted(root.rglob('*')):
        if not f.is_file() or any(p in SKIP for p in f.relative_to(root).parts):continue
        label=f.relative_to(root).as_posix();count+=1;scan(label,label)
        if f.suffix.lower() in ['.pptx','.docx','.xlsx','.zip']:
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    if n.endswith('/'):continue
                    data=z.read(n)
                    if Path(n).suffix.lower() in TEXT:scan(data.decode('utf-8','ignore'),label+'::'+n)
                    elif Path(n).suffix.lower() in ['.png','.jpg','.jpeg','.webp']:raster(data,label+'::'+n)
        elif f.suffix.lower() in TEXT or f.name in ['LICENSE','.gitignore']:scan(f.read_text(encoding='utf-8',errors='replace'),label)
        elif f.suffix.lower() in ['.png','.jpg','.jpeg','.webp']:
            raw=f.read_bytes();raster(raw,label)
            try:
                from PIL import Image
                with Image.open(f) as im:scan(json.dumps(im.info,ensure_ascii=False,default=str),label+'::metadata')
            except ImportError:findings.append({'file':label,'kind':'image_metadata_check_unavailable'})
    return {'status':'passed' if not findings and all(m['reviewed'] for m in media) else 'needs_review','files':count,'findings':findings,'media':media}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--deny-file',type=Path);p.add_argument('--media-review',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    deny=a.deny_file.read_text(encoding='utf-8').splitlines() if a.deny_file else []
    reviewed=json.loads(a.media_review.read_text(encoding='utf-8')) if a.media_review else {}
    result=audit(a.root.resolve(),deny,reviewed);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'files':result['files'],'findings':len(result['findings']),'unreviewed_media':sum(not m['reviewed'] for m in result['media'])}))
    raise SystemExit(0 if result['status']=='passed' else 1)
