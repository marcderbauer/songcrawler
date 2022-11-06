import os
def file_empty(path):
    return not (os.path.isfile(path) and os.path.getsize(path) > 0)