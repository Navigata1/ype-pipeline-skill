import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ype-pipeline/scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_pipeline import fixture,full_fixture,VID
import core,publish,ype

class SourcePackaging(unittest.TestCase):
    def test_video_packets_do_not_blend_two_video_identities(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run,dest=fixture(root);other='00000000001';new=root/'videos'/other
            import shutil
            shutil.copytree(dest,new)
            # Make each synthetic source genuinely bind to its own ID and frame location.
            media=core.read(new/'media.json');media['id']=other;core.write(new/'media.json',media)
            mf=core.read(new/'frames/manifest.json')
            for row in mf['frames']:row['path']=str(new/'frames'/row['name'])
            core.write(new/'frames/manifest.json',mf)
            v=dict(run['videos'][0],id=other,url='https://www.youtube.com/watch?v='+other,title='Second distinct video');run['videos'].append(v);run['membership'].append({'position':2,'id':other,'title':v['title']});ype.save(root,run)
            pkg=publish.packets(root,granularity='video');self.assertEqual(len(pkg['packets']),2)
            self.assertEqual({p['video_id'] for p in pkg['packets']},{VID,other})
            self.assertTrue(all(Path(p['path']).read_text().count('Video ID:')==1 for p in pkg['packets']))
    def test_reference_mode_preserves_local_captions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run,dest=fixture(root);before=core.sha(dest/'transcript.txt')
            pkg=publish.packets(root,caption_mode='references');text=Path(pkg['packets'][0]['path']).read_text()
            self.assertNotIn('Original timestamped captions',text);self.assertIn('Original source reference',text)
            self.assertEqual(before,core.sha(dest/'transcript.txt'))
    def test_new_source_contract_rejects_omitted_intervals(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run,dest=full_fixture(root);run['source_fidelity_contract']='timed-source-account/1';ype.save(root,run)
            m=core.read(dest/'media.json');mapping={'source_sha256':m['source']['sha256'],'transcript_sha256':core.sha(dest/'transcript.txt'),'enhanced_sha256':core.sha(dest/'enhanced-transcript.md'),'reviewer':'fixture','examples_and_qualifications_checked':True,'sections':[{'heading':'Synthetic fixture substance.','cue_start':0,'cue_end':0,'frame_names':[]}]};core.write(dest/'enhanced-source-map.json',mapping)
            review=core.read(dest/'full-review.json');review['source_map_sha256']=core.sha(dest/'enhanced-source-map.json');core.write(dest/'full-review.json',review)
            self.assertIn('expanded source map omits caption intervals',publish.video_checks(root,run['videos'][0],'full'))

if __name__=='__main__':unittest.main()
