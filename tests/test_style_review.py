"""Behavior checks for fresh, complete style assessments; not an aesthetic scorer."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
SKILL=Path(__file__).resolve().parents[1]/'skills/reference-slide-workflow'
sys.path.insert(0,str(SKILL/'scripts'))
import style_review as sr
from project_state import save, sha

class StyleReviewTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='slide-style-test-'))
        (self.root/'project').mkdir();(self.root/'screenshots').mkdir()
        self.profile={'reference_mode':'single','style_targets':[{'id':'subject-space','reference':'reference cover','observable':'Subject silhouette and type share a controlled whitespace boundary','pages':[1]}]}
        save(self.root/'project/style-profile.json',self.profile)
        for n in (1,2):(self.root/f'screenshots/{n:02}.png').write_bytes(f'fixture pixels {n}'.encode())
        self.report={'status':'passed','build_digest':'build-a','pages':[{'page':n,'visual_digest':f'visual-{n}','screenshot_sha256':sha(self.root/f'screenshots/{n:02}.png')} for n in (1,2)]}
        save(self.root/'preview-report.json',self.report)
        self.manifest=patch.object(sr,'verify_manifest',return_value={'build_digest':'build-a'})
        self.manifest.start();self.addCleanup(self.manifest.stop)
        self.input={'targets':[{'id':'subject-space','page':1,'status':'adapted','observation':'The wider subject meets the title whitespace while its roofline remains clear; the crop changes for the new photograph.'}]}
    def test_missing_assessment_blocks(self):
        with self.assertRaisesRegex(ValueError,'before export'):sr.require(self.root)
    def test_failed_target_blocks(self):
        value=copy.deepcopy(self.input);value['targets'][0]['status']='failed';sr.record(self.root,value)
        with self.assertRaisesRegex(ValueError,'Unresolved'):sr.require(self.root)
    def test_changed_representative_render_requires_review(self):
        sr.record(self.root,self.input);sr.require(self.root)
        (self.root/'screenshots/01.png').write_bytes(b'changed picture')
        self.report['pages'][0].update(screenshot_sha256=sha(self.root/'screenshots/01.png'),visual_digest='changed-visual')
        save(self.root/'preview-report.json',self.report)
        with self.assertRaisesRegex(ValueError,'stale'):sr.require(self.root)
    def test_unrelated_page_render_preserves_review(self):
        sr.record(self.root,self.input)
        (self.root/'screenshots/02.png').write_bytes(b'other picture changed')
        self.report['pages'][1].update(screenshot_sha256=sha(self.root/'screenshots/02.png'),visual_digest='other-visual')
        save(self.root/'preview-report.json',self.report);sr.require(self.root)
    def test_changed_style_definition_requires_review(self):
        sr.record(self.root,self.input);self.profile['style_targets'][0]['observable']='Subject follows the new diagonal whitespace boundary'
        save(self.root/'project/style-profile.json',self.profile)
        with self.assertRaisesRegex(ValueError,'profile changed'):sr.require(self.root)
    def test_incomplete_or_wrong_page_assessment_rejected(self):
        with self.assertRaisesRegex(ValueError,'exactly once'):sr.record(self.root,{'targets':[]})
        value=copy.deepcopy(self.input);value['targets'][0]['page']=2
        with self.assertRaisesRegex(ValueError,'representative'):sr.record(self.root,value)
    def test_legacy_project_can_receive_local_revision(self):
        save(self.root/'project/style-profile.json',{'typography':{'body':{'family':'Arial'}}});sr.require(self.root)

    def enable_pair_review(self):
        from PIL import Image
        self.profile['review_protocol']='reference-pair-v1';save(self.root/'project/style-profile.json',self.profile)
        self.reference=self.root/'reference.png';Image.new('RGB',(320,180),'brown').save(self.reference)
        Image.new('RGB',(320,180),'tan').save(self.root/'screenshots/01.png')
        self.report['pages'][0]['screenshot_sha256']=sha(self.root/'screenshots/01.png');save(self.root/'preview-report.json',self.report)
        self.input['targets'][0].update(reference_observation='The reference places a compact paragraph next to the subject and leaves the opposite field quiet.',adaptation_reason='The new subject is wider, so the short paragraph moves along its edge without becoming a detached sidebar.',remaining_gaps=[])

    def test_comparative_approval_requires_actual_pair(self):
        self.enable_pair_review()
        with self.assertRaisesRegex(ValueError,'comparison before'):sr.record(self.root,self.input)

    def test_open_loss_blocks_an_otherwise_adapted_approval(self):
        self.enable_pair_review();sr.prepare_comparison(self.root,self.reference,1)
        self.input['targets'][0]['remaining_gaps']=['The paragraph is still detached from its subject.'];sr.record(self.root,self.input)
        with self.assertRaisesRegex(ValueError,'Unresolved reference-style gaps'):sr.require(self.root)

    def test_current_pair_and_resolved_loss_review_pass(self):
        self.enable_pair_review();sr.prepare_comparison(self.root,self.reference,1);sr.record(self.root,self.input);sr.require(self.root)

    def test_changed_pair_invalidates_approval(self):
        self.enable_pair_review();sr.prepare_comparison(self.root,self.reference,1);sr.record(self.root,self.input)
        (self.root/'style-comparisons/pair-01.png').write_bytes(b'changed board')
        with self.assertRaisesRegex(ValueError,'stale or altered'):sr.require(self.root)

if __name__=='__main__':unittest.main()
