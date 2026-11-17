"""Exercise export failure modes against copies of a real exported deck."""
import argparse, json, subprocess, sys, zipfile
import xml.etree.ElementTree as E
from pathlib import Path
from project_state import sha, save
from verify_pptx import verify, ordered_slides, P, A

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pptx',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    tiny=a.out/'tiny-frame.pptx';external=a.out/'external-edit.pptx'
    if tiny.exists() or external.exists():raise FileExistsError('Use a new test directory')
    original=verify(a.pptx)
    assert original['status']=='passed',original
    with zipfile.ZipFile(a.pptx) as source,zipfile.ZipFile(tiny,'w',zipfile.ZIP_DEFLATED) as dest:
        slide=ordered_slides(source)[0]
        for entry in source.infolist():
            raw=source.read(entry.filename)
            if entry.filename==slide:
                tree=E.fromstring(raw)
                for shape in tree.iter('{'+P+'}sp'):
                    ext=shape.find(f'{{{P}}}spPr/{{{A}}}xfrm/{{{A}}}ext')
                    if ext is not None and any(t.text for t in shape.iter('{'+A+'}t')):
                        ext.set('cx','1');ext.set('cy','1');break
                else:raise AssertionError('No suitable text frame')
                raw=E.tostring(tree,encoding='utf-8',xml_declaration=True)
            dest.writestr(entry,raw)
    bad=verify(tiny)
    assert bad['status']=='failed' and bad['tiny_text_frames'],bad
    external.write_bytes(a.pptx.read_bytes())
    before=sha(external)
    save(a.out/'export-manifest.json',{'pptx':str(external.resolve()),'pptx_sha256':before})
    with external.open('ab') as f:f.write(b'External edit simulation')
    result=subprocess.run([sys.executable,str(Path(__file__).with_name('export_pptx.py')),'--out',str(a.out),'--pptx',str(a.out/'must-not-export.pptx')],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode and 'edited outside this project' in result.stderr,result.stderr
    assert not (a.out/'must-not-export.pptx').exists()
    report={'status':'passed','tests':['real deck control passes','tiny native text frame rejected','externally modified PPT blocks stale-source export'],'tiny_frame_evidence':bad['tiny_text_frames']}
    save(a.out/'export-guard-tests.json',report)
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
