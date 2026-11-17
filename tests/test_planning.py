"""Behavior checks for planning, material scope and retained-source revisions."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / 'skills/reference-slide-workflow'
sys.path.insert(0, str(SKILL / 'scripts'))
from plan_project import validate, write_documents, verify_build
from build_html import initialize
from project_state import refresh


class PlanningTests(unittest.TestCase):
    def test_page_design_outline_rejects_missing_design_decisions(self):
        self.plan['brief']['design_depth'] = 'page-design'
        with self.assertRaisesRegex(ValueError, 'design.visual_hierarchy'):
            validate(self.plan)

    def test_page_design_decisions_are_in_the_readable_outline(self):
        self.plan['brief']['design_depth'] = 'page-design'
        for slide in self.plan['slides']:
            slide['design'] = {
                'visual_hierarchy': 'Enter at the single wide photo, then read its nearby explanation.',
                'typography': 'Large serif title and compact sans captions attach to the image edge.',
                'image_treatment': 'Preserve the full evidence photo, with native framing only.',
                'style_continuity': 'Keep the quiet margin and relative title weight from the reference.',
                'composition_reason': 'The page explains one subject; unequal areas express its dominance.'}
        p = self.project()
        outline = (p / 'outline.md').read_text(encoding='utf-8')
        for text in self.plan['slides'][0]['design'].values():
            self.assertIn(text, outline)

    def setUp(self):
        self.plan = json.loads((SKILL / 'references/plan.example.json').read_text(encoding='utf-8'))
        self.root = Path(tempfile.mkdtemp(prefix='slide-plan-test-'))

    def project(self):
        p = self.root / 'project'
        p.mkdir(exist_ok=True)
        (p / 'plan.json').write_text(json.dumps(self.plan), encoding='utf-8')
        write_documents(p / 'plan.json')
        pages = []
        for s in self.plan['slides']:
            relative = 'project/' + s['id'] + '.svg'
            (self.root / relative).write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
            pages.append({'id': s['id'], 'svg': relative})
        (self.root / 'build.json').write_text(json.dumps({'planning_required': True, 'pages': pages}), encoding='utf-8')
        return p

    def test_detailed_plan_matches_actual_page_order(self):
        self.project()
        self.assertEqual(verify_build(self.root)['status'], 'passed')
        self.plan['slides'].reverse()
        (self.root / 'project/plan.json').write_text(json.dumps(self.plan), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'page order'):
            verify_build(self.root)

    def test_missing_requirement_and_duration_are_detected(self):
        plan = copy.deepcopy(self.plan)
        plan['requirements'].append({'id': 'new', 'text': 'Explain cost', 'origin': 'user', 'scope': 'pages'})
        with self.assertRaisesRegex(ValueError, 'without a page'):
            validate(plan)
        self.plan['slides'][0]['seconds'] = 120
        with self.assertRaisesRegex(ValueError, 'duration'):
            validate(self.plan)

    def test_restricted_material_and_scoped_exception(self):
        self.plan['sources'].append({'id': 'photo', 'kind': 'external', 'locator': 'source-page', 'rights': 'licensed'})
        self.plan['assets'].append({'id': 'a', 'source': 'photo', 'role': 'context', 'description': 'Photo of the reading room'})
        self.plan['slides'][0]['visuals'] = [{'kind': 'raster', 'asset': 'a', 'description': 'Reading room', 'placement': 'right'}]
        with self.assertRaisesRegex(ValueError, 'External image disallowed'):
            validate(self.plan)
        self.plan['policy']['overrides'] = [{'slide': 'need', 'basis': 'User permits a photo here', 'allow': {'external_images': True}}]
        validate(self.plan)
        self.plan['slides'][1]['visuals'] = copy.deepcopy(self.plan['slides'][0]['visuals'])
        with self.assertRaisesRegex(ValueError, 'External image disallowed on process'):
            validate(self.plan)

    def test_derived_source_cannot_hide_external_or_generated_origin(self):
        self.plan['sources'] += [
            {'id': 'web', 'kind': 'external', 'locator': 'article', 'rights': 'licensed'},
            {'id': 'redraw', 'kind': 'derived', 'parents': ['web'], 'locator': 'redrawn-chart.svg', 'rights': 'same'}]
        self.plan['slides'][0]['sources'] = ['redraw']
        with self.assertRaisesRegex(ValueError, 'External facts disallowed'):
            validate(self.plan)
        self.plan['sources'][-2]['kind'] = 'generated'
        self.plan['policy']['generated_images'] = True
        with self.assertRaisesRegex(ValueError, 'not a factual source'):
            validate(self.plan)

    def test_generated_image_permission_does_not_allow_fake_evidence(self):
        self.plan['policy']['generated_images'] = True
        self.plan['sources'].append({'id': 'g', 'kind': 'generated', 'locator': 'generation-brief', 'rights': 'created for project'})
        self.plan['assets'] = [{'id': 'a', 'source': 'g', 'role': 'evidence', 'description': 'Experiment picture'}]
        self.plan['slides'][0]['visuals'] = [{'kind': 'raster', 'asset': 'a', 'description': 'Experiment', 'placement': 'right'}]
        with self.assertRaisesRegex(ValueError, 'cannot be evidence'):
            validate(self.plan)
        self.plan['assets'][0]['role'] = 'concept'
        validate(self.plan)

    def test_production_questions_stay_separate_and_block_final_only(self):
        self.plan['decisions'] = [{'question': 'Which source is approved?', 'status': 'pending', 'required': True}]
        p = self.project()
        self.assertNotIn('Which source is approved?', (p / 'outline.md').read_text(encoding='utf-8'))
        self.assertIn('Which source is approved?', (p / 'materials-and-decisions.md').read_text(encoding='utf-8'))
        verify_build(self.root)
        with self.assertRaisesRegex(ValueError, 'pending'):
            verify_build(self.root, final=True)

    def test_changed_image_and_stale_readable_outline_are_detected(self):
        payload = b'fixture image bytes'
        self.plan['assets'] = [{'id': 'a', 'source': 'notes', 'role': 'context', 'description': 'User image', 'sha256': hashlib.sha256(payload).hexdigest()}]
        self.plan['slides'][0]['visuals'] = [{'kind': 'raster', 'asset': 'a', 'description': 'User image', 'placement': 'right'}]
        p = self.project()
        (p / 'image.png').write_bytes(payload)
        (p / 'need.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="image.png"/></svg>', encoding='utf-8')
        verify_build(self.root)
        (p / 'image.png').write_bytes(b'different image')
        with self.assertRaisesRegex(ValueError, 'raster assets differ'):
            verify_build(self.root)
        (p / 'outline.md').write_text('stale outline', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Stale readable'):
            verify_build(self.root)

    def test_new_custom_build_requires_outline_before_writing_project(self):
        source = self.root / 'source'
        source.mkdir()
        profile = {'canvas': [1280, 720], 'typography': {'body': {'family': 'Arial', 'size': 24}}}
        (source / 'profile.json').write_text(json.dumps(profile), encoding='utf-8')
        (source / 'deck.json').write_text(json.dumps({'profile': 'profile.json', 'slides': [{'id': 'need', 'svg': 'need.svg'}]}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'detailed outline'):
            initialize(source / 'deck.json', self.root / 'build')
        self.assertFalse((self.root / 'build').exists())

    def test_custom_build_retains_plan_and_plan_only_revision_reuses_page_pixels(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'plan.json').write_text(json.dumps(self.plan), encoding='utf-8')
        write_documents(source / 'plan.json')
        profile = {'canvas': [1280, 720], 'typography': {'body': {'family': 'Arial', 'size': 24}}}
        (source / 'profile.json').write_text(json.dumps(profile), encoding='utf-8')
        slides = []
        for page in self.plan['slides']:
            (source / (page['id'] + '.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"><text id="title" x="60" y="90" font-family="Arial" font-size="24">Example</text></svg>', encoding='utf-8')
            slides.append({'id': page['id'], 'svg': page['id'] + '.svg'})
        spec = source / 'deck.json'
        spec.write_text(json.dumps({'profile': 'profile.json', 'plan': 'plan.json', 'slides': slides}), encoding='utf-8')
        out = self.root / 'build'
        initialize(spec, out)
        before = json.loads((out / 'build.json').read_text(encoding='utf-8'))
        plan_file = out / 'project/plan.json'
        current = json.loads(plan_file.read_text(encoding='utf-8'))
        current['slides'][0]['speaker_focus'] = 'Updated speaker emphasis; no visible change'
        plan_file.write_text(json.dumps(current), encoding='utf-8')
        write_documents(plan_file)
        refresh(out)
        after = json.loads((out / 'build.json').read_text(encoding='utf-8'))
        self.assertNotEqual(before['build_digest'], after['build_digest'])
        self.assertEqual(after['changed_visual_pages'], [])
        self.assertTrue((out / 'project/materials-and-decisions.md').is_file())


if __name__ == '__main__':
    unittest.main()
