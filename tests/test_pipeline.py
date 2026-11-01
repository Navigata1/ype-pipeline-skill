import copy, importlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ype-pipeline/scripts'))
import os, tempfile as _tempfile, json as _json
# Isolate the suite from the owner's workspace settings. The observance is
# switched off here only so tests stay deterministic on any day of the week;
# test_v83.py exercises the Sabbath window with explicit clocks.
_SETTINGS=Path(_tempfile.mkdtemp(prefix='ype-settings-'))/'settings.json'
_SETTINGS.write_text(_json.dumps({'notebook_account_label':'Pulse Vibe Daily','sabbath':{'enabled':False}}))
os.environ['YPE_SETTINGS']=str(_SETTINGS)
import core, media, publish, ype

VID='XIk-Ru85xmA'; URL='https://www.youtube.com/watch?v='+VID

def fixture(root,mode='quick'):
    root=Path(root);run=ype.make_run([URL],'Fixture playlist',mode,test_fixture=True)
    # Historical receipt fixtures exercise compatibility. New contracts have
    # dedicated positive and mutation tests in test_source_packaging.py.
    for key in ['editorial_contract','source_fidelity_contract','infographic_quality_contract','notebook_source_contract','notebook_caption_mode','depth_contract','notebook_account_label']:run.pop(key,None)
    dest=root/'videos'/VID;dest.mkdir(parents=True)
    source=dest/'fixture.webm';source.write_bytes(b'synthetic-video-not-a-real-download')
    sub=dest/'fixture.vtt';sub.write_text('WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nA useful idea about persistent records.\n\n00:00:05.000 --> 00:00:10.000\nRecords can keep context across sessions.\n')
    info={'id':VID,'url':URL,'metadata':{'id':VID,'title':'Fixture playlist','duration':20},'source':core.evidence(source),'caption':core.evidence(sub),'retention':'keep','origin':'test-fixture'}
    media.materialize(root,run['videos'][0],info);ype.save(root,run)
    frames=dest/'frames';frames.mkdir();rows=[]
    for i in range(3):
        from PIL import Image
        p=frames/f'f_{i:04}.jpg';Image.new('RGB',(8,8),(i*80,50,90)).save(p);rows.append({'name':p.name,'timestamp_seconds':float(i*5),'method':'synthetic','source_sha256':info['source']['sha256'],**core.evidence(p)})
    core.write(frames/'manifest.json',{'source_sha256':info['source']['sha256'],'frames':rows})
    prose='\n'.join('## '+h+'\nEvidence-grounded synthetic fixture for contract testing only.\n' for h in ['Thesis','What was said','What the frames add','Uncertainties','Application'])
    (dest/'analysis.md').write_text(prose)
    review={'source_sha256':info['source']['sha256'],'transcript_sha256':core.sha(dest/'transcript.txt'),'analysis_sha256':core.sha(dest/'analysis.md'),'reviewer':'synthetic-fixture','transcript_reviewed':True,'inspected_frames':[r['name'] for r in rows],'observations':[{'frame':rows[0]['name'],'timestamp_seconds':0.,'description':'This is a synthetic observation that does not assert actual viewing.'}],'claims':[{'text':'Synthetic claim references first caption cue.','cue_indices':[0],'frames':[]}]}
    review['inspected_frame_sha256']={r['name']:r['sha256'] for r in rows}
    core.write(dest/'analysis.json',review)
    return run,dest

def full_fixture(root):
    run,dest=fixture(root,'full');m=core.read(dest/'media.json');a=core.read(dest/'analysis.json')
    core.write(dest/'moments.json',{'source_sha256':m['source']['sha256'],'transcript_sha256':a['transcript_sha256'],'transcript_reviewed':True,'moments':[{'start':0,'end':15,'importance':'high','reason':'synthetic important moment','capture_seconds':[0,5,10]}]})
    mf=core.read(dest/'frames/manifest.json')
    for f in mf['frames']:f['moment_index']=0
    mf['moment_map_sha256']=core.sha(dest/'moments.json');core.write(dest/'frames/manifest.json',mf)
    files={}
    for name in ['enhanced-transcript.md','intelligence-report.md']:
        p=dest/name;p.write_text('Synthetic fixture substance. '*200);files[name]=core.evidence(p)
    core.write(dest/'full-review.json',{'reviewer':'fixture','source_faithfulness_checked':True,'analysis_sha256':a['analysis_sha256'],'files':files})
    request=dest/'image-request.txt';request.write_text('Synthetic adapter contract, no generation occurred.')
    core.write(dest/'infographic.json',{'provider':'native-image-gen','generated_at':'fixture','tool_call_ref':'synthetic-no-real-call','request':core.evidence(request),'file':mf['frames'][0],'analysis_sha256':a['analysis_sha256'],'visually_reviewed':True})
    p=Path(root)/'master-compilation.md';p.write_text('Synthetic master fixture. '*200)
    core.write(Path(root)/'synthesis.json',{'reviewer':'fixture','collection_digest':core.identity_hash(run),'file':core.evidence(p),'analyses':{VID:a['analysis_sha256']}})
    core.write(Path(root)/'categories.json',{'categories':[{'name':'Fixture','video_ids':[VID]}]})
    package=publish.packets(root);psha=core.sha(Path(root)/'notebooklm/package.json');browser=Path(root)/'synthetic-browser.txt';browser.write_text('Synthetic UI receipt; no remote action took place.')
    ready={'status':'ready','title':'fixture','artifact_id':'synthetic-id','opened_and_checked':True,'source_package_sha256':psha}
    state={'account_label':'Pulse Vibe Daily','account_verified':True,'collection_key':run['collection_key'],'notebook_title':run['title'],'notebook_url':'https://notebooklm.google.com/notebook/fixture','source_package_sha256':psha,'observed_at':'fixture','observed_by':'synthetic','browser_evidence':core.evidence(browser),'sources':[{'sha256':x['sha256'],'remote_source_id':'synthetic-'+str(i),'visible_title_verified':True} for i,x in enumerate(package['packets'])],'retrieval_checks':[{'question':'fixture','source_citation':'fixture','matches_local_evidence':True}],'audio':ready,'slides':ready}
    core.write(Path(root)/'notebooklm/state.json',state);return run,dest

class FullContracts(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.run,self.dest=full_fixture(self.root)
    def tearDown(self):self.tmp.cleanup()
    def test_full_contract_can_pass_as_fixture_only(self):
        r=publish.validate(self.root);self.assertTrue(r['integrity_pass'],r);self.assertTrue(r['test_fixture'])
    def test_audio_without_slides_fails(self):
        p=self.root/'notebooklm/state.json';s=core.read(p);s['slides']['status']='generating';core.write(p,s);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_browser_blocker_reports_all_missing_remote_stages(self):
        p=self.root/'notebooklm/state.json';s=core.read(p)
        s.update(notebook_url=None,account_verified=False,sources=[],retrieval_checks=[])
        s['audio']={'status':'blocked'};s['slides']={'status':'blocked'};core.write(p,s)
        r=publish.validate(self.root)
        self.assertFalse(r['integrity_pass'])
        self.assertIn('notebook URL absent or invalid',r['batch_errors'])
        self.assertIn('audio not visibly ready and checked',r['batch_errors'])
        self.assertIn('slides not visibly ready and checked',r['batch_errors'])
        self.assertIn('NotebookLM substantive retrieval check absent',r['batch_errors'])
    def test_empty_moment_map_rejected(self):
        p=self.dest/'moments.json';s=core.read(p);s['moments']=[];core.write(p,s)
        m=self.dest/'frames/manifest.json';d=core.read(m);d['moment_map_sha256']=core.sha(p);core.write(m,d)
        self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_wrong_time_with_matching_label_rejected(self):
        p=self.dest/'moments.json';s=core.read(p);s['moments'][0].update(start=16,end=19);core.write(p,s)
        m=self.dest/'frames/manifest.json';d=core.read(m);d['moment_map_sha256']=core.sha(p);core.write(m,d)
        self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_packet_tamper_rejected(self):
        p=self.root/'notebooklm/source-001.txt';p.write_text(p.read_text()+' unrelated bytes');self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_changed_enhanced_deliverable_rejected(self):
        p=self.dest/'enhanced-transcript.md';p.write_text(p.read_text()+' changed');self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_wrong_account_rejected(self):
        p=self.root/'notebooklm/state.json';s=core.read(p);s['account_label']='Other';core.write(p,s);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_categories_must_cover_all_videos(self):
        core.write(self.root/'categories.json',{'categories':[]});self.assertFalse(publish.validate(self.root)['integrity_pass'])

class Contracts(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.run,self.dest=fixture(self.root)
    def tearDown(self):self.tmp.cleanup()
    def test_valid_quick_fixture_is_labeled_fixture(self):
        r=publish.validate(self.root);self.assertTrue(r['integrity_pass']);self.assertTrue(r['test_fixture']);self.assertIn('attestations',r['status'])
    def test_source_tamper_fails(self):
        (self.dest/'fixture.webm').write_bytes(b'changed');self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_frame_missing_fails(self):
        (self.dest/'frames/f_0000.jpg').unlink();self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_duplicate_frame_manifest_fails(self):
        p=self.dest/'frames/manifest.json';m=core.read(p);m['frames'][1]=m['frames'][0];core.write(p,m);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_frame_wrong_time_fails(self):
        p=self.dest/'analysis.json';a=core.read(p);a['observations'][0]['timestamp_seconds']=11;core.write(p,a);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_replaced_frame_even_with_updated_manifest_fails(self):
        p=self.dest/'frames/manifest.json';m=core.read(p);f=Path(m['frames'][0]['path']);f.write_bytes(b'replaced');m['frames'][0].update(core.evidence(f));core.write(p,m)
        self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_nan_observation_fails(self):
        p=self.dest/'analysis.json';a=core.read(p);a['observations'][0]['timestamp_seconds']='nan';core.write(p,a);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_unprocessed_valid_member_fails(self):
        self.run['membership'].append({'position':2,'id':'00000000001'});ype.save(self.root,self.run);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_caption_cues_cannot_be_substituted(self):
        core.write(self.dest/'cues.json',[{'start':0,'end':10,'text':'unrelated'}]);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_changed_analysis_fails(self):
        with (self.dest/'analysis.md').open('a') as f:f.write('later edit')
        self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_pending_semantic_review_fails(self):
        p=self.dest/'analysis.json';a=core.read(p);a['transcript_reviewed']=False;core.write(p,a);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_uninspected_claim_fails(self):
        p=self.dest/'analysis.json';a=core.read(p);a['claims'][0]['frames']=['not-seen.jpg'];core.write(p,a);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_skipped_never_counts_as_complete(self):
        self.run['videos'][0]['state']='skipped';self.run['videos'][0]['skip_reason']='Private';ype.save(self.root,self.run);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_unknown_inventory_entry_blocks_completion(self):
        self.run['membership'].append({'position':2,'id':None});ype.save(self.root,self.run);self.assertFalse(publish.validate(self.root)['integrity_pass'])
    def test_quick_cannot_pass_full(self):
        self.run['mode']='full';ype.save(self.root,self.run);r=publish.validate(self.root);self.assertFalse(r['integrity_pass']);self.assertTrue(r['batch_errors'])
    def test_packet_contains_captions_visuals_analysis(self):
        p=publish.packets(self.root);text=Path(p['packets'][0]['path']).read_text();self.assertIn('Records can keep context',text);self.assertIn('Reviewed visual observations',text);self.assertIn('## Thesis',text)
    def test_packet_split_no_word_omission(self):
        p=self.dest/'analysis.md';words=['UNIQUE'+str(i) for i in range(700)];p.write_text(p.read_text()+'\n'+' '.join(words))
        a=core.read(self.dest/'analysis.json');a['analysis_sha256']=core.sha(p);core.write(self.dest/'analysis.json',a)
        pkg=publish.packets(self.root,100,50);text='\n'.join(Path(x['path']).read_text() for x in pkg['packets'])
        self.assertTrue(all(w in text.split() for w in words));self.assertTrue(all(x['words']<=100 for x in pkg['packets']))
    def test_packet_capacity_failure_preserves_sources(self):
        before=core.sha(self.dest/'fixture.webm')
        p=self.dest/'analysis.md';p.write_text(p.read_text()+'\n'+'word '*1000)
        a=core.read(self.dest/'analysis.json');a['analysis_sha256']=core.sha(p);core.write(self.dest/'analysis.json',a)
        with self.assertRaises(ValueError):publish.packets(self.root,100,2)
        self.assertEqual(before,core.sha(self.dest/'fixture.webm'))
    def test_renderer_no_script_images_or_javascript_links(self):
        text=publish.markdown('<script>alert(1)</script> [bad](javascript:alert(2)) ![tracking](https://evil.invalid/pixel.png)')
        self.assertNotIn('<script',text);self.assertNotIn('<img',text);self.assertNotIn('href="javascript:',text)
    def test_html_is_self_contained(self):
        p=publish.render(self.root);t=p.read_text();self.assertIn('<details>',t);self.assertNotIn('<script src',t);self.assertNotIn('<link',t)
    def test_registry_reuse_and_conflict(self):
        b=self.root/'browser.txt';b.write_text('synthetic observed account/title/url')
        state={'collection_key':self.run['collection_key'],'notebook_title':self.run['title'],'account_label':'Pulse Vibe Daily','account_verified':True,'browser_evidence':core.evidence(b),'notebook_url':'https://notebooklm.google.com/notebook/test-fixture','observed_at':'fixture'}
        core.write(self.root/'notebooklm/state.json',state);registry=self.root/'registry/registry.json'
        a=ype.registry_action(self.root,self.run,registry);c=ype.registry_action(self.root,self.run,registry);self.assertEqual(a,c);self.assertEqual(len(core.read(registry)['notebooks']),1)
        state['notebook_url']='https://notebooklm.google.com/notebook/other';core.write(self.root/'notebooklm/state.json',state)
        with self.assertRaises(ValueError):ype.registry_action(self.root,self.run,registry)

class Primitives(unittest.TestCase):
    def test_video_url_rejects_non_youtube_and_injection(self):
        for url in ['file:///etc/passwd','https://youtube.com.evil.invalid/?v='+VID,'https://user:pass@youtube.com/watch?v='+VID,'https://youtube.com/watch?v=../../bad']:
            with self.assertRaises(ValueError):core.youtube(url)
    def test_mixed_playlist_urls_fail_cleanly(self):
        with self.assertRaises(ValueError):core.collection_key([URL,'https://www.youtube.com/playlist?list=PL123'])
    def test_stable_playlist_identity(self):
        self.assertEqual(core.collection_key([], 'https://www.youtube.com/playlist?list=PL123'),core.collection_key([],'https://www.youtube.com/watch?v='+VID+'&list=PL123'))
    def test_rolling_captions_keep_new_suffix(self):
        raw='WEBVTT\n\n00:00.000 --> 00:02.000\nhello world\n\n00:01.000 --> 00:03.000\nhello world and more\n\n00:02.000 --> 00:04.000\nand more follows\n'
        self.assertEqual([x['text'] for x in core.captions(raw)],['hello world','and more','follows'])
    def test_long_prefix_keeps_distinct_endings(self):
        prefix='word '*300;raw=f'00:00.000 --> 00:01.000\n{prefix}alpha\n\n00:02.000 --> 00:03.000\n{prefix}beta\n'
        self.assertIn('beta',core.captions(raw)[1]['text']);self.assertEqual(len(core.captions(raw)),2)
    def test_backoff_and_retry_cap(self):
        v={'state':'pending'};core.record_failure(v,'HTTP 429',100);self.assertFalse(core.eligible(v,159));self.assertTrue(core.eligible(v,160))
        for _ in range(4):core.record_failure(v,'HTTP 429',200)
        self.assertEqual(v['state'],'needs_owner');self.assertFalse(core.eligible(v,100000))
    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):core.local(d,'../outside')
    def test_temp_symlink_cannot_redirect_write(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);outside=root/'outside';outside.write_text('preserve');(root/'run.json.tmp').symlink_to(outside)
            core.write(root/'run.json',{'ok':True});self.assertEqual(outside.read_text(),'preserve')
    def test_download_monitor_stops_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'partial').write_bytes(b'12345')
            with self.assertRaises(ValueError):media.command([sys.executable,'-c','import time;time.sleep(10)'],30,(p,1))
            self.assertTrue((p/'partial').exists())
    def test_missing_external_volume_no_fallback(self):
        with self.assertRaises(ValueError):ype.archive_ready('/Volumes/YPE-test-missing-volume/archive')
    def test_400_inventory_deduplicates_work_preserves_membership(self):
        entries=[{'id':f'{i:011}','title':str(i)} for i in range(400)]+[{'id':'00000000001'},{'id':None,'title':'Private'}]
        run=ype.make_run([],'400-fixture','quick',playlist='https://youtube.com/playlist?list=PLfixture',inventory_data=entries,test_fixture=True)
        self.assertEqual(len(run['videos']),400);self.assertEqual(len(run['membership']),402);self.assertEqual(run['membership'][-2]['state'],'duplicate')
    def test_batch_bound_resume_and_rate_limit_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=ype.make_run(['https://youtube.com/watch?v='+f'{i:011}' for i in range(400)],'large-fixture','quick',archive=str(root/'archive'),test_fixture=True)
            def materialize(root,v,data):v['state']='materials_ready'
            with patch.object(media,'preflight',return_value={'pass':True}),patch.object(media,'acquire',return_value={}) as acq,patch.object(media,'materialize',side_effect=materialize):
                self.assertEqual(ype.batch(root,run,2)['processed'],2);self.assertEqual(acq.call_count,2)
                self.assertEqual(ype.batch(root,run,2)['processed'],2);self.assertEqual(acq.call_count,4)
            with patch.object(media,'preflight',return_value={'pass':True}),patch.object(media,'acquire',side_effect=RuntimeError('HTTP 429')) as acq:
                self.assertEqual(ype.batch(root,run,2)['processed'],1);self.assertEqual(acq.call_count,1)
            saved=ype.load(root);self.assertEqual(sum(v['state']=='materials_ready' for v in saved['videos']),4);self.assertEqual(saved['videos'][4]['state'],'rate_limited')
            with patch.object(media,'acquire') as acq:
                self.assertEqual(ype.batch(root,saved)['processed'],0);acq.assert_not_called()
    def test_low_disk_stops_before_download(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=ype.make_run([URL],'disk-fixture','quick',archive=str(root/'archive'))
            with patch.object(media,'preflight',return_value={'pass':False}),patch.object(media,'acquire') as acq:
                r=ype.batch(root,run);self.assertEqual(r['status'],'blocked_preflight');acq.assert_not_called()
    def test_single_writer_lock(self):
        with tempfile.TemporaryDirectory() as d:
            with core.lock(d):
                code='import sys;sys.path.insert(0,sys.argv[1]);from core import lock\nwith lock(sys.argv[2]):print("WRITER")'
                r=subprocess.run([sys.executable,'-c',code,str(Path(core.__file__).parent),d],capture_output=True,text=True)
                self.assertNotEqual(r.returncode,0);self.assertNotIn('WRITER',r.stdout)

if __name__=='__main__':unittest.main()
