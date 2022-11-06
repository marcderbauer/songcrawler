import os
from pathlib import Path
import shutil
def file_empty(path):
    return not (os.path.isfile(path) and os.path.getsize(path) > 0)

def overwrite_dir(path, verbose=False):
    """
    Overwrites a directory no matter the contents. Only used for temp directories
    """
    path = Path(path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    os.mkdir(path)
    if verbose:
        print(f"Force created directory {path}")