import os
import sys

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)

if hasattr(sys, '_pytest_mode'):
    # don't do anything
    pass 
else:
    # initialize anki addon
    from . import addon
    addon.initialize()