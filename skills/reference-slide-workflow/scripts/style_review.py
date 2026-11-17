"""Bind project-specific style judgments to inspected HTML screenshots."""
import argparse
from pathlib import Path
from project_state import read, save, sha, digest, verify_manifest

PAIR_PROTOCOL = 'reference-pair-v1'


def paired_protocol(root):
    return read(root / 'project/style-profile.json').get('review_protocol') == PAIR_PROTOCOL


def prepare_comparison(root, reference, page, crop=None):
    """Create a private, equal-scale review board; never a slide asset."""
    from PIL import Image, ImageOps, ImageDraw
    _, pages, _ = current(root)
    if page not in pages:
        raise ValueError('Choose a currently rendered representative page')
    with Image.open(reference) as original:
        original.load()
        ref = original.convert('RGB')
    if crop:
        x, y, w, h = crop
        if min(x,y) < 0 or min(w,h) <= 0 or x+w > ref.width or y+h > ref.height:
            raise ValueError('Reference crop must stay inside the source image')
        ref = ref.crop((x,y,x+w,y+h))
    folder=root/'style-comparisons';folder.mkdir(exist_ok=True)
    ref_path=folder/f'reference-{page:02}.png';ref.save(ref_path)
    with Image.open(root/f'screenshots/{page:02}.png') as im:
        rendered=im.convert('RGB')
    width=800;height=round(width*rendered.height/rendered.width)
    board=Image.new('RGB',(width*2,height+38),'#E4E2DE')
    draw=ImageDraw.Draw(board);draw.text((12,12),'REFERENCE',(30,30,30));draw.text((width+12,12),'CURRENT',(30,30,30))
    for x,im in [(0,ref),(width,rendered)]:
        fit=ImageOps.contain(im,(width,height),Image.Resampling.LANCZOS)
        board.paste(fit,(x+(width-fit.width)//2,38+(height-fit.height)//2))
    pair_path=folder/f'pair-{page:02}.png';board.save(pair_path)
    evidence={'page':page,'reference_sha256':sha(ref_path),'pair_sha256':sha(pair_path),'render_evidence':pages[page],'original_reference_sha256':sha(reference),'reference_crop':crop}
    save(folder/f'pair-{page:02}.json',evidence)
    return pair_path


def comparison_evidence(root,page,pages):
    folder=root/'style-comparisons';path=folder/f'pair-{page:02}.json'
    if not path.exists():
        raise ValueError('Create and inspect a reference comparison before recording style approval')
    evidence=read(path)
    try:
        valid=evidence['page']==page and evidence['render_evidence']==pages[page] and evidence['reference_sha256']==sha(folder/f'reference-{page:02}.png') and evidence['pair_sha256']==sha(folder/f'pair-{page:02}.png')
    except (KeyError,FileNotFoundError):
        valid=False
    if not valid:
        raise ValueError('Reference comparison is stale or altered; rebuild and inspect it')
    return evidence


def validate_comparative_row(row):
    if not isinstance(row.get('reference_observation'),str) or len(row['reference_observation'].strip())<20:
        raise ValueError('Describe the reference relationship, not just the result')
    if row.get('status')=='adapted' and (not isinstance(row.get('adaptation_reason'),str) or len(row['adaptation_reason'].strip())<20):
        raise ValueError('Explain why the changed relationship fits the new content')
    gaps=row.get('remaining_gaps')
    if not isinstance(gaps,list) or any(not isinstance(s,str) or not s.strip() for s in gaps):
        raise ValueError('Record remaining reference-style gaps explicitly as a list')


def targets(profile):
    rows = profile.get('style_targets', [])
    if not rows:
        return {}
    if profile.get('reference_mode') not in ('single', 'synthesis', 'showcase'):
        raise ValueError('Style targets need reference_mode: single, synthesis or showcase')
    result = {}
    for row in rows:
        for key in ('id', 'reference', 'observable'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('Style target needs concrete ' + key)
        if row['id'] in result:
            raise ValueError('Duplicate style target: ' + row['id'])
        if not isinstance(row.get('pages'), list) or not row['pages'] or any(type(p) is not int or p < 1 for p in row['pages']):
            raise ValueError('Style target needs representative page numbers')
        result[row['id']] = row
    return result


def current(root):
    manifest = verify_manifest(root)
    profile = read(root / 'project/style-profile.json')
    desired = targets(profile)
    if not desired:
        return desired, {}, None
    report = read(root / 'preview-report.json')
    if report.get('status') != 'passed' or report.get('build_digest') != manifest['build_digest']:
        raise ValueError('Style review needs a current passing HTML render')
    pages = {}
    for row in report['pages']:
        p = row['page']
        actual = sha(root / f'screenshots/{p:02}.png')
        if actual != row['screenshot_sha256']:
            raise ValueError('Style screenshot changed after render')
        pages[p] = {'visual_digest':row['visual_digest'], 'screenshot_sha256':actual}
    for target in desired.values():
        if any(p not in pages for p in target['pages']):
            raise ValueError('Style target references a missing page')
    return desired, pages, digest(profile)


def record(root, supplied):
    desired, pages, profile_digest = current(root)
    if not desired:
        raise ValueError('Declare project-specific style targets first')
    records = supplied.get('targets', [])
    if len(records) != len(desired) or {r.get('id') for r in records} != set(desired):
        raise ValueError('Review every declared target exactly once')
    output = {'profile_digest':profile_digest, 'targets':[]}
    for row in records:
        target = desired[row['id']]
        if row.get('status') not in ('retained', 'adapted', 'failed'):
            raise ValueError('Target status must be retained, adapted or failed')
        if row.get('page') not in target['pages']:
            raise ValueError('Inspect a declared representative page for this target')
        if not isinstance(row.get('observation'), str) or len(row['observation'].strip()) < 20:
            raise ValueError('Record a concrete reference-to-result observation')
        extra={}
        if paired_protocol(root):
            validate_comparative_row(row)
            extra['comparison_evidence']=comparison_evidence(root,row['page'],pages)
        output['targets'].append({**row, 'evidence':pages[row['page']], **extra})
    save(root / 'style-review.json', output)
    return output


def require(root):
    desired, pages, profile_digest = current(root)
    if not desired:
        return
    path = root / 'style-review.json'
    if not path.exists():
        raise ValueError('Inspect and record reference-style targets before export')
    review = read(path)
    if review.get('profile_digest') != profile_digest:
        raise ValueError('Style profile changed; inspect its current targets')
    records = review.get('targets', [])
    if len(records) != len(desired) or {r.get('id') for r in records} != set(desired):
        raise ValueError('Incomplete style review')
    for row in records:
        target = desired[row['id']]
        if row.get('status') not in ('retained', 'adapted'):
            raise ValueError('Unresolved style target: ' + row['id'])
        p = row.get('page')
        if p not in target['pages'] or row.get('evidence') != pages.get(p):
            raise ValueError('Style review is stale for target: ' + row['id'])
        if paired_protocol(root):
            validate_comparative_row(row)
            if row.get('comparison_evidence') != comparison_evidence(root,p,pages):
                raise ValueError('Style approval does not match the inspected comparison')
            if row['remaining_gaps']:
                raise ValueError('Unresolved reference-style gaps: ' + '; '.join(row['remaining_gaps']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['record', 'check', 'compare'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--file', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--page', type=int)
    parser.add_argument('--crop', type=int, nargs=4, metavar=('X','Y','W','H'))
    args = parser.parse_args()
    if args.action == 'compare':
        if not args.reference or not args.page:
            parser.error('compare requires --reference and --page')
        print(prepare_comparison(args.out.resolve(),args.reference.resolve(),args.page,args.crop))
        raise SystemExit(0)
    if args.action == 'record':
        if not args.file:
            parser.error('record needs --file after actual comparison')
        record(args.out.resolve(), read(args.file))
    require(args.out.resolve())
    print('Style targets reviewed and current.')
