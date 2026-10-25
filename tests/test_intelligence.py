import tempfile,unittest,json
from pathlib import Path
from agent_system.core import connect,scan
from agent_system import intelligence as I
class IntelligenceTests(unittest.TestCase):
    def test_context_impact_stale_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);repo=root/'repo';repo.mkdir();(repo/'a.py').write_text('def calculate_price(x):\n    return x * 2\n');(repo/'b.py').write_text('def checkout():\n    return calculate_price(3)\n')
            db=connect(root/'state.sqlite3');I.init(db)
            db.execute('INSERT INTO repositories(name,path) VALUES(?,?)',('demo',str(repo)));db.commit();scan(db,'demo')
            self.assertTrue(I.search(db,'calculate_price'))
            self.assertTrue(I.impact(db,'demo','a.py')['possible_dependents'])
            self.assertIn('calculate_price',I.context(db,'calculate_price',2000)['text'])
            I.save_artifact(db,'business-1','demo','business','price x2',['a.py'])
            self.assertFalse(I.stale(db))
            (repo/'a.py').write_text('def calculate_price(x):\n    return x * 3\n');scan(db,'demo')
            self.assertEqual(I.stale(db)[0]['id'],'business-1')
            self.assertFalse(I.quality(db,'t1')['passed'])
            for kind in ['unit','integration','regression']:
                db.execute('INSERT INTO checks(task,repo,kind,status,created_at) VALUES(?,?,?,?,?)',('t1','demo',kind,'pass','now'))
            db.commit();self.assertTrue(I.quality(db,'t1')['passed']);db.close()
if __name__=='__main__':unittest.main()
