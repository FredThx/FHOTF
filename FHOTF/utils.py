from pathlib import Path

def dict_file(filename):
    filename = Path(filename)
    return {
        'filename' : str(filename),
        'name' : filename.name,
        'suffix' : filename.suffix,
        'path' : filename.drive+filename.stem,
        'basename' : filename.stem,
        'path_basename' : filename.parent/filename.stem
        }
