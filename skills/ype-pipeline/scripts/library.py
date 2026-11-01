"""Reuse reviewed work across runs, and plan incremental playlist updates.

A carried-over review is reused only when every byte it covered is identical:
retained source, captions, cues, transcript and each inspected frame. The new
receipt records where it came from; nothing is re-attested as a fresh review.
"""
from __future__ import annotations
import time
from pathlib import Path
from core import evidence_ok, lock, read, sha, write
import publish

def prior_video(prior_root,vid):
    prior=read(Path(prior_root)/'run.json');video=next((v for v in prior['videos'] if v['id']==vid),None)
    if not video:raise ValueError('Video is not in the prior run.')
    return prior,video

def identity(root,vid):
    """Hashes recomputed from the files on disk, not taken from their receipts."""
    dest=Path(root)/'videos'/vid;media=read(dest/'media.json');rows=read(dest/'frames/manifest.json')['frames']
    if not evidence_ok(media['source']) or not evidence_ok(media['caption']) or not all(evidence_ok(r) for r in rows):raise ValueError('Retained evidence in '+str(root)+' does not match its receipts.')
    frames={r['name']:(r['timestamp_seconds'],r['sha256']) for r in rows}
    return {'source':media['source']['sha256'],'caption':media['caption']['sha256'],'cues':sha(dest/'cues.json'),'transcript':sha(dest/'transcript.txt')},frames

def carry_over(root,run,video,prior_root):
    root=Path(root);prior_root=Path(prior_root).resolve();vid=video['id'];dest=root/'videos'/vid
    if prior_root==root.resolve():raise ValueError('Carry-over needs a different prior run.')
    if (dest/'analysis.json').exists() or (dest/'analysis.md').exists():raise ValueError('This run already has an analysis for the video; carry-over never overwrites.')
    with lock(prior_root):
        prior,pv=prior_video(prior_root,vid)
        problems=publish.video_checks(prior_root,pv,prior['mode'])
        if problems:raise ValueError('Prior review does not verify, so it cannot be carried over: '+'; '.join(problems[:3]))
        old,old_frames=identity(prior_root,vid);new,new_frames=identity(root,vid)
        changed=[k for k in old if old[k]!=new[k]]
        a=read(prior_root/'videos'/vid/'analysis.json');prose=(prior_root/'videos'/vid/'analysis.md').read_bytes()
    missing=[n for n in a.get('inspected_frames',[]) if new_frames.get(n)!=old_frames.get(n)]
    if changed or missing:raise ValueError('Evidence differs from the prior review ('+', '.join(changed+[f'frame {n}' for n in missing[:5]])+'); review this video afresh.')
    if sha_bytes(prose)!=a.get('analysis_sha256'):raise ValueError('Prior analysis changed while being read; retry.')
    record={'from_run':str(prior_root),'from_run_version':prior.get('version'),'from_mode':prior['mode'],'carried_at':time.time(),'identical':sorted(old)+['inspected frames'],'original_reviewer':a.get('reviewer'),'note':'Review reused because every byte it covered is identical. Not a fresh review.'}
    if a.get('carried_over'):record['previous']=a['carried_over']
    a['carried_over']=record
    write(dest/'analysis.json',a)
    try:(dest/'analysis.md').write_bytes(prose)
    except OSError:(dest/'analysis.json').unlink(missing_ok=True);raise
    result={'carried':vid,'from':str(prior_root)}
    if run['mode']=='full':result['not_carried']='Full deliverables (expanded account, report, infographic, notebook) are redone in this run.'
    if run.get('depth_contract')=='depth/1':
        result['depth_problems']=publish.video_checks(root,video,run['mode'])
    return result

def sha_bytes(data):
    import hashlib;return hashlib.sha256(data).hexdigest()

def plan_update(root,run,prior_root):
    """Compare membership with a prior run of the same collection and list what can be reused."""
    prior=read(Path(prior_root)/'run.json')
    if prior.get('collection_key')!=run['collection_key']:raise ValueError('Prior run is a different collection.')
    old={v['id'] for v in prior['videos']};new={v['id'] for v in run['videos']}
    reusable=[]
    for vid in sorted(old&new):
        pv=next(v for v in prior['videos'] if v['id']==vid)
        try:
            ok=not publish.video_checks(prior_root,pv,prior['mode']);m=read(Path(prior_root)/'videos'/vid/'frames/manifest.json')
            if ok:reusable.append({'id':vid,'sample_count':m.get('requested_count'),'dedup':m.get('dedup',True)})
        except (OSError,ValueError,KeyError):pass
    plan={'prior_run':str(Path(prior_root).resolve()),'added':sorted(new-old),'removed':sorted(old-new),'retained':sorted(old&new),'carry_candidates':reusable,
          'next':'Acquire (retained media is reused by hash), sample carry candidates with the same count and dedup, then carry-over --from the prior run. Review added videos afresh. Synthesis is always redone.'}
    write(Path(root)/'update-plan.json',plan);return plan
