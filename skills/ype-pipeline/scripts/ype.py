#!/usr/bin/env python3
"""YPE material and evidence CLI. Semantic, image and browser work belongs to the active agent."""
from __future__ import annotations
import argparse, collections, json, os, sys, time
from pathlib import Path
from core import VERSION, collection_key, eligible, evidence, evidence_ok, lock, read, record_failure, safe_id, sha, write, youtube
import community, media, publish

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
    return {'schema':'ype-run/1','version':VERSION,'created_at':time.time(),'title':title,'mode':mode,'collection_key':key,'playlist_url':playlist,'inventory_complete':True,'membership':members,'videos':videos,'archive':str(Path(archive).expanduser().absolute()) if archive else None,'retention':'keep','test_fixture':test_fixture,'limits':{'max_items':2,'max_height':720,'max_bytes_per_video':2*1024**3,'batch_seconds':900},'status':'awaiting_materials'}

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
            check=media.preflight(archive,max_bytes);write(Path(root)/'preflight.json',check)
            if not check['pass']:
                run['status']='blocked_preflight';save(root,run);return {'processed':processed,'status':run['status'],'preflight':check}
            video['state']='acquiring';save(root,run);processed+=1
            try:
                data=media.acquire(video,archive,max_height,max_bytes,max(1,int(budget-(time.monotonic()-started))))
                media.materialize(root,video,data)
                video['last_error']=None;video['retry_after']=None
            except (Exception,KeyboardInterrupt) as e:
                # Each interrupted item is checkpointed. SystemExit is intentionally not caught.
                record_failure(video,type(e).__name__+': '+str(e))
                if isinstance(e,ValueError):video['state']='needs_owner';video['retry_after']=None
                save(root,run)
                if isinstance(e,KeyboardInterrupt):raise
                if video['state'] in ('rate_limited','needs_owner'):break
            save(root,run)
    run['status']='awaiting_semantic_worker' if all(v['state']=='materials_ready' for v in run['videos']) else 'materials_partial'
    save(root,run);return {'processed':processed,'status':run['status'],'states':dict(collections.Counter(v['state'] for v in run['videos']))}

def registry_action(root,run,path):
    state=read(Path(root)/'notebooklm/state.json')
    # This records an observed mapping. It is not a replacement for complete remote validation.
    if state.get('collection_key')!=run['collection_key'] or state.get('notebook_title')!=run['title'] or state.get('account_label')!='Pulse Vibe Daily' or not state.get('account_verified') or not evidence_ok(state.get('browser_evidence',{})):
        raise ValueError('Verify intended account, title, collection and browser evidence before registration.')
    url=state.get('notebook_url','')
    if not publish.notebook_url_ok(url):raise ValueError('Notebook URL must be an observed supported URL.')
    path=Path(path).expanduser().resolve();path.parent.mkdir(parents=True,exist_ok=True)
    with lock(path.parent):
        db=read(path) if path.exists() else {'schema':'ype-notebooks/1','notebooks':{}}
        key='Pulse Vibe Daily|'+run['collection_key'];old=db['notebooks'].get(key)
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
    a=p.parse_args(argv);root=Path(a.run).expanduser().resolve()
    with lock(root):
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
    print(json.dumps(result,indent=2))
    return 2 if (a.command=='verify' and not result['integrity_pass']) or (a.command=='claim-matrix' and result.get('problems')) else 0

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,RuntimeError,KeyError) as e:
        print(json.dumps({'status':'blocked','error':str(e)}),file=sys.stderr);sys.exit(2)
