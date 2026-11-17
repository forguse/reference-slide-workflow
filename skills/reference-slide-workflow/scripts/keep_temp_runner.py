"""Keep third-party temporary directories; do not modify third-party source or checks."""
import runpy,shutil,sys
from pathlib import Path
def retain(path,*args,**kwargs):print('[Temporary directory retained]',path)
shutil.rmtree=retain
script=Path(sys.argv[1]).resolve();sys.argv=[str(script),*sys.argv[2:]]
sys.path.insert(0,str(script.parent))
runpy.run_path(str(script),run_name='__main__')
