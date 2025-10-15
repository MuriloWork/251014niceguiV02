import sys
import os

path = '/home/muWork01/251014niceguiV02/src'
if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

from main import ui
application = ui.server