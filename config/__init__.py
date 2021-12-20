from .config import *
try:
    from .config_production import *
except ModuleNotFoundError:
    pass
