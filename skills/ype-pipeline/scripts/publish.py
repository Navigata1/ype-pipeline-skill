"""Integrity checks and two views of the same evidence: human HTML and flat source packets."""
from __future__ import annotations
import base64, html, json, re, math
from html.parser import HTMLParser
from urllib.parse import urlparse
from pathlib import Path
from core import captions, evidence, evidence_ok, identity_hash, local, read, sha, timestamp, write, write_text
import community

def notebook_url_ok(url):
    return isinstance(url,str) and bool(re.fullmatch(r'https://(?:notebooklm\.google\.com|notebook\.google\.com)/notebook/[A-Za-z0-9_-]+',url))

def image_ok(path):
    try:
        from PIL import Image
        with Image.open(path) as im:im.verify()
        with Image.open(path) as im:im.load();return im.width>0 and im.height>0
    except (ImportError,OSError,ValueError,SyntaxError):return False

def video_checks(root,video,mode):
    errors=[]; vid=video.get('id');dest=Path(root)/'videos'/str(vid);run=read(Path(root)/'run.json')
    if video.get('state')=='skipped':
        return ['Skipped item is an explicit coverage gap: '+video.get('skip_reason','reason missing')]
    try:
        media=read(dest/'media.json'); mf=read(dest/'frames/manifest.json'); cues=read(dest/'cues.json')
        if not evidence_ok(media['source']) or not evidence_ok(media['caption']):errors.append('source/caption hash mismatch')
        if media.get('id')!=vid:errors.append('media identity does not match video')
        if mf['source_sha256']!=media['source']['sha256']:errors.append('frames belong to another source')
        rows=mf['frames'];frames={r['name']:r for r in rows}
        if not rows or len(rows)!=len(frames) or not all(evidence_ok(r) for r in rows):errors.append('missing, duplicate or changed frames')
        if any(Path(r['name']).name!=r['name'] or Path(r['path']).resolve()!=(dest/'frames'/r['name']).resolve() or not image_ok(r['path']) for r in rows):errors.append('frame is outside expected directory or cannot decode')
        if any(not math.isfinite(float(r['timestamp_seconds'])) or not 0<=r['timestamp_seconds']<media['metadata']['duration'] for r in rows):errors.append('frame time outside source')
        original_cues=captions(Path(media['caption']['path']).read_text(errors='replace'))
        if original_cues!=cues:errors.append('cue evidence changed against retained captions')
        if not cues or sha(dest/'transcript.txt')!=video.get('transcript_sha256'):errors.append('empty or changed transcript')
        a=read(dest/'analysis.json')
        if a.get('source_sha256')!=media['source']['sha256'] or a.get('transcript_sha256')!=sha(dest/'transcript.txt'):errors.append('analysis is stale against sources')
        if not a.get('reviewer') or not a.get('transcript_reviewed'):errors.append('missing semantic-review attestation')
        inspected=a.get('inspected_frames',[])
        if len(set(inspected))<min(3,len(rows)) or any(n not in frames for n in inspected):errors.append('inspected frame references are incomplete or invalid')
        if a.get('inspected_frame_sha256')!={n:frames[n]['sha256'] for n in inspected if n in frames}:errors.append('review is stale against inspected frame bytes')
        observations=a.get('observations',[])
        if not observations:errors.append('no visual observations')
        for o in observations:
            f=frames.get(o.get('frame'))
            if not f or o['frame'] not in inspected or len(o.get('description','').strip())<30:errors.append('unsubstantiated frame observation');continue
            t=o.get('timestamp_seconds',-999)
            if type(t) not in (int,float) or not math.isfinite(t) or abs(t-f['timestamp_seconds'])>.05:errors.append('observation timestamp does not match its frame')
        claims=a.get('claims',[])
        if not claims:errors.append('no sourced claims')
        for c in claims:
            if not c.get('text') or (not c.get('cue_indices') and not c.get('frames')):errors.append('claim lacks evidence reference')
            if any(type(i) is not int or i<0 or i>=len(cues) for i in c.get('cue_indices',[])):errors.append('claim cue index invalid')
            if any(f not in inspected for f in c.get('frames',[])):errors.append('claim cites an uninspected frame')
        text=(dest/'analysis.md').read_text()
        if a.get('analysis_sha256')!=sha(dest/'analysis.md'):errors.append('analysis prose changed after review')
        headings=['Thesis','What was said','What the frames add','Uncertainties']
        if run.get('editorial_contract')!='source-first/1':headings.append('Application')
        for heading in headings:
            if not re.search(r'^#{1,6}\s+'+re.escape(heading)+r'\s*$',text,re.M|re.I):errors.append('analysis section missing: '+heading)
        if mode=='full':
            mp=dest/'moments.json';plan=read(mp);moments=plan['moments']
            if not moments or not plan.get('transcript_reviewed') or plan.get('source_sha256')!=media['source']['sha256'] or plan.get('transcript_sha256')!=sha(dest/'transcript.txt'):errors.append('moment map empty or stale against evidence')
            if mf.get('moment_map_sha256')!=sha(mp):errors.append('moment map changed or was never captured')
            for i,m in enumerate(moments):
                covered=[r for r in rows if r.get('moment_index')==i and m['start']<=r['timestamp_seconds']<=m['end'] and evidence_ok(r)]
                if not 0<=m['start']<=m['end']<=media['metadata']['duration'] or not m.get('reason'):errors.append('invalid moment interval or reason')
                if len({r['timestamp_seconds'] for r in covered})<(3 if m.get('importance')=='high' else 1):errors.append('moment lacks real in-range captures')
                if not any(r['name'] in inspected for r in covered):errors.append('moment has no actually inspected capture')
            review=read(dest/'full-review.json')
            if review.get('analysis_sha256')!=sha(dest/'analysis.md') or not review.get('reviewer') or not review.get('source_faithfulness_checked'):errors.append('full review is missing or stale')
            for filename in ['enhanced-transcript.md','intelligence-report.md']:
                p=dest/filename
                floor=500 if filename=='enhanced-transcript.md' else 350
                if not p.is_file() or len(p.read_text().split())<floor:errors.append('full deliverable below substance floor: '+filename)
                if not evidence_ok(review.get('files',{}).get(filename,{})) or review.get('files',{}).get(filename,{}).get('sha256')!=sha(p):errors.append('full deliverable review mismatch: '+filename)
            asset=read(dest/'infographic.json')
            if asset.get('provider')!='native-image-gen' or not evidence_ok(asset['file']) or not asset.get('visually_reviewed'):errors.append('native infographic absent, changed or unreviewed')
            if not image_ok(asset['file']['path']):errors.append('native infographic does not decode as an image')
            if asset.get('analysis_sha256')!=sha(dest/'analysis.md'):errors.append('infographic based on stale analysis')
            if not asset.get('generated_at') or not asset.get('tool_call_ref') or not evidence_ok(asset.get('request',{})):errors.append('image generation request/receipt absent')
            if run.get('source_fidelity_contract')=='timed-source-account/1':
                account=read(dest/'enhanced-source-map.json')
                if account.get('source_sha256')!=media['source']['sha256'] or account.get('transcript_sha256')!=sha(dest/'transcript.txt') or account.get('enhanced_sha256')!=sha(dest/'enhanced-transcript.md'):errors.append('expanded source map is stale')
                if not account.get('reviewer') or not account.get('examples_and_qualifications_checked'):errors.append('expanded source semantic review absent')
                covered=set();mapped_frames=set();previous_end=-1
                for section in account.get('sections',[]):
                    if type(section.get('cue_start')) is not int or type(section.get('cue_end')) is not int or not 0<=section['cue_start']<=section['cue_end']<len(cues):errors.append('expanded source cue range invalid');continue
                    if run.get('editorial_contract')=='source-first/1' and section['cue_start']<=previous_end:errors.append('expanded source sections overlap or are out of order')
                    previous_end=section['cue_end']
                    covered.update(range(section['cue_start'],section['cue_end']+1))
                    if not section.get('heading') or section['heading'] not in (dest/'enhanced-transcript.md').read_text():errors.append('expanded source heading missing')
                    if any(name not in inspected for name in section.get('frame_names',[])):errors.append('expanded source cites uninspected frame')
                    mapped_frames.update(section.get('frame_names',[]))
                if covered!=set(range(len(cues))):errors.append('expanded source map omits caption intervals')
                if run.get('editorial_contract')=='source-first/1' and not {o['frame'] for o in observations}<=mapped_frames:errors.append('reviewed visual observations are not mapped into source sections')
                if review.get('source_map_sha256')!=sha(dest/'enhanced-source-map.json'):errors.append('full review does not bind expanded source map')
                if run.get('editorial_contract')=='source-first/1':
                    for key in ['substance_preserved','visuals_integrated','source_first','project_applications_separate','stale_uncertainties_resolved']:
                        if review.get(key) is not True:errors.append('full semantic acceptance absent: '+key)
            if run.get('infographic_quality_contract')=='source-coverage/1':
                errors+=infographic_checks(dest,asset,cues,inspected)
    except (OSError,ValueError,KeyError,TypeError,StopIteration) as e:
        errors.append('missing or invalid artifact: '+str(e))
    errors+=community_checks(root,video)
    return list(dict.fromkeys(errors))

def infographic_checks(dest,asset,cues,inspected):
    """Bind the content plan and human quality judgment; neither is proof of beauty."""
    errors=[];brief_path=dest/'infographic-brief.json';brief=read(brief_path)
    if not evidence_ok(asset.get('brief',{})) or asset.get('brief',{}).get('sha256')!=sha(brief_path):errors.append('infographic brief absent or changed')
    if brief.get('enhanced_sha256')!=sha(dest/'enhanced-transcript.md') or asset.get('enhanced_sha256')!=sha(dest/'enhanced-transcript.md'):errors.append('infographic stale against expanded source account')
    if brief.get('source_map_sha256')!=sha(dest/'enhanced-source-map.json'):errors.append('infographic source coverage map is stale')
    composition=brief.get('composition',{})
    if not composition.get('form') or not composition.get('rationale'):errors.append('infographic composition lacks a source-specific rationale')
    concepts=brief.get('concepts',[]);ids=[c.get('id') for c in concepts]
    if not ids or any(not isinstance(i,str) or not i.strip() for i in ids) or len(set(ids))!=len(ids):errors.append('infographic main-concept inventory absent or duplicated')
    for concept in concepts:
        if not concept.get('title') or not concept.get('represented_as') or not (concept.get('cue_indices') or concept.get('frames')):errors.append('infographic concept lacks content, representation or evidence')
        if any(type(i) is not int or not 0<=i<len(cues) for i in concept.get('cue_indices',[])):errors.append('infographic concept cue reference invalid')
        if any(f not in inspected for f in concept.get('frames',[])):errors.append('infographic concept cites uninspected frame')
    review=asset.get('quality_review',{});reviewed=review.get('concept_ids',[])
    if len(reviewed)!=len(ids) or set(reviewed)!=set(ids):errors.append('infographic quality review does not cover every main concept')
    if not review.get('reviewer') or not review.get('review_notes'):errors.append('infographic quality review lacks reviewer or substantive notes')
    for key in ['coverage_checked','relationships_checked','labels_checked','legibility_checked','source_specificity_checked']:
        if review.get(key) is not True:errors.append('infographic quality acceptance absent: '+key)
    return errors

def community_checks(root,video):
    try:return community.video_checks(root,video,read(Path(root)/'run.json'))
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as e:return ['community check invalid: '+str(e)]

def validate(root):
    root=Path(root);run=read(root/'run.json')
    rows=[{'id':v.get('id'),'errors':video_checks(root,v,run['mode'])} for v in run['videos']]
    errors=[]
    if not rows:errors.append('empty batch')
    if run.get('inventory_complete') is not True:errors.append('inventory incomplete')
    if any(not m.get('id') for m in run.get('membership',[])):errors.append('inventory contains unresolved unavailable items')
    members=run.get('membership',[]);ids=[v.get('id') for v in run['videos']]
    if not members or {m.get('id') for m in members if m.get('id')}!=set(ids) or len(ids)!=len(set(ids)) or [m.get('position') for m in members]!=list(range(1,len(members)+1)):errors.append('membership and unique video work records disagree')
    master=root/'master-compilation.md';review_path=root/'synthesis.json'
    if len(run['videos'])>1 or run['mode']=='full':
        try:
            review=read(review_path)
            if not master.is_file() or not master.read_text().strip() or review.get('file',{}).get('sha256')!=sha(master) or not evidence_ok(review.get('file',{})):errors.append('cross-video synthesis missing or changed')
            if review.get('collection_digest')!=identity_hash(run) or not review.get('reviewer'):errors.append('synthesis membership/reviewer invalid')
            expected={v['id']:sha(root/'videos'/v['id']/'analysis.md') for v in run['videos']}
            if review.get('analyses')!=expected:errors.append('synthesis is stale against analyses')
        except (OSError,ValueError,KeyError,TypeError) as e:errors.append('synthesis incomplete: '+str(e))
    if run['mode']=='full':
        for p in ['master-compilation.md','categories.json']:
            if not (root/p).is_file():errors.append('full compilation missing: '+p)
        try:
            categories=read(root/'categories.json')['categories'];categorized=[vid for c in categories for vid in c['video_ids']]
            if sorted(categorized)!=sorted(ids) or any(not c.get('name') for c in categories):errors.append('primary categories do not cover each video exactly once')
        except (OSError,ValueError,KeyError,TypeError) as e:errors.append('categories invalid: '+str(e))
        try:
            package=read(root/'notebooklm/package.json');state=read(root/'notebooklm/state.json')
            if package['collection_digest']!=identity_hash(run):errors.append('source package membership is stale')
            if state.get('source_package_sha256')!=sha(root/'notebooklm/package.json'):errors.append('NotebookLM receipt does not match current package')
            if state.get('account_label')!='Pulse Vibe Daily' or state.get('account_verified') is not True:errors.append('intended browser account not verified')
            if state.get('notebook_title')!=run['title'] or state.get('collection_key')!=run['collection_key']:errors.append('notebook identity/title mismatch')
            if not notebook_url_ok(state.get('notebook_url','')):errors.append('notebook URL absent or invalid')
            packets=package['packets'];receipts=state.get('sources',[])
            if run.get('notebook_source_contract')=='one-video/1':
                packet_ids=[p.get('video_id') for p in packets]
                if package.get('source_contract')!='one-video/1' or sorted(packet_ids,key=str)!=sorted(ids):errors.append('NotebookLM requires exactly one source per video')
                remote_ids=[s.get('remote_source_id') for s in receipts]
                if len(receipts)!=len(packets) or len(set(remote_ids))!=len(remote_ids):errors.append('NotebookLM per-video source receipts are duplicated or incomplete')
            expected={x['sha256'] for x in packets}
            if expected!={x.get('sha256') for x in receipts} or any(not x.get('remote_source_id') or not x.get('visible_title_verified') for x in receipts):errors.append('source receipts do not match all packaged bytes')
            if not all(evidence_ok(p) for p in packets):errors.append('source packet changed after packaging')
            expected_inputs=package_inputs(root,run)
            if package.get('input_hashes')!=expected_inputs:errors.append('packaged sources are stale against current deliverables')
            if not state.get('observed_at') or not state.get('observed_by') or not evidence_ok(state.get('browser_evidence',{})):errors.append('dated browser observation absent')
            for name in ['audio','slides']:
                asset=state.get(name,{})
                if asset.get('status')!='ready' or not asset.get('title') or not asset.get('artifact_id') or not asset.get('opened_and_checked'):errors.append(name+' not visibly ready and checked')
                if asset.get('source_package_sha256')!=sha(root/'notebooklm/package.json'):errors.append(name+' source revision is stale')
            if not state.get('retrieval_checks') or any(not c.get('question') or not c.get('source_citation') or not c.get('matches_local_evidence') for c in state.get('retrieval_checks',[])):errors.append('NotebookLM substantive retrieval check absent')
            if package.get('caption_mode')=='references' and run.get('notebook_source_contract')!='one-video/1':
                originals=state.get('original_sources',[])
                if {x.get('video_id') for x in originals}!=set(ids) or any(not x.get('source_account_verified') or not x.get('remote_source_id') for x in originals):errors.append('per-video original/source-account receipts absent')
        except (OSError,ValueError,KeyError,TypeError) as e:errors.append('NotebookLM incomplete: '+str(e))
    errors+=community.matrix_problems(root,run)
    ok=not errors and all(not r['errors'] for r in rows)
    report={'mode':run['mode'],'integrity_pass':ok,'status':run['mode']+'_complete_with_review_attestations' if ok else 'incomplete','test_fixture':run.get('test_fixture',False),'per_video':rows,'batch_errors':errors,'limits':'Checks bind local bytes, references and recorded observations. Semantic correctness and remote actions are agent attestations, not independently proven by this script.'}
    if run.get('editorial_contract')=='source-first/1' and run['mode']=='full':report['acceptance']={'artifact_integrity':ok,'semantic_and_visual':'attested' if all(not r['errors'] for r in rows) else 'pending','independently_proven':False}
    write(root/'validation.json',report);return report

class SafeHTML(HTMLParser):
    allowed={'p','br','hr','pre','code','em','strong','del','blockquote','ul','ol','li','h1','h2','h3','h4','h5','h6','a','table','thead','tbody','tr','td','th'}
    def __init__(self):super().__init__(convert_charrefs=False);self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag not in self.allowed:return
        keep=[]
        if tag=='a':
            href=dict(attrs).get('href','');scheme=urlparse(html.unescape(href).strip()).scheme.lower()
            if scheme in ('https','http','file') or href.startswith('#'):keep=[('href',href)]
        self.parts.append('<'+tag+''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in keep)+'>')
    def handle_endtag(self,tag):
        if tag in self.allowed:self.parts.append('</'+tag+'>')
    def handle_data(self,data):self.parts.append(html.escape(data))
    def handle_entityref(self,name):self.parts.append('&'+name+';')
    def handle_charref(self,name):self.parts.append('&#'+name+';')

def markdown(text):
    try:
        import markdown as md
        # All source prose is treated as text, never arbitrary HTML from a video.
        out=SafeHTML();out.feed(md.markdown(html.escape(text),extensions=['tables','fenced_code']));return ''.join(out.parts)
    except ImportError:
        # Portable small Markdown subset, without embedded images or arbitrary HTML.
        def inline(line):
            value=html.escape(line)
            value=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',value)
            value=re.sub(r'`([^`]+)`',r'<code>\1</code>',value)
            value=re.sub(r'(?<!!)\[([^]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2">\1</a>',value)
            return value
        out=[];paragraph=[];table=[];in_code=False
        def flush():
            if paragraph:out.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
            if table:out.append(table_html(table,inline));table.clear()
        for line in text.splitlines():
            row=not in_code and line.lstrip().startswith('|')
            if row!=bool(table):flush()
            if row:table.append(line)
            elif line.startswith('```'):
                flush();out.append('</code></pre>' if in_code else '<pre><code>');in_code=not in_code
            elif in_code:out.append(html.escape(line)+'\n')
            elif re.match(r'^#{1,6} ',line):
                flush();level=len(line)-len(line.lstrip('#'));out.append(f'<h{level}>'+inline(line[level:].strip())+f'</h{level}>')
            elif line.startswith(('- ','* ')):flush();out.append('<p>• '+inline(line[2:])+'</p>')
            elif not line.strip():flush()
            else:paragraph.append(line)
        flush()
        if in_code:out.append('</code></pre>')
        safe=SafeHTML();safe.feed(''.join(out));return ''.join(safe.parts)

def table_html(lines,inline):
    """A markdown pipe table for the dependency-free renderer; a |---| separator makes the row above it the header."""
    rows=[]
    for line in lines:
        cells=line.strip().strip('|').split('|')
        if rows and all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells):rows[-1]=('th',rows[-1][1])
        else:rows.append(('td',cells))
    return '<table>'+''.join('<tr>'+''.join(f'<{tag}>{inline(c.strip())}</{tag}>' for c in cells)+'</tr>' for tag,cells in rows)+'</table>'

STYLE='''*{box-sizing:border-box}body{margin:0;background:#08121f;color:#e6eef8;font:17px/1.65 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:48px 24px}h1{font-size:clamp(2rem,5vw,3.7rem);line-height:1.1}h2,h3{line-height:1.3}p,li{color:#b9c9db}a{color:#79c6ff;overflow-wrap:anywhere}.eyebrow{color:#5ee1c0;text-transform:uppercase;letter-spacing:.13em;font-size:.75rem}details{border:1px solid #2a4056;background:#0e2032;border-radius:16px;margin:18px 0;padding:20px;overflow-wrap:anywhere}summary{cursor:pointer;font-weight:700;font-size:1.12rem}summary:focus-visible,a:focus-visible{outline:3px solid #5ee1c0;outline-offset:5px}.meta{font-size:.83rem;color:#8bb0cc}.body{padding-top:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere}code{font-size:.88em}table{display:block;overflow-x:auto;max-width:100%;border-collapse:collapse}th,td{border:1px solid #31445a;padding:12px;min-width:120px;text-align:left}.notice{border-left:3px solid #5ee1c0;padding-left:18px}.chip{padding:5px 9px;background:#16334a;border-radius:8px;margin-right:6px;font-size:.8rem}.card{border:1px solid #2a4056;padding:18px;border-radius:12px;margin:20px 0}@media(max-width:450px){main{padding:26px 16px}details{padding:15px}}@media print{body{background:#fff;color:#111}p,li,.meta{color:#222}details{background:#fff}details:not([open])>.body{display:block}a{color:#174c73}}'''

def render(root):
    root=Path(root);run=read(root/'run.json');validation=validate(root);sections=[]
    for v,r in zip(run['videos'],validation['per_video']):
        dest=root/'videos'/str(v.get('id'));p=dest/'analysis.md'
        body=markdown(p.read_text()) if p.exists() else '<p>Analysis has not been completed. This entry preserves the input and its current disposition.</p>'
        links=[f'<a href="{html.escape(v.get("url",""),quote=True)}">Source video</a>']
        if (dest/'media.json').exists():
            media=read(dest/'media.json');links.append(f'<a href="{Path(media["source"]["path"]).as_uri()}">Retained video</a>')
            links.append(f'<a href="{(dest/"transcript.txt").as_uri()}">Timestamped transcript</a>')
        if run['mode']=='full':
            for filename,label in [('enhanced-transcript.md','Expanded timed source account'),('intelligence-report.md','Intelligence report')]:
                artifact=dest/filename
                if artifact.exists():body+='<details><summary>'+label+'</summary><div class="body">'+markdown(artifact.read_text())+'</div></details>'
            image_receipt=dest/'infographic.json'
            if image_receipt.exists():
                asset=read(image_receipt);img=asset.get('file',{})
                if evidence_ok(img) and image_ok(img['path']):
                    from PIL import Image
                    from io import BytesIO
                    # Inline a display copy while preserving the generated original unchanged.
                    im=Image.open(img['path']).convert('RGB');im.thumbnail((1600,1600));buffer=BytesIO();im.save(buffer,format='JPEG',quality=88)
                    body+='<figure><img style="max-width:100%;height:auto" alt="Source-specific infographic for '+html.escape(v.get('title') or v['id'],quote=True)+'" src="data:image/jpeg;base64,'+base64.b64encode(buffer.getvalue()).decode()+'"><figcaption>Native GPT infographic; interpreted from this video and visually reviewed.</figcaption></figure>'
        body+=community_html(dest,run)
        status='Integrity checks passed; semantic review attested' if not r['errors'] else 'Incomplete — '+str(v.get('state','pending'))
        sections.append(f'<details><summary>{html.escape(v.get("title") or v.get("id") or "Unavailable entry")}</summary><div class="body"><p class="meta">{html.escape(status)} · {" · ".join(links)}</p>{body}</div></details>')
    master=root/'master-compilation.md';synthesis=markdown(master.read_text()) if master.exists() else '<p>A cross-video synthesis has not been added yet.</p>'
    synthesis+=matrix_html(root,run)
    applications=root/'project-applications.md'
    if applications.is_file():synthesis+='<details><summary>Separate project applications — analyst interpretation</summary><div class="body">'+markdown(applications.read_text())+'</div></details>'
    fixture_notice='<p class="notice"><strong>Synthetic test fixture. This page does not prove real video analysis or remote generation.</strong></p>' if run.get('test_fixture') else ''
    page=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(run["title"])} — YPE</title><style>{STYLE}</style></head><body><main><p class="eyebrow">YouTube Pipeline Experience · {run["mode"]} analysis</p><h1>{html.escape(run["title"])}</h1>{fixture_notice}<p class="notice">{html.escape(validation["status"])} · {len(run["membership"])} inventory entries / {len(run["videos"])} unique videos. Raw media is retained. Transcripts and sampled frames are evidence; claims and limitations are distinguished in each analysis.</p><section aria-labelledby="synthesis"><h2 id="synthesis">Across the videos</h2>{synthesis}</section><section aria-labelledby="videos"><h2 id="videos">Video research and source evidence</h2>{"".join(sections)}</section><p class="meta">{html.escape(validation["limits"])} No remote resources load with this report. Evidence links point to this machine.</p></main></body></html>'
    write_text(root/'report.html',page);return root/'report.html'

def community_html(dest,run):
    """The scored community read for one video; raw comment text never enters the report."""
    if not (run.get('community') or {}).get('enabled'):return ''
    out=dest/'community';opening='<details><summary>Community check: how it landed</summary><div class="body">'
    if (out/'community.md').is_file():return opening+markdown((out/'community.md').read_text())+'</div></details>'
    try:empty=read(out/'harvest.json').get('comments_available') is False
    except (OSError,ValueError,AttributeError):empty=False
    note='No comments were available when they were harvested.' if empty else 'The community check has not been scored yet.'
    return opening+'<p>'+note+'</p></div></details>'

def matrix_html(root,run):
    if not run.get('claim_matrix'):return ''
    try:return '<h3>Claim matrix</h3>'+markdown(community.matrix_markdown(read(root/'claim-matrix.json'),run))
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return '<h3>Claim matrix</h3><p>The claim matrix has not been written yet.</p>'

def package_inputs(root,run):
    out={};scored=(run.get('community') or {}).get('enabled')
    for v in run['videos']:
        filenames=['analysis.md','analysis.json','transcript.txt','cues.json','frames/manifest.json']
        if run['mode']=='full':filenames+=['enhanced-transcript.md','intelligence-report.md','moments.json','infographic.json','full-review.json']
        if (Path(root)/'videos'/v['id']/'enhanced-source-map.json').exists():filenames+=['enhanced-source-map.json']
        if run.get('infographic_quality_contract')=='source-coverage/1':filenames+=['infographic-brief.json']
        if scored:filenames+=[n for n in ['community/top.json','community/metrics.json','community/community.md'] if (Path(root)/'videos'/v['id']/n).exists()]
        for name in filenames:
            p=Path(root)/'videos'/v['id']/name;out[str(p.relative_to(root))]=sha(p)
    for name in ['master-compilation.md','synthesis.json','categories.json','claim-matrix.json']:
        if run.get('notebook_source_contract')!='one-video/1' and (Path(root)/name).exists():out[name]=sha(Path(root)/name)
    return out

def video_sources(root,run,words_per_source,source_cap,caption_mode):
    """One neutral enriched account per unique video, or a blocker before any write."""
    if len(run['videos'])>source_cap-1:raise ValueError('One source per video exceeds the notebook source budget (one slot reserved). Plan named volumes; do not combine or omit videos.')
    planned=[]
    for video in run['videos']:
        errors=video_checks(root,video,run['mode'])
        if errors:raise ValueError('Only reviewed and linked analyses can be packaged: '+video['id']+' '+errors[0])
        dest=root/'videos'/video['id'];analysis=read(dest/'analysis.json');mf=read(dest/'frames/manifest.json')
        chunks=[f'# {video["title"]} — expanded source account\nSource: {video["url"]}\nVideo ID: {video["id"]}',(dest/'enhanced-transcript.md').read_text(),
            '## Reviewed visual evidence\n'+'\n'.join(f'- [{timestamp(o["timestamp_seconds"])}] {o["frame"]}: {o["description"]}' for o in analysis['observations']),
            f'Captured frames: {len(mf["frames"])}. Inspected frames: {len(set(analysis["inspected_frames"]))}. Sampled viewing; actual image pixels are not embedded in this text source.']
        if caption_mode=='retained':chunks.append('## Original timestamped captions\n'+(dest/'transcript.txt').read_text())
        else:chunks.append('## Original source reference\n'+video['url']+'\nOriginal captions and media remain in the local archive. This source contains the reviewed expanded account; the original URL is a reference, not a separate required notebook import.')
        text='\n\n'.join(chunks)+'\n'
        if len(text.split())>words_per_source:raise ValueError('Video '+video['id']+' exceeds the configured per-source word budget. Verify actual provider limits or plan an explicit exception; do not split, truncate or summarize it to fit.')
        if len(text.encode('utf-8'))>190*1024**2:raise ValueError('Video '+video['id']+' exceeds the local 190 MiB source budget. Resolve the limit before upload.')
        planned.append((video,text))
    out=root/'notebooklm';out.mkdir(exist_ok=True);parts=[]
    for i,(video,text) in enumerate(planned,1):
        p=out/f'source-{i:03}.txt';write_text(p,text)
        parts.append({'title':video['title']+' — YPE expanded source account','video_id':video['id'],'words':len(text.split()),**evidence(p)})
    result={'collection_key':run['collection_key'],'collection_digest':identity_hash(run),'input_hashes':package_inputs(root,run),'notebook_title':run['title'],'account_label':'Pulse Vibe Daily','packets':parts,'source_cap':source_cap,'words_per_source':words_per_source,'granularity':'video','caption_mode':caption_mode,'source_contract':'one-video/1','purpose':'One neutral enriched source per video. Project applications, audience reception and cross-video synthesis stay in separate local reports. No upload has occurred.'}
    write(out/'package.json',result);return result

def packets(root,words_per_source=40000,source_cap=50,granularity=None,caption_mode=None):
    if not 100<=words_per_source<=400000 or not 2<=source_cap<=1000:raise ValueError('Invalid source packet bounds.')
    root=Path(root);run=read(root/'run.json');blocks=[];owners=[]
    granularity=granularity or ('video' if run['mode']=='full' else 'batch')
    caption_mode=caption_mode or run.get('notebook_caption_mode','retained')
    if granularity not in ('video','batch') or caption_mode not in ('retained','references'):raise ValueError('Unknown source packaging policy.')
    if run.get('notebook_source_contract')=='one-video/1':
        if granularity!='video':raise ValueError('This run requires one NotebookLM source per video; batch packing is incompatible.')
        return video_sources(root,run,words_per_source,source_cap,caption_mode)
    for v in run['videos']:
        errors=video_checks(root,v,run['mode'])
        if errors:raise ValueError('Only reviewed and linked analyses can be packaged: '+str(v.get('id'))+' '+errors[0])
        dest=root/'videos'/v['id']
        chunks=[f'# {v["title"]}\nSource: {v["url"]}\nVideo ID: {v["id"]}\n', (dest/'analysis.md').read_text()]
        scored=dest/'community/community.md'
        if (run.get('community') or {}).get('enabled') and scored.is_file():chunks.append('## Community check (scored comments)\n'+scored.read_text())
        if run['mode']=='full':chunks += [(dest/'enhanced-transcript.md').read_text(),(dest/'intelligence-report.md').read_text()]
        a=read(dest/'analysis.json');mf=read(dest/'frames/manifest.json')
        chunks += ['## Reviewed visual observations\n'+'\n'.join(f'- [{timestamp(o["timestamp_seconds"])}] {o["frame"]}: {o["description"]}' for o in a['observations']),f'Captured frames: {len(mf["frames"])}. Inspected frames: {len(set(a["inspected_frames"]))}. Sampling is not continuous viewing.']
        if caption_mode=='retained':chunks += ['## Original timestamped captions\n'+(dest/'transcript.txt').read_text()]
        else:chunks += ['## Original source reference\n'+v['url']+'\nThe original video URL is retained for reference; import it separately where the provider supports it. This packet supplies the reviewed timed source account and visual analysis, expressed in our own words. Remote ingestion is verified separately.']
        # Split by lines when a single long video exceeds a packet; keep source identity in each part.
        header=chunks[0];current=header
        for line in '\n\n'.join(chunks[1:]).splitlines(keepends=True):
            words=line.split()
            while len(words)>words_per_source//2:
                segment=' '.join(words[:words_per_source//2]);words=words[words_per_source//2:]
                if len((current+segment).split())>words_per_source:blocks.append(current);owners.append(v);current=header
                current+=segment+'\n'
            line=' '.join(words)+'\n'
            if len((current+line).split())>words_per_source:blocks.append(current);owners.append(v);current=header
            current+=line
        if current.strip()!=header.strip():blocks.append(current);owners.append(v)
    packed=[];labels=[];current=''
    if granularity=='video':
        packed=blocks;labels=[{'video_id':v['id'],'title':v['title']} for v in owners]
    else:
        for block in blocks:
            if current and len((current+block).split())>words_per_source:packed.append(current);labels.append({'title':run['title']});current=''
            current+=block+'\n\n'
        if current:packed.append(current);labels.append({'title':run['title']})
    master=root/'master-compilation.md'
    if master.exists():
        text=master.read_text()
        if run.get('claim_matrix') and (root/'claim-matrix.json').is_file():text+='\n\n## Claim matrix\n'+community.matrix_markdown(read(root/'claim-matrix.json'),run)
        if len(text.split())>words_per_source:raise ValueError('Master compilation exceeds configured packet size; split deliberately.')
        packed.insert(0,text);labels.insert(0,{'title':run['title']+' — cross-video synthesis'})
    if len(packed)>source_cap-1:raise ValueError('Packets exceed the notebook source budget (one slot reserved). Split into named volumes; do not silently omit videos.')
    if any(len(text.encode('utf-8'))>190*1024**2 for text in packed):raise ValueError('Packet exceeds the local 190 MiB upload budget; split deliberately.')
    out=root/'notebooklm';out.mkdir(exist_ok=True);parts=[]
    for i,text in enumerate(packed,1):
        p=out/f'source-{i:03}.txt';write_text(p,text);label=labels[i-1];title=label['title']+' — YPE visual intelligence'
        parts.append({'title':title,'video_id':label.get('video_id'),'words':len(text.split()),**evidence(p)})
    result={'collection_key':run['collection_key'],'collection_digest':identity_hash(run),'input_hashes':package_inputs(root,run),'notebook_title':run['title'],'account_label':'Pulse Vibe Daily','packets':parts,'source_cap':source_cap,'words_per_source':words_per_source,'granularity':granularity,'caption_mode':caption_mode,'purpose':'Flat evidence for source ingestion; the rich HTML report is the human view. No upload has occurred.'}
    write(out/'package.json',result);return result
