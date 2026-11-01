#!/usr/bin/env python3
"""YPE material and evidence CLI. Semantic, image and browser work belongs to the active agent."""
from __future__ import annotations
import argparse, collections, contextlib, json, os, sys, time
from pathlib import Path
from core import VERSION, account_label, collection_key, eligible, evidence, evidence_ok, lock, read, record_failure, safe_id, settings, sha, write, youtube
import community, depth, library, media, publish, sabbath

def save(root,run):
    run['updated_at']=time.time();run['revision']=run.get('revision',0)+1
    write(Path(root)/'run.json',run)

def make_run(urls,title,mode,archive=None,playlist=None,inventory_data=None,test_fixture=False):
    key=collection_key(urls,playlist);videos=[];members=[];seen={}
    entries=inventory_data if inventory_data is not None else [{'id':youtube(u)[0],'title':None} for u in urls]
    for pos,e in enumerate(entries,1):
        vid=e.get('id');label=e.get('title') or vid or 'Unavailable entry'
        try:safe_id(vid or '')
        except ValueError:
            members.append({'position':pos,'id':None,'title':label,'state':'unavailable','reason':'Provider returned no usable video ID'});continue
        members.append({'position':pos,'id':vid,'title':label,'state':'duplicate' if vid in seen else 'listed'})
        if vid in seen:continue
        seen[vid]=True
        videos.append({'id':vid,'url':'https://www.youtube.com/watch?v='+vid,'title':label,'state':'pending','attempts':0})
    run={'schema':'ype-run/1','version':VERSION,'created_at':time.time(),'title':title,'mode':mode,'collection_key':key,'playlist_url':playlist,'inventory_complete':True,'membership':members,'videos':videos,'archive':str(Path(archive).expanduser().absolute()) if archive else None,'retention':'keep','test_fixture':test_fixture,'limits':{'max_items':2,'max_height':720,'max_bytes_per_video':2*1024**3,'batch_seconds':900},'status':'awaiting_materials','editorial_contract':'source-first/1','depth_contract':'depth/1','notebook_account_label':settings().get('notebook_account_label')}
    if mode=='full':run.update(source_fidelity_contract='timed-source-account/1',infographic_quality_contract='source-coverage/1',notebook_source_contract='one-video/1',notebook_caption_mode='references')
    return run

def load(root):
    run=read(Path(root)/'run.json')
    if run.get('schema')!='ype-run/1' or run.get('mode') not in ('quick','full'):raise ValueError('Unknown run schema or mode.')
    for v in run['videos']:
        safe_id(v['id'])
        if v.get('url')!='https://www.youtube.com/watch?v='+v['id']:raise ValueError('Video URL/identity mismatch.')
    if len({v['id'] for v in run['videos']})!=len(run['videos']):raise ValueError('Duplicate work records; use membership for duplicates.')
    return run

def selected(run,vid):
    safe_id(vid)
    return next((v for v in run['videos'] if v['id']==vid),None) or (_ for _ in ()).throw(ValueError('Video not in this run.'))

def archive_ready(path):
    if not path:raise ValueError('Choose a retained archive with init --archive; no silent internal-disk fallback.')
    p=Path(path)
    if str(p).startswith('/Volumes/'):
        mount=Path('/Volumes')/p.parts[2]
        if not mount.is_dir() or not os.path.ismount(mount):raise ValueError('Configured external volume is not mounted. Resume when available.')
    p.mkdir(parents=True,exist_ok=True);return p

def batch(root,run,max_items=2,budget=900,max_height=720,max_bytes=2*1024**3):
    if not 1<=max_items<=10 or not 30<=budget<=3600 or not 240<=max_height<=2160 or not 1024**2<=max_bytes<=20*1024**3:raise ValueError('Batch options exceed supported bounds.')
    cooldown=max([v.get('retry_after') or 0 for v in run['videos'] if v.get('state')=='rate_limited'] or [0])
    if cooldown>time.time():
        run['status']='waiting_rate_limit';save(root,run);return {'processed':0,'status':run['status'],'retry_after':cooldown}
    archive=archive_ready(run.get('archive'));started=time.monotonic();processed=0
    with lock(archive):
        for video in run['videos']:
            if processed>=max_items or time.monotonic()-started>=budget:break
            if not eligible(video):continue
            observance=sabbath.state(settings())
            if observance['active']:return pause(root,run,observance)
            until=sabbath.seconds_until_start(settings())
            check=media.preflight(archive,max_bytes);write(Path(root)/'preflight.json',check)
            if not check['pass']:
                run['status']='blocked_preflight';save(root,run);return {'processed':processed,'status':run['status'],'preflight':check}
            video['state']='acquiring';save(root,run);processed+=1
            try:
                data=media.acquire(video,archive,max_height,max_bytes,max(1,int(min(budget-(time.monotonic()-started),until))))
                media.materialize(root,video,data)
                video['last_error']=None;video['retry_after']=None
            except (Exception,KeyboardInterrupt) as e:
                # Each interrupted item is checkpointed. SystemExit is intentionally not caught.
                record_failure(video,type(e).__name__+': '+str(e))
                if isinstance(e,ValueError):video['state']='needs_owner';video['retry_after']=None
                observance=sabbath.state(settings())
                if isinstance(e,TimeoutError) and sabbath.seconds_until_start(settings())<=60:
                    # Cut off by the observance deadline, not by a fault: the attempt does not count.
                    video.update(state='pending',attempts=video['attempts']-1,retry_after=None,last_error=None);save(root,run);return pause(root,run,observance)
                if observance['active'] and not isinstance(e,KeyboardInterrupt):save(root,run);return pause(root,run,observance)
                save(root,run)
                if isinstance(e,KeyboardInterrupt):raise
                if video['state'] in ('rate_limited','needs_owner'):break
            save(root,run)
    run['status']='awaiting_semantic_worker' if all(v['state']=='materials_ready' for v in run['videos']) else 'materials_partial'
    save(root,run);return {'processed':processed,'status':run['status'],'states':dict(collections.Counter(v['state'] for v in run['videos']))}

def pause(root,run,observance):
    """Checkpoint and pause for the Sabbath. The run is kept, not ended."""
    if run.get('status')!='paused_sabbath':run['paused_from']=run.get('status')
    run.update(status='paused_sabbath',resume_at=observance['ends_at']);save(root,run)
    return {'status':'paused_sabbath','resume_at':observance['ends_at'],'resume_local':observance['ends_local'],'note':'Sabbath observance ('+observance['rule']+', '+observance['location']+'). State is checkpointed; work resumes after sunset.'}

def unpause(root,run):
    if run.get('status')=='paused_sabbath':
        states={v.get('state') for v in run['videos']}
        derived='awaiting_semantic_worker' if states=={'materials_ready'} else 'materials_partial' if 'materials_ready' in states else 'awaiting_materials'
        run['status']=run.pop('paused_from',None) or derived;run.pop('resume_at',None);save(root,run)

def drive(root,run,max_items=2,budget=900,max_hours=72.0,sleep=time.sleep):
    """Acquire batch after batch, waiting through rate-limit backoff and the Sabbath, until nothing is eligible."""
    clock=lambda:sabbath.clock();deadline=clock()+max_hours*3600;log=[]
    while clock()<deadline:
        observance=sabbath.state(settings())
        if observance['active']:
            log.append(pause(root,run,observance));sleep(max(1.0,min(observance['ends_at']+60,deadline)-clock()));continue
        unpause(root,run);result=batch(root,run,max_items,budget);log.append({k:result.get(k) for k in ('status','processed','retry_after')})
        if result['status']=='waiting_rate_limit':sleep(max(1.0,min(result['retry_after']+1,deadline)-clock()));continue
        if result['status']=='paused_sabbath':continue
        waiting=[v['retry_after'] for v in run['videos'] if v.get('state') in ('retryable','rate_limited') and (v.get('retry_after') or 0)>clock()]
        if not result.get('processed') and waiting and result['status']!='blocked_preflight':sleep(max(1.0,min(min(waiting)+1,deadline)-clock()));continue
        if not result.get('processed') or result['status'] in ('blocked_preflight','awaiting_semantic_worker'):return {'status':run['status'],'states':result.get('states'),'log':log[-20:]}
    return {'status':'drive_deadline','note':'Stopped at --max-hours; state is checkpointed. Run again to continue.','log':log[-20:]}

def registry_action(root,run,path):
    state=read(Path(root)/'notebooklm/state.json')
    # This records an observed mapping. It is not a replacement for complete remote validation.
    if state.get('collection_key')!=run['collection_key'] or state.get('notebook_title')!=run['title'] or not account_label(run) or state.get('account_label')!=account_label(run) or not state.get('account_verified') or not evidence_ok(state.get('browser_evidence',{})):
        raise ValueError('Verify intended account, title, collection and browser evidence before registration.')
    url=state.get('notebook_url','')
    if not publish.notebook_url_ok(url):raise ValueError('Notebook URL must be an observed supported URL.')
    path=Path(path).expanduser().resolve();path.parent.mkdir(parents=True,exist_ok=True)
    with lock(path.parent):
        db=read(path) if path.exists() else {'schema':'ype-notebooks/1','notebooks':{}}
        key=account_label(run)+'|'+run['collection_key'];old=db['notebooks'].get(key)
        if old and old['notebook_url']!=url:raise ValueError('Playlist already has a different notebook. Resolve the conflict explicitly; no automatic replacement.')
        db['notebooks'][key]={'notebook_url':url,'title':run['title'],'last_run':str(Path(root).resolve()),'observed_at':state.get('observed_at'),'source_package_sha256':state.get('source_package_sha256')}
        write(path,db);return db['notebooks'][key]

def audience(q):
    q.add_argument('--community',nargs='?',type=int,const=community.DEFAULTS['top'],metavar='N',help='rank, label and score the top N comments of each video (default 100)')
    q.add_argument('--second-labeller',action='store_true',help='a blind second labeller from another model family; reports kappa')
    q.add_argument('--synthesis',action='store_true',help='a cited cross-video claim matrix (two or more videos)')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    q=s.add_parser('init');q.add_argument('run');q.add_argument('--mode',choices=['quick','full'],default='quick');q.add_argument('--title');q.add_argument('--url',action='append',default=[]);q.add_argument('--playlist');q.add_argument('--archive');q.add_argument('--test-fixture',action='store_true');audience(q)
    q=s.add_parser('enable');q.add_argument('run');audience(q)
    for name in ['status','verify','render']:
        s.add_parser(name).add_argument('run')
    q=s.add_parser('community');q.add_argument('run');q.add_argument('video_id');q.add_argument('--from-info',help='a retained yt-dlp info.json with comments, instead of a live fetch')
    for name in ['community-blind','community-score']:
        q=s.add_parser(name);q.add_argument('run');q.add_argument('video_id')
    q=s.add_parser('claim-matrix');q.add_argument('run');q.add_argument('action',choices=['skeleton','check'])
    q=s.add_parser('acquire');q.add_argument('run');q.add_argument('--max-items',type=int,default=2);q.add_argument('--budget-seconds',type=int,default=900);q.add_argument('--max-height',type=int,default=720);q.add_argument('--max-bytes',type=int,default=2*1024**3)
    q=s.add_parser('import-cache');q.add_argument('run');q.add_argument('video_id');q.add_argument('folder')
    q=s.add_parser('sample');q.add_argument('run');q.add_argument('video_id');q.add_argument('--count',type=int,default=100);q.add_argument('--no-dedup',action='store_true')
    q=s.add_parser('capture-moments');q.add_argument('run');q.add_argument('video_id')
    q=s.add_parser('skip');q.add_argument('run');q.add_argument('video_id');q.add_argument('--reason',required=True)
    q=s.add_parser('package');q.add_argument('run');q.add_argument('--words-per-source',type=int,default=40000);q.add_argument('--source-cap',type=int,default=50);q.add_argument('--granularity',choices=['video','batch']);q.add_argument('--caption-mode',choices=['retained','references'])
    q=s.add_parser('register-notebook');q.add_argument('run');q.add_argument('--registry',required=True)
    q=s.add_parser('sabbath',help='show the observance window');q.add_argument('run',nargs='?')
    q=s.add_parser('run',help='acquire until done, waiting through backoff and the Sabbath');q.add_argument('run');q.add_argument('--max-items',type=int,default=2);q.add_argument('--budget-seconds',type=int,default=900);q.add_argument('--max-hours',type=float,default=72.0)
    q=s.add_parser('carry-over');q.add_argument('run');q.add_argument('video_id');q.add_argument('--from',dest='prior',required=True)
    q=s.add_parser('plan-update');q.add_argument('run');q.add_argument('--from',dest='prior',required=True)
    q=s.add_parser('sampling-audit');q.add_argument('run');q.add_argument('video_id')
    q=s.add_parser('contact-sheets');q.add_argument('run');q.add_argument('video_id');q.add_argument('--per-sheet',type=int,default=20)
    q=s.add_parser('enlarge');q.add_argument('run');q.add_argument('video_id');q.add_argument('frame');q.add_argument('--box',required=True,help='x0,y0,x1,y1');q.add_argument('--scale',type=int,default=3)
    q=s.add_parser('capture');q.add_argument('run');q.add_argument('video_id');q.add_argument('--at',type=float,action='append',required=True);q.add_argument('--purpose',required=True);q.add_argument('--height',type=int,help='download a derived higher-resolution section')
    q=s.add_parser('priority');q.add_argument('run');q.add_argument('video_id');q.add_argument('--start',type=float,required=True);q.add_argument('--end',type=float,required=True);q.add_argument('--reason',required=True)
    a=p.parse_args(argv)
    if a.command=='sabbath' and not a.run:
        print(json.dumps(sabbath.state(settings()),indent=2));return 0
    root=Path(a.run).expanduser().resolve()
    # status and sabbath only read, so they work while `run` holds the writer lock through a pause.
    with (contextlib.nullcontext() if a.command in sabbath.EXEMPT else lock(root)):
        if a.command not in sabbath.EXEMPT and a.command!='run':
            observance=sabbath.state(settings())
            if observance['active']:
                result=pause(root,load(root),observance) if (root/'run.json').exists() else {'status':'paused_sabbath','resume_at':observance['ends_at'],'resume_local':observance['ends_local'],'note':'Sabbath observance; nothing was started.'}
                print(json.dumps(result,indent=2));return 75
            if a.command!='init':unpause(root,load(root))
        if a.command=='init':
            if (root/'run.json').exists():raise ValueError('Run exists. Resume it or choose a new run folder.')
            if bool(a.playlist)==bool(a.url):raise ValueError('Provide either explicit --url values or one --playlist.')
            data=None;title=a.title
            if a.playlist:
                collection_key([],a.playlist);info,data=media.inventory(a.playlist);title=title or info.get('title')
            if not title:raise ValueError('Curated inputs require --title; playlist title could not be resolved.')
            run=make_run(a.url,title,a.mode,a.archive,a.playlist,data,a.test_fixture);community.configure(run,a.community,a.second_labeller,a.synthesis);save(root,run)
            result={'run':str(root),'videos':len(run['videos']),'membership_entries':len(run['membership']),'mode':run['mode'],'status':run['status'],**{k:run[k] for k in ('community','claim_matrix') if k in run}}
        else:
            run=load(root)
            if a.command=='status':
                result={'run':str(root),'title':run['title'],'mode':run['mode'],'status':run['status'],'revision':run['revision'],'states':dict(collections.Counter(v['state'] for v in run['videos'])),'inventory_entries':len(run['membership']),'unique_videos':len(run['videos']),'validation':read(root/'validation.json') if (root/'validation.json').exists() else 'not run','note':'Stored validation may be stale; use verify to recompute.'}
                result.update(community=community.status(root,run),claim_matrix=community.matrix_state(root,run))
            elif a.command=='enable':
                if a.community is None and not a.second_labeller and not a.synthesis:raise ValueError('Nothing to enable: pass --community, --second-labeller or --synthesis.')
                community.configure(run,a.community,a.second_labeller,a.synthesis);save(root,run);result={'community':run.get('community'),'claim_matrix':run.get('claim_matrix',False)}
            elif a.command=='community':result=community.harvest(root,run,selected(run,a.video_id),a.from_info)
            elif a.command=='community-blind':result=community.blind(root,run,selected(run,a.video_id))
            elif a.command=='community-score':result=community.score(root,run,selected(run,a.video_id))
            elif a.command=='claim-matrix':
                if a.action=='skeleton':result=community.matrix_skeleton(root,run)
                else:community.require_matrix(run);problems=community.matrix_problems(root,run);result={'claim_matrix':'ok' if not problems else 'incomplete','problems':problems}
            elif a.command=='acquire':result=batch(root,run,a.max_items,a.budget_seconds,a.max_height,a.max_bytes)
            elif a.command=='import-cache':
                v=selected(run,a.video_id)
                if (root/'videos'/v['id']/'media.json').exists():raise ValueError('Media already imported. Use a new run for a different source revision.')
                d=media.import_existing(v,a.folder);media.materialize(root,v,d);run['status']='awaiting_semantic_worker';save(root,run);result={'state':v['state'],'origin':d['origin'],'retention':d['retention']}
            elif a.command=='sample':result=media.sample(root,selected(run,a.video_id),a.count,not a.no_dedup);result={'frames':len(result['frames']),'manifest':str(root/'videos'/a.video_id/'frames/manifest.json')}
            elif a.command=='capture-moments':result=media.capture_moments(root,selected(run,a.video_id));result={'frames':len(result['frames'])}
            elif a.command=='skip':
                if not a.reason.strip():raise ValueError('A skip needs a meaningful reason.')
                v=selected(run,a.video_id);v.update(state='skipped',skip_reason=a.reason);save(root,run);result={'status':'partial','note':'Skipping does not satisfy all-video completion.'}
            elif a.command=='verify':result=publish.validate(root)
            elif a.command=='render':result={'report':str(publish.render(root))}
            elif a.command=='package':result=publish.packets(root,a.words_per_source,a.source_cap,a.granularity,a.caption_mode)
            elif a.command=='register-notebook':result=registry_action(root,run,a.registry)
            elif a.command=='sabbath':result={**sabbath.state(settings()),'run_status':run['status'],'resume_at':run.get('resume_at')}
            elif a.command=='run':result=drive(root,run,a.max_items,a.budget_seconds,a.max_hours)
            elif a.command=='carry-over':result=library.carry_over(root,run,selected(run,a.video_id),a.prior)
            elif a.command=='plan-update':result=library.plan_update(root,run,a.prior)
            elif a.command=='sampling-audit':
                v=selected(run,a.video_id);dest=root/'videos'/v['id'];rows=read(dest/'frames/manifest.json')['frames']
                inspected=read(dest/'analysis.json').get('inspected_frames',[]) if (dest/'analysis.json').exists() else []
                result=depth.sampling_report(rows,read(dest/'cues.json'),inspected,float(read(dest/'media.json')['metadata']['duration']))
            elif a.command=='contact-sheets':result=media.contact_sheets(root,selected(run,a.video_id),a.per_sheet)
            elif a.command=='enlarge':result=media.enlarge(root,selected(run,a.video_id),a.frame,tuple(int(x) for x in a.box.split(',')),a.scale)
            elif a.command=='capture':
                v=selected(run,a.video_id);result=media.capture(root,v,a.at,a.purpose,a.height,lock(archive_ready(run.get('archive'))) if a.height else None)
            elif a.command=='priority':
                v=selected(run,a.video_id)
                if not 0<=a.start<a.end or (v.get('duration') and a.end>v['duration']) or len(a.reason.strip())<10:raise ValueError('Priority section needs 0 <= start < end within the video and a reason.')
                v.setdefault('priority_sections',[]).append({'start':a.start,'end':a.end,'reason':a.reason.strip()});save(root,run);result={'priority_sections':v['priority_sections']}
    print(json.dumps(result,indent=2))
    return 2 if (a.command=='verify' and not result['integrity_pass']) or (a.command=='claim-matrix' and result.get('problems')) else 0

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,RuntimeError,KeyError) as e:
        print(json.dumps({'status':'blocked','error':str(e)}),file=sys.stderr);sys.exit(2)
