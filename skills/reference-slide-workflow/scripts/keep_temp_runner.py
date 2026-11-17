"""Keep third-party temporary directories; do not modify third-party source or checks."""
import runpy,shutil,sys
def retain(path,*args,**kwargs):print('[Temporary directory retained]',path)
shutil.rmtree=retain
script=sys.argv[1];sys.argv=sys.argv[1:]
runpy.run_path(script,run_name='__main__')
