from importlib import metadata

__version__ = "unknown"

for _dist_name in ("minichatagent", "miniagent", "amrita"):
    try:
        __version__ = metadata.version(_dist_name)
        break
    except metadata.PackageNotFoundError:
        continue


def get_amrita_version():
    return __version__
