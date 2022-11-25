import os
import pathlib
import shutil
def file_empty(path):
    return not (os.path.isfile(path) and os.path.getsize(path) > 0)

def delete_dir(path, verbose=False):
    path = pathlib.Path(path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    if verbose:
        print(f"Deleted dir {path}")

def overwrite_dir(path, verbose=False):
    """
    Overwrites a directory no matter the contents. Primarily used for temp directories
    """
    delete_dir(path)
    os.makedirs(path)
    if verbose:
        print(f"Force created directory {path}")

def get_int_input(num_results=10):
    """
    Takes an input and insures that it's of type int
    """
    print("Please enter a valid index.")
    index = None
    while not index:
        try:
            i = input()
            index = int(i)
            if index in range(num_results):
                return index
            else:
                print(f"Please enter a index in range {num_results}")
        except ValueError:
            print("Please enter a valid index")
        finally:
            index = None
    