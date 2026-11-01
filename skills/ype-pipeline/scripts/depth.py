"""Coverage and depth checks for runs created at v8.3 or later (depth_contract: depth/1).

Each check has a recorded escape: an agent can accept a static video, a quiet
caption gap or a condensed section, but only by writing down why. The checks
find thin or lopsided work; they never reward padding and cannot prove quality.
"""
from __future__ import annotations
import math, re
from pathlib import Path
from core import evidence_ok, read, sha

# (upper bound in minutes, minimum sampled frames), from the v7.2 coverage formula.
COVERAGE=[(5,15),(15,30),(30,50),(60,80),(90,120),(math.inf,150)]
VERDICTS={'pass','visual_static_downgrade_accepted'}
LEGIBILITY={'clear','partial','illegible'}
# Template markers only. Ordinary words such as "placeholder" in an analysis are legitimate prose.
PLACEHOLDER=re.compile(r'(?i:lorem ipsum|\[insert|\{\{|to be (?:written|filled in)|summary goes here)|\bTBD\b|\bTODO:')
REPORT_HEADINGS=['Claims and evidence','Tools and technologies','Code, prompts and configurations','Visual evidence that changed the understanding','Unverified or overstated claims']
CATEGORY_HEADINGS=['Agreements','Contradictions','Gaps']

def minimums(duration):
    sampled=next(n for limit,n in COVERAGE if duration/60<=limit)
    return sampled,math.ceil(sampled/3)

def gaps(times,duration):
    """Uncovered stretches longer than the allowance, between inspected frames and the source edges."""
    allowed=max(120,duration/8);points=[0.0,*sorted(times),float(duration)]
    return [(a,b) for a,b in zip(points,points[1:]) if b-a>allowed],allowed

def has_reason(value,size=40):
    return isinstance(value,str) and len(value.strip())>=size

def sampling_report(rows,cues,inspected,duration):
    """What the coverage checks see; printed by `sampling-audit` and recomputed by verify."""
    sampled_min,inspected_min=minimums(duration);times={r['name']:r['timestamp_seconds'] for r in rows}
    found=gaps([times[n] for n in inspected if n in times],duration)
    edge=max(15,.05*duration);head=max(2,min(10,.05*duration))
    return {'duration':duration,'sampled':len(rows),'sampled_minimum':sampled_min,'inspected':len(inspected),'inspected_minimum':inspected_min,
            'gaps_over_allowance':[{'start':a,'end':b} for a,b in found[0]],'gap_allowance_seconds':found[1],
            'opening_frame':any(t<=head for t in times.values()),'closing_frame':any(t>=duration-edge for t in times.values()),
            'caption_problems':caption_problems(cues,duration)}

def caption_problems(cues,duration):
    if not cues:return ['no captions']
    slack=max(60,.1*duration);out=[]
    if cues[0]['start']>slack:out.append(f'captions start late ({cues[0]["start"]:.0f}s)')
    if cues[-1]['end']<duration-slack:out.append(f'captions end early ({cues[-1]["end"]:.0f}s of {duration:.0f}s)')
    worst=max([b['start']-a['end'] for a,b in zip(cues,cues[1:])] or [0])
    if worst>max(120,.05*duration):out.append(f'caption silence of {worst:.0f}s')
    return out

def video_checks(run,video,dest,rows,cues,a,inspected,duration,mode):
    if not duration>0:return ['source duration is not positive']
    errors=[];report=sampling_report(rows,cues,inspected,duration);audit=a.get('sampling_audit') or {}
    verdict=audit.get('verdict');downgraded=verdict=='visual_static_downgrade_accepted'
    if verdict not in VERDICTS:errors.append('sampling audit verdict absent (pass or visual_static_downgrade_accepted)')
    if downgraded and not has_reason(audit.get('reason')):errors.append('static downgrade needs a written reason')
    below=report['sampled']<report['sampled_minimum'] or report['inspected']<report['inspected_minimum']
    if below and not downgraded:errors.append(f'visual coverage below the duration minimum ({report["sampled"]}/{report["sampled_minimum"]} sampled, {report["inspected"]}/{report["inspected_minimum"]} inspected)')
    accepted=[g for g in audit.get('accepted_gaps',[]) if has_reason(g.get('reason'),20)]
    for g in report['gaps_over_allowance']:
        if not downgraded and not any(x.get('start',math.inf)<=g['start'] and x.get('end',-1)>=g['end'] for x in accepted):errors.append(f'uninspected stretch {g["start"]:.0f}-{g["end"]:.0f}s exceeds {report["gap_allowance_seconds"]:.0f}s')
    if not report['opening_frame'] or not report['closing_frame']:errors.append('opening or closing scout frame missing; use capture --at')
    if report['caption_problems'] and not has_reason(a.get('caption_gaps_acknowledged')):errors.append('caption coverage problem not acknowledged: '+'; '.join(report['caption_problems']))
    observations=a.get('observations',[])
    if any(o.get('legibility') not in LEGIBILITY for o in observations):errors.append('observation legibility absent (clear, partial or illegible)')
    if not isinstance(a.get('producer'),dict) or not str(a['producer'].get('model','')).strip():errors.append('analysis producer model not recorded')
    times=[cues[i]['start'] for c in a.get('claims',[]) for i in c.get('cue_indices',[]) if type(i) is int and 0<=i<len(cues)]+[o.get('timestamp_seconds',-1) for o in observations]
    quarters={min(3,int(4*t/duration)) for t in times if isinstance(t,(int,float)) and 0<=t<=duration}
    if quarters!={0,1,2,3} and not has_reason(a.get('coverage_exception')):errors.append('claims and observations do not reach every quarter of the source')
    for p in video.get('priority_sections',[]):
        inside=[n for n in inspected if p['start']<=next((r['timestamp_seconds'] for r in rows if r['name']==n),-1)<=p['end']]
        cited=any(cues[i]['start']<=p['end'] and cues[i]['end']>=p['start'] for c in a.get('claims',[]) for i in c.get('cue_indices',[]) if type(i) is int and 0<=i<len(cues))
        if len(inside)<2 or not cited:errors.append(f'priority section {p["start"]:.0f}-{p["end"]:.0f}s needs two inspected frames and a cited claim')
    for name in ['analysis.md']+(['enhanced-transcript.md','intelligence-report.md'] if mode=='full' else []):
        p=dest/name
        if p.is_file() and PLACEHOLDER.search(p.read_text()):errors.append('placeholder text left in '+name)
    if mode=='full':errors+=full_checks(dest,cues,duration)
    return errors

def section_texts(text,headings):
    """Body text under each mapped heading, up to the next mapped heading.

    Headings match case-insensitively after the Markdown marker, in order, so a
    repeated heading text maps to its next occurrence rather than the first."""
    lines=text.splitlines();titles=[(k,m.group(1).strip().lower()) for k,l in enumerate(lines) for m in [re.match(r'\s*#{1,6}\s+(.*)$',l)] if m]
    starts=[];used=set()
    for h in headings:
        key=str(h).strip().lower()
        i=next((k for k,t in titles if t==key and k not in used and k>max(used,default=-1)),None) if key else None
        if i is not None:used.add(i)
        starts.append(i)
    order=sorted(k for k in starts if k is not None)
    out={}
    for n,(h,i) in enumerate(zip(headings,starts)):
        if i is None:continue
        nxt=next((k for k in order if k>i),len(lines));out[n]=' '.join(lines[i+1:nxt])
    return out

def full_checks(dest,cues,duration):
    errors=[]
    report=(dest/'intelligence-report.md').read_text() if (dest/'intelligence-report.md').is_file() else ''
    for h in REPORT_HEADINGS:
        if not re.search(r'^#{1,6}\s+'+re.escape(h)+r'\s*$',report,re.M|re.I):errors.append('intelligence report section missing: '+h)
    try:account=read(dest/'enhanced-source-map.json');review=read(dest/'full-review.json')
    except (OSError,ValueError):return errors
    sections=[s for s in account.get('sections',[]) if type(s.get('cue_start')) is int and type(s.get('cue_end')) is int and 0<=s['cue_start']<=s['cue_end']<len(cues)]
    bodies=section_texts((dest/'enhanced-transcript.md').read_text(),[s.get('heading','') for s in sections])
    for n,s in enumerate(sections):
        source_words=sum(len(c['text'].split()) for c in cues[s['cue_start']:s['cue_end']+1]);words=len(bodies.get(n,'').split())
        if source_words and words<.35*source_words and not has_reason(s.get('thin_reason'),30):errors.append(f'section "{s.get("heading")}" is thin ({words} words for {source_words} source words) without a thin_reason')
        span=cues[s['cue_end']]['end']-cues[s['cue_start']]['start']
        if span>max(600,duration/4) and not has_reason(s.get('long_section_reason'),30):errors.append(f'section "{s.get("heading")}" spans {span:.0f}s without a long_section_reason')
    checks={c.get('position'):c for c in review.get('spot_checks',[])};n=len(cues)
    for third,pos in enumerate(['early','middle','late']):
        c=checks.get(pos,{});i=c.get('cue_index')
        if type(i) is not int or not 0<=i<n or min(2,3*i//n)!=third or not has_reason(c.get('finding'),30):errors.append(pos+' spot check against the source is absent or misplaced')
    for name,blob in (('full review',review),('infographic',read(dest/'infographic.json') if (dest/'infographic.json').is_file() else {})):
        if not isinstance(blob.get('producer'),dict) or not str(blob['producer'].get('model','')).strip():errors.append(name+' producer model not recorded')
    return errors

def batch_checks(root,run):
    if run['mode']!='full':return []
    errors=[];root=Path(root);master=root/'master-compilation.md'
    if master.is_file():
        text=master.read_text()
        if not re.search(r'^#{1,6}\s+Gaps\b',text,re.M|re.I):errors.append('master compilation lacks a Gaps section')
        if PLACEHOLDER.search(text):errors.append('placeholder text left in master-compilation.md')
    try:categories=read(root/'categories.json')['categories']
    except (OSError,ValueError,KeyError):return errors
    for c in categories:
        if len(c.get('video_ids',[]))<2:continue
        comp=c.get('compilation') or {}
        if not evidence_ok(comp):errors.append('category compilation absent or changed: '+str(c.get('name')));continue
        text=Path(comp['path']).read_text()
        for h in CATEGORY_HEADINGS:
            if not re.search(r'^#{1,6}\s+'+h+r'\b',text,re.M|re.I):errors.append(f'category compilation {c.get("name")} lacks {h}')
        try:expected={v:sha(root/'videos'/v/'analysis.md') for v in c['video_ids']}
        except OSError:expected=None
        if c.get('analyses')!=expected:errors.append('category compilation is stale against analyses: '+str(c.get('name')))
    return errors
