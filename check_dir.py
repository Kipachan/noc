from pathlib import Path


def check_dir(path):
    if not path.exists():
        Path(path).mkdir()
