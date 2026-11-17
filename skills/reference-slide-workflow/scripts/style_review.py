"""Bind project-specific style judgments to inspected HTML screenshots."""
import argparse
from pathlib import Path
from project_state import read, save, sha, digest, verify_manifest


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
        output['targets'].append({**row, 'evidence':pages[row['page']]})
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['record', 'check'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--file', type=Path)
    args = parser.parse_args()
    if args.action == 'record':
        if not args.file:
            parser.error('record needs --file after actual comparison')
        record(args.out.resolve(), read(args.file))
    require(args.out.resolve())
    print('Style targets reviewed and current.')
