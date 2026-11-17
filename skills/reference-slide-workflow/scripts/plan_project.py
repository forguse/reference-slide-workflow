"""Validate a presentation plan and write its readable outline and material record."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

PERMISSIONS = ('external_facts', 'external_images', 'generated_images')
KINDS = {'supplied', 'external', 'generated', 'derived'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be concrete, nonempty text')


def index(rows, label):
    if not isinstance(rows, list):
        raise ValueError(f'{label} must be a list')
    result = {}
    for row in rows:
        nonempty(row.get('id'), f'{label}.id')
        if row['id'] in result:
            raise ValueError(f'Duplicate {label} ID: {row["id"]}')
        result[row['id']] = row
    return result


def permissions(plan, slide_id):
    result = {key: plan['policy'][key] for key in PERMISSIONS}
    for override in plan['policy'].get('overrides', []):
        if override['slide'] == slide_id:
            result.update(override['allow'])
    return result


def source_kinds(source_id, sources, seen=()):
    if source_id not in sources or source_id in seen:
        raise ValueError('Unknown or cyclic source: ' + source_id)
    source = sources[source_id]
    if source['kind'] != 'derived':
        return {source['kind']}
    parents = source.get('parents', [])
    if not parents:
        raise ValueError('Derived source needs parents: ' + source_id)
    result = set()
    for parent in parents:
        result |= source_kinds(parent, sources, (*seen, source_id))
    return result


def validate(plan):
    if plan.get('schema') != 1:
        raise ValueError('Unsupported plan schema')
    brief = plan['brief']
    for key in ('title', 'audience', 'purpose', 'narrative'):
        nonempty(brief.get(key), 'brief.' + key)
    if brief.get('input_mode') not in ('broad_brief', 'detailed_brief', 'user_outline', 'existing_deck'):
        raise ValueError('Record how the user supplied the brief')
    policy = plan['policy']
    nonempty(policy.get('basis'), 'policy.basis')
    for key in PERMISSIONS:
        if type(policy.get(key)) is not bool:
            raise ValueError('Explicit boolean permission required: ' + key)
    slides = index(plan['slides'], 'slides')
    if not slides:
        raise ValueError('The outline needs at least one page')
    if brief.get('page_count') is not None and brief['page_count'] != len(slides):
        raise ValueError('Outline does not match the requested page count')
    sources = index(plan.get('sources', []), 'sources')
    assets = index(plan.get('assets', []), 'assets')
    requirements = index(plan.get('requirements', []), 'requirements')
    for req in requirements.values():
        nonempty(req.get('text'), 'requirement.text')
        if req.get('origin') not in ('user', 'proposed') or req.get('scope') not in ('deck', 'pages'):
            raise ValueError('Requirement needs origin user/proposed and scope deck/pages')
    seen_overrides = set()
    for override in policy.get('overrides', []):
        slide = override.get('slide')
        if slide not in slides or slide in seen_overrides:
            raise ValueError('Unknown or duplicate policy override page')
        seen_overrides.add(slide)
        nonempty(override.get('basis'), 'override.basis')
        if not override.get('allow') or any(k not in PERMISSIONS or type(v) is not bool for k, v in override['allow'].items()):
            raise ValueError('Invalid page-scoped permissions')
    for source in sources.values():
        if source.get('kind') not in KINDS:
            raise ValueError('Unknown source kind')
        nonempty(source.get('locator'), 'source.locator')
        nonempty(source.get('rights'), 'source.rights')
        source_kinds(source['id'], sources)
    for asset in assets.values():
        nonempty(asset.get('description'), 'asset.description')
        source_kinds(asset['source'], sources)
        if asset.get('role') not in ('evidence', 'context', 'concept', 'decoration'):
            raise ValueError('Asset needs a meaningful role')
        value = asset.get('sha256')
        if value is not None and (not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value)):
            raise ValueError('Invalid asset SHA-256')
    covered = set()
    duration = 0
    for slide in slides.values():
        for key in ('title', 'purpose', 'message', 'layout'):
            nonempty(slide.get(key), slide['id'] + '.' + key)
        if not isinstance(slide.get('content'), list) or not slide['content']:
            raise ValueError('Each page needs concrete content')
        if brief.get('design_depth') == 'page-design' or 'design' in slide:
            design = slide.get('design', {})
            for key in ('visual_hierarchy', 'typography', 'image_treatment', 'style_continuity', 'composition_reason'):
                nonempty(design.get(key), slide['id'] + '.design.' + key)
        for item in slide['content']:
            nonempty(item, 'page.content')
        if type(slide.get('seconds')) not in (int, float) or slide['seconds'] < 0:
            raise ValueError('Page timing must be nonnegative; use 0 for an untimed deck')
        duration += slide['seconds']
        for key in ('sources', 'requirements', 'visuals'):
            if not isinstance(slide.get(key), list):
                raise ValueError('Page needs a ' + key + ' list')
        for req in slide['requirements']:
            if req not in requirements:
                raise ValueError('Unknown requirement: ' + req)
            covered.add(req)
        allow = permissions(plan, slide['id'])
        for source in slide['sources']:
            kinds = source_kinds(source, sources)
            if 'generated' in kinds:
                raise ValueError('Generated imagery is not a factual source: ' + slide['id'])
            if 'external' in kinds and not allow['external_facts']:
                raise ValueError('External facts disallowed on ' + slide['id'])
        if not slide['visuals']:
            nonempty(slide.get('visual_rationale'), 'Reason for a text-only page')
        for visual in slide['visuals']:
            nonempty(visual.get('description'), 'visual.description')
            nonempty(visual.get('placement'), 'visual.placement')
            if visual.get('kind') == 'raster':
                if visual.get('asset') not in assets:
                    raise ValueError('Undeclared visual asset')
                asset = assets[visual['asset']]
                kinds = source_kinds(asset['source'], sources)
                if 'external' in kinds and not allow['external_images']:
                    raise ValueError('External image disallowed on ' + slide['id'])
                if 'generated' in kinds:
                    if not allow['generated_images']:
                        raise ValueError('Generated image disallowed on ' + slide['id'])
                    if asset['role'] == 'evidence':
                        raise ValueError('Generated image cannot be evidence')
            elif visual.get('kind') == 'native':
                for source in visual.get('sources', []):
                    kinds = source_kinds(source, sources)
                    if 'generated' in kinds or ('external' in kinds and not allow['external_facts']):
                        raise ValueError('Disallowed native visual source on ' + slide['id'])
            else:
                raise ValueError('Visual kind must be raster or native')
    missing = [r['id'] for r in requirements.values() if r['scope'] == 'pages' and r['id'] not in covered]
    if missing:
        raise ValueError('Requirements without a page: ' + ', '.join(missing))
    expected = brief.get('duration_seconds')
    if expected is not None and abs(duration - expected) > max(5, expected * .05):
        raise ValueError('Page timing does not fit the requested duration')
    for decision in plan.get('decisions', []):
        nonempty(decision.get('question'), 'decision.question')
        if decision.get('status') not in ('pending', 'resolved') or type(decision.get('required')) is not bool:
            raise ValueError('Decision needs status and required flag')
    return plan


def documents(plan):
    validate(plan)
    b = plan['brief']
    lines = [f'# {b["title"]}：逐页大纲', '', f'受众：{b["audience"]}', '', f'目的：{b["purpose"]}', '', f'主线：{b["narrative"]}', '', f'页数：{len(plan["slides"])}；预计讲述：{sum(s["seconds"] for s in plan["slides"]):g} 秒（0 表示不计时）', '', '## 需求覆盖', '']
    for req in plan.get('requirements', []):
        locations = '全稿' if req['scope'] == 'deck' else ', '.join(str(i) for i, s in enumerate(plan['slides'], 1) if req['id'] in s['requirements'])
        lines.append(f'- {req["id"]} [{req["origin"]}] {req["text"]} → {locations}')
    for i, s in enumerate(plan['slides'], 1):
        lines += ['', f'## 第 {i} 页｜{s["title"]}', '', f'页面 ID：{s["id"]}；讲述时间：{s["seconds"]:g} 秒', '', f'目的：{s["purpose"]}', '', f'核心信息：{s["message"]}', '', '### 页面文字与内容', ''] + ['- ' + text for text in s['content']]
        lines += ['', '### 图表与图片安排', '']
        for v in s['visuals']:
            lines.append(f'- {v["description"]}；位置：{v["placement"]}；素材/依据：{v.get("asset") or ", ".join(v.get("sources", [])) or "原生表达"}')
        if not s['visuals']:
            lines.append(s['visual_rationale'])
        lines += ['', f'布局与阅读顺序：{s["layout"]}', '', '内容来源：' + (', '.join(s['sources']) or '无外部事实主张'), '', f'讲述重点：{s.get("speaker_focus", s["message"])}', '', f'过渡：{s.get("transition", "本页收束")}', '', '落实要求：' + ', '.join(s['requirements'])]
        if s.get('design'):
            lines += ['', '### 本页设计方案', '']
            for key, label in [('visual_hierarchy','视觉重心与阅读顺序'), ('typography','字体与文字位置'), ('image_treatment','图片处理与保护内容'), ('style_continuity','参考风格的保留与拓展'), ('composition_reason','本页采用这种构图的理由')]:
                lines += [label + '：' + s['design'][key], '']
    lines += ['', '## 来源定位索引', '']
    for source in plan.get('sources', []):
        lines.append(f'- {source["id"]}：{source["locator"]}')
    record = [f'# {b["title"]}：素材与待确认事项', '', '本文件是制作记录，不作为幻灯片正文。', '', '## 素材边界', '', '```json', json.dumps(plan['policy'], ensure_ascii=False, indent=2), '```', '', '## 制作假设', '']
    record += ['- ' + item for item in b.get('assumptions', [])] or ['无额外假设。']
    record += ['', '## 来源', '']
    for source in plan.get('sources', []):
        record += [f'### {source["id"]}', '', f'类型：{source["kind"]}', '', f'定位：{source["locator"]}', '', f'使用依据：{source["rights"]}', '', f'说明：{source.get("note", "")}', '', '派生自：' + ', '.join(source.get('parents', [])), '']
    record += ['## 实际图片', '']
    for asset in plan.get('assets', []):
        record += [f'- {asset["id"]}：{asset["description"]}；来源 {asset["source"]}；用途 {asset["role"]}；SHA-256：{asset.get("sha256") or "待素材确定后绑定"}']
    record += ['', '## 待确认与已处理事项', '']
    for d in plan.get('decisions', []):
        record += [f'- [{d["status"]}] {d["question"]}；影响交付：{"是" if d["required"] else "否"}；方案/结论：{d.get("resolution", "待确认")}']
    if not plan.get('decisions'):
        record.append('无待确认事项。')
    return '\n'.join(lines) + '\n', '\n'.join(record) + '\n'


def write_documents(path):
    path = Path(path)
    outline, record = documents(read(path))
    (path.parent / 'outline.md').write_text(outline, encoding='utf-8')
    (path.parent / 'materials-and-decisions.md').write_text(record, encoding='utf-8')


def verify_build(root, final=False):
    root = Path(root)
    build = read(root / 'build.json')
    path = root / 'project/plan.json'
    if not path.exists():
        if build.get('planning_required'):
            raise ValueError('Required project outline is missing')
        return {'status': 'legacy-or-explicit-exemption'}
    plan = validate(read(path))
    if [s['id'] for s in plan['slides']] != [s['id'] for s in build['pages']]:
        raise ValueError('Actual page order differs from the outline; update the affected plan entries')
    for filename, expected in zip(('outline.md', 'materials-and-decisions.md'), documents(plan)):
        p = path.parent / filename
        if not p.exists() or p.read_text(encoding='utf-8') != expected:
            raise ValueError('Stale readable planning document: ' + filename)
    assets = index(plan.get('assets', []), 'assets')
    for spec, page in zip(plan['slides'], build['pages']):
        declared = {assets[v['asset']].get('sha256') for v in spec['visuals'] if v['kind'] == 'raster'}
        actual = set()
        svg = (root / page['svg']).resolve()
        for element in ET.parse(svg).getroot().iter('{http://www.w3.org/2000/svg}image'):
            href = element.get('href') or element.get('{http://www.w3.org/1999/xlink}href', '')
            asset_path = (svg.parent / href).resolve()
            if not asset_path.is_relative_to(root.resolve()) or not asset_path.is_file():
                raise ValueError('Image must be a local project file')
            actual.add(hashlib.sha256(asset_path.read_bytes()).hexdigest())
        if actual != declared:
            raise ValueError('Actual raster assets differ from page plan: ' + spec['id'])
    if final and any(d['status'] == 'pending' and d['required'] for d in plan.get('decisions', [])):
        raise ValueError('A required factual or material decision is pending; resolve it before final export')
    return {'status': 'passed', 'pages': len(plan['slides']), 'semantic_review': 'agent-owned'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('write').add_argument('--plan', type=Path, required=True)
    check = sub.add_parser('check')
    check.add_argument('--out', type=Path, required=True)
    check.add_argument('--final', action='store_true')
    args = parser.parse_args()
    if args.action == 'write':
        write_documents(args.plan)
        print(json.dumps({'outline': str(args.plan.parent / 'outline.md'), 'materials': str(args.plan.parent / 'materials-and-decisions.md')}, ensure_ascii=False))
    else:
        print(json.dumps(verify_build(args.out, args.final), ensure_ascii=False))


if __name__ == '__main__':
    main()
