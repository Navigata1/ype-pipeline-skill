"""Durable state and evidence primitives for the YPE preparation runner."""
from __future__ import annotations
import contextlib, fcntl, hashlib, html, json, os, re, time, tempfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs

VERSION = '8.0'

def read(path):
    return json.loads(Path(path).read_text())

def write(path, data):
    write_text(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def write_text(path, text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink() or path.parent.is_symlink():raise ValueError('Refusing symlinked artifact output.')
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:
            f.write(text);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

@contextlib.contextmanager
def lock(root):
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    with (root/'.ype.lock').open('a') as f:
        try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('Another writer holds this YPE folder; retry after it finishes.')
        yield

def safe_id(value):
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', value): raise ValueError('Expected a YouTube video ID.')
    return value

def youtube(url):
    u = urlparse(url)
    if u.scheme != 'https' or u.hostname not in ('youtube.com','www.youtube.com','m.youtube.com','youtu.be') or u.username or u.password:
        raise ValueError('Only explicit HTTPS YouTube URLs are accepted.')
    q = parse_qs(u.query)
    vid = u.path.strip('/').split('/')[0] if u.hostname == 'youtu.be' else q.get('v',[None])[0]
    if u.path.startswith(('/shorts/','/embed/')): vid = u.path.split('/')[2]
    pid = q.get('list',[None])[0]
    if pid and not re.fullmatch(r'[A-Za-z0-9_-]+',pid): raise ValueError('Invalid playlist ID.')
    if vid: safe_id(vid)
    if not vid and not pid: raise ValueError('YouTube URL has no video or playlist ID.')
    return vid, pid

def collection_key(urls, playlist=None):
    if playlist:
        _, pid = youtube(playlist)
        if not pid: raise ValueError('Playlist URL requires list=...')
        return 'youtube-playlist:'+pid
    ids = {youtube(u)[0] for u in urls}
    if not ids or None in ids: raise ValueError('Use --playlist for a playlist-only URL.')
    ids=sorted(ids)
    return 'youtube-curated:'+hashlib.sha256('\n'.join(ids).encode()).hexdigest()[:24]

def cue_seconds(value):
    parts = value.replace(',','.').split(':')
    if len(parts)==2: parts=['0']+parts
    return int(parts[0])*3600+int(parts[1])*60+float(parts[2])

def timestamp(seconds):
    s=int(seconds);return f'{s//3600:02}:{s%3600//60:02}:{s%60:02}'

def captions(text):
    """Return timed cues; use captions_with_audit() to inspect cleanup decisions."""
    return captions_with_audit(text)['cues']

def captions_with_audit(text):
    """Conservatively clean captions without changing their original cue times.

    A rolling prefix needs at least two identical words, fresh trailing words,
    and overlapping windows whose start does not regress and whose end advances.
    Touching, separated, identical-window-but-distinct, and otherwise ambiguous
    cues remain intact. Only identical text at identical times is dropped whole.
    The downloaded caption file remains the source of truth; this audit describes
    normalized cue text after the existing tag and whitespace cleanup.
    """
    out=[]; decisions=[]; previous=None
    for block in re.split(r'\n\s*\n',text.replace('\r','')):
        lines=block.splitlines(); timing=next((i for i,l in enumerate(lines) if '-->' in l),None)
        if timing is None: continue
        a,b=lines[timing].split('-->',1)
        value=html.unescape(re.sub(r'<[^>]*>','', ' '.join(lines[timing+1:])))
        value=re.sub(r'\s+',' ',value).strip()
        if not value: continue
        cue={'start':cue_seconds(a.strip()),'end':cue_seconds(b.strip().split()[0]),'text':value}
        decision={'input_cue_index':len(decisions),'output_cue_index':len(out),
                  'start':cue['start'],'end':cue['end'],'original_text':value,
                  'action':'kept','reason':'no_demonstrable_rolling_overlap','removed_prefix':''}
        fresh=value
        if previous == cue:
            fresh=''
            decision.update(action='skipped_same_time_duplicate',reason='identical_text_and_times',
                            removed_prefix=value,output_cue_index=None)
        elif previous and previous['start'] <= cue['start'] < previous['end'] < cue['end']:
            words=value.split(); prev=previous['text'].split()
            for n in range(min(len(prev),len(words)),1,-1):
                if prev[-n:]==words[:n]:
                    if n < len(words):
                        fresh=' '.join(words[n:])
                        decision.update(action='trimmed_rolling_prefix',
                                        reason='overlapping_advancing_window_with_multiword_match_and_new_suffix',
                                        removed_prefix=' '.join(words[:n]))
                    break
        if fresh: out.append({**cue,'text':fresh})
        decisions.append(decision)
        previous=cue
    return {'policy':'caption-time-v1','input_cue_count':len(decisions),
            'output_cue_count':len(out),'cues':out,'decisions':decisions}

def failure_kind(message):
    lower=message.lower()
    if any(x in lower for x in ['429','too many requests','rate limit']): return 'rate_limited'
    if any(x in lower for x in ['sign in','login','private video','members-only','not a bot','age-restricted']): return 'needs_owner'
    if any(x in lower for x in ['unavailable','removed','copyright']): return 'unavailable'
    return 'retryable'

def record_failure(video, message, now=None):
    now=time.time() if now is None else now
    kind=failure_kind(message);video['attempts']=video.get('attempts',0)+1
    video['state']=kind
    video['last_error']=message[-1500:]
    video['retry_after']=now+min(3600,60*2**min(video['attempts']-1,6)) if kind in ('retryable','rate_limited') else None
    if video['attempts']>=5: video['state']='needs_owner';video['retry_after']=None

def eligible(video, now=None):
    return video.get('state') in ('pending','acquiring','retryable','rate_limited') and (video.get('retry_after') or 0)<=(time.time() if now is None else now)

def evidence(path):
    p=Path(path).resolve()
    return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}

def evidence_ok(item):
    try:
        p=Path(item['path']);return p.is_file() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
    except (OSError,KeyError,TypeError):return False

def local(root, value):
    root=Path(root).resolve(); p=(root/value).resolve()
    if not p.is_relative_to(root): raise ValueError('Artifact path escapes the run directory.')
    return p

def identity_hash(run):
    return hashlib.sha256(json.dumps({'collection':run['collection_key'],'videos':[v.get('id') for v in run['videos']],'membership':run.get('membership',[])},sort_keys=True).encode()).hexdigest()
