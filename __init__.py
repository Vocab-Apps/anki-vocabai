import os
import sys
import logging

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)

if hasattr(sys, '_pytest_mode'):
    # don't do anything
    pass 
else:
    # initalize logger, basic logging with debug logging level
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout)])

    # initialize anki addon
    from . import addon
    addon.initialize()