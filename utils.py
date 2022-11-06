import os
from pathlib import Path
import shutil
def file_empty(path):
    return not (os.path.isfile(path) and os.path.getsize(path) > 0)

def delete_dir(path, verbose=False):
    path = Path(path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    if verbose:
        print(f"Deleted dir {path}")

def overwrite_dir(path, verbose=False):
    """
    Overwrites a directory no matter the contents. Only used for temp directories
    """
    delete_dir(path)
    os.mkdir(path)
    if verbose:
        print(f"Force created directory {path}")

