import sys
import os
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if src_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(src_dir))
from ftm.cli import main
main()
