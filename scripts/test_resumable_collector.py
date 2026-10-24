"""Execute bounded collector against the same mock as the synchronous collector."""
import json
import shutil
import subprocess
import unittest

import penpot_conformance as audit


@unittest.skipUnless(shutil.which('node'), 'Node required for collector integration')
class ResumableCollectorTests(unittest.TestCase):
    def run_collector(self, mutation=''):
        manifest = audit.build_manifest()
        script = '''
const storage={};
const makeNode=id=>({id,type:'text',name:'Title',hidden:false,opacity:null,
 x:1,y:2,width:30,height:20,characters:'Привет',fills:[],children:[],
 component:()=>null,isComponentCopyInstance:()=>false,isComponentHead:()=>false,isVariantContainer:()=>false,
 componentRefShape:()=>null,getPluginData:()=>''});
const nodes=Array.from({length:125},(_,i)=>makeNode(String(i)));
const a={id:'a',name:'Row',path:'Component',mainInstance:()=>({id:'main-a'}),variantProps:{State:'one'},isVariant:()=>true};
const b={...a,id:'b',mainInstance:()=>({id:'main-b'}),variantProps:{State:'two'}};
a.variants=b.variants={variantComponents:()=>[a,b]};
const penpot={currentFile:{id:'file',name:'Generated UI (do not edit)',
 pages:[{id:'page',name:'Test',root:{children:nodes}}]},library:{local:{components:[a]}}};
let result=(new Function('penpot','storage', RESUMABLE))(penpot,storage);
const firstBatch=result.nodes;
let steps=0;
while(!result.done&&!result.failed&&steps++<30){
 MUTATION
 result=storage.conformanceCollectStep();
}
const synchronous=(new Function('penpot', SYNCHRONOUS))(penpot);
process.stdout.write(JSON.stringify({result,firstBatch,steps,snapshot:storage.conformanceSnapshot,synchronous}));
'''.replace('RESUMABLE', json.dumps(audit.emit_collector(manifest, resumable=True)))
        script = script.replace('SYNCHRONOUS', json.dumps(audit.emit_collector(manifest))).replace('MUTATION', mutation)
        result = subprocess.run(['node', '-e', script], text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_bounded_two_pass_collection_retains_all_facts(self):
        evidence = self.run_collector()
        self.assertLessEqual(evidence['firstBatch'], 50)
        self.assertGreater(evidence['steps'], 2)
        self.assertTrue(evidence['result']['done'], evidence)
        snapshot = evidence['snapshot']
        synchronous = evidence['synchronous']
        for key in ('pages', 'nodes', 'records', 'fingerprint', 'coverage', 'complete', 'collectionErrors'):
            self.assertEqual(synchronous[key], snapshot[key], key)
        self.assertEqual(2, len(snapshot['records']))

    def test_changed_fact_between_passes_invalidates_capture(self):
        evidence = self.run_collector("if(result.pass===2)nodes[0].characters='changed';")
        self.assertTrue(evidence['result']['failed'])
        self.assertFalse(evidence['snapshot']['complete'])
        self.assertIn('changed between', evidence['snapshot']['collectionErrors'][0])

    def test_identity_change_and_cycles_fail_closed(self):
        for mutation in ("penpot.currentFile.id='other';", 'nodes[60].children=[nodes[60]];'):
            evidence = self.run_collector(mutation)
            self.assertTrue(evidence['result']['failed'], evidence)
            self.assertFalse(evidence['snapshot']['complete'])


if __name__ == '__main__':
    unittest.main()