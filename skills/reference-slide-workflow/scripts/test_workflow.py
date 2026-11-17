"""Behavioral tests for custom canvas, local revision and inactive source handling."""
import argparse,sys
from pathlib import Path
from build_html import initialize
from project_state import read,save,sha,refresh
from revise_project import apply

def run(out):
    if out.exists():raise FileExistsError('Use a new test directory')
    author=out/'authoring';author.mkdir(parents=True)
    profile={'canvas':[1024,768],'language':'en-US','typography':{'body':{'family':'Arial','size':28,'weight':400}},'identity_assets':[]}
    save(author/'style-profile.json',profile)
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="768" viewBox="0 0 1024 768" lang="en-US" font-family="Arial" data-pptx-page-role="content"><rect id="background" width="1024" height="768" fill="#FFFFFF" data-pptx-role="background"/><text id="title" x="60" y="110" font-size="42" font-weight="700" fill="#162433">Reference evidence</text><text id="body" x="60" y="200" font-size="28" fill="#162433">A custom four-to-three canvas.</text></svg>'
    (author/'page.svg').write_text(svg,encoding='utf-8')
    contract={'rules':[{'kind':'align','items':['title','body'],'edge':'anchorX','tolerance':1},{'kind':'inside','items':['title','body'],'box':[55,50,900,600]}]}
    save(author/'deck.json',{'title':'Custom canvas test','profile':'style-profile.json','slides':[{'id':'first','svg':'page.svg','notes':'Synthetic test content.','contract':contract},{'id':'second','svg':'page.svg','notes':'Synthetic test content.','contract':contract}]})
    root=out/'project';initialize(author/'deck.json',root);m=read(root/'build.json');assert m['canvas']==[1024,768]
    before={r['page']:sha(root/r['svg']) for r in m['pages']};refresh(root);assert before=={r['page']:sha(root/r['svg']) for r in m['pages']}
    try:initialize(author/'deck.json',root)
    except ValueError:pass
    else:raise AssertionError('Existing project was reset')
    patch=out/'patch.json';save(patch,{'base_digest':read(root/'build.json')['build_digest'],'edits':[{'page':1,'id':'p1-title','expect':{'text':'Reference evidence'},'text':'Revised comparison'}]});apply(root,patch)
    after=read(root/'build.json');assert after['changed_visual_pages']==[1];assert sha(root/after['pages'][1]['svg'])==before[2]
    try:apply(root,patch)
    except ValueError:pass
    else:raise AssertionError('Stale patch was accepted')
    note=root/'project/notes/01_first.md';note.write_text('Revised notes only.',encoding='utf-8');refresh(root);assert read(root/'build.json')['changed_visual_pages']==[]
    (author/'active.svg').write_text(svg.replace('</svg>','<script>void 0</script></svg>'),encoding='utf-8')
    bad=read(author/'deck.json');bad['slides'][0]['svg']='active.svg';save(author/'bad.json',bad)
    try:initialize(author/'bad.json',out/'blocked-active-source')
    except ValueError:pass
    else:raise AssertionError('Active source content was accepted')
    result={'status':'passed','checks':['custom 4:3 canvas','refresh preserves source bytes','existing project protected','local patch changes one page','stale patch rejected','notes preserve visual digests','active SVG source rejected']}
    save(out/'test-report.json',result);print(result)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path);a=p.parse_args();run(a.out)
