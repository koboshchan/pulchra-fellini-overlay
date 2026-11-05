import importlib
import sys

name = "windows" if sys.platform == "win32" else "mac" if sys.platform == "darwin" else "linux"
platform_support = importlib.import_module(name)
