import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
if len(sys.argv)>1 and sys.argv[1]=='advanced':
 from agent_system.advanced_cli import run
 run(sys.argv[2:])
elif len(sys.argv)>1 and sys.argv[1]=='intelligence':
 from agent_system.extended_cli import run
 run(sys.argv[2:])
else:
 from agent_system.cli import main
 main()
