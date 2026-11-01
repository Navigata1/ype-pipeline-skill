"""Bounded sequential acquisition; retained originals and timestamped frame evidence."""
from __future__ import annotations
import contextlib, json, re, shutil, subprocess, time, math, tempfile, os, signal
from pathlib import Path
from core import captions, captions_with_audit, evidence, evidence_ok, read, safe_id, timestamp, write, write_text

def command(args, timeout=300, monitor=None):
    """Bound wall time and terminate the process group, including an ffmpeg merger."""
    started=time.monotonic()
    with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
        proc=subprocess.Popen(args,stdout=out,stderr=err,start_new_session=True)
        try:
            while proc.poll() is None:
                if time.monotonic()-started>timeout:raise TimeoutError('Command deadline reached; partial files preserved.')
                if monitor:
                    folder,limit=monitor
                    size=sum(p.stat().st_size for p in Path(folder).rglob('*') if p.is_file() and not p.is_symlink())
                    if size>limit or shutil.disk_usage(folder).free<15*1024**3:raise ValueError('Download working-set or free-space boundary reached; partial files preserved.')
                time.sleep(.25)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=3)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        out.seek(0);err.seek(0);stdout=out.read().decode(errors='replace');stderr=err.read().decode(errors='replace')
        if proc.returncode:raise RuntimeError((stderr or stdout)[-1600:])
        return stdout,stderr

def ytdlp(extra,url,timeout=300,monitor=None):
    return command(['yt-dlp','--ignore-config','--no-warnings','--no-progress','--socket-timeout','20','--retries','2','--fragment-retries','2','--concurrent-fragments','1',*extra,'--',url],timeout,monitor)

def metadata(url,timeout=300):
    out,_=ytdlp(['--no-playlist','--skip-download','--dump-single-json'],url,timeout)
    d=json.loads(out)
    out={k:d.get(k) for k in ['id','title','channel','duration','upload_date','webpage_url']}
    out.update(manual_caption_languages=sorted(d.get('subtitles') or {}),automatic_captions_available=bool(d.get('automatic_captions')))
    return out

def caption_provenance(info,track='en'):
    """yt-dlp prefers an uploaded track over automatic speech recognition for the same language."""
    manual=info.get('manual_caption_languages')
    if manual is None:return 'unknown'
    return 'manual' if any(l==track or l.startswith(track+'-') for l in manual) else 'automatic'

def inventory(url,limit=1000):
    out,_=ytdlp(['--flat-playlist','--skip-download','--dump-single-json','--playlist-end',str(limit)],url,600)
    data=json.loads(out); entries=data.get('entries',[])
    if not entries: raise ValueError('Playlist returned no entries; nothing has been marked complete.')
    if (data.get('playlist_count') or len(entries))>limit or len(entries)==limit:
        raise ValueError('Inventory reached its safety cap; explicitly increase the inventory limit and retry.')
    return data,entries

def preflight(root,max_bytes):
    tools={x:shutil.which(x) for x in ['yt-dlp','ffmpeg','ffprobe']}
    free=shutil.disk_usage(root).free;required=15*1024**3+int(2.5*max_bytes)
    return {'tools':tools,'free_bytes':free,'required_free_bytes':required,'pass':all(tools.values()) and free>=required,'note':'Working set is bounded one download at a time; this is a local safety margin, not a storage forecast.'}

def probe(path,timeout=60):
    out,_=command(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,height,width','-of','json',str(path)],timeout)
    d=json.loads(out);duration=float(d['format']['duration'])
    video=next(s for s in d['streams'] if s.get('codec_type')=='video')
    if duration<=0:raise ValueError('Invalid media duration.')
    return {'duration':duration,'height':video.get('height'),'width':video.get('width')}

def acquire(video,archive,max_height,max_bytes,timeout):
    vid=safe_id(video['id']);dest=Path(archive)/vid;dest.mkdir(parents=True,exist_ok=True)
    mf=dest/'media.json'
    if mf.exists():
        old=read(mf)
        if old.get('id')==vid and evidence_ok(old['source']) and evidence_ok(old['caption']):
            if old['metadata']['height']>max_height or old['source']['bytes']>max_bytes:raise ValueError('Retained source exceeds this run policy. Keep original and explicitly choose a compatible policy.')
            return old
        raise ValueError('Retained media or captions changed. Preserve this folder and inspect before replacing it.')
    started=time.monotonic()
    def remaining():
        value=int(timeout-(time.monotonic()-started))
        if value<1:raise TimeoutError('Per-item time budget reached; retained partials can resume.')
        return value
    info=metadata(video['url'],remaining())
    if info['id']!=vid:raise ValueError('YouTube metadata identity changed.')
    write(dest/'metadata.json',info)
    caption_error=None
    subs=sorted(dest.glob('captions*.vtt'))+sorted(dest.glob('captions*.srt'))
    if not subs:
        # Prefer the original English track to an automatic English translation.
        track=video.get('caption_language','en')
        try:
            ytdlp(['--no-playlist','--skip-download','--write-subs','--write-auto-subs','--sub-langs',track,'--sub-format','vtt','-o',str(dest/'captions.%(ext)s')],video['url'],min(remaining(),360))
        except RuntimeError as e:
            if any(x in str(e).lower() for x in ['429','too many requests','sign in','not a bot']):raise
            caption_error=str(e)
        subs=sorted(dest.glob('captions*.vtt'))+sorted(dest.glob('captions*.srt'))
    if not subs:raise ValueError('Owner input needed: no usable English captions. Preserve files and supply an approved timestamped transcript/ASR. '+(caption_error or ''))
    fmt=f'b[height<={max_height}]/bv[height<={max_height}]+ba'
    ytdlp(['--no-playlist','--continue','--no-overwrites','--max-filesize',str(max_bytes),'-f',fmt,'--merge-output-format','mkv','-o',str(dest/'source.%(ext)s')],video['url'],remaining(),(dest,int(2.5*max_bytes)+50*1024**2))
    sources=[p for p in dest.glob('source.*') if p.suffix.lower() in ('.mp4','.mkv','.webm','.mov')]
    if len(sources)!=1 or any(dest.glob('*.part')):raise RuntimeError('Download incomplete or absent; retained partials are not valid evidence.')
    info.update(probe(sources[0],remaining()))
    if info['height']>max_height or sources[0].stat().st_size>max_bytes:raise ValueError('Retrieved media exceeds the configured size or resolution bound; preserved for inspection.')
    version,_=command(['yt-dlp','--version'],min(10,remaining()))
    data={'id':vid,'url':video['url'],'metadata':info,'source':evidence(sources[0]),'caption':evidence(subs[0]),'retention':'keep','origin':'fresh-download','retrieved_at':time.time(),'extractor_version':version.strip(),'format_policy':fmt,'source_extent':'full','max_bytes':max_bytes,'caption_provenance':caption_provenance(info,video.get('caption_language','en'))}
    write(mf,data);return data

def import_existing(video,folder):
    folder=Path(folder).resolve();sources=[p for p in folder.glob('source.*') if p.suffix.lower() in ('.mp4','.mkv','.webm','.mov')]
    subs=sorted(folder.glob('*.srt'))+sorted(folder.glob('*.vtt'))
    if len(sources)!=1 or not subs:raise ValueError('Existing capture needs one source video and timestamped SRT/VTT captions.')
    meta=read(folder/'metadata.json')
    if meta.get('id')!=video['id']:raise ValueError('Cached metadata must identify the requested video exactly.')
    return {'id':video['id'],'url':video['url'],'metadata':{'id':video['id'],'title':meta.get('title') or video.get('title') or video['id'],**probe(sources[0])},'source':evidence(sources[0]),'caption':evidence(subs[0]),'retention':'keep','origin':'cached-reprocessing','source_extent':'full','source_folder':str(folder),'imported_at':time.time(),'caption_provenance':caption_provenance(meta)}

def materialize(root,video,data):
    root=Path(root);vid=video['id'];dest=root/'videos'/vid;dest.mkdir(parents=True,exist_ok=True)
    cleanup=captions_with_audit(Path(data['caption']['path']).read_text(errors='replace'));cues=cleanup['cues']
    if not cues:raise ValueError('Caption file parsed to zero cues.')
    write(dest/'caption-cleanup-audit.json',cleanup)
    write(dest/'cues.json',cues)
    clean=dest/'transcript.txt';write_text(clean,'\n'.join(f'[{timestamp(c["start"])}] {c["text"]}' for c in cues)+'\n')
    write(dest/'media.json',data)
    video.update({'title':data['metadata']['title'],'duration':data['metadata']['duration'],'state':'materials_ready','media':str((dest/'media.json').relative_to(root)),'transcript_sha256':evidence(clean)['sha256']})

def sample(root,video,count=100,dedup=True):
    if not 1<=count<=1000:raise ValueError('Frame count must be in 1..1000.')
    dest=Path(root)/'videos'/video['id'];data=read(dest/'media.json')
    if not evidence_ok(data['source']):raise ValueError('Source hash mismatch.')
    frames=dest/'frames';mf=frames/'manifest.json'
    if mf.exists():
        saved=read(mf)
        if saved.get('sampling_schema')==2 and saved.get('source_sha256')==data['source']['sha256'] and saved.get('requested_count')==count and saved.get('dedup')==dedup and all(evidence_ok(r) for r in saved['frames']):return saved
        raise ValueError('Existing frame policy differs or evidence changed. Use a new run for a new scout policy.')
    if frames.exists() and any(frames.iterdir()):
        recovery=dest/('frames-interrupted-'+str(time.time_ns()));frames.rename(recovery)
    frames.mkdir(exist_ok=True)
    interval=float(data['metadata']['duration'])/count
    filt=f'select=isnan(prev_selected_t)+gte(t-prev_selected_t\\,{interval:.10f})'
    if dedup:filt+=',mpdecimate=hi=768:lo=320:frac=0.33'
    filt+=',showinfo'
    _,log=command(['ffmpeg','-hide_banner','-loglevel','info','-i',data['source']['path'],'-vf',filt,'-fps_mode','vfr','-q:v','3',str(frames/'f_%04d.jpg')],1800)
    pts=[float(n) for n in re.findall(r'\bn:\s*\d+.*?pts_time:([0-9.e+-]+)',log)]
    files=sorted(frames.glob('f_*.jpg'))
    if not files or len(files)!=len(pts):raise ValueError('Frame/time mapping is incomplete; no frame manifest certified.')
    rows=[{'name':p.name,'timestamp_seconds':t,'method':'original-source-presentation-time',**evidence(p)} for p,t in zip(files,pts)]
    result={'sampling_schema':2,'requested_count':count,'dedup':dedup,'duration':data['metadata']['duration'],'source_sha256':data['source']['sha256'],'frames':rows}
    write(mf,result);return result

def capture_moments(root,video):
    dest=Path(root)/'videos'/video['id'];plan=read(dest/'moments.json');data=read(dest/'media.json')
    duration=float(data['metadata']['duration']);moments=plan['moments'];frames=dest/'frames';mf=read(frames/'manifest.json')
    if not evidence_ok(data['source']):raise ValueError('Source hash mismatch.')
    if not moments or not plan.get('transcript_reviewed'):raise ValueError('Full capture needs a transcript-reviewed moment map.')
    wanted=[]
    for i,m in enumerate(moments):
        if not str(m.get('reason','')).strip() or not 0<=float(m['start'])<=float(m['end'])<=duration:raise ValueError('Moment range/reason invalid.')
        seconds=m.get('capture_seconds',[])
        if not seconds or any(not math.isfinite(float(s)) or not float(m['start'])<=float(s)<=float(m['end']) or float(s)>=duration for s in seconds):raise ValueError('Capture requests must lie within their moment and before the final media boundary.')
        if m.get('importance')=='high' and len(set(seconds))<3:raise ValueError('High-importance moments need at least three distinct captures.')
        wanted.extend((i,float(s)) for s in seconds)
    if len(wanted)>600:raise ValueError('Split a very large moment map into a separate run; at most 600 supplemental frames per video.')
    existing={r['name']:r for r in mf['frames']}
    for i,s in wanted:
        name=f'm_{i:03}_{int(s*1000):09}.jpg';path=frames/name
        if name in existing and evidence_ok(existing[name]):continue
        command(['ffmpeg','-v','error','-ss',str(s),'-i',data['source']['path'],'-frames:v','1','-q:v','2','-y',str(path)],90)
        existing[name]={'name':name,'timestamp_seconds':s,'method':'requested-seek-nearest-frame','moment_index':i,**evidence(path)}
        mf['frames']=list(existing.values());write(frames/'manifest.json',mf)
    mf['moment_map_sha256']=evidence(dest/'moments.json')['sha256'];write(frames/'manifest.json',mf)
    return mf

def capture(root,video,seconds,purpose,height=None,archive_lock=None):
    """Targeted frames at original times: scouts, priority sections, or a higher-resolution derived section."""
    dest=Path(root)/'videos'/video['id'];data=read(dest/'media.json');frames=dest/'frames';mf=read(frames/'manifest.json')
    if not evidence_ok(data['source']):raise ValueError('Source hash mismatch.')
    duration=float(data['metadata']['duration']);seconds=sorted({round(float(s),3) for s in seconds})
    if not seconds or len(seconds)>200 or any(not math.isfinite(s) or not 0<=s<duration for s in seconds):raise ValueError('Capture times must lie inside the source (at most 200 per call).')
    if not str(purpose).strip():raise ValueError('A capture needs a purpose.')
    source=data['source'];offset=0.0;derived=None
    if height:
        if not 240<=int(height)<=2160:raise ValueError('Derived height must be 240..2160.')
        start=max(0.0,seconds[0]-2);end=min(duration,seconds[-1]+2)
        if end-start>180:raise ValueError('A derived section is at most 180 seconds; capture separate sections.')
        folder=Path(source['path']).parent/'derived';folder.mkdir(exist_ok=True);stem=f'h{int(height)}_{int(start*1000):09}_{int(end*1000):09}'
        existing=[p for p in folder.glob(stem+'.*') if p.suffix.lower() in ('.mp4','.mkv','.webm')]
        if not existing:
            with (archive_lock or contextlib.nullcontext()):
                ytdlp(['--no-playlist','--download-sections',f'*{start:.3f}-{end:.3f}','-f',f'bv[height<={int(height)}]/b[height<={int(height)}]','-o',str(folder/(stem+'.%(ext)s'))],video['url'],600)
            existing=[p for p in folder.glob(stem+'.*') if p.suffix.lower() in ('.mp4','.mkv','.webm')]
        if len(existing)!=1:raise RuntimeError('Derived section download incomplete; partials preserved.')
        derived={**evidence(existing[0]),'height':probe(existing[0])['height'],'section_start':start,'section_end':end,'note':'Derived capture for legibility; the retained source is unchanged.'}
        source=derived;offset=start
    rows={r['name']:r for r in mf['frames']}
    for s in seconds:
        # Millisecond names; a derived frame also names its height and section so captures never alias.
        name=(f'h{int(height)}s{round(offset*1000):09}' if derived else 't')+f'_{round(s*1000):09}.jpg';path=frames/name
        if name in rows and evidence_ok(rows[name]):continue
        command(['ffmpeg','-v','error','-ss',str(max(0.0,s-offset)),'-i',source['path'],'-frames:v','1','-q:v','2','-y',str(path)],120)
        row={'name':name,'timestamp_seconds':s,'method':'requested-seek-nearest-frame','purpose':str(purpose).strip(),**evidence(path)}
        if derived:row['derived_source']=derived
        rows[name]=row;mf['frames']=list(rows.values());write(frames/'manifest.json',mf)
    return {'frames':len(mf['frames']),'captured':[n for n in rows if rows[n]['timestamp_seconds'] in seconds]}

def contact_sheets(root,video,per_sheet=20,columns=5,width=320):
    """Labelled orientation sheets. They help choose originals to open; they are not evidence of inspection."""
    from PIL import Image, ImageDraw
    if not 4<=per_sheet<=48 or not 2<=columns<=8:raise ValueError('Sheet layout out of range.')
    dest=Path(root)/'videos'/video['id'];rows=sorted(read(dest/'frames/manifest.json')['frames'],key=lambda r:r['timestamp_seconds'])
    if not all(evidence_ok(r) for r in rows):raise ValueError('Frame evidence changed; resample before building sheets.')
    out=dest/'review-contact-sheets';out.mkdir(exist_ok=True);index=[]
    for k in range(0,len(rows),per_sheet):
        chunk=rows[k:k+per_sheet];thumbs=[]
        for r in chunk:
            with Image.open(r['path']) as im:im=im.convert('RGB');h=max(1,round(im.height*width/im.width));thumbs.append(im.resize((width,h)))
        cell=max(t.height for t in thumbs)+22;sheet=Image.new('RGB',(columns*width,cell*math.ceil(len(chunk)/columns)),'white');draw=ImageDraw.Draw(sheet)
        for i,(r,t) in enumerate(zip(chunk,thumbs)):
            x,y=i%columns*width,i//columns*cell;sheet.paste(t,(x,y));draw.text((x+4,y+t.height+4),f'{r["name"]}  {timestamp(r["timestamp_seconds"])}',fill='black')
        name=f'sheet_{k//per_sheet+1:02}.jpg';sheet.save(out/name,quality=88);index.append({'sheet':name,'frames':[r['name'] for r in chunk]})
    write(out/'index.json',{'note':'Orientation only. Record inspected originals in analysis.json.','sheets':index});return {'sheets':len(index),'folder':str(out)}

def enlarge(root,video,frame,box,scale=3):
    """A cropped, enlarged view of one frame for reading small UI or code text."""
    from PIL import Image
    dest=Path(root)/'videos'/video['id'];rows={r['name']:r for r in read(dest/'frames/manifest.json')['frames']}
    if frame not in rows or not evidence_ok(rows[frame]):raise ValueError('Unknown or changed frame.')
    if not 2<=scale<=6:raise ValueError('Scale must be 2..6.')
    x0,y0,x1,y1=box;out=dest/'review-enlargements';out.mkdir(exist_ok=True)
    with Image.open(rows[frame]['path']) as im:
        if not 0<=x0<x1<=im.width or not 0<=y0<y1<=im.height:raise ValueError('Crop box outside the frame.')
        path=out/f'{Path(frame).stem}_x{scale}_{x0}_{y0}_{x1}_{y1}.png';im.crop(box).resize(((x1-x0)*scale,(y1-y0)*scale),Image.LANCZOS).save(path)
    return {'enlargement':str(path),'frame':frame}
