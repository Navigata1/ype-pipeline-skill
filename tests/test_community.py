"""Contracts for --community, --second-labeller and --synthesis. Synthetic fixtures only: no network, no media."""
import contextlib, io, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ype-pipeline/scripts'))
import community, core, media, publish, ype

A,B='Synthetic_A','Synthetic_B'
TOPICS={'T1':'the claim','GEN':'general'}
# Ranked order is c2 (2 likes + 3 x 3 replies = 11), c1 (10), c4 (5 + 3 x 1 = 8, the channel's own), c3 (0).
LABELS={'1':['E','T1',1,'','agrees once the setup is persistent'],'2':['C','T1',1,'',''],'3':['P','GEN',0,'creator',''],'4':['H','GEN',0,'','']}
LABELS_B={**LABELS,'1':['N','T1',1,'','']}
PROSE=''.join(f'## {h}\nEvidence-grounded synthetic fixture for contract testing only.\n' for h in ['Thesis','What was said','What the frames add','Uncertainties','Application'])
SECTION='## Community check\nSynthetic reading of the scored comments.\n'
IDENTITY=('Some Person','UC123','example.invalid')

def url(vid):return 'https://www.youtube.com/watch?v='+vid

def info(vid,comments=True,comment_count=None):
    def c(cid,likes,parent='root',uploader=False):
        return {'id':cid,'text':f'raw words {cid}','like_count':likes,'parent':parent,'author':'Some Person','author_id':'UC123','author_thumbnail':'https://example.invalid/a.jpg','author_url':'https://example.invalid/@someone','author_is_uploader':uploader,'_time_text':'1 day ago','timestamp':1760000000}
    rows=[c('c1',10),c('c2',2),c('r1',0,'c2'),c('r2',1,'c2'),c('r3',0,'c2'),c('c3',0),c('c4',5,uploader=True),c('r4',0,'c4')] if comments else []
    return {'id':vid,'title':'Fixture '+vid,'channel':'Fixture channel','duration':20,'comment_count':len(rows) if comment_count is None else comment_count,'epoch':1760000000,'comments':rows}

def materials(root,video):
    vid=video['id'];dest=root/'videos'/vid;dest.mkdir(parents=True)
    source=dest/'fixture.webm';source.write_bytes(b'synthetic-video-'+vid.encode())
    sub=dest/'fixture.vtt';sub.write_text('WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nA useful idea about persistent records.\n\n00:00:05.000 --> 00:00:10.000\nRecords can keep context across sessions.\n')
    data={'id':vid,'url':video['url'],'metadata':{'id':vid,'title':'Fixture '+vid,'duration':20},'source':core.evidence(source),'caption':core.evidence(sub),'retention':'keep','origin':'test-fixture'}
    media.materialize(root,video,data);frames=dest/'frames';frames.mkdir();rows=[]
    for i in range(3):
        p=frames/f'f_{i:04}.jpg';Image.new('RGB',(8,8),(i*80,50,90)).save(p)
        rows.append({'name':p.name,'timestamp_seconds':float(i*5),'method':'synthetic','source_sha256':data['source']['sha256'],**core.evidence(p)})
    core.write(frames/'manifest.json',{'source_sha256':data['source']['sha256'],'frames':rows})
    (dest/'analysis.md').write_text(PROSE)
    core.write(dest/'analysis.json',{'source_sha256':data['source']['sha256'],'transcript_sha256':core.sha(dest/'transcript.txt'),'analysis_sha256':core.sha(dest/'analysis.md'),'reviewer':'synthetic-fixture','transcript_reviewed':True,'inspected_frames':[r['name'] for r in rows],'inspected_frame_sha256':{r['name']:r['sha256'] for r in rows},'observations':[{'frame':rows[0]['name'],'timestamp_seconds':0.,'description':'This is a synthetic observation that does not assert actual viewing.'}],'claims':[{'text':'Synthetic claim references first caption cue.','cue_indices':[0],'frames':[]}]})

def build(root,vids=(A,),**options):
    run=ype.make_run([url(v) for v in vids],'Fixture playlist','quick',test_fixture=True);community.configure(run,**options)
    for video in run['videos']:materials(root,video)
    ype.save(root,run);bind_synthesis(root,run);return run

def bind_synthesis(root,run):
    if len(run['videos'])<2:return
    p=root/'master-compilation.md';p.write_text('Synthetic master fixture. '*50)
    core.write(root/'synthesis.json',{'reviewer':'fixture','collection_digest':core.identity_hash(run),'file':core.evidence(p),'analyses':{v['id']:core.sha(root/'videos'/v['id']/'analysis.md') for v in run['videos']}})

def bind_analysis(root,vid):
    dest=root/'videos'/vid;a=core.read(dest/'analysis.json');a['analysis_sha256']=core.sha(dest/'analysis.md')
    if (dest/'community/metrics.json').is_file():a['community_metrics_sha256']=core.sha(dest/'community/metrics.json')
    core.write(dest/'analysis.json',a)

def video(run,vid):return next(v for v in run['videos'] if v['id']==vid)
def out(root,vid):return root/'videos'/vid/'community'

def harvest(base,root,run,vid,**kw):
    p=base/(vid+'.info.json');p.write_text(json.dumps(info(vid,**kw)))
    return community.harvest(root,run,video(run,vid),str(p))

def label(root,vid,labels=LABELS,name='claude-fixture',file='labels.json',topics=TOPICS):
    core.write(out(root,vid)/file,{'labeller':name,vid:{'topics':topics,'labels':labels}})

def finish(root,run,vid,section=SECTION):
    (root/'videos'/vid/'analysis.md').write_text(PROSE+section);bind_analysis(root,vid);bind_synthesis(root,run)

def errors(root,vid):return next(r['errors'] for r in publish.validate(root)['per_video'] if r['id']==vid)

def quiet(argv):
    with contextlib.redirect_stdout(io.StringIO()):return ype.main(argv)

class Case(unittest.TestCase):
    vids=(A,);options={'top':100}
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.root=self.base/'run'
        self.run=build(self.root,self.vids,**self.options)
    def tearDown(self):self.tmp.cleanup()
    def complete(self,vid=A,second=False):
        harvest(self.base,self.root,self.run,vid);label(self.root,vid)
        if second:community.blind(self.root,self.run,video(self.run,vid));label(self.root,vid,LABELS_B,'codex-fixture','labels.b.json')
        result=community.score(self.root,self.run,video(self.run,vid));finish(self.root,self.run,vid);return result

class Harvest(Case):
    def test_import_ranks_by_likes_plus_three_replies(self):
        r=harvest(self.base,self.root,self.run,A);top=core.read(out(self.root,A)/'top.json')
        self.assertEqual([c['id'] for c in top['comments']],['c2','c1','c4','c3'])
        self.assertEqual([c['score'] for c in top['comments']],[11,10,8,0])
        self.assertEqual((r['origin'],r['fetched_total'],r['ranked']),('imported-info',8,4))
        self.assertTrue(top['comments'][2]['by_creator']);self.assertIsNone(top['meta']['reply_cap'])
    def test_commenter_identity_is_never_retained(self):
        harvest(self.base,self.root,self.run,A)
        for p in out(self.root,A).rglob('*'):
            if p.is_file():self.assertFalse(any(x in p.read_text() for x in IDENTITY),p.name)
    def test_labels_skeleton_has_one_empty_entry_per_rank(self):
        harvest(self.base,self.root,self.run,A);labels=core.read(out(self.root,A)/'labels.json')
        self.assertEqual(labels['labeller'],'');self.assertEqual(labels[A]['labels'],{'1':None,'2':None,'3':None,'4':None})
    def test_second_harvest_is_refused(self):
        harvest(self.base,self.root,self.run,A)
        with self.assertRaisesRegex(ValueError,'already harvested'):harvest(self.base,self.root,self.run,A)
    def test_reported_but_missing_comments_record_nothing(self):
        with self.assertRaisesRegex(ValueError,'reported comments but returned none'):harvest(self.base,self.root,self.run,A,comments=False,comment_count=12)
        self.assertFalse((out(self.root,A)/'harvest.json').exists())
    def test_identity_mismatch_is_refused(self):
        p=self.base/'other.info.json';p.write_text(json.dumps(info(B)))
        with self.assertRaisesRegex(ValueError,'does not identify'):community.harvest(self.root,self.run,video(self.run,A),str(p))
    def test_interrupted_harvest_is_preserved(self):
        stale=out(self.root,A)/'stale.txt';stale.parent.mkdir(parents=True);stale.write_text('partial')
        harvest(self.base,self.root,self.run,A)
        kept=list((self.root/'videos'/A).glob('community-interrupted-*/stale.txt'))
        self.assertEqual(len(kept),1);self.assertEqual(kept[0].read_text(),'partial')
    def test_live_fetch_passes_comment_flags_and_keeps_only_the_scrubbed_copy(self):
        calls=[]
        def fake(extra,link,timeout=300,monitor=None):
            calls.append((extra,link));(Path(extra[extra.index('-o')+1]).parent/'video.info.json').write_text(json.dumps(info(A)));return '',''
        with patch.object(media,'ytdlp',side_effect=fake),patch.object(media,'command',return_value=('2026.10.01\n','')):
            community.harvest(self.root,self.run,video(self.run,A))
        extra,link=calls[0];receipt=core.read(out(self.root,A)/'harvest.json')
        self.assertEqual(link,url(A))
        for flag in ['--skip-download','--write-comments','--no-playlist','youtube:comment_sort=top;max_comments=1500,all,all,40']:self.assertIn(flag,extra)
        self.assertEqual((receipt['origin'],receipt['extractor_version'],receipt['caps']['per_thread']),('fresh-fetch','2026.10.01',40))
        self.assertEqual(core.read(out(self.root,A)/'top.json')['meta']['reply_cap'],40)
        self.assertFalse(any(x in (out(self.root,A)/'comments.json').read_text() for x in IDENTITY))
    def test_reply_cap_marks_saturated_threads(self):
        _,comments=community.scrub(info(A))
        top=community.rank({'video_id':A,'metadata':{},'comments':comments,'caps':{'per_thread':3}},{**community.DEFAULTS,'top':100})
        self.assertEqual([c['replies_saturated'] for c in top['comments']],[True,False,False,False])
    def test_no_comments_needs_only_the_section(self):
        harvest(self.base,self.root,self.run,A,comments=False,comment_count=0)
        self.assertFalse((out(self.root,A)/'labels.json').exists())
        self.assertEqual(errors(self.root,A),['analysis section missing: Community check'])
        with self.assertRaisesRegex(ValueError,'nothing to score'):community.score(self.root,self.run,video(self.run,A))
        finish(self.root,self.run,A);self.assertTrue(publish.validate(self.root)['integrity_pass'])
        self.assertIn('No comments were available',publish.render(self.root).read_text())

class Scoring(Case):
    def test_unharvested_video_fails_validation(self):
        self.assertIn('community comments not harvested',errors(self.root,A))
    def test_unfilled_labels_are_refused_with_each_problem(self):
        harvest(self.base,self.root,self.run,A)
        with self.assertRaises(ValueError) as e:community.score(self.root,self.run,video(self.run,A))
        for text in ['name the labeller','declare at least one topic code','labels #1','labels #4']:self.assertIn(text,str(e.exception))
    def test_invalid_codes_are_each_listed(self):
        harvest(self.base,self.root,self.run,A);label(self.root,A,{**LABELS,'4':['Z','NOPE',2,'boss',1]})
        with self.assertRaises(ValueError) as e:community.score(self.root,self.run,video(self.run,A))
        self.assertEqual(str(e.exception).count('labels #4'),5)
    def test_metrics_equal_hand_computed_values(self):
        harvest(self.base,self.root,self.run,A);label(self.root,A);r=community.score(self.root,self.run,video(self.run,A))
        m=core.read(out(self.root,A)/'metrics.json')
        self.assertEqual((r['agreement_by_engagement'],r['agreement_by_voice']),(0.048,0.0))  # (11 - 10) / 21; one support, one challenge
        self.assertEqual((m['excluded_speaker_or_creator'],m['noise_share'],m['sensitivity']),(1,0.045,{'max_shift':1.048,'by_rank':1}))
        text=(out(self.root,A)/'community.md').read_text()
        self.assertIn('Agreement **+0.05**',text);self.assertIn('above 0.1',text);self.assertIn('agrees once the setup is persistent',text)
    def test_complete_check_passes_and_report_shows_no_raw_comment(self):
        self.complete();self.assertTrue(publish.validate(self.root)['integrity_pass'])
        page=publish.render(self.root).read_text()
        self.assertIn('Community check: how it landed',page);self.assertIn('<table>',page);self.assertNotIn('raw words',page)
    def test_packets_carry_the_scored_read_not_the_comments(self):
        self.complete();publish.packets(self.root);text=(self.root/'notebooklm/source-001.txt').read_text()
        self.assertIn('Community check (scored comments)',text);self.assertNotIn('raw words',text)
        self.assertIn('videos/'+A+'/community/metrics.json',core.read(self.root/'notebooklm/package.json')['input_hashes'])
    def test_reordered_top_is_caught_by_the_re_rank(self):
        self.complete();d=out(self.root,A);top=core.read(d/'top.json');top['comments'].reverse();core.write(d/'top.json',top)
        receipt=core.read(d/'harvest.json');receipt['top']=core.evidence(d/'top.json');core.write(d/'harvest.json',receipt)
        self.assertIn('top.json does not match a re-rank of the retained comments',errors(self.root,A))
    def test_changed_comments_are_caught(self):
        self.complete();p=out(self.root,A)/'comments.json';p.write_text(p.read_text().replace('raw words c1','other words'))
        self.assertIn('community harvest bytes changed or moved',errors(self.root,A))
    def test_labels_changed_after_scoring_are_stale(self):
        self.complete();label(self.root,A,{**LABELS,'4':['O','GEN',0,'','']})
        self.assertIn('community metrics are stale against top.json or the labels',errors(self.root,A))
    def test_hand_edited_metrics_are_caught(self):
        self.complete();p=out(self.root,A)/'metrics.json';m=core.read(p);m['agreement_by_engagement']=0.9;core.write(p,m)
        self.assertIn('community metrics do not match a recomputation from the bound labels',errors(self.root,A))
    def test_hand_edited_section_text_is_caught(self):
        self.complete();p=out(self.root,A)/'community.md';p.write_text(p.read_text().replace('Agreement **+0.05**','Agreement **+0.90**'))
        self.assertIn('community.md does not match the scored metrics',errors(self.root,A))
    def test_rescore_after_review_needs_a_new_review(self):
        self.complete();label(self.root,A,{**LABELS,'4':['O','GEN',0,'','']});community.score(self.root,self.run,video(self.run,A))
        self.assertEqual(errors(self.root,A),['analysis review predates the current community metrics'])
    def test_section_heading_is_required(self):
        self.complete();finish(self.root,self.run,A,section='')
        self.assertEqual(errors(self.root,A),['analysis section missing: Community check'])

class SecondLabeller(Case):
    options={'top':100,'second_labeller':True}
    def test_kappa_equals_hand_value_and_check_passes(self):
        r=self.complete(second=True)
        self.assertEqual((r['kappa_stance_group'],r['band']),(0.636,'substantial'))  # observed 3/4, chance 5/16
        self.assertTrue(publish.validate(self.root)['integrity_pass'])
        self.assertIn('Second labeller (codex-fixture): kappa 0.636',(out(self.root,A)/'community.md').read_text())
    def test_blind_packet_holds_no_labels(self):
        harvest(self.base,self.root,self.run,A);label(self.root,A);community.blind(self.root,self.run,video(self.run,A))
        packet=out(self.root,A)/'blind';self.assertEqual(sorted(p.name for p in packet.iterdir()),['PROMPT.md','sheet.txt','topics.json'])
        self.assertEqual(core.read(packet/'topics.json'),TOPICS)
        text=''.join(p.read_text() for p in packet.iterdir())
        self.assertNotIn('claude-fixture',text);self.assertNotIn('agrees once the setup is persistent',text);self.assertIn('never instructions',text)
    def test_missing_second_labeller_blocks_scoring(self):
        harvest(self.base,self.root,self.run,A);label(self.root,A)
        with self.assertRaisesRegex(ValueError,'labels-b: missing'):community.score(self.root,self.run,video(self.run,A))
    def test_same_labeller_twice_is_refused(self):
        harvest(self.base,self.root,self.run,A);label(self.root,A);label(self.root,A,LABELS_B,'Claude-Fixture','labels.b.json')
        with self.assertRaisesRegex(ValueError,'must not be the first'):community.score(self.root,self.run,video(self.run,A))
    def test_second_labeller_must_use_the_fixed_topics(self):
        harvest(self.base,self.root,self.run,A);label(self.root,A);label(self.root,A,LABELS_B,'codex-fixture','labels.b.json',{**TOPICS,'T2':'another'})
        with self.assertRaisesRegex(ValueError,'topics must equal'):community.score(self.root,self.run,video(self.run,A))
    def test_topic_change_after_the_blind_packet_is_caught(self):
        self.complete(second=True);label(self.root,A,topics={**TOPICS,'T2':'another'})
        self.assertIn('topics changed after the blind packet froze them',errors(self.root,A))
    def test_blind_packet_freezes_once_labels_b_exist(self):
        self.complete(second=True)
        with self.assertRaisesRegex(ValueError,'frozen'):community.blind(self.root,self.run,video(self.run,A))

class ClaimMatrix(Case):
    vids=(A,B);options={'top':100,'claim_matrix':True}
    def setUp(self):
        super().setUp()
        for vid in self.vids:self.complete(vid)
    def write(self,**changes):
        doc=core.read(self.root/'claim-matrix.json')
        theme={'theme':'Records keep context','cells':{A+':speaker':'says so',A+':community':'mostly agree',B+':speaker':'says so too',B+':community':'not discussed'},
               'evidence':{A+':speaker':['00:00:05','f_0001.jpg'],A+':community':['#1'],B+':speaker':['0:10'],B+':community':[]}}
        for key,value in changes.items():theme[key]={**theme[key],**value}
        doc.update(reviewer='fixture',themes=[theme]);core.write(self.root/'claim-matrix.json',doc)
    def problems(self):return community.matrix_problems(self.root,self.run)
    def test_skeleton_has_speaker_and_commenter_columns(self):
        r=community.matrix_skeleton(self.root,self.run);doc=core.read(self.root/'claim-matrix.json')
        self.assertEqual(doc['columns'],[A+':speaker',A+':community',B+':speaker',B+':community']);self.assertEqual(r['columns'],4)
        self.assertEqual(set(doc['topic_hints']),{A,B})
        with self.assertRaisesRegex(ValueError,'exists'):community.matrix_skeleton(self.root,self.run)
    def test_cited_matrix_passes_renders_and_packs(self):
        community.matrix_skeleton(self.root,self.run);self.write();self.assertEqual(self.problems(),[])
        self.assertTrue(publish.validate(self.root)['integrity_pass']);self.assertEqual(quiet(['claim-matrix',str(self.root),'check']),0)
        page=publish.render(self.root).read_text();self.assertIn('Claim matrix',page);self.assertIn('Records keep context',page)
        publish.packets(self.root);self.assertIn('## Claim matrix',(self.root/'notebooklm/source-001.txt').read_text())
    def test_missing_matrix_fails_validation(self):
        self.assertIn('claim matrix missing; run claim-matrix RUN skeleton',publish.validate(self.root)['batch_errors'])
    def test_bad_citations_are_each_refused(self):
        community.matrix_skeleton(self.root,self.run)
        cases={'cited nothing':({'evidence':{B+':speaker':[]}},'no evidence'),
               'uninspected frame':({'evidence':{A+':speaker':['f_0009.jpg']}},'neither a timestamp'),
               'past the end':({'evidence':{B+':speaker':['0:30']}},'lies outside the video'),
               'unranked comment':({'evidence':{A+':community':['#9']}},'not a comment rank'),
               'speaker cites a rank':({'evidence':{A+':speaker':['#1']}},'neither a timestamp'),
               'not discussed but cited':({'cells':{B+':community':'Not discussed'},'evidence':{B+':community':['#1']}},'marked not discussed but cites evidence')}
        for name,(change,message) in cases.items():
            with self.subTest(name):self.write(**change);self.assertTrue(any(message in p for p in self.problems()),self.problems())
    def test_one_video_theme_is_not_cross_video(self):
        community.matrix_skeleton(self.root,self.run);self.write(cells={B+':speaker':'not discussed'},evidence={B+':speaker':[]})
        self.assertTrue(any('fewer than two videos' in p for p in self.problems()))
    def test_matrix_goes_stale_when_an_analysis_changes(self):
        community.matrix_skeleton(self.root,self.run);self.write();finish(self.root,self.run,A,SECTION+'A revised reading.\n')
        self.assertIn('claim matrix is stale against the analyses or community metrics',self.problems())
        self.assertEqual(quiet(['claim-matrix',str(self.root),'check']),2)
    def test_reviewer_is_required(self):
        community.matrix_skeleton(self.root,self.run);self.write();doc=core.read(self.root/'claim-matrix.json');doc['reviewer']='';core.write(self.root/'claim-matrix.json',doc)
        self.assertIn('claim matrix: name the reviewer',self.problems())

class Options(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'run'
    def tearDown(self):self.tmp.cleanup()
    def init(self,*flags,urls=(A,B)):return quiet(['init',str(self.root),'--title','Fixture',*[x for v in urls for x in ('--url',url(v))],*flags])
    def run_json(self):return core.read(self.root/'run.json')
    def test_init_records_all_three_options(self):
        self.init('--community','50','--second-labeller','--synthesis');run=self.run_json()
        self.assertEqual((run['community']['top'],run['community']['second_labeller'],run['claim_matrix']),(50,True,True))
    def test_bare_community_flag_means_one_hundred(self):
        self.init('--community');self.assertEqual(self.run_json()['community']['top'],100)
    def test_runs_without_flags_have_no_audience_channel(self):
        self.init();self.assertNotIn('community',self.run_json());self.assertNotIn('claim_matrix',self.run_json())
    def test_second_labeller_needs_community(self):
        with self.assertRaisesRegex(ValueError,'needs --community'):self.init('--second-labeller')
        self.assertFalse((self.root/'run.json').exists())
    def test_synthesis_needs_two_videos(self):
        with self.assertRaisesRegex(ValueError,'two or more videos'):self.init('--synthesis',urls=(A,))
    def test_out_of_range_sample_is_refused(self):
        with self.assertRaisesRegex(ValueError,'1 to 500'):self.init('--community','0')
    def test_enable_widens_but_never_resizes(self):
        self.init('--community')
        with self.assertRaisesRegex(ValueError,'fixed at 100'):quiet(['enable',str(self.root),'--community','50'])
        with self.assertRaisesRegex(ValueError,'Nothing to enable'):quiet(['enable',str(self.root)])
        quiet(['enable',str(self.root),'--second-labeller','--synthesis']);run=self.run_json()
        self.assertEqual((run['community']['top'],run['community']['second_labeller'],run['claim_matrix']),(100,True,True))
    def test_status_counts_community_stages(self):
        self.init('--community');run=self.run_json();base=self.root.parent
        p=base/'a.info.json';p.write_text(json.dumps(info(A)));community.harvest(self.root,run,video(run,A),str(p))
        self.assertEqual(community.status(self.root,run),{'awaiting labels':1,'not harvested':1})
        label(self.root,A);community.score(self.root,run,video(run,A));self.assertEqual(community.status(self.root,run),{'scored':1,'not harvested':1})
        quiet(['enable',str(self.root),'--second-labeller']);run=self.run_json()
        self.assertEqual(community.status(self.root,run),{'awaiting second labeller':1,'not harvested':1})

class Markdown(unittest.TestCase):
    def test_dependency_free_renderer_draws_pipe_tables(self):
        with patch.dict(sys.modules,{'markdown':None}):page=publish.markdown('Intro line\n\n| A | B |\n|---|--:|\n| 1 | x<y |\n\nAfter')
        self.assertIn('<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>x&lt;y</td></tr></table>',page)
        self.assertIn('<p>Intro line</p>',page);self.assertIn('<p>After</p>',page)

if __name__=='__main__':unittest.main()
