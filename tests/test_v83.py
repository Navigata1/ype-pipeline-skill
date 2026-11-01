"""v8.3 contracts: coverage and depth, carry-over, review tools, account settings and the Sabbath pause.
All media, reviews and clocks are synthetic; no network is used."""
import contextlib, datetime as dt, io, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ype-pipeline/scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_pipeline  # noqa: F401  (isolates settings for the suite)
from PIL import Image
import core, depth, library, media, publish, sabbath, ype

VID='XIk-Ru85xmA';CHI=ZoneInfo('America/Chicago')
ON={'notebook_account_label':'Pulse Vibe Daily','sabbath':{'enabled':True}}

def at(text):return dt.datetime.fromisoformat(text).replace(tzinfo=CHI).timestamp()

def depth_fixture(root,frames=16,inspect=(0,3,6,9,12,15)):
    root=Path(root);run=ype.make_run(['https://www.youtube.com/watch?v='+VID],'Depth fixture','quick',archive=str(root/'archive'),test_fixture=True)
    dest=root/'videos'/VID;dest.mkdir(parents=True)
    source=dest/'fixture.webm';source.write_bytes(b'synthetic-video-not-a-real-download')
    sub=dest/'fixture.vtt';sub.write_text('WEBVTT\n\n'+'\n\n'.join(f'00:00:{a:02}.000 --> 00:00:{b:02}.000\n{t}' for a,b,t in [(0,5,'Records keep context across sessions.'),(5,10,'A folder carries sequence and scope.'),(10,15,'One librarian walks the catalog.'),(15,19,'Templates are fixed versions.')])+'\n')
    info={'id':VID,'url':run['videos'][0]['url'],'metadata':{'id':VID,'title':'Depth fixture','duration':20},'source':core.evidence(source),'caption':core.evidence(sub),'retention':'keep','origin':'test-fixture'}
    media.materialize(root,run['videos'][0],info);ype.save(root,run)
    folder=dest/'frames';folder.mkdir();rows=[]
    for i in range(frames):
        p=folder/f'f_{i:04}.jpg';Image.new('RGB',(64,36),(i*15%255,60,120)).save(p);rows.append({'name':p.name,'timestamp_seconds':i*1.25,'method':'synthetic',**core.evidence(p)})
    core.write(folder/'manifest.json',{'sampling_schema':2,'requested_count':frames,'dedup':True,'source_sha256':info['source']['sha256'],'frames':rows})
    review(root,dest,[rows[i] for i in inspect])
    return run,dest

def review(root,dest,inspected):
    (dest/'analysis.md').write_text('\n'.join('## '+h+'\nSynthetic fixture prose for contract testing only.\n' for h in ['Thesis','What was said','What the frames add','Uncertainties']))
    a={'source_sha256':core.read(dest/'media.json')['source']['sha256'],'transcript_sha256':core.sha(dest/'transcript.txt'),'analysis_sha256':core.sha(dest/'analysis.md'),'reviewer':'synthetic-fixture','transcript_reviewed':True,
       'producer':{'model':'synthetic-fixture-model'},'sampling_audit':{'verdict':'pass'},'inspected_frames':[r['name'] for r in inspected],'inspected_frame_sha256':{r['name']:r['sha256'] for r in inspected},
       'observations':[{'frame':r['name'],'timestamp_seconds':r['timestamp_seconds'],'legibility':'clear','description':'Synthetic observation; no actual viewing is asserted here.'} for r in inspected],
       'claims':[{'text':'Synthetic claim '+str(i),'cue_indices':[i],'frames':[]} for i in range(4)]}
    core.write(dest/'analysis.json',a)

class DepthQuick(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.run,self.dest=depth_fixture(self.root)
    def tearDown(self):self.tmp.cleanup()
    def errors(self):return publish.video_checks(self.root,core.read(self.root/'run.json')['videos'][0],'quick')
    def edit(self,fn):
        a=core.read(self.dest/'analysis.json');fn(a);core.write(self.dest/'analysis.json',a)
    def test_new_runs_carry_depth_contract_and_settings_account(self):
        self.assertEqual(self.run['depth_contract'],'depth/1');self.assertEqual(self.run['notebook_account_label'],'Pulse Vibe Daily');self.assertEqual(self.run['version'],'8.3')
    def test_complete_depth_fixture_passes(self):
        self.assertEqual(self.errors(),[]);self.assertTrue(publish.validate(self.root)['integrity_pass'])
    def test_below_duration_minimum_needs_static_downgrade(self):
        run,dest=depth_fixture(self.root/'thin',frames=8,inspect=(0,3,7))
        errs=publish.video_checks(self.root/'thin',run['videos'][0],'quick');self.assertTrue(any('below the duration minimum' in e for e in errs))
        a=core.read(dest/'analysis.json');a['sampling_audit']={'verdict':'visual_static_downgrade_accepted','reason':'Static talking head; probe showed no slides, code or UI.'};core.write(dest/'analysis.json',a)
        self.assertEqual(publish.video_checks(self.root/'thin',run['videos'][0],'quick'),[])
    def test_downgrade_without_reason_fails(self):
        self.edit(lambda a:a.update(sampling_audit={'verdict':'visual_static_downgrade_accepted'}));self.assertIn('static downgrade needs a written reason',self.errors())
    def test_missing_sampling_verdict_fails(self):
        self.edit(lambda a:a.pop('sampling_audit'));self.assertTrue(any('sampling audit verdict' in e for e in self.errors()))
    def test_closing_scout_required(self):
        mf=core.read(self.dest/'frames/manifest.json');mf['frames']=[r for r in mf['frames'] if r['timestamp_seconds']<4];core.write(self.dest/'frames/manifest.json',mf)
        self.assertTrue(any('closing scout' in e for e in self.errors()))
    def test_legibility_and_producer_required(self):
        self.edit(lambda a:(a['observations'][0].pop('legibility'),a.pop('producer')));e=self.errors()
        self.assertTrue(any('legibility' in x for x in e));self.assertTrue(any('producer' in x for x in e))
    def test_every_quarter_must_be_cited_or_excepted(self):
        def early(a):
            a['claims']=[{'text':'early','cue_indices':[0],'frames':[]}];a['observations']=a['observations'][:1]
        self.edit(early);self.assertTrue(any('quarter' in e for e in self.errors()))
        self.edit(lambda a:a.update(coverage_exception='The second half is a silent screen recording with no new content.'))
        self.assertFalse(any('quarter' in e for e in self.errors()))
    def test_placeholder_text_fails(self):
        (self.dest/'analysis.md').write_text((self.dest/'analysis.md').read_text()+'\nTBD\n')
        self.edit(lambda a:a.update(analysis_sha256=core.sha(self.dest/'analysis.md')));self.assertIn('placeholder text left in analysis.md',self.errors())
    def test_ordinary_word_placeholder_is_not_a_template_marker(self):
        (self.dest/'analysis.md').write_text((self.dest/'analysis.md').read_text()+'\nThe 0 B entry may be a placeholder record or a display bug.\n')
        self.edit(lambda a:a.update(analysis_sha256=core.sha(self.dest/'analysis.md')));self.assertEqual(self.errors(),[])
    def test_priority_section_needs_frames_and_claim(self):
        run=core.read(self.root/'run.json');run['videos'][0]['priority_sections']=[{'start':6,'end':9,'reason':'Owner flagged demo'}];core.write(self.root/'run.json',run)
        self.assertTrue(any('priority section' in e for e in self.errors()))
        run['videos'][0]['priority_sections']=[{'start':3,'end':8,'reason':'Owner flagged demo'}];core.write(self.root/'run.json',run)
        self.assertEqual(self.errors(),[])
    def test_derived_capture_source_is_bound(self):
        def fake_ytdlp(args,url,timeout=300,monitor=None):
            out=args[args.index('-o')+1].replace('%(ext)s','mp4');Path(out).write_bytes(b'derived-section')
        def fake_command(args,timeout=300,monitor=None):Image.new('RGB',(192,108),'white').save(args[-1]);return '',''
        with patch.object(media,'ytdlp',fake_ytdlp),patch.object(media,'probe',lambda p,timeout=60:{'duration':5,'height':1080,'width':1920}),patch.object(media,'command',fake_command):
            r=media.capture(self.root,self.run['videos'][0],[7.0],'read the settings panel',height=1080)
        self.assertIn('h1080s000005000_000007000.jpg',r['captured']);self.assertEqual(self.errors(),[])
        row=next(x for x in core.read(self.dest/'frames/manifest.json')['frames'] if x['name']=='h1080s000005000_000007000.jpg');Path(row['derived_source']['path']).write_bytes(b'tampered')
        self.assertIn('derived capture source missing or changed',self.errors())
    def test_close_capture_times_do_not_alias(self):
        def fake_command(args,timeout=300,monitor=None):Image.new('RGB',(64,36),'white').save(args[-1]);return '',''
        with patch.object(media,'command',fake_command):r=media.capture(self.root,self.run['videos'][0],[1.0,1.001],'two adjacent moments')
        self.assertEqual(sorted(r['captured']),['t_000001000.jpg','t_000001001.jpg'])
    def test_zero_duration_reports_instead_of_crashing(self):
        self.assertEqual(depth.video_checks(self.run,self.run['videos'][0],self.dest,[],[],{},[],0.0,'quick'),['source duration is not positive'])
    def test_capture_rejects_out_of_range_and_missing_purpose(self):
        with self.assertRaises(ValueError):media.capture(self.root,self.run['videos'][0],[25],'beyond the end')
        with self.assertRaises(ValueError):media.capture(self.root,self.run['videos'][0],[5],' ')
    def test_contact_sheets_and_enlargement(self):
        r=media.contact_sheets(self.root,self.run['videos'][0],per_sheet=8);self.assertEqual(r['sheets'],2)
        self.assertTrue((self.dest/'review-contact-sheets/sheet_02.jpg').is_file())
        e=media.enlarge(self.root,self.run['videos'][0],'f_0003.jpg',(0,0,32,18),3)
        with Image.open(e['enlargement']) as im:self.assertEqual(im.size,(96,54))
        with self.assertRaises(ValueError):media.enlarge(self.root,self.run['videos'][0],'f_0003.jpg',(0,0,99,18),3)

class Coverage(unittest.TestCase):
    def test_duration_table(self):
        self.assertEqual(depth.minimums(240),(15,5));self.assertEqual(depth.minimums(12*60),(30,10));self.assertEqual(depth.minimums(100*60),(150,50))
    def test_gaps_against_edges(self):
        found,allowed=depth.gaps([100,400],1200);self.assertEqual(allowed,150);self.assertEqual(found,[(100,400),(400,1200)])
    def test_caption_problems(self):
        cues=[{'start':0,'end':5,'text':'a'},{'start':400,'end':405,'text':'b'}]
        p=depth.caption_problems(cues,1200);self.assertTrue(any('end early' in x for x in p));self.assertTrue(any('silence' in x for x in p))
        self.assertEqual(depth.caption_problems([{'start':0,'end':1195,'text':'x'}],1200),[])
    def test_caption_provenance(self):
        self.assertEqual(media.caption_provenance({'manual_caption_languages':['en-US']}),'manual')
        self.assertEqual(media.caption_provenance({'manual_caption_languages':['fr']}),'automatic')
        self.assertEqual(media.caption_provenance({}),'unknown')

class DepthFull(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.dest=Path(self.tmp.name)
        self.cues=[{'start':i*60.,'end':i*60+55.,'text':' '.join(['word']*20)} for i in range(9)]
        body=lambda n:' '.join(['substance']*n)
        (self.dest/'enhanced-transcript.md').write_text('# Account\n## Opening\n'+body(60)+'\n## Middle\n'+body(60)+'\n### Detail inside middle\n'+body(5)+'\n## Close\n'+body(60)+'\n')
        (self.dest/'intelligence-report.md').write_text('\n'.join('## '+h+'\nNone beyond the source account.\n' for h in depth.REPORT_HEADINGS))
        core.write(self.dest/'enhanced-source-map.json',{'sections':[{'heading':'Opening','cue_start':0,'cue_end':2},{'heading':'Middle','cue_start':3,'cue_end':5},{'heading':'Close','cue_start':6,'cue_end':8}]})
        core.write(self.dest/'full-review.json',{'producer':{'model':'synthetic'},'spot_checks':[{'position':'early','cue_index':1,'finding':'Opening matches the source wording closely.'},{'position':'middle','cue_index':4,'finding':'Middle preserves the worked example in full.'},{'position':'late','cue_index':7,'finding':'Closing qualification is retained as stated.'}]})
        core.write(self.dest/'infographic.json',{'producer':{'model':'synthetic'}})
    def tearDown(self):self.tmp.cleanup()
    def errors(self):return depth.full_checks(self.dest,self.cues,540)
    def test_complete_full_depth_passes(self):self.assertEqual(self.errors(),[])
    def test_section_headings_match_like_markdown(self):
        b=depth.section_texts('## 1. Intro\nalpha\n## setup\nbeta beta\n## Setup\ngamma\n## C# tips\ndelta',['1. intro','Setup','Setup','C# tips'])
        self.assertEqual(b,{0:'alpha',1:'beta beta',2:'gamma',3:'delta'})
    def test_missing_report_section_fails(self):
        (self.dest/'intelligence-report.md').write_text('## Claims and evidence\nx\n');self.assertTrue(any('Tools and technologies' in e for e in self.errors()))
    def test_thin_section_needs_reason(self):
        text=(self.dest/'enhanced-transcript.md').read_text();(self.dest/'enhanced-transcript.md').write_text(text.replace('## Opening\n'+' '.join(['substance']*60),'## Opening\n'+' '.join(['substance']*15)))
        m=core.read(self.dest/'enhanced-source-map.json')
        self.assertTrue(any('is thin' in e for e in self.errors()))
        m['sections'][0]['thin_reason']='Cues 3-5 repeat the same sponsor read verbatim.';core.write(self.dest/'enhanced-source-map.json',m)
        self.assertFalse(any('is thin' in e for e in self.errors()))
    def test_long_section_needs_reason(self):
        self.cues=[dict(c,start=c['start']*5,end=c['end']*5) for c in self.cues]
        self.assertTrue(any('spans' in e for e in depth.full_checks(self.dest,self.cues,2700)))
    def test_misplaced_spot_check_fails(self):
        r=core.read(self.dest/'full-review.json');r['spot_checks'][2]['cue_index']=1;core.write(self.dest/'full-review.json',r)
        self.assertIn('late spot check against the source is absent or misplaced',self.errors())
    def test_category_compilations_for_shared_categories(self):
        root=self.dest/'run';(root/'videos/a').mkdir(parents=True);(root/'videos/b').mkdir(parents=True)
        for v in 'ab':(root/'videos'/v/'analysis.md').write_text('analysis '+v)
        (root/'master-compilation.md').write_text('## Findings\nx\n## Gaps and under-represented topics\ny\n')
        comp=root/'cat.md';comp.write_text('## Agreements\nx\n## Contradictions\ny\n## Gaps\nz\n')
        cat={'name':'Shared','video_ids':['a','b'],'compilation':core.evidence(comp),'analyses':{v:core.sha(root/'videos'/v/'analysis.md') for v in 'ab'}}
        core.write(root/'categories.json',{'categories':[cat]});run={'mode':'full'}
        self.assertEqual(depth.batch_checks(root,run),[])
        (root/'videos/a/analysis.md').write_text('changed');self.assertTrue(any('stale' in e for e in depth.batch_checks(root,run)))
        cat.pop('compilation');core.write(root/'categories.json',{'categories':[cat]});self.assertTrue(any('absent' in e for e in depth.batch_checks(root,run)))

class CarryOver(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();base=Path(self.tmp.name);self.prior=base/'prior';self.new=base/'new'
        depth_fixture(self.prior);self.run,self.dest=depth_fixture(self.new)
        for n in ['analysis.md','analysis.json']:(self.dest/n).unlink()
    def tearDown(self):self.tmp.cleanup()
    def test_identical_evidence_carries_and_verifies(self):
        r=library.carry_over(self.new,self.run,self.run['videos'][0],self.prior);self.assertEqual(r['depth_problems'],[])
        a=core.read(self.dest/'analysis.json');self.assertIn('Not a fresh review',a['carried_over']['note']);self.assertTrue(publish.validate(self.new)['integrity_pass'])
    def test_changed_frame_refuses(self):
        mf=core.read(self.dest/'frames/manifest.json');p=Path(mf['frames'][3]['path']);Image.new('RGB',(64,36),'red').save(p);mf['frames'][3].update(core.evidence(p));core.write(self.dest/'frames/manifest.json',mf)
        with self.assertRaisesRegex(ValueError,'frame f_0003'):library.carry_over(self.new,self.run,self.run['videos'][0],self.prior)
    def test_tampered_new_frame_bytes_refuse_even_with_old_manifest(self):
        Image.new('RGB',(64,36),'red').save(self.dest/'frames/f_0003.jpg')
        with self.assertRaisesRegex(ValueError,'does not match its receipts'):library.carry_over(self.new,self.run,self.run['videos'][0],self.prior)
        self.assertFalse((self.dest/'analysis.json').exists())
    def test_never_overwrites_and_needs_verified_prior(self):
        (self.dest/'analysis.md').write_text('existing')
        with self.assertRaisesRegex(ValueError,'never overwrites'):library.carry_over(self.new,self.run,self.run['videos'][0],self.prior)
        (self.dest/'analysis.md').unlink();a=core.read(self.prior/'videos'/VID/'analysis.json');a['reviewer']='';core.write(self.prior/'videos'/VID/'analysis.json',a)
        with self.assertRaisesRegex(ValueError,'does not verify'):library.carry_over(self.new,self.run,self.run['videos'][0],self.prior)
    def test_plan_update_lists_added_removed_and_candidates(self):
        run=core.read(self.new/'run.json');run['videos'].append({'id':'abcdefghijk','url':'https://www.youtube.com/watch?v=abcdefghijk','state':'pending'})
        plan=library.plan_update(self.new,run,self.prior);self.assertEqual(plan['added'],['abcdefghijk']);self.assertEqual(plan['carry_candidates'][0]['sample_count'],16)

class Account(unittest.TestCase):
    def test_legacy_runs_keep_original_account_and_new_runs_need_settings(self):
        self.assertEqual(core.account_label({}),'Pulse Vibe Daily')
        self.assertIsNone(core.account_label({'depth_contract':'depth/1'}))
        with tempfile.TemporaryDirectory() as d:
            run,_=depth_fixture(d);run=core.read(Path(d)/'run.json');run['notebook_account_label']=None;core.write(Path(d)/'run.json',run)
            with self.assertRaisesRegex(ValueError,'notebook_account_label'):publish.packets(d)

class Sabbath(unittest.TestCase):
    def test_window_runs_from_before_friday_sunset_to_saturday_sunset(self):
        self.assertFalse(sabbath.state(ON,at('2026-10-30T17:30'))['active'])
        s=sabbath.state(ON,at('2026-10-30T17:45'));self.assertTrue(s['active']);self.assertTrue(s['ends_local'].startswith('2026-10-31T17:5'))
        self.assertTrue(sabbath.state(ON,at('2026-10-31T17:50'))['active'])
        self.assertFalse(sabbath.state(ON,at('2026-10-31T18:00'))['active'])
        self.assertFalse(sabbath.state(ON,at('2026-11-04T12:00'))['active'])
    def test_sunset_accuracy_against_published_value(self):
        # Published: earliest Huntsville sunset of 2026 is 4:36 PM on December 5.
        t=dt.datetime.fromtimestamp(sabbath.sunset(dt.date(2026,12,5),34.7304,-86.5861,CHI),CHI);self.assertLess(abs((t.hour*60+t.minute)-(16*60+36)),2)
    def test_disabled_never_active(self):self.assertFalse(sabbath.state({'sabbath':{'enabled':False}},at('2026-10-30T20:00'))['active'])
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def make(self,n=3):
        run=ype.make_run(['https://www.youtube.com/watch?v='+f'{i:011}' for i in range(n)],'Sabbath fixture','quick',archive=str(self.root/'archive'),test_fixture=True);ype.save(self.root,run);return run
    def patches(self,clock,acquire):
        def materialize(root,v,data):v['state']='materials_ready'
        return [patch.object(ype,'settings',lambda:ON),patch.object(sabbath,'clock',clock),patch.object(media,'preflight',lambda a,b:{'pass':True}),patch.object(media,'acquire',acquire),patch.object(media,'materialize',materialize)]
    def test_batch_pauses_and_keeps_run(self):
        run=self.make();now=[at('2026-10-30T18:00')]
        with contextlib.ExitStack() as st:
            for p in self.patches(lambda:now[0],lambda *a:self.fail('no download during the Sabbath')):st.enter_context(p)
            r=ype.batch(self.root,run)
        self.assertEqual(r['status'],'paused_sabbath');saved=core.read(self.root/'run.json');self.assertEqual(saved['status'],'paused_sabbath');self.assertEqual(saved['paused_from'],'awaiting_materials')
        self.assertTrue(all(v['state']=='pending' for v in saved['videos']))
    def test_deadline_interrupted_item_is_not_a_failed_attempt(self):
        run=self.make(1);now=[at('2026-10-30T17:30')];seen={}
        def acquire(video,archive,h,b,timeout):
            seen['timeout']=timeout;now[0]=at('2026-10-30T17:40');raise TimeoutError('Per-item time budget reached')
        with contextlib.ExitStack() as st:
            for p in self.patches(lambda:now[0],acquire):st.enter_context(p)
            r=ype.batch(self.root,run)
        self.assertLessEqual(seen['timeout'],10*60);self.assertEqual(r['status'],'paused_sabbath')
        v=core.read(self.root/'run.json')['videos'][0];self.assertEqual((v['state'],v['attempts']),('pending',0))
    def test_timeout_just_before_window_is_not_a_failed_attempt(self):
        run=self.make(1);now=[at('2026-10-30T17:30')]
        def acquire(video,archive,h,b,timeout):now[0]+=timeout;raise TimeoutError('Per-item time budget reached')
        with contextlib.ExitStack() as st:
            for p in self.patches(lambda:now[0],acquire):st.enter_context(p)
            r=ype.batch(self.root,run)
        v=core.read(self.root/'run.json')['videos'][0];self.assertEqual((r['status'],v['state'],v['attempts']),('paused_sabbath','pending',0))
    def test_real_fault_during_deadline_is_kept(self):
        run=self.make(1);now=[at('2026-10-30T17:30')]
        def acquire(*a):now[0]=at('2026-10-30T17:45');raise ValueError('Retrieved media exceeds the configured size')
        with contextlib.ExitStack() as st:
            for p in self.patches(lambda:now[0],acquire):st.enter_context(p)
            ype.batch(self.root,run)
        self.assertEqual(core.read(self.root/'run.json')['videos'][0]['state'],'needs_owner')
    def test_drive_waits_for_retry_backoff(self):
        run=self.make(1);now=[at('2026-11-02T12:00')];sleeps=[];calls=[]
        def sleep(s):sleeps.append(s);now[0]+=s
        def acquire(*a):
            calls.append(1)
            if len(calls)==1:raise RuntimeError('transient network error')
            return {}
        with contextlib.ExitStack() as st:
            for p in self.patches(lambda:now[0],acquire):st.enter_context(p)
            st.enter_context(patch('time.time',lambda:now[0]))  # backoff timestamps follow the same clock
            r=ype.drive(self.root,run,sleep=sleep)
        self.assertEqual(r['status'],'awaiting_semantic_worker');self.assertEqual(len(calls),2);self.assertTrue(sleeps)
    def test_status_reads_while_writer_lock_is_held(self):
        self.make(1)
        with core.lock(self.root),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(ype.main(['status',str(self.root)]),0)
    def test_unpause_without_record_derives_status(self):
        run=self.make(1);run['videos'][0]['state']='materials_ready';run['status']='paused_sabbath';ype.unpause(self.root,run)
        self.assertEqual(run['status'],'awaiting_semantic_worker')
    def test_drive_waits_through_the_sabbath_and_resumes(self):
        run=self.make(3);now=[at('2026-10-30T18:00')];sleeps=[]
        def sleep(s):sleeps.append(s);now[0]+=s
        with contextlib.ExitStack() as st:
            for p in self.patches(lambda:now[0],lambda *a:{}):st.enter_context(p)
            r=ype.drive(self.root,run,max_items=2,sleep=sleep)
        self.assertEqual(r['status'],'awaiting_semantic_worker');self.assertEqual(len(sleeps),1)
        self.assertGreater(now[0],at('2026-10-31T17:53'));self.assertNotIn('resume_at',core.read(self.root/'run.json'))
    def test_cli_pauses_with_exit_75_then_unpauses(self):
        self.make(1);now=[at('2026-10-31T12:00')]
        with patch.object(ype,'settings',lambda:ON),patch.object(sabbath,'clock',lambda:now[0]),contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(ype.main(['render',str(self.root)]),75)
            self.assertEqual(core.read(self.root/'run.json')['status'],'paused_sabbath');self.assertIn('resume_local',out.getvalue())
            self.assertEqual(ype.main(['status',str(self.root)]),0)
            now[0]=at('2026-10-31T19:00');ype.main(['render',str(self.root)])
        self.assertEqual(core.read(self.root/'run.json')['status'],'awaiting_materials')

if __name__=='__main__':unittest.main()
