import unittest,tempfile,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from agent_system import advanced as a
class AdvancedTests(unittest.TestCase):
 def test_parser(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x.py';p.write_text('def f(x):\n return x + 1\n')
   r=a.parse_symbols(p);self.assertTrue(any(x['name']=='f' for x in r['symbols']))
 def test_redact(self):
  r=a.redact('email me at person@example.com and password="supersecretpassword123"')
  self.assertNotIn('person@example.com',r['text']);self.assertNotIn('supersecretpassword123',r['text'])
 def test_contract(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'a.json';q=Path(t)/'b.json';p.write_text(json.dumps({'openapi':'3.0.0','paths':{'/x':{'get':{'responses':{'200':{}}}}}}));q.write_text(json.dumps({'openapi':'3.0.0','paths':{}}))
   self.assertEqual(a.contract_diff(p,q)['breaking_candidates'][0]['kind'],'removed_path')
 def test_coverage(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'c.json';p.write_text(json.dumps({'files':{'src/x.py':{'executed_lines':[1],'missing_lines':[2]}}}))
   self.assertEqual(a.coverage_map(p,['x.py'])[0]['missing_lines'],[2])
 def test_mutation(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'logic.py').write_text('def flag():\n return True\n')
   (root/'test_logic.py').write_text('from logic import flag\nassert flag() is True\n')
   r=a.mutation_test(root,'logic.py',[sys.executable,'test_logic.py']);self.assertEqual(r['status'],'killed')
if __name__=='__main__':unittest.main()
