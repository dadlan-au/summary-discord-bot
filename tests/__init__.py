import sys

if sys.version_info < (3, 12):
    raise SystemError("This application requires Python version >= 3.12")
