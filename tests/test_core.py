import subprocess
import tempfile
import unittest
from pathlib import Path
from agent_system.core import collect, connect, scan, inventory_python

class CoreTests(unittest.TestCase):
    def test_merkle_changes_and_restores(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'a.py').write_text('x=1')
            first,_=collect(root)
            (root/'a.py').write_text('x=2')
            second,_=collect(root)
            self.assertNotEqual(first,second)
            (root/'a.py').write_text('x=1')
            self.assertEqual(first,collect(root)[0])
    def test_gitignore_respected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); subprocess.run(['git','init','-q',str(root)],check=True)
            (root/'.gitignore').write_text('*.log\ncache/\n'); (root/'a.py').write_text('x=1')
            (root/'b.log').write_text('x'); (root/'cache').mkdir(); (root/'cache'/'c.py').write_text('x')
            self.assertEqual(sorted(collect(root)[1]),['.gitignore','a.py'])
    def test_incremental_scan(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); repo=root/'repo';repo.mkdir()
            (repo/'mod.py').write_text('def f(x: int) -> bool:\n    return bool(x)\n')
            db=connect(root/'state.sqlite3')
            db.execute('INSERT INTO repositories(name,path) VALUES(?,?)',('r',str(repo)));db.commit()
            self.assertEqual(scan(db,'r')['changed'],['mod.py'])
            self.assertEqual(scan(db,'r')['changed'],[])
            (repo/'mod.py').unlink()
            self.assertEqual(scan(db,'r')['deleted'],['mod.py'])
            db.close()
    def test_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.py';p.write_text('def hello(name: str) -> str:\n    return name.upper()\n')
            self.assertEqual(inventory_python(p)[0]['calls'],['upper'])

if __name__=='__main__': unittest.main()
