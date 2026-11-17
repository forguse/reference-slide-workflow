"""Read-only reference inventory. Measurements are evidence, not an automatic design decision."""
import argparse,collections,json,zipfile
from pathlib import Path
import xml.etree.ElementTree as E
from project_state import sha,save
A='http://schemas.openxmlformats.org/drawingml/2006/main';P='http://schemas.openxmlformats.org/presentationml/2006/main'

def inspect(path):
    result={'source':path.name,'sha256':sha(path),'inference':'Inspect rendered pages before approving a style profile.'}
    if path.suffix.lower()=='.pptx':
        from verify_pptx import ordered_slides
        with zipfile.ZipFile(path) as z:
            pr=E.fromstring(z.read('ppt/presentation.xml'));size=pr.find('{'+P+'}sldSz')
            result['size_emu']=dict(size.attrib);result['aspect_ratio']=int(size.get('cx'))/int(size.get('cy'))
            fonts=collections.Counter();colors=collections.Counter();sizes=collections.Counter();pages=[]
            for part in ordered_slides(z):
                root=E.fromstring(z.read(part));blocks=[]
                for shape in root.findall('.//{'+P+'}sp'):
                    text=''.join(t.text or '' for t in shape.iter('{'+A+'}t'))
                    if not text.strip():continue
                    xfrm=shape.find('{'+P+'}spPr/{'+A+'}xfrm')
                    blocks.append({'text':text,'own_transform':E.tostring(xfrm,encoding='unicode') if xfrm is not None else None})
                for e in root.iter():
                    if e.tag in ['{'+A+'}latin','{'+A+'}ea'] and e.get('typeface'):fonts[e.get('typeface')]+=1
                    if e.tag=='{'+A+'}srgbClr':colors[e.get('val')]+=1
                    if e.get('sz'):sizes[e.get('sz')]+=1
                pages.append({'page':len(pages)+1,'text_blocks':blocks,'pictures':len(root.findall('.//{'+P+'}pic'))})
            result.update(pages=pages,explicit_fonts=fonts.most_common(),explicit_colors=colors.most_common(20),explicit_font_sizes_hundredths_pt=sizes.most_common(),
                          media_count=sum(n.startswith('ppt/media/') for n in z.namelist()),warning='Inherited theme/master styling and grouped transforms require rendered inspection; these are explicit values only.')
    elif path.suffix.lower()=='.pdf':
        import fitz
        with fitz.open(path) as doc:result['pages']=[{'page':i+1,'size_points':[p.rect.width,p.rect.height],'text':p.get_text()} for i,p in enumerate(doc)]
    else:
        from PIL import Image
        with Image.open(path) as im:
            result.update(size_pixels=list(im.size),mode=im.mode,dominant_colors=[{'rgb':list(rgb),'count':count} for count,rgb in sorted(im.convert('RGB').resize((160,90)).getcolors(160*90),reverse=True)[:12]])
            result['warning']='Pixels do not prove font identity or editable object geometry. Inspect the image itself.'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('reference',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('Use a new evidence filename')
    a.out.parent.mkdir(parents=True,exist_ok=True);save(a.out,inspect(a.reference));print('Reference evidence written locally. Review actual page visuals next.')
