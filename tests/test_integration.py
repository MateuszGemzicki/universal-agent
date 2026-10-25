import json, tempfile, unittest
from pathlib import Path
from agent_system.core import collect, connect, scan
class IntegrationTests(unittest.TestCase):
    def test_merkle_change(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'a.py').write_text('def a(): return 1')
            h,files=collect(p);(p/'a.py').write_text('def a(): return 2')
            h2,files2=collect(p);self.assertNotEqual(h,h2);self.assertNotEqual(files,files2)
    def test_incremental(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'repo';root.mkdir();(root/'x.py').write_text('def x(a:int)->int:\n return a')
            db=connect(Path(t)/'state.db');db.execute('INSERT INTO repositories(name,path) VALUES(?,?)',('r',str(root)));db.commit()
            self.assertEqual(scan(db,'r')['changed'],['x.py']);self.assertEqual(scan(db,'r')['changed'],[])
            (root/'x.py').unlink();self.assertEqual(scan(db,'r')['deleted'],['x.py']);db.close()
