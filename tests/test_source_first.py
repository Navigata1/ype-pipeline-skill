"""Behavioral checks for source-first runs; all media and reviews are synthetic."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ype-pipeline/scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_pipeline import fixture,full_fixture,VID,URL
import core,publish,ype

CONTRACTS=('editorial_contract','source_fidelity_contract','infographic_quality_contract','notebook_source_contract','notebook_caption_mode')

def source_fixture(root):
    run,dest=full_fixture(root)
    current=ype.make_run([URL],run['title'],'full',test_fixture=True)
    run.update({k:current[k] for k in CONTRACTS});ype.save(root,run)
    (dest/'enhanced-transcript.md').write_text('## Complete timed section\n'+'Synthetic source explanations, examples and qualifications. '*100)
    (dest/'analysis.md').write_text((dest/'analysis.md').read_text().split('## Application')[0])
    a=core.read(dest/'analysis.json');a['analysis_sha256']=core.sha(dest/'analysis.md');core.write(dest/'analysis.json',a)
    m=core.read(dest/'media.json');frames=a['inspected_frames']
    core.write(dest/'enhanced-source-map.json',{'source_sha256':m['source']['sha256'],'transcript_sha256':core.sha(dest/'transcript.txt'),'enhanced_sha256':core.sha(dest/'enhanced-transcript.md'),'reviewer':'synthetic','examples_and_qualifications_checked':True,'sections':[{'heading':'Complete timed section','cue_start':0,'cue_end':1,'frame_names':frames}]})
    review=core.read(dest/'full-review.json');review.update(analysis_sha256=a['analysis_sha256'],source_map_sha256=core.sha(dest/'enhanced-source-map.json'))
    review['files']['enhanced-transcript.md']=core.evidence(dest/'enhanced-transcript.md')
    for key in ['substance_preserved','visuals_integrated','source_first','project_applications_separate','stale_uncertainties_resolved']:review[key]=True
    core.write(dest/'full-review.json',review)
    concepts=[{'id':'persistent-records','title':'Records retain context','cue_indices':[0,1],'frames':[],'represented_as':'A record with a continuation example'}, {'id':'visible-evidence','title':'Synthetic visible example','cue_indices':[],'frames':[frames[0]],'represented_as':'Annotated synthetic display'}]
    core.write(dest/'infographic-brief.json',{'enhanced_sha256':core.sha(dest/'enhanced-transcript.md'),'source_map_sha256':core.sha(dest/'enhanced-source-map.json'),'composition':{'form':'comparison','rationale':'Synthetic example compares records and transient recollection'},'concepts':concepts})
    asset=core.read(dest/'infographic.json');asset.update(analysis_sha256=a['analysis_sha256'],enhanced_sha256=core.sha(dest/'enhanced-transcript.md'),brief=core.evidence(dest/'infographic-brief.json'),quality_review={'reviewer':'synthetic','concept_ids':[c['id'] for c in concepts],'review_notes':'Synthetic fixture only, no actual image generation or review occurred.'})
    for k in ['coverage_checked','relationships_checked','labels_checked','legibility_checked','source_specificity_checked']:asset['quality_review'][k]=True
    core.write(dest/'infographic.json',asset)
    sr=core.read(root/'synthesis.json');sr['analyses'][VID]=a['analysis_sha256'];core.write(root/'synthesis.json',sr)
    package=publish.packets(root);state=core.read(root/'notebooklm/state.json');psha=core.sha(root/'notebooklm/package.json')
    state['source_package_sha256']=psha;state['sources']=[{'sha256':p['sha256'],'remote_source_id':'synthetic-'+p['video_id'],'visible_title_verified':True} for p in package['packets']]
    for k in ['audio','slides']:state[k]['source_package_sha256']=psha
    core.write(root/'notebooklm/state.json',state)
    return run,dest

class SourceFirst(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.run,self.dest=source_fixture(self.root)
    def tearDown(self):self.tmp.cleanup()
    def errors(self):return publish.video_checks(self.root,self.run['videos'][0],'full')
    def rewrite(self,name,fn):
        p=self.dest/name;data=core.read(p);fn(data);core.write(p,data)
    def test_new_init_activates_contracts_without_opt_in(self):
        run=ype.make_run([URL],'new','full');self.assertTrue(all(run.get(k) for k in CONTRACTS));self.assertEqual(run['notebook_source_contract'],'one-video/1')
    def test_legacy_timed_contract_does_not_require_new_attestations(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run,dest=full_fixture(root);run['source_fidelity_contract']='timed-source-account/1';ype.save(root,run)
            media=core.read(dest/'media.json')
            core.write(dest/'enhanced-source-map.json',{'source_sha256':media['source']['sha256'],'transcript_sha256':core.sha(dest/'transcript.txt'),'enhanced_sha256':core.sha(dest/'enhanced-transcript.md'),'reviewer':'legacy synthetic','examples_and_qualifications_checked':True,'sections':[{'heading':'Synthetic fixture substance.','cue_start':0,'cue_end':1,'frame_names':[]}]})
            review=core.read(dest/'full-review.json');review['source_map_sha256']=core.sha(dest/'enhanced-source-map.json');core.write(dest/'full-review.json',review)
            self.assertFalse(publish.video_checks(root,run['videos'][0],'full'))
    def test_complete_source_contract_passes_as_fixture_only(self):
        result=publish.validate(self.root);self.assertTrue(result['integrity_pass'],result);self.assertTrue(result['test_fixture']);self.assertFalse(result['acceptance']['independently_proven'])
    def test_project_heading_is_not_required_for_new_quick_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run,dest=fixture(root);run['editorial_contract']='source-first/1';ype.save(root,run)
            (dest/'analysis.md').write_text((dest/'analysis.md').read_text().split('## Application')[0]);a=core.read(dest/'analysis.json');a['analysis_sha256']=core.sha(dest/'analysis.md');core.write(dest/'analysis.json',a)
            self.assertFalse(publish.video_checks(root,run['videos'][0],'quick'))
    def test_unintegrated_written_observation_fails(self):
        self.rewrite('enhanced-source-map.json',lambda x:x['sections'][0].update(frame_names=[]));self.assertIn('reviewed visual observations are not mapped into source sections',self.errors())
    def test_missing_cue_interval_fails(self):
        self.rewrite('enhanced-source-map.json',lambda x:x['sections'][0].update(cue_end=0));self.assertIn('expanded source map omits caption intervals',self.errors())
    def test_overlapping_sections_fail(self):
        self.rewrite('enhanced-source-map.json',lambda x:x['sections'].append(dict(x['sections'][0])));self.assertIn('expanded source sections overlap or are out of order',self.errors())
    def test_missing_semantic_acceptance_fails(self):
        self.rewrite('full-review.json',lambda x:x.pop('substance_preserved'));self.assertIn('full semantic acceptance absent: substance_preserved',self.errors())
    def test_unresolved_stale_uncertainty_fails(self):
        self.rewrite('full-review.json',lambda x:x.update(stale_uncertainties_resolved=False));self.assertIn('full semantic acceptance absent: stale_uncertainties_resolved',self.errors())
    def test_unreviewed_major_concept_fails(self):
        self.rewrite('infographic.json',lambda x:x['quality_review']['concept_ids'].pop());self.assertIn('infographic quality review does not cover every main concept',self.errors())
    def test_false_label_acceptance_fails(self):
        self.rewrite('infographic.json',lambda x:x['quality_review'].update(labels_checked=False));self.assertIn('infographic quality acceptance absent: labels_checked',self.errors())
    def test_changed_source_invalidates_image(self):
        p=self.dest/'enhanced-transcript.md';p.write_text(p.read_text()+' Revised source detail.');self.assertIn('infographic stale against expanded source account',self.errors())
    def test_revised_brief_requires_new_bound_review(self):
        self.rewrite('infographic-brief.json',lambda x:x['concepts'][0].update(title='Corrected label'));self.assertIn('infographic brief absent or changed',self.errors())
    def test_invalid_concept_citation_fails(self):
        self.rewrite('infographic-brief.json',lambda x:x['concepts'][0].update(cue_indices=[999]));self.assertIn('infographic concept cue reference invalid',self.errors())
    def test_batch_merge_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'one NotebookLM source per video'):publish.packets(self.root,granularity='batch')
    def test_one_video_cannot_be_split_and_failure_preserves_package(self):
        before={str(p):p.read_bytes() for p in (self.root/'notebooklm').iterdir()}
        with self.assertRaisesRegex(ValueError,'do not split'):publish.packets(self.root,words_per_source=100)
        self.assertEqual(before,{str(p):p.read_bytes() for p in (self.root/'notebooklm').iterdir()})
    def test_only_enriched_source_enters_default_notebook(self):
        (self.root/'project-applications.md').write_text('UNIQUE_PROJECT_PLAN')
        (self.root/'master-compilation.md').write_text('UNIQUE_CROSS_VIDEO_SYNTHESIS')
        community=self.dest/'community';community.mkdir();(community/'community.md').write_text('UNIQUE_AUDIENCE_RECEPTION')
        package=publish.packets(self.root);self.assertEqual(len(package['packets']),1);self.assertEqual(package['packets'][0]['video_id'],VID)
        text=Path(package['packets'][0]['path']).read_text();self.assertIn('Complete timed section',text)
        for marker in ['UNIQUE_PROJECT_PLAN','UNIQUE_CROSS_VIDEO_SYNTHESIS','UNIQUE_AUDIENCE_RECEPTION']:self.assertNotIn(marker,text)
    def test_project_report_is_visible_separately(self):
        (self.root/'project-applications.md').write_text('UNIQUE_PROJECT_PLAN')
        self.assertIn('UNIQUE_PROJECT_PLAN',publish.render(self.root).read_text())
    def test_local_synthesis_changes_do_not_invalidate_source_package(self):
        before=publish.package_inputs(self.root,self.run);(self.root/'master-compilation.md').write_text('Changed downstream synthesis')
        self.assertEqual(before,publish.package_inputs(self.root,self.run))
    def test_duplicate_notebook_video_identity_fails(self):
        p=self.root/'notebooklm/package.json';data=core.read(p);data['packets'].append(dict(data['packets'][0]));core.write(p,data)
        self.assertIn('NotebookLM requires exactly one source per video',publish.validate(self.root)['batch_errors'])
    def add_video(self,vid):
        import shutil
        dest=self.root/'videos'/vid;shutil.copytree(self.dest,dest)
        media=core.read(dest/'media.json');media['id']=vid;core.write(dest/'media.json',media)
        mf=core.read(dest/'frames/manifest.json')
        for row in mf['frames']:row['path']=str(dest/'frames'/row['name'])
        core.write(dest/'frames/manifest.json',mf)
        video=dict(self.run['videos'][0],id=vid,url='https://www.youtube.com/watch?v='+vid,title='Distinct source '+vid)
        self.run['videos'].append(video);self.run['membership'].append({'position':len(self.run['videos']),'id':vid,'title':video['title']});ype.save(self.root,self.run)
    def test_37_video_collection_has_37_distinct_sources(self):
        for i in range(36):self.add_video(f'{i:011}')
        package=publish.packets(self.root,source_cap=50)
        self.assertEqual(len(package['packets']),37);self.assertEqual(len({p['video_id'] for p in package['packets']}),37)
        for p in package['packets']:
            text=Path(p['path']).read_text();self.assertEqual(text.count('Video ID:'),1);self.assertIn('Video ID: '+p['video_id'],text)
    def test_capacity_failure_preserves_prior_package(self):
        self.add_video('00000000001');before=(self.root/'notebooklm/package.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'do not combine or omit'):publish.packets(self.root,source_cap=2)
        self.assertEqual(before,(self.root/'notebooklm/package.json').read_bytes())

if __name__=='__main__':unittest.main()
